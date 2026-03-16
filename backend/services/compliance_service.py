"""
Mietpreisbremse compliance engine.

Implements:
- §556d BGB: Mietpreisbremse (rent brake) — max 10% above ortsübliche Vergleichsmiete
- §559 BGB: Modernization rent increase — 8% passthrough with caps
- Simplified Berlin Mietspiegel 2023 lookup

Exceptions handled:
- Post-2014 new builds (Neubau exemption)
- First rental after comprehensive modernization
- Vormiete (previous tenant's rent) exception
"""

import json
from pathlib import Path
from typing import Optional

from backend.models.compliance import (
    ComplianceInput,
    ComplianceResult,
    LocationQuality,
    MietpreisbremseResult,
    MietspiegelLookup,
    ModernizationInput,
    ModernizationResult,
)

# Load Mietspiegel data once at module level
_MIETSPIEGEL_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "mietspiegel_simplified.json"

with open(_MIETSPIEGEL_PATH, "r", encoding="utf-8") as f:
    _MIETSPIEGEL = json.load(f)

RENT_TABLE = _MIETSPIEGEL["rent_table"]
EQUIPMENT_ADJ = _MIETSPIEGEL["equipment_adjustments"]
DISTRICT_LOCATION = _MIETSPIEGEL["district_location_mapping"]
MODERNIZATION_RULES = _MIETSPIEGEL["modernization_rules_559"]

# Mietpreisbremse: max 10% above ortsübliche Vergleichsmiete
MIETPREISBREMSE_PREMIUM = 0.10


def _get_building_year_category(year: int) -> str:
    """Map a building year to the Mietspiegel category key."""
    if year <= 1918:
        return "pre_1918"
    elif year <= 1949:
        return "1919_1949"
    elif year <= 1964:
        return "1950_1964"
    elif year <= 1972:
        return "1965_1972"
    elif year <= 1990:
        return "1973_1990"
    elif year <= 2002:
        return "1991_2002"
    elif year <= 2013:
        return "2003_2013"
    else:
        return "2014_plus"


def _get_size_category(sqm: float) -> str:
    """Map living space to the Mietspiegel size category key."""
    if sqm < 40:
        return "under_40"
    elif sqm < 60:
        return "40_60"
    elif sqm < 90:
        return "60_90"
    else:
        return "over_90"


def _get_location_quality(inp: ComplianceInput) -> str:
    """Determine location quality — use explicit override or derive from district."""
    if inp.location_quality is not None:
        return inp.location_quality.value
    return DISTRICT_LOCATION.get(inp.district, "mittel")


def _compute_equipment_adjustment(inp: ComplianceInput) -> float:
    """Sum equipment adjustments based on apartment features."""
    total = 0.0

    feature_map = {
        "modern_bathroom": inp.has_modern_bathroom,
        "fitted_kitchen": inp.has_fitted_kitchen,
        "balcony": inp.has_balcony,
        "elevator": inp.has_elevator,
        "parquet_flooring": inp.has_parquet_flooring,
        "modern_heating": inp.has_modern_heating,
        "good_insulation": inp.has_good_insulation,
        "basement_storage": inp.has_basement_storage,
    }

    for key, value in feature_map.items():
        if value is None:
            continue
        adj = EQUIPMENT_ADJ[key]
        total += adj["present"] if value else adj["absent"]

    return round(total, 2)


def lookup_mietspiegel(inp: ComplianceInput) -> MietspiegelLookup:
    """Look up the ortsübliche Vergleichsmiete from the simplified Mietspiegel."""
    year_cat = _get_building_year_category(inp.building_year)
    size_cat = _get_size_category(inp.living_space_sqm)
    location = _get_location_quality(inp)

    rent_entry = RENT_TABLE[year_cat][size_cat][location]
    equipment_adj = _compute_equipment_adjustment(inp)

    # Clamp adjusted mid to the Mietspiegel range
    adjusted_mid = round(rent_entry["mid"] + equipment_adj, 2)
    adjusted_mid = max(rent_entry["lower"], min(adjusted_mid, rent_entry["upper"]))

    # Human-readable labels
    year_labels = _MIETSPIEGEL["building_year_categories"]
    size_labels = _MIETSPIEGEL["size_categories"]
    loc_labels = _MIETSPIEGEL["location_quality"]

    return MietspiegelLookup(
        building_year_category=year_labels[year_cat]["label"],
        size_category=size_labels[size_cat]["label"],
        location_quality=loc_labels[location]["label"],
        lower=rent_entry["lower"],
        mid=rent_entry["mid"],
        upper=rent_entry["upper"],
        equipment_adjustment=equipment_adj,
        adjusted_mid=adjusted_mid,
    )


