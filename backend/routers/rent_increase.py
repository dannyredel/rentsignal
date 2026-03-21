"""Mieterhöhung (rent increase) calculator — §558 BGB.

Separate from Mietpreisbremse (§556d, which governs NEW leases).
§558 governs rent increases on EXISTING tenants.

Rules:
- Landlord can raise rent to Mietspiegel mid value (ortsübliche Vergleichsmiete)
- Kappungsgrenze: max 15% increase within any 3-year period (Berlin: 15%, most cities: 20%)
- 15-month minimum between increases
- Formal written request required (Mieterhöhungsverlangen)
"""

import json
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.auth import User, get_current_user
from backend.models.compliance import ComplianceInput
from backend.services.compliance_service import lookup_mietspiegel
from backend.supabase_client import get_supabase
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


# ---------------------------------------------------------------------------
# Portfolio-level rent increase calculator
# ---------------------------------------------------------------------------

# Map modern merged district names to old Bezirk names for Mietspiegel lookup
_DISTRICT_MAP = {
    "Charlottenburg-Wilmersdorf": "Charlottenburg",
    "Friedrichshain-Kreuzberg": "Kreuzberg",
    "Marzahn-Hellersdorf": "Marzahn",
    "Steglitz-Zehlendorf": "Steglitz",
    "Tempelhof-Schöneberg": "Tempelhof",
    "Treptow-Köpenick": "Treptow",
    "Mitte": "Mitte",
    "Neukölln": "Neukölln",
    "Pankow": "Pankow",
    "Lichtenberg": "Lichtenberg",
    "Reinickendorf": "Reinickendorf",
    "Spandau": "Spandau",
    # Nominatim sometimes returns suburb names directly
    "Wilmersdorf": "Wilmersdorf",
    "Charlottenburg": "Charlottenburg",
    "Kreuzberg": "Kreuzberg",
    "Friedrichshain": "Friedrichshain",
    "Schöneberg": "Schöneberg",
    "Tempelhof": "Tempelhof",
    "Steglitz": "Steglitz",
    "Zehlendorf": "Zehlendorf",
    "Neukölln": "Neukölln",
    "Treptow": "Treptow",
    "Köpenick": "Köpenick",
    "Marzahn": "Marzahn",
    "Hellersdorf": "Hellersdorf",
    "Hohenschönhausen": "Hohenschönhausen",
    "Lichtenberg": "Lichtenberg",
    "Weißensee": "Weißensee",
    "Pankow": "Pankow",
    "Reinickendorf": "Reinickendorf",
    "Wedding": "Wedding",
    "Prenzlauer Berg": "Prenzlauer Berg",
}


