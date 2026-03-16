"""CO2KostAufG energy compliance — landlord CO2 cost-sharing calculation.

Since 2023, landlords of energy-inefficient buildings pay a share of tenant
carbon costs. The share depends on the building's energy class (CO2 emissions
per m² per year). This directly reduces net rental income.

CO2 price schedule:
- 2024: €45/tonne
- 2025: €55/tonne
- 2026: €65/tonne (expected)
"""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.auth import User, get_current_user
from backend.tier import check_tier

router = APIRouter(tags=["compliance"])

# CO2KostAufG: landlord share by building CO2 class
# Based on kg CO2/m²/year emissions
CO2_SHARING_TABLE = [
    # (min_kg, max_kg, landlord_share_pct, tenant_share_pct)
    (0, 12, 0, 100),       # Very efficient — tenant pays all
    (12, 17, 10, 90),
    (17, 22, 20, 80),
    (22, 27, 30, 70),
    (27, 32, 40, 60),
    (32, 37, 50, 50),
    (37, 42, 60, 40),
    (42, 47, 70, 30),
    (47, 52, 80, 20),
    (52, float("inf"), 90, 10),  # Very inefficient — landlord pays 90%
]

# Energy class boundaries (kWh/m²/year) per Energieausweis
ENERGY_CLASS_BINS = [
    (0, 30, "A+"), (30, 50, "A"), (50, 75, "B"), (75, 100, "C"),
    (100, 130, "D"), (130, 160, "E"), (160, 200, "F"), (200, 250, "G"),
    (250, float("inf"), "H"),
]

# Approximate CO2 emissions by energy class (kg CO2/m²/year)
# Based on typical gas heating — used as fallback when thermalChar not provided
ENERGY_CLASS_TO_CO2 = {
    "A+": 5, "A": 10, "B": 15, "C": 25, "D": 35,
    "E": 45, "F": 60, "G": 80, "H": 120,
}

# CO2 emission factors by heating type (kg CO2 per kWh) — Source: UBA 2024
EMISSION_FACTORS = {
    "gas": 0.201, "central_heating": 0.201, "self_contained_central_heating": 0.201,
    "oil": 0.266, "oil_heating": 0.266,
    "district": 0.130, "district_heating": 0.130, "combined_heat_and_power_plant": 0.130,
    "floor_heating": 0.201, "heat_pump": 0.045,
    "electric": 0.420, "electric_heating": 0.420, "night_storage_heater": 0.420,
    "solar": 0.020, "solar_heating": 0.020,
    "wood_pellet": 0.023, "wood_pellet_heating": 0.023,
    "stove_heating": 0.266,
}

# CO2 price in €/tonne by year
CO2_PRICE = {2024: 45, 2025: 55, 2026: 65}


def derive_energy_class(thermal_char: float) -> str:
    """Derive Energieausweis class from kWh/m²/year."""
    for low, high, cls in ENERGY_CLASS_BINS:
        if low <= thermal_char < high:
            return cls
    return "H"


class EnergyComplianceInput(BaseModel):
    """Input for CO2KostAufG calculation."""

    energy_class: Optional[str] = Field(None, description="Building energy class (A+ to H). Auto-derived from thermal_char if not provided.")
    thermal_char: Optional[float] = Field(None, description="Energy consumption kWh/m²/year (from Energieausweis). If provided, energy_class is auto-derived.")
    living_space_sqm: float = Field(..., gt=0)
    co2_kg_per_sqm: Optional[float] = Field(
        None, description="CO2 emissions kg/m²/year (if known, overrides calculation from thermal_char)"
    )
    heating_fuel: str = Field("gas", description="Heating fuel type: gas, oil, district, heat_pump")
    year: int = Field(2026, description="Year for CO2 price lookup")