def check_mietpreisbremse(inp: ComplianceInput) -> MietpreisbremseResult:
    """
    Check §556d BGB Mietpreisbremse.

    The legal maximum rent is: ortsübliche Vergleichsmiete × 1.10
    (i.e., max 10% above the local comparative rent).

    Exceptions:
    1. Post-2014 new builds → exempt
    2. First rental after comprehensive modernization → exempt
    3. Previous tenant paid more (Vormiete) → previous rent is the floor
    """
    mietspiegel = lookup_mietspiegel(inp)

    # Exception 1: Neubau (post-Oct 1, 2014 per §556f BGB)
    # Note: The legal cutoff is October 1, 2014 (not January 1).
    # We use building_year >= 2015 as a safe proxy since we don't have
    # the exact first-use date. Buildings from 2014 are edge cases that
    # would need manual verification of the first-use date.
    if inp.building_year >= 2015:
        return MietpreisbremseResult(
            is_exempt=True,
            exemption_reason="Neubau-Ausnahme: Erstmalige Nutzung und Vermietung nach dem 1. Oktober 2014 (§556f BGB)",
            exemption_reason_en="New build exemption: first use and rental after October 1, 2014 (§556f BGB)",
            mietspiegel=mietspiegel,
            legal_max_rent_per_sqm=mietspiegel.upper,  # No cap, use upper as reference
            legal_max_rent_total=round(mietspiegel.upper * inp.living_space_sqm, 2),
        )

    # Exception 2: First rental after comprehensive modernization
    if inp.is_first_rental_after_comprehensive_modernization:
        return MietpreisbremseResult(
            is_exempt=True,
            exemption_reason="Umfassende Modernisierung: Erstvermietung nach umfassender Modernisierung (§556f BGB)",
            exemption_reason_en="Comprehensive modernization: first rental after full modernization (§556f BGB)",
            mietspiegel=mietspiegel,
            legal_max_rent_per_sqm=mietspiegel.upper,
            legal_max_rent_total=round(mietspiegel.upper * inp.living_space_sqm, 2),
        )

    # Standard case: max 10% above ortsübliche Vergleichsmiete
    legal_max = round(mietspiegel.adjusted_mid * (1 + MIETPREISBREMSE_PREMIUM), 2)

    # Exception 3: Vormiete — if previous tenant paid more, that's the floor
    if inp.previous_rent_per_sqm is not None and inp.previous_rent_per_sqm > legal_max:
        legal_max = inp.previous_rent_per_sqm

    return MietpreisbremseResult(
        is_exempt=False,
        exemption_reason=None,
        mietspiegel=mietspiegel,
        legal_max_rent_per_sqm=legal_max,
        legal_max_rent_total=round(legal_max * inp.living_space_sqm, 2),
    )


def check_compliance(inp: ComplianceInput) -> ComplianceResult:
    """
    Full compliance check: Mietspiegel lookup + Mietpreisbremse + recommendation.

    Returns compliance status, overpayment/headroom amounts, and a plain-language recommendation.
    """
    bremse = check_mietpreisbremse(inp)

    # If no current rent provided, we can only return the legal max
    if inp.current_rent_per_sqm is None:
        exempt_de = " Diese Wohnung ist von der Mietpreisbremse ausgenommen." if bremse.is_exempt else ""
        exempt_en = " This apartment is exempt from the rent brake." if bremse.is_exempt else ""
        return ComplianceResult(
            mietpreisbremse=bremse,
            recommendation=(
                f"Maximale zulässige Miete: {bremse.legal_max_rent_per_sqm:.2f} €/m² "
                f"({bremse.legal_max_rent_total:.2f} €/Monat).{exempt_de}"
            ),
            recommendation_en=(
                f"Maximum legal rent: {bremse.legal_max_rent_per_sqm:.2f} €/m² "
                f"({bremse.legal_max_rent_total:.2f} €/month).{exempt_en}"
            ),
        )

    current = inp.current_rent_per_sqm
    legal_max = bremse.legal_max_rent_per_sqm
    sqm = inp.living_space_sqm

    is_compliant = current <= legal_max
    overpayment = max(0.0, round(current - legal_max, 2))
    headroom = max(0.0, round(legal_max - current, 2))

    # Build bilingual recommendations
    if bremse.is_exempt:
        recommendation = (
            f"Diese Wohnung ist von der Mietpreisbremse ausgenommen ({bremse.exemption_reason}). "
            f"Aktuelle Miete: {current:.2f} €/m². "
            f"Mietspiegel-Referenz: {bremse.mietspiegel.adjusted_mid:.2f} €/m² (Mittelwert)."
        )
        recommendation_en = (
            f"This apartment is EXEMPT from the rent brake (Mietpreisbremse). "
            f"Current rent: {current:.2f} €/m². "
            f"Mietspiegel reference: {bremse.mietspiegel.adjusted_mid:.2f} €/m² (midpoint)."
        )
    elif is_compliant and headroom > 0.5:
        recommendation = (
            f"Miete ist gesetzeskonform. "
            f"Spielraum: +{headroom:.2f} €/m² ({headroom * sqm:.0f} €/Monat) "
            f"bis zur gesetzlichen Obergrenze von {legal_max:.2f} €/m²."
        )
        recommendation_en = (
            f"Rent is legally compliant. "
            f"Headroom: +{headroom:.2f} €/m² ({headroom * sqm:.0f} €/month) "
            f"up to the legal ceiling of {legal_max:.2f} €/m²."
        )
    elif is_compliant:
        recommendation = (
            f"Miete ist gesetzeskonform und nahe der Obergrenze. "
            f"Gesetzliches Maximum: {legal_max:.2f} €/m². "
            f"Verbleibender Spielraum: {headroom:.2f} €/m²."
        )
        recommendation_en = (
            f"Rent is legally compliant but near the ceiling. "
            f"Legal maximum: {legal_max:.2f} €/m². "
            f"Remaining headroom: {headroom:.2f} €/m²."
        )
    else:
        recommendation = (
            f"⚠ Miete überschreitet die gesetzliche Obergrenze! "
            f"Aktuelle Miete: {current:.2f} €/m² — Maximum: {legal_max:.2f} €/m². "
            f"Überzahlung: {overpayment:.2f} €/m² ({overpayment * sqm:.0f} €/Monat, "
            f"{overpayment * sqm * 12:.0f} €/Jahr). "
            f"Mieter können die Überzahlung rückwirkend einfordern."
        )
        recommendation_en = (
            f"⚠ Rent EXCEEDS the legal maximum! "
            f"Current rent: {current:.2f} €/m² — Maximum: {legal_max:.2f} €/m². "
            f"Overpayment: {overpayment:.2f} €/m² ({overpayment * sqm:.0f} €/month, "
            f"{overpayment * sqm * 12:.0f} €/year). "
            f"Tenants can retroactively reclaim the overpayment."
        )

    return ComplianceResult(
        mietpreisbremse=bremse,
        current_rent_per_sqm=current,
        is_compliant=is_compliant,
        overpayment_per_sqm=overpayment,
        overpayment_total_monthly=round(overpayment * sqm, 2),
        overpayment_annual=round(overpayment * sqm * 12, 2),
        headroom_per_sqm=headroom,
        headroom_total_monthly=round(headroom * sqm, 2),
        recommendation=recommendation,
        recommendation_en=recommendation_en,
    )