def _calc_increase_for_unit(unit: dict) -> dict:
    """Calculate rent increase potential for a single portfolio unit."""
    current_sqm = float(unit.get("current_rent_per_sqm", 0) or 0)
    sqm = float(unit.get("living_space_sqm", 60))
    year = int(unit.get("year_built", 1960) or 1960)
    raw_district = unit.get("district", "")

    # Map to Bezirk name the Mietspiegel expects
    district = _DISTRICT_MAP.get(raw_district, raw_district)

    if current_sqm <= 0:
        return {"unit_id": unit.get("id"), "address": unit.get("address"), "can_increase": False,
                "reason": "No current rent set"}

    try:
        compliance_input = ComplianceInput(
            district=district,
            living_space_sqm=sqm,
            building_year=year,
            current_rent_per_sqm=current_sqm,
            has_fitted_kitchen=unit.get("has_kitchen"),
            has_balcony=unit.get("has_balcony"),
            has_elevator=unit.get("has_elevator"),
        )
        mietspiegel = lookup_mietspiegel(compliance_input)
    except Exception as e:
        return {"unit_id": unit.get("id"), "address": unit.get("address"), "can_increase": False,
                "reason": f"Mietspiegel lookup failed: {str(e)[:50]}"}

    mietspiegel_mid = mietspiegel.adjusted_mid if hasattr(mietspiegel, 'adjusted_mid') else mietspiegel.get("adjusted_mid", 0)
    max_increase = max(0, mietspiegel_mid - current_sqm)

    # Kappungsgrenze
    prior_sqm = float(unit.get("previous_rent_per_sqm", 0) or 0)
    kappung_max = None
    if prior_sqm > 0:
        kappung_max = prior_sqm * (1 + KAPPUNGSGRENZE_PCT)
        effective_max = min(mietspiegel_mid, kappung_max)
        max_increase = max(0, effective_max - current_sqm)

    # Timing
    last_increase = unit.get("last_rent_increase_date")
    can_now = True
    earliest = None
    if last_increase:
        try:
            if isinstance(last_increase, str):
                last_increase = date.fromisoformat(last_increase)
            earliest = last_increase + timedelta(days=MIN_MONTHS_BETWEEN_INCREASES * 30)
            can_now = date.today() >= earliest
        except (ValueError, TypeError):
            pass

    return {
        "unit_id": unit.get("id"),
        "address": unit.get("address", "Unknown"),
        "plz": str(unit.get("plz", "")),
        "living_space_sqm": sqm,
        "current_rent_sqm": current_sqm,
        "mietspiegel_mid": mietspiegel_mid,
        "max_increase_sqm": round(max_increase, 2),
        "max_increase_monthly": round(max_increase * sqm, 2),
        "max_increase_annual": round(max_increase * sqm * 12, 2),
        "new_rent_sqm": round(current_sqm + max_increase, 2),
        "new_rent_monthly": round((current_sqm + max_increase) * sqm, 2),
        "can_increase": max_increase > 0 and can_now,
        "can_increase_now": can_now,
        "earliest_date": earliest.isoformat() if earliest else None,
        "kappungsgrenze_max": round(kappung_max, 2) if kappung_max else None,
    }


@router.get("/portfolio")
async def portfolio_rent_increases(user: User = Depends(get_current_user)):
    """Calculate rent increase potential for all units in portfolio."""
    sb = get_supabase()
    resp = sb.table("units").select("*").eq("user_id", user.user_id).execute()
    units = resp.data or []

    results = [_calc_increase_for_unit(u) for u in units]
    can_increase = [r for r in results if r.get("can_increase")]
    total_monthly = sum(r.get("max_increase_monthly", 0) for r in can_increase)
    total_annual = sum(r.get("max_increase_annual", 0) for r in can_increase)

    return {
        "units": results,
        "summary": {
            "total_units": len(results),
            "units_can_increase": len(can_increase),
            "total_monthly_uplift": round(total_monthly, 2),
            "total_annual_uplift": round(total_annual, 2),
        },
    }


# ---------------------------------------------------------------------------
# Letter generation
# ---------------------------------------------------------------------------

