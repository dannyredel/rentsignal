"""Prediction router — XGBoost rent prediction + SHAP explanation."""

from fastapi import APIRouter

from backend.models.apartment import ApartmentInput, PredictionResult, SHAPFeature
from backend.services.ml_service import predict

router = APIRouter(tags=["predict"])

# Map merged Berlin district names to the bezirk names the model was trained on
# The model uses pre-2001 individual district names (23 Bezirke)
DISTRICT_TO_BEZIRK = {
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
}

CONDITION_MAP = {
    "good": "well_kept",
    "normal": "well_kept",
    "simple": "need_of_renovation",
    "luxury": "mint_condition",
    "renovated": "refurbished",
    "fully_renovated": "fully_renovated",
    "first_time_use": "first_time_use",
    "needs_renovation": "need_of_renovation",
    "well_kept": "well_kept",
    "mint_condition": "mint_condition",
    "refurbished": "refurbished",
    "modernized": "modernized",
    "first_time_use_after_refurbishment": "first_time_use_after_refurbishment",
    "need_of_renovation": "need_of_renovation",
    "unknown": "unknown",
}


def _year_to_era(year: int) -> str:
    if year < 1918: return "pre_1918"
    elif year < 1950: return "1919_1949"
    elif year < 1965: return "1950_1964"
    elif year < 1973: return "1965_1972"
    elif year < 1991: return "1973_1990"
    elif year < 2003: return "1991_2002"
    elif year < 2015: return "2003_2014"
    else: return "2015_plus"


@router.post("/predict", response_model=PredictionResult)
def predict_rent(apt: ApartmentInput):
    """Predict market rent for an apartment and explain with SHAP.

    v4.2: Uses 75 features (structural + spatial + NLP + Gemini image).
    Spatial features computed on-the-fly from coordinates when available.
    """
    # Map district name to model bezirk
    district = apt.bezirk or apt.district
    bezirk = DISTRICT_TO_BEZIRK.get(district, district)

    # Map condition
    condition = CONDITION_MAP.get(apt.condition, apt.condition)

    # Derive building era
    building_era = apt.building_era
    if building_era == "pre_1918" and apt.year_built >= 1918:
        building_era = _year_to_era(apt.year_built)

    # Structural features (from user form input)
    model_input = {
        "livingSpace": apt.living_space_sqm,
        "noRooms": apt.rooms,
        "yearConstructed": apt.year_built,
        "floor": apt.floor,
        "numberOfFloors": apt.building_floors,
        "thermalChar": apt.thermal_char,
        "balcony": int(apt.has_balcony),
        "hasKitchen": int(apt.has_kitchen),
        "lift": int(apt.has_elevator),
        "cellar": int(apt.has_cellar),
        "garden": int(apt.has_garden),
        "newlyConst": int(apt.is_new_construction),
        "condition": condition,
        "interiorQual": apt.interior_quality,
        "typeOfFlat": apt.flat_type,
        "heatingType": apt.heating_type,
        "building_era": building_era,
        "bezirk": bezirk,
    }

    # Extract lat/lon if available (for unit-level spatial features)
    lat = getattr(apt, "lat", None)
    lon = getattr(apt, "lon", None)

    # Gemini features (if provided, e.g. from photo upload)
    gemini_features = getattr(apt, "gemini_features", None)

    # NLP features (if provided, e.g. from URL scrape)
    nlp_features = getattr(apt, "nlp_features", None)

    result = predict(
        model_input,
        plz=apt.plz,
        lat=lat,
        lon=lon,
        gemini_features=gemini_features,
        nlp_features=nlp_features,
    )

    # Gap analysis
    gap_sqm = None
    gap_pct = None
    status = None
    if apt.current_rent_per_sqm is not None:
        gap_sqm = round(result["predicted_rent_sqm"] - apt.current_rent_per_sqm, 2)
        gap_pct = round((gap_sqm / apt.current_rent_per_sqm) * 100, 1)
        if gap_sqm > 0.5:
            status = "UNDERPRICED"
        elif gap_sqm < -0.5:
            status = "OVERPRICED"
        else:
            status = "FAIRLY_PRICED"

    return PredictionResult(
        predicted_rent_sqm=result["predicted_rent_sqm"],
        current_rent_sqm=apt.current_rent_per_sqm,
        gap_sqm=gap_sqm,
        gap_pct=gap_pct,
        status=status,
        base_value=result["base_value"],
        shap_top_features=[SHAPFeature(**f) for f in result["shap_top_features"]],
        prediction_interval_80=result.get("prediction_interval_80"),
        prediction_interval_50=result.get("prediction_interval_50"),
        model_r2=result["model_r2"],
        model_version=result["model_version"],
    )