def calculate_modernization_increase(inp: ModernizationInput) -> ModernizationResult:
    """
    Calculate §559 or §559e BGB modernization rent increase.

    Standard path (§559 BGB):
    - 8% of eligible modernization costs can be added to annual rent
    - Maintenance costs must be subtracted (not eligible)
    - Cap: if rent ≤ €7/m² → max +€2/m² in 6 years
    - Cap: if rent > €7/m² → max +€3/m² in 6 years

    GEG heating path (§559e BGB, since Jan 2024):
    - 10% of eligible cost (after subsidies and maintenance) to annual rent
    - Hard cap: max €0.50/m²/month regardless of rent level
    """
    # Step 1: Eligible cost = total - maintenance share - subsidies (for §559e)
    eligible_cost = inp.modernization_cost * (1 - inp.maintenance_share)
    if inp.is_geg_heating_replacement:
        eligible_cost = max(0, eligible_cost - inp.public_subsidy)

    # Step 2: Annual increase depends on path
    if inp.is_geg_heating_replacement:
        # §559e: 10% passthrough rate
        passthrough_rate = 0.10
    else:
        # §559: 8% passthrough rate
        passthrough_rate = MODERNIZATION_RULES["passthrough_rate"]

    annual_increase = eligible_cost * passthrough_rate

    # Step 3: Convert to monthly per m²
    monthly_increase_uncapped = annual_increase / 12 / inp.living_space_sqm

    # Step 4: Apply cap
    if inp.is_geg_heating_replacement:
        # §559e: hard cap of €0.50/m²/month
        cap_type = "geg_heating"
        monthly_increase = min(monthly_increase_uncapped, 0.50)
        remaining_headroom = 0.50
        cap_applies = monthly_increase < monthly_increase_uncapped
    else:
        # §559: 6-year rolling cap based on current rent level
        if inp.current_rent_per_sqm <= MODERNIZATION_RULES["cap_low_rent"]["threshold_rent_per_sqm"]:
            cap_type = "low_rent"
            max_6yr = MODERNIZATION_RULES["cap_low_rent"]["max_increase_per_sqm_6yr"]
        else:
            cap_type = "high_rent"
            max_6yr = MODERNIZATION_RULES["cap_high_rent"]["max_increase_per_sqm_6yr"]

        remaining_headroom = max(0.0, max_6yr - inp.prior_increases_6yr)
        monthly_increase = min(monthly_increase_uncapped, remaining_headroom)
        cap_applies = monthly_increase < monthly_increase_uncapped

    new_rent = inp.current_rent_per_sqm + monthly_increase

    return ModernizationResult(
        eligible_cost=round(eligible_cost, 2),
        annual_increase_uncapped=round(annual_increase, 2),
        monthly_increase_per_sqm_uncapped=round(monthly_increase_uncapped, 2),
        cap_applies=cap_applies,
        cap_type=cap_type,
        remaining_cap_headroom=round(remaining_headroom, 2),
        monthly_increase_per_sqm=round(monthly_increase, 2),
        monthly_increase_total=round(monthly_increase * inp.living_space_sqm, 2),
        new_rent_per_sqm=round(new_rent, 2),
        new_rent_total=round(new_rent * inp.living_space_sqm, 2),
    )
