"""Prediction router — XGBoost rent prediction + SHAP explanation."""

from fastapi import APIRouter

from backend.models.apartment import ApartmentInput, PredictionResult, SHAPFeature
from backend.services.ml_service import predict

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictionResult)
def predict_rent(apt: ApartmentInput):
    """Predict market rent for an apartment and explain with SHAP."""
    # Convert Pydantic model to the dict format ml_service expects
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
        "condition": apt.condition,
        "interiorQual": apt.interior_quality,
        "typeOfFlat": apt.flat_type,
        "heatingType": apt.heating_type,
        "building_era": apt.building_era,
        "bezirk": apt.bezirk or apt.district,
    }

    result = predict(model_input, plz=apt.plz)

    # Gap analysis if current rent provided
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
        model_r2=result["model_r2"],
        model_version=result["model_version"],
    )
