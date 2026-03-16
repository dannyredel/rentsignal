"""Mieterhöhung (rent increase) calculator — §558 BGB.

Separate from Mietpreisbremse (§556d, which governs NEW leases).
§558 governs rent increases on EXISTING tenants.

Rules:
- Landlord can raise rent to Mietspiegel mid value (ortsübliche Vergleichsmiete)
- Kappungsgrenze: max 15% increase within any 3-year period (Berlin: 15%, most cities: 20%)
- 15-month minimum between increases
- Formal written request required (Mieterhöhungsverlangen)
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.auth import User, get_current_user
from backend.services.compliance_service import lookup_mietspiegel
from backend.tier import check_tier

router = APIRouter(prefix="/rent-increase", tags=["rent-increase"])

# Berlin uses 15% Kappungsgrenze (stricter than the federal 20%)
KAPPUNGSGRENZE_PCT = 0.15
MIN_MONTHS_BETWEEN_INCREASES = 15


class RentIncreaseInput(BaseModel):
    """Input for §558 BGB rent increase calculation."""

    current_rent_per_sqm: float = Field(..., gt=0, description="Current nettokalt rent €/m²")
    living_space_sqm: float = Field(..., gt=0)
    building_year: int = Field(..., ge=1800, le=2030)
    district: str

    # Equipment (for Mietspiegel lookup)
    has_modern_bathroom: Optional[bool] = None
    has_fitted_kitchen: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_elevator: Optional[bool] = None
    has_parquet_flooring: Optional[bool] = None
    has_modern_heating: Optional[bool] = None
    has_good_insulation: Optional[bool] = None
    has_basement_storage: Optional[bool] = None
    location_quality: Optional[str] = None

    # Timing
    last_increase_date: Optional[date] = None
    rent_3_years_ago: Optional[float] = Field(
        None, description="Rent 3 years ago in €/m² (for Kappungsgrenze check)"
    )


class RentIncreaseResult(BaseModel):
    """§558 BGB rent increase calculation result."""

    can_increase: bool
    reason: str
    reason_en: str

    # Mietspiegel reference
    mietspiegel_mid: float = Field(..., description="Mietspiegel mid value €/m²")
    mietspiegel_upper: float

    # Increase limits
    max_rent_mietspiegel: float = Field(..., description="Max rent from Mietspiegel mid €/m²")
    max_rent_kappungsgrenze: Optional[float] = Field(
        None, description="Max rent from 15% cap over 3 years €/m²"
    )
    effective_max_rent: float = Field(..., description="Lower of Mietspiegel and Kappungsgrenze €/m²")
    max_increase_sqm: float = Field(..., description="Maximum increase €/m²")
    max_increase_total: float = Field(..., description="Maximum monthly increase €")
    max_increase_annual: float = Field(..., description="Maximum annual increase €")

    # Timing
    earliest_increase_date: Optional[date] = None
    can_increase_now: bool = True


@router.post("/calculate", response_model=RentIncreaseResult)
async def calculate_rent_increase(
    data: RentIncreaseInput,
    user: User = Depends(get_current_user),
):
    """Calculate maximum §558 BGB rent increase for an existing tenant."""
    await check_tier(user, "pro")

    # Look up Mietspiegel mid value
    equipment_flags = {
        "has_modern_bathroom": data.has_modern_bathroom,
        "has_fitted_kitchen": data.has_fitted_kitchen,
        "has_balcony": data.has_balcony,
        "has_elevator": data.has_elevator,
        "has_parquet_flooring": data.has_parquet_flooring,
        "has_modern_heating": data.has_modern_heating,
        "has_good_insulation": data.has_good_insulation,
        "has_basement_storage": data.has_basement_storage,
    }
    mietspiegel = lookup_mietspiegel(
        building_year=data.building_year,
        living_space_sqm=data.living_space_sqm,
        district=data.district,
        location_quality=data.location_quality,
        **{k: v for k, v in equipment_flags.items() if v is not None},
    )

    mietspiegel_mid = mietspiegel["adjusted_mid"]
    mietspiegel_upper = mietspiegel["upper"]

    # §558: can raise up to Mietspiegel mid
    max_from_mietspiegel = mietspiegel_mid

    # Kappungsgrenze: max 15% over 3 years
    max_from_kappung = None
    if data.rent_3_years_ago:
        max_from_kappung = data.rent_3_years_ago * (1 + KAPPUNGSGRENZE_PCT)

    # Effective max = lower of the two constraints
    if max_from_kappung is not None:
        effective_max = min(max_from_mietspiegel, max_from_kappung)
    else:
        effective_max = max_from_mietspiegel

    max_increase = max(0, effective_max - data.current_rent_per_sqm)

    # Timing check
    can_increase_now = True
    earliest_date = None
    if data.last_increase_date:
        earliest_date = data.last_increase_date + timedelta(days=MIN_MONTHS_BETWEEN_INCREASES * 30)
        can_increase_now = date.today() >= earliest_date

    # Build result
    can_increase = max_increase > 0 and can_increase_now

    if max_increase <= 0:
        reason = "Miete liegt bereits auf oder über dem Mietspiegel-Mittelwert."
        reason_en = "Rent is already at or above the Mietspiegel mid value."
    elif not can_increase_now:
        reason = f"Nächste Mieterhöhung erst ab {earliest_date.isoformat()} möglich (15-Monats-Frist)."
        reason_en = f"Next increase possible from {earliest_date.isoformat()} (15-month minimum)."
    else:
        reason = f"Mieterhöhung um bis zu €{max_increase:.2f}/m² möglich."
        reason_en = f"Rent increase of up to €{max_increase:.2f}/m² is possible."

    return RentIncreaseResult(
        can_increase=can_increase,
        reason=reason,
        reason_en=reason_en,
        mietspiegel_mid=mietspiegel_mid,
        mietspiegel_upper=mietspiegel_upper,
        max_rent_mietspiegel=max_from_mietspiegel,
        max_rent_kappungsgrenze=max_from_kappung,
        effective_max_rent=effective_max,
        max_increase_sqm=max_increase,
        max_increase_total=round(max_increase * data.living_space_sqm, 2),
        max_increase_annual=round(max_increase * data.living_space_sqm * 12, 2),
        earliest_increase_date=earliest_date,
        can_increase_now=can_increase_now,
    )
