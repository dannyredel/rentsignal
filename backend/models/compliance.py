"""Pydantic schemas for the Mietpreisbremse compliance engine."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LocationQuality(str, Enum):
    einfach = "einfach"
    mittel = "mittel"
    gut = "gut"


class ComplianceInput(BaseModel):
    """Input for the Mietpreisbremse compliance check."""

    district: str = Field(..., description="Berlin district (Bezirk), e.g. 'Friedrichshain-Kreuzberg'")
    living_space_sqm: float = Field(..., gt=0, description="Living space in m²")
    building_year: int = Field(..., ge=1800, le=2030, description="Year the building was constructed")
    current_rent_per_sqm: Optional[float] = Field(None, ge=0, description="Current base rent in €/m² (nettokalt)")
    previous_rent_per_sqm: Optional[float] = Field(None, ge=0, description="Previous tenant's rent in €/m² (Vormiete)")

    # Equipment features for Mietspiegel adjustment
    has_modern_bathroom: Optional[bool] = None
    has_fitted_kitchen: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_elevator: Optional[bool] = None
    has_parquet_flooring: Optional[bool] = None
    has_modern_heating: Optional[bool] = None
    has_good_insulation: Optional[bool] = None
    has_basement_storage: Optional[bool] = None

    # Location override (if known, otherwise derived from district)
    location_quality: Optional[LocationQuality] = None

    # Modernization context
    is_first_rental_after_comprehensive_modernization: bool = False


class MietspiegelLookup(BaseModel):
    """Result of the Mietspiegel table lookup."""

    building_year_category: str
    size_category: str
    location_quality: str
    lower: float = Field(..., description="Lower bound €/m²")
    mid: float = Field(..., description="Mid-point €/m²")
    upper: float = Field(..., description="Upper bound €/m²")
    equipment_adjustment: float = Field(0.0, description="Equipment adjustment €/m²")
    adjusted_mid: float = Field(..., description="Mid-point after equipment adjustment €/m²")


class MietpreisbremseResult(BaseModel):
    """Result of the §556d BGB Mietpreisbremse check."""

    is_exempt: bool = Field(..., description="True if apartment is exempt from Mietpreisbremse")
    exemption_reason: Optional[str] = Field(None, description="Why the apartment is exempt (German)")
    exemption_reason_en: Optional[str] = Field(None, description="Why the apartment is exempt (English)")
    mietspiegel: MietspiegelLookup
    legal_max_rent_per_sqm: float = Field(..., description="Maximum legal rent in €/m²")
    legal_max_rent_total: float = Field(..., description="Maximum legal rent total €/month")


class ComplianceResult(BaseModel):
    """Full compliance check result."""

    mietpreisbremse: MietpreisbremseResult
    current_rent_per_sqm: Optional[float] = None
    is_compliant: Optional[bool] = Field(None, description="True if current rent ≤ legal max")
    overpayment_per_sqm: Optional[float] = Field(None, description="Amount above legal max in €/m² (0 if compliant)")
    overpayment_total_monthly: Optional[float] = Field(None, description="Monthly overpayment in €")
    overpayment_annual: Optional[float] = Field(None, description="Annual overpayment in €")
    headroom_per_sqm: Optional[float] = Field(None, description="Room to increase rent within legal bounds €/m²")
    headroom_total_monthly: Optional[float] = Field(None, description="Monthly headroom in €")
    recommendation: str = Field(..., description="German recommendation for the landlord")
    recommendation_en: str = Field(..., description="English recommendation for the landlord")


class ModernizationInput(BaseModel):
    """Input for §559 BGB modernization rent increase calculation."""

    current_rent_per_sqm: float = Field(..., gt=0, description="Current base rent in €/m²")
    living_space_sqm: float = Field(..., gt=0, description="Living space in m²")
    modernization_cost: float = Field(..., gt=0, description="Total modernization cost in €")
    maintenance_share: float = Field(
        0.0, ge=0, le=1,
        description="Share of cost that is maintenance (not modernization), 0-1"
    )
    prior_increases_6yr: float = Field(
        0.0, ge=0,
        description="Sum of §559 rent increases in the past 6 years in €/m²"
    )
    is_geg_heating_replacement: bool = Field(
        False,
        description="True if this is a heating replacement under GEG (§559e BGB). "
        "Uses 10% passthrough rate with €0.50/m²/month cap instead of standard §559."
    )
    public_subsidy: float = Field(
        0.0, ge=0,
        description="Public subsidies received for the modernization in € (deducted from cost for §559e)"
    )


class ModernizationResult(BaseModel):
    """Result of §559 BGB modernization rent increase calculation."""

    eligible_cost: float = Field(..., description="Modernization cost minus maintenance share, in €")
    annual_increase_uncapped: float = Field(..., description="8% of eligible cost, per year, in €")
    monthly_increase_per_sqm_uncapped: float = Field(..., description="Uncapped monthly increase per m²")
    cap_applies: bool
    cap_type: str = Field(..., description="'low_rent' (≤€7) or 'high_rent' (>€7)")
    remaining_cap_headroom: float = Field(..., description="Remaining increase allowed under 6-year cap, €/m²")
    monthly_increase_per_sqm: float = Field(..., description="Actual increase after cap, €/m²")
    monthly_increase_total: float = Field(..., description="Actual monthly increase, total €")
    new_rent_per_sqm: float = Field(..., description="Rent after modernization increase, €/m²")
    new_rent_total: float = Field(..., description="New total monthly rent, €")
