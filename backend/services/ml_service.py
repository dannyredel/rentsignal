"""ML prediction service — loads XGBoost model and computes SHAP explanations."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent.parent

# Load artifacts once at module level — with graceful fallback
try:
    _model = joblib.load(_ROOT / "models" / "xgboost_rent.joblib")
    _encoder = joblib.load(_ROOT / "models" / "feature_encoder.joblib")
    # Compute SHAP explainer on-the-fly instead of loading 26MB file
    import shap
    _explainer = shap.TreeExplainer(_model)

    with open(_ROOT / "models" / "model_config.json") as f:
        MODEL_CONFIG = json.load(f)

    # Spatial data for PLZ lookup
    _df_osm = pd.read_csv(_ROOT / "data" / "processed" / "spatial_osm_features.csv")
    _df_sat = pd.read_csv(_ROOT / "data" / "processed" / "spatial_satellite_features.csv")
    _df_spatial = _df_osm.merge(_df_sat, on="plz", how="left")
    _ML_READY = True
except Exception as e:
    import sys
    print(f"WARNING: ML service failed to load: {e}", file=sys.stderr)
    _model = _encoder = _explainer = _df_spatial = None
    MODEL_CONFIG = {}
    _ML_READY = False

# Human-readable feature labels
FEATURE_LABELS = {
    "livingSpace": "Living Space (m²)",
    "noRooms": "Rooms",
    "yearConstructed": "Year Built",
    "floor": "Floor",
    "numberOfFloors": "Building Floors",
    "thermalChar": "Energy (kWh/m²)",
    "sqm_per_room": "m² per Room",
    "balcony": "Balcony",
    "hasKitchen": "Modern Kitchen",
    "lift": "Elevator",
    "cellar": "Cellar",
    "garden": "Garden",
    "newlyConst": "New Construction",
    "condition": "Condition",
    "interiorQual": "Interior Quality",
    "typeOfFlat": "Flat Type",
    "heatingType": "Heating",
    "building_era": "Building Era",
    "bezirk": "District",
    "count_food_1000m": "Restaurants (1km)",
    "count_food_500m": "Restaurants (500m)",
    "count_shop_1000m": "Shops (1km)",
    "count_shop_500m": "Shops (500m)",
    "count_transit_1000m": "Transit Stops (1km)",
    "dist_transit_m": "Distance to Transit",
    "dist_park_m": "Distance to Park",
    "dist_water_m": "Distance to Water",
    "dist_school_m": "Distance to School",
    "ndvi_mean": "Vegetation (NDVI)",
    "ndvi_std": "Vegetation Variation",
    "ndvi_median": "Vegetation (median)",
    "ndwi_mean": "Water Index (NDWI)",
    "ndwi_std": "Water Variation",
    "ndwi_median": "Water Index (median)",
    "ndbi_mean": "Built-up (NDBI)",
    "ndbi_std": "Built-up Variation",
    "ndbi_median": "Built-up (median)",
}


def prepare_features(apt: dict, plz: int | None = None) -> pd.DataFrame:
    """Build a single-row DataFrame with all 37 model features."""
    row = {}

    # Numeric
    for f in MODEL_CONFIG["numeric_features"]:
        if f == "sqm_per_room":
            row[f] = apt["livingSpace"] / max(apt["noRooms"], 1)
        else:
            row[f] = apt[f]

    # Binary
    for f in MODEL_CONFIG["binary_features"]:
        row[f] = apt[f]

    # Categorical (encode via OrdinalEncoder)
    cat_values = [apt[f] for f in MODEL_CONFIG["categorical_features"]]
    cat_encoded = _encoder.transform([cat_values])[0]
    for f, val in zip(MODEL_CONFIG["categorical_features"], cat_encoded):
        row[f] = val

    # Spatial (PLZ lookup)
    plz_val = plz or apt.get("plz")
    if plz_val is not None:
        plz_row = _df_spatial[_df_spatial["plz"] == plz_val]
        if len(plz_row) > 0:
            plz_row = plz_row.iloc[0]
            for f in MODEL_CONFIG["osm_features"] + MODEL_CONFIG["satellite_features"]:
                row[f] = plz_row.get(f, 0)
        else:
            for f in MODEL_CONFIG["osm_features"] + MODEL_CONFIG["satellite_features"]:
                row[f] = 0
    else:
        for f in MODEL_CONFIG["osm_features"] + MODEL_CONFIG["satellite_features"]:
            row[f] = 0

    return pd.DataFrame([row])[MODEL_CONFIG["features"]]


def predict(apt: dict, plz: int | None = None) -> dict:
    """Predict rent and compute SHAP explanation.

    Args:
        apt: dict with raw apartment features (model feature names as keys)
        plz: optional postal code for spatial feature lookup

    Returns:
        dict with predicted_rent_sqm, base_value, shap_top_features
    """
    X = prepare_features(apt, plz)
    pred = float(_model.predict(X)[0])
    shap_values = _explainer.shap_values(X)[0]
    base_value = float(_explainer.expected_value)

    # Top 10 features by |SHAP|
    feat_shap = list(zip(MODEL_CONFIG["features"], shap_values))
    feat_shap.sort(key=lambda x: abs(x[1]), reverse=True)
    top_features = [
        {
            "feature": f,
            "label": FEATURE_LABELS.get(f, f),
            "value": round(float(v), 4),
        }
        for f, v in feat_shap[:10]
    ]

    return {
        "predicted_rent_sqm": round(pred, 2),
        "base_value": round(base_value, 2),
        "shap_top_features": top_features,
        "model_r2": MODEL_CONFIG["metrics"]["r2"],
        "model_version": "v3_spatial",
    }