@router.post("/letter/{unit_id}")
async def generate_rent_increase_letter(
    unit_id: str,
    target_rent_sqm: Optional[float] = None,
    user: User = Depends(get_current_user),
):
    """Generate a formal §558a BGB Mieterhöhungsverlangen letter for a unit.

    If target_rent_sqm is not provided, uses the maximum allowed increase.
    """
    sb = get_supabase()
    resp = sb.table("units").select("*").eq("id", unit_id).eq("user_id", user.user_id).execute()
    if not resp.data:
        return {"error": "Unit not found"}

    unit = resp.data[0]
    calc = _calc_increase_for_unit(unit)

    if not calc.get("can_increase"):
        return {"error": "No rent increase possible", "reason": calc.get("reason", "Unknown")}

    # Use target or max
    increase_sqm = target_rent_sqm - calc["current_rent_sqm"] if target_rent_sqm else calc["max_increase_sqm"]
    increase_sqm = min(increase_sqm, calc["max_increase_sqm"])  # can't exceed max
    new_rent_sqm = calc["current_rent_sqm"] + increase_sqm
    sqm = calc["living_space_sqm"]

    # Effective dates: §558 requires 2 months notice + end of month
    today = date.today()
    # Tenant has until end of 2nd month after receipt to agree
    consent_deadline = today + timedelta(days=75)  # ~2.5 months
    # New rent takes effect 3rd month after receipt
    effective_date = today + timedelta(days=90)  # ~3 months

    letter = {
        "letter_type": "§558a BGB Mieterhöhungsverlangen",
        "date": today.isoformat(),
        "address": unit.get("address", ""),
        "plz": str(unit.get("plz", "")),
        "current_rent_sqm": calc["current_rent_sqm"],
        "current_rent_total": round(calc["current_rent_sqm"] * sqm, 2),
        "new_rent_sqm": round(new_rent_sqm, 2),
        "new_rent_total": round(new_rent_sqm * sqm, 2),
        "increase_sqm": round(increase_sqm, 2),
        "increase_total": round(increase_sqm * sqm, 2),
        "increase_pct": round(increase_sqm / calc["current_rent_sqm"] * 100, 1),
        "mietspiegel_mid": calc["mietspiegel_mid"],
        "mietspiegel_reference": f"Berliner Mietspiegel 2024, {unit.get('year_built', '?')}, {sqm}m²",
        "consent_deadline": consent_deadline.isoformat(),
        "effective_date": effective_date.isoformat(),
        "living_space_sqm": sqm,
        "legal_basis": "§558 Abs. 1 BGB i.V.m. §558a Abs. 2 Nr. 1 BGB",
        "letter_text_de": _generate_letter_de(
            address=unit.get("address", ""),
            current_total=round(calc["current_rent_sqm"] * sqm, 2),
            new_total=round(new_rent_sqm * sqm, 2),
            increase_total=round(increase_sqm * sqm, 2),
            mietspiegel_mid=calc["mietspiegel_mid"],
            sqm=sqm,
            consent_deadline=consent_deadline,
            effective_date=effective_date,
        ),
        "timeline": [
            {"step": 1, "date": today.isoformat(), "action": "Send letter to tenant",
             "detail": "Per Post (Einschreiben empfohlen) oder persönliche Übergabe"},
            {"step": 2, "date": consent_deadline.isoformat(), "action": "Tenant consent deadline",
             "detail": "Mieter hat bis Ende des 2. Monats nach Zugang Zeit zuzustimmen"},
            {"step": 3, "date": effective_date.isoformat(), "action": "New rent takes effect",
             "detail": "Neue Miete gilt ab Beginn des 3. Monats nach Zugang"},
        ],
    }

    return letter


def _generate_letter_de(address, current_total, new_total, increase_total,
                        mietspiegel_mid, sqm, consent_deadline, effective_date):
    """Generate formal German rent increase letter text."""
    return f"""Mieterhöhungsverlangen gemäß §558 BGB

Sehr geehrte Mieterin, sehr geehrter Mieter,

hiermit verlange ich die Zustimmung zur Erhöhung der Nettokaltmiete für die Wohnung

    {address}

Die derzeitige Nettokaltmiete beträgt {current_total:.2f} € monatlich.

Ich verlange die Zustimmung zur Erhöhung der Nettokaltmiete auf {new_total:.2f} € monatlich
(Erhöhung um {increase_total:.2f} €).

Begründung:
Die verlangte Miete überschreitet nicht die ortsübliche Vergleichsmiete gemäß dem
Berliner Mietspiegel 2024. Der Mittelwert für vergleichbare Wohnungen ({sqm:.0f} m²)
beträgt {mietspiegel_mid:.2f} €/m².

Rechtsgrundlage: §558 Abs. 1 BGB i.V.m. §558a Abs. 2 Nr. 1 BGB.

Ich bitte um Ihre Zustimmung bis zum {consent_deadline.strftime('%d.%m.%Y')}.
Die erhöhte Miete ist ab dem {effective_date.strftime('%d.%m.%Y')} zu entrichten.

Mit freundlichen Grüßen,

[Vermieter/in]

---
Hinweis: Dieses Schreiben wurde mit RentSignal erstellt. Es ersetzt keine Rechtsberatung.
Für verbindliche Rechtsauskunft wenden Sie sich bitte an einen Fachanwalt für Mietrecht."""