class EnergyComplianceResult(BaseModel):
    """CO2KostAufG calculation result."""

    energy_class: str
    co2_kg_per_sqm: float = Field(..., description="CO2 emissions kg/m²/year")
    co2_total_kg: float = Field(..., description="Total annual CO2 emissions kg")

    landlord_share_pct: int
    tenant_share_pct: int

    co2_price_per_tonne: float
    total_co2_cost: float = Field(..., description="Total annual CO2 cost €")
    landlord_cost_annual: float = Field(..., description="Landlord's annual CO2 cost share €")
    landlord_cost_monthly: float = Field(..., description="Landlord's monthly CO2 cost share €")
    landlord_cost_per_sqm_monthly: float = Field(..., description="Landlord's CO2 cost per m²/month €")

    severity: str = Field(..., description="none, low, medium, high, critical")
    recommendation: str
    recommendation_en: str


@router.post("/compliance/energy", response_model=EnergyComplianceResult)
async def energy_compliance(
    data: EnergyComplianceInput,
    user: User = Depends(get_current_user),
):
    """Calculate landlord CO2 cost-sharing under CO2KostAufG."""
    await check_tier(user, "pro")

    # Derive energy class from thermal_char if not provided
    energy_class = data.energy_class
    if data.thermal_char is not None and not energy_class:
        energy_class = derive_energy_class(data.thermal_char)
    elif not energy_class:
        energy_class = "D"  # default if nothing provided

    # Get CO2 emissions (kg CO2/m²/year)
    if data.co2_kg_per_sqm is not None:
        co2_kg = data.co2_kg_per_sqm
    elif data.thermal_char is not None:
        # Precise: thermal_char × emission factor for heating type
        emission_factor = EMISSION_FACTORS.get(data.heating_fuel, 0.201)
        co2_kg = data.thermal_char * emission_factor
    else:
        # Fallback: estimate from energy class (assumes gas)
        co2_kg = ENERGY_CLASS_TO_CO2.get(energy_class, 50)

    # Look up sharing percentage
    landlord_pct = 0
    tenant_pct = 100
    for min_kg, max_kg, l_pct, t_pct in CO2_SHARING_TABLE:
        if min_kg <= co2_kg < max_kg:
            landlord_pct = l_pct
            tenant_pct = t_pct
            break

    # Calculate costs
    co2_total_kg = co2_kg * data.living_space_sqm
    co2_price = CO2_PRICE.get(data.year, 65)
    total_cost = (co2_total_kg / 1000) * co2_price  # convert kg to tonnes
    landlord_cost = total_cost * (landlord_pct / 100)

    # Severity
    if landlord_pct == 0:
        severity = "none"
    elif landlord_pct <= 20:
        severity = "low"
    elif landlord_pct <= 50:
        severity = "medium"
    elif landlord_pct <= 70:
        severity = "high"
    else:
        severity = "critical"

    # Recommendations
    if landlord_pct == 0:
        rec_de = "Keine CO2-Kostenbeteiligung erforderlich. Ihr Gebäude ist effizient."
        rec_en = "No CO2 cost-sharing required. Your building is efficient."
    elif landlord_pct <= 30:
        rec_de = f"CO2-Kostenanteil: {landlord_pct}% (€{landlord_cost:.0f}/Jahr). Moderate Belastung."
        rec_en = f"CO2 cost share: {landlord_pct}% (€{landlord_cost:.0f}/year). Moderate exposure."
    else:
        rec_de = (
            f"CO2-Kostenanteil: {landlord_pct}% (€{landlord_cost:.0f}/Jahr). "
            f"Energetische Sanierung empfohlen — prüfen Sie KfW-Förderprogramme."
        )
        rec_en = (
            f"CO2 cost share: {landlord_pct}% (€{landlord_cost:.0f}/year). "
            f"Energy renovation recommended — check KfW subsidy programs."
        )

    return EnergyComplianceResult(
        energy_class=energy_class,
        co2_kg_per_sqm=co2_kg,
        co2_total_kg=co2_total_kg,
        landlord_share_pct=landlord_pct,
        tenant_share_pct=tenant_pct,
        co2_price_per_tonne=co2_price,
        total_co2_cost=round(total_cost, 2),
        landlord_cost_annual=round(landlord_cost, 2),
        landlord_cost_monthly=round(landlord_cost / 12, 2),
        landlord_cost_per_sqm_monthly=round(landlord_cost / 12 / data.living_space_sqm, 2),
        severity=severity,
        recommendation=rec_de,
        recommendation_en=rec_en,
    )
