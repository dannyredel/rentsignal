"""Pydantic schemas for apartment input/output."""

from typing import Optional

from pydantic import BaseModel, Field


class ApartmentInput(BaseModel):
    """Input for rent prediction — raw apartment features."""

    district: str = Field(..., description="Berlin district (Bezirk)")
    plz: Optional[int] = Field(None, description="Postal code for spatial features")
    living_space_sqm: float = Field(..., gt=0, alias="livingSpace")
    rooms: float = Field(..., gt=0, alias="noRooms")
    year_built: int = Field(..., ge=1800, le=2030, alias="yearConstructed")
    floor: int = Field(0, ge=0)
    building_floors: int = Field(1, ge=1, alias="numberOfFloors")
    thermal_char: float = Field(100, ge=0, alias="thermalChar")

    # Binary amenities
    has_kitchen: bool = Field(False, alias="hasKitchen")
    has_balcony: bool = Field(False, alias="balcony")
    has_elevator: bool = Field(False, alias="lift")
    has_cellar: bool = Field(False, alias="cellar")
    has_garden: bool = Field(False, alias="garden")
    is_new_construction: bool = Field(False, alias="newlyConst")

    # Categorical
    condition: str = "well_kept"
    interior_quality: str = Field("normal", alias="interiorQual")
    flat_type: str = Field("apartment", alias="typeOfFlat")
    heating_type: str = Field("central_heating", alias="heatingType")
    building_era: str = Field("pre_1918")
    bezirk: Optional[str] = Field(None, description="Bezirk override (defaults to district)")

    # Optional: current rent for gap analysis
    current_rent_per_sqm: Optional[float] = Field(None, alias="current_rent_sqm")

    # Optional: coordinates for unit-level spatial features (v4.2)
    lat: Optional[float] = Field(None, description="Latitude WGS84 (for unit-level spatial)")
    lon: Optional[float] = Field(None, description="Longitude WGS84 (for unit-level spatial)")

    # Optional: enrichment features (from photo upload or URL scrape)
    gemini_features: Optional[dict] = Field(None, description="Gemini image analysis results")
    nlp_features: Optional[dict] = Field(None, description="NLP title features")

    model_config = {"populate_by_name": True}


class SHAPFeature(BaseModel):
    feature: str
    label: str
    value: float = Field(..., description="SHAP contribution in €/m²")


class PredictionResult(BaseModel):
    predicted_rent_sqm: float
    current_rent_sqm: Optional[float] = None
    gap_sqm: Optional[float] = None
    gap_pct: Optional[float] = None
    status: Optional[str] = None  # UNDERPRICED / OVERPRICED / FAIRLY_PRICED
    base_value: float = Field(..., description="SHAP base value (average rent)")
    shap_top_features: list[SHAPFeature]
    prediction_interval_80: Optional[list[float]] = Field(None, description="80% prediction interval [lower, upper]")
    prediction_interval_50: Optional[list[float]] = Field(None, description="50% prediction interval [lower, upper]")
    model_r2: float
    model_version: str


class RenovationOption(BaseModel):
    treatment: str
    label: str
    already_has: bool
    cost_eur: Optional[int] = None
    cate_sqm: Optional[float] = None
    cate_ci: Optional[list[float]] = None
    wtp_sqm: Optional[float] = None
    combined_sqm: Optional[float] = None
    monthly_uplift_eur: Optional[float] = None
    annual_uplift_eur: Optional[float] = None
    payback_months: Optional[float] = None
    legal_passthrough_sqm: Optional[float] = None
    roi_annual_pct: Optional[float] = None


class RenovationResult(BaseModel):
    apartment_id: Optional[str] = None
    living_space_sqm: float
    options: list[RenovationOption]
