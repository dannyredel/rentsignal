"""ML prediction service v4.2 — XGBoost with unit-level spatial + Gemini image features.

Computes spatial features on-the-fly from coordinates using cached KDTrees and rasters.
Gemini/NLP features are filled with defaults when not available (form mode).
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Spatial computation helpers
# ---------------------------------------------------------------------------

LAT_TO_M = 111_320
LON_TO_M = 111_320 * np.cos(np.radians(52.5))  # ~67,700m at Berlin


def _latlon_to_meters(lat, lon):
    return np.array([[lon * LON_TO_M, lat * LAT_TO_M]])


def _build_kdtree(pois):
    coords = np.array([[p["lat"], p["lon"]] for p in pois])
    xy = np.column_stack([coords[:, 1] * LON_TO_M, coords[:, 0] * LAT_TO_M])
    return cKDTree(xy)


# Alexanderplatz coordinates for CBD distance
_ALEX_XY = np.array([[13.4132 * LON_TO_M, 52.5219 * LAT_TO_M]])

# ---------------------------------------------------------------------------
# Load artifacts at module level
# ---------------------------------------------------------------------------

try:
    _model = joblib.load(_ROOT / "models" / "xgboost_rent_v4.joblib")
    _encoder = joblib.load(_ROOT / "models" / "feature_encoder_v4.joblib")
    _explainer = joblib.load(_ROOT / "models" / "shap_explainer_v4.joblib")

    with open(_ROOT / "models" / "model_config.json") as f:
        MODEL_CONFIG = json.load(f)

    # Build KDTrees from cached POI JSONs
    _POI_DIR = _ROOT / "data" / "processed" / "osm_pois"
    _kdtrees = {}
    for name in ["transit", "ubahn", "food", "restaurant", "cafe", "shop", "park", "water", "school", "building"]:
        poi_file = _POI_DIR / f"{name}.json"
        if poi_file.exists():
            with open(poi_file) as f:
                pois = json.load(f)
            if pois:
                _kdtrees[name] = _build_kdtree(pois)

    # Load pre-computed satellite grid (lightweight alternative to raster files)
    _sat_grid = None
    _sat_kdtree = None
    sat_grid_path = _ROOT / "data" / "processed" / "satellite_grid.parquet"
    if sat_grid_path.exists():
        _sat_grid = pd.read_parquet(sat_grid_path)
        _sat_grid_xy = np.column_stack([
            _sat_grid["lon"].values * LON_TO_M,
            _sat_grid["lat"].values * LAT_TO_M,
        ])
        _sat_kdtree = cKDTree(_sat_grid_xy)
        print(f"Satellite grid loaded: {len(_sat_grid):,} points", file=sys.stderr)

    # PLZ-level spatial fallback (for when geocoding isn't available)
    _df_osm = pd.read_csv(_ROOT / "data" / "processed" / "spatial_osm_features.csv")
    _df_sat = pd.read_csv(_ROOT / "data" / "processed" / "spatial_satellite_features.csv")
    _df_spatial_plz = _df_osm.merge(_df_sat, on="plz", how="left")

    # Load rent neighbor lookup for spatial rent features (v4.3)
    _rent_lookup = None
    _rent_kdtree = None
    _plz_median_rents = {}
    rent_lookup_path = _ROOT / "data" / "processed" / "rent_neighbors_lookup.parquet"
    plz_median_path = _ROOT / "data" / "processed" / "plz_median_rents.json"
    if rent_lookup_path.exists():
        _rent_lookup = pd.read_parquet(rent_lookup_path)
        _rent_xy = np.column_stack([
            _rent_lookup["lon"].values * LON_TO_M,
            _rent_lookup["lat"].values * LAT_TO_M,
        ])
        _rent_values = _rent_lookup["rent_sqm"].values
        _rent_kdtree = cKDTree(_rent_xy)
        print(f"Rent neighbor lookup loaded: {len(_rent_lookup):,} points", file=sys.stderr)
    if plz_median_path.exists():
        with open(plz_median_path) as f:
            _plz_median_rents = json.load(f)

    _ML_READY = True
    print(f"ML service loaded: v{MODEL_CONFIG.get('model_version', '?')}, "
          f"{len(MODEL_CONFIG.get('features', []))} features, "
          f"{len(_kdtrees)} KDTrees, "
          f"sat_grid={'yes' if _sat_grid is not None else 'no'}, "
          f"rent_neighbors={'yes' if _rent_kdtree is not None else 'no'}", file=sys.stderr)

except Exception as e:
    print(f"WARNING: ML service failed to load: {e}", file=sys.stderr)
    _model = _encoder = _explainer = None
    _kdtrees = {}
    _sat_grid = _sat_kdtree = None
    _df_spatial_plz = None
    MODEL_CONFIG = {}
    _ML_READY = False

# No inflation adjustment for v4.2 (trained on 2026 data)
INFLATION_FACTOR = 1.0

# ---------------------------------------------------------------------------
# Feature labels (human-readable for SHAP display)
# ---------------------------------------------------------------------------

FEATURE_LABELS = {
    # Structural
    "livingSpace": "Living Space (m²)",
    "noRooms": "Rooms",
    "yearConstructed": "Year Built",
    "floor": "Floor",
    "numberOfFloors": "Building Floors",
    "thermalChar": "Energy (kWh/m²)",
    "sqm_per_room": "m² per Room",
    "nebenkosten_sqm": "Utilities (€/m²)",
    "picturecount": "Photos in Listing",
    "balcony": "Balcony",
    "hasKitchen": "Fitted Kitchen",
    "lift": "Elevator",
    "cellar": "Cellar",
    "garden": "Garden",
    "newlyConst": "New Construction",
    "condition": "Condition",
    "interiorQual": "Interior Quality",
    "typeOfFlat": "Flat Type",
    "heatingGroup": "Heating Type",
    "building_era": "Building Era",
    "bezirk": "District",
    "sizeCategory": "Size Category",
    # NLP title
    "is_altbau": "Altbau (title)",
    "is_neubau": "Neubau (title)",
    "is_furnished": "Furnished",
    "is_tauschwohnung": "Apartment Swap",
    "is_renovated": "Renovated (title)",
    "is_wg": "Flatshare (WG)",
    "is_befristet": "Temporary Rental",
    "has_terrasse": "Terrace (title)",
    "is_dachgeschoss": "Top Floor (DG)",
    # Gemini image
    "interior_quality": "Visual Interior Quality",
    "kitchen_quality": "Visual Kitchen Quality",
    "bathroom_quality": "Visual Bathroom Quality",
    "brightness": "Brightness (photo)",
    "renovation_level": "Renovation Level (photo)",
    "bldg_condition": "Building Facade",
    # Spatial rent features (v4.3)
    "avg_rent_500m": "Avg Nearby Rent (500m)",
    "avg_rent_1km": "Avg Nearby Rent (1km)",
    "median_rent_plz": "PLZ Median Rent",
    "rent_dispersion_500m": "Rent Dispersion (500m)",
    "n_listings_500m": "Listings Nearby (500m)",
    "bldg_floors": "Visible Floors",
    "rooms_shown": "Rooms in Photos",
    "is_render": "3D Render",
    "has_visible_kitchen": "Kitchen in Photos",
    "has_visible_balcony": "Balcony in Photos",
    "bldg_green": "Green Surroundings",
    "bldg_commercial_gf": "Commercial Ground Floor",
    "style": "Style (photo)",
    "floor_type": "Floor Type (photo)",
    "ceiling_height": "Ceiling Height",
    "bldg_style": "Building Style",
    "staging": "Staging",
    "view_type": "View from Window",
    "color_warmth": "Color Warmth",
    # Spatial
    "dist_cbd_m": "Distance to Center",
    "dist_transit_m": "Distance to Transit",
    "dist_ubahn_m": "Distance to U-Bahn",
    "dist_park_m": "Distance to Park",
    "dist_water_m": "Distance to Water",
    "dist_school_m": "Distance to School",
    "count_food_500m": "Food Venues (500m)",
    "count_food_1000m": "Food Venues (1km)",
    "count_restaurant_500m": "Restaurants (500m)",
    "count_restaurant_1000m": "Restaurants (1km)",
    "count_cafe_500m": "Cafés (500m)",
    "count_shop_500m": "Shops (500m)",
    "count_shop_1000m": "Shops (1km)",
    "count_transit_1000m": "Transit Stops (1km)",
    "count_building_200m": "Building Density",
    "ndvi_100m": "Vegetation (100m)",
    "ndvi_250m": "Vegetation (250m)",
    "ndvi_500m": "Vegetation (500m)",
    "ndwi_100m": "Water Index (100m)",
    "ndwi_250m": "Water Index (250m)",
    "ndwi_500m": "Water Index (500m)",
    "ndbi_100m": "Built-up (100m)",
    "ndbi_250m": "Built-up (250m)",
    "ndbi_500m": "Built-up (500m)",
}

# Median defaults for features not available at prediction time
_FEATURE_DEFAULTS = {
    # Gemini image features (medians from training data)
    "interior_quality": 3, "kitchen_quality": 2, "bathroom_quality": 2,
    "brightness": 3, "renovation_level": 3, "bldg_condition": 0,
    "bldg_floors": 0, "rooms_shown": 2,
    "is_render": 0, "has_visible_kitchen": 1, "has_visible_balcony": 1,
    "bldg_green": 0, "bldg_commercial_gf": 0,
    "style": "modern", "floor_type": "unknown", "ceiling_height": "normal",
    "bldg_style": "unknown", "staging": "empty", "view_type": "nv",
    "color_warmth": "neutral",
    # NLP title features (default to 0 = not detected)
    "is_altbau": 0, "is_neubau": 0, "is_furnished": 0, "is_tauschwohnung": 0,
    "is_renovated": 0, "is_wg": 0, "is_befristet": 0, "has_terrasse": 0,
    "is_dachgeschoss": 0,
    # Quick features
    "picturecount": 8, "nebenkosten_sqm": 3.27,
    "sizeCategory": "medium",
}

# Heating type grouping
_HEATING_GROUPS = {
    "gas": ["gas", "natural_gas", "liquid_gas"],
    "district": ["district_heating"],
    "oil": ["oil"],
    "electric": ["electric", "electricity", "night_storage_heater"],
    "heat_pump": ["heat_pump", "geothermal", "environmental_thermal_energy"],
    "central": ["central_heating", "self_contained_central_heating"],
    "floor": ["floor_heating", "underfloor_heating"],
    "combined": ["combined_heat_and_power"],
}


def _group_heating(ht: str) -> str:
    ht_lower = str(ht).lower().strip()
    for group, keywords in _HEATING_GROUPS.items():
        for kw in keywords:
            if kw in ht_lower:
                return group
    return "unknown"


def _size_category(sqm: float) -> str:
    if sqm < 30: return "micro"
    if sqm < 50: return "small"
    if sqm < 70: return "medium"
    if sqm < 100: return "large"
    return "xlarge"


# ---------------------------------------------------------------------------
# Spatial feature computation
# ---------------------------------------------------------------------------

def compute_spatial_features(lat: float, lon: float) -> dict:
    """Compute all 24 spatial features from coordinates using KDTrees + rasters."""
    unit_xy = _latlon_to_meters(lat, lon)
    features = {}

    # CBD distance
    features["dist_cbd_m"] = float(np.sqrt(((unit_xy[0, 0] - _ALEX_XY[0, 0]) ** 2) +
                                            ((unit_xy[0, 1] - _ALEX_XY[0, 1]) ** 2)))

    # Distance to nearest POI
    for name in ["transit", "ubahn", "park", "water", "school"]:
        if name in _kdtrees:
            dist, _ = _kdtrees[name].query(unit_xy[0], k=1)
            features[f"dist_{name}_m"] = float(dist)
        else:
            features[f"dist_{name}_m"] = 0

    # Count within radius
    count_specs = [("food", [500, 1000]), ("restaurant", [500, 1000]),
                   ("cafe", [500]), ("shop", [500, 1000]),
                   ("transit", [1000]), ("building", [200])]
    for name, radii in count_specs:
        if name in _kdtrees:
            for r in radii:
                count = _kdtrees[name].query_ball_point(unit_xy[0], r=r, return_length=True)
                features[f"count_{name}_{r}m"] = int(count)
        else:
            for r in radii:
                features[f"count_{name}_{r}m"] = 0

    # Satellite indices (from pre-computed grid — nearest neighbor lookup)
    if _sat_kdtree is not None:
        dist, idx = _sat_kdtree.query(unit_xy[0], k=1)
        grid_row = _sat_grid.iloc[idx]
        for idx_name in ["ndvi", "ndwi", "ndbi"]:
            for buffer_m in [100, 250, 500]:
                col = f"{idx_name}_{buffer_m}m"
                features[col] = float(grid_row.get(col, 0))
    else:
        for idx_name in ["ndvi", "ndwi", "ndbi"]:
            for buffer_m in [100, 250, 500]:
                features[f"{idx_name}_{buffer_m}m"] = 0

    # Spatial rent features (v4.3 — neighbor rents)
    if _rent_kdtree is not None:
        # avg_rent_500m
        indices_500 = _rent_kdtree.query_ball_point(unit_xy[0], r=500)
        if len(indices_500) > 1:
            rents_500 = _rent_values[indices_500]
            features["avg_rent_500m"] = float(np.mean(rents_500))
            features["rent_dispersion_500m"] = float(np.std(rents_500))
            features["n_listings_500m"] = len(indices_500)
        else:
            features["avg_rent_500m"] = 0
            features["rent_dispersion_500m"] = 0
            features["n_listings_500m"] = 0

        # avg_rent_1km
        indices_1k = _rent_kdtree.query_ball_point(unit_xy[0], r=1000)
        if len(indices_1k) > 1:
            features["avg_rent_1km"] = float(np.mean(_rent_values[indices_1k]))
        else:
            features["avg_rent_1km"] = 0
    else:
        features["avg_rent_500m"] = 0
        features["avg_rent_1km"] = 0
        features["rent_dispersion_500m"] = 0
        features["n_listings_500m"] = 0

    return features


def compute_rent_plz_median(plz: int) -> float:
    """Get median rent for a PLZ from pre-computed lookup."""
    return _plz_median_rents.get(str(plz), 0)


def get_spatial_from_plz(plz: int) -> dict:
    """Fallback: get spatial features from PLZ-level data."""
    features = {}
    if _df_spatial_plz is not None:
        row = _df_spatial_plz[_df_spatial_plz["plz"] == plz]
        if len(row) > 0:
            row = row.iloc[0]
            for col in _df_spatial_plz.columns:
                if col != "plz":
                    features[col] = row.get(col, 0)
    return features


# ---------------------------------------------------------------------------
# Feature preparation
# ---------------------------------------------------------------------------

def _describe_feature_value(feature: str, apt: dict, X_row) -> str:
    """Describe what the user has for a feature in human language."""
    # Binary features
    binary_map = {
        "hasKitchen": ("Yes", "No"),
        "balcony": ("Yes", "No"),
        "lift": ("Yes", "No"),
        "cellar": ("Yes", "No"),
        "garden": ("Yes", "No"),
        "newlyConst": ("Yes", "No"),
        "is_tauschwohnung": ("Yes (swap)", "No"),
        "is_furnished": ("Yes", "No"),
        "is_altbau": ("Yes", "No"),
        "is_neubau": ("Yes", "No"),
        "is_renovated": ("Yes", "No"),
        "is_render": ("Yes", "No"),
        "has_visible_kitchen": ("Yes", "No"),
        "has_visible_balcony": ("Yes", "No"),
        "bldg_green": ("Yes", "No"),
        "bldg_commercial_gf": ("Yes", "No"),
    }
    if feature in binary_map:
        val = apt.get(feature, 0)
        yes, no = binary_map[feature]
        return yes if val else no

    # Numeric features with units
    numeric_formats = {
        "livingSpace": "{:.0f} m²",
        "noRooms": "{:.0f} rooms",
        "yearConstructed": "{:.0f}",
        "floor": "Floor {:.0f}",
        "numberOfFloors": "{:.0f} floors",
        "thermalChar": "{:.0f} kWh/m²",
        "sqm_per_room": "{:.0f} m²/room",
        "picturecount": "{:.0f} photos",
        "nebenkosten_sqm": "€{:.2f}/m²",
        "interior_quality": "{:.0f}/5",
        "kitchen_quality": "{:.0f}/5",
        "bathroom_quality": "{:.0f}/5",
        "brightness": "{:.0f}/5",
        "renovation_level": "{:.0f}/5",
        "bldg_condition": "{:.0f}/5",
        "dist_cbd_m": "{:.0f}m to center",
        "dist_transit_m": "{:.0f}m to transit",
        "dist_ubahn_m": "{:.0f}m to U-Bahn",
        "dist_park_m": "{:.0f}m to park",
        "dist_water_m": "{:.0f}m to water",
        "count_food_1000m": "{:.0f} venues",
        "count_food_500m": "{:.0f} venues",
        "count_restaurant_1000m": "{:.0f} restaurants",
        "count_cafe_500m": "{:.0f} cafés",
        "count_shop_1000m": "{:.0f} shops",
        "count_transit_1000m": "{:.0f} stops",
    }
    if feature in numeric_formats:
        val = apt.get(feature)
        if val is None:
            # Try from the feature row
            try:
                idx = MODEL_CONFIG["features"].index(feature)
                val = float(X_row.iloc[0, idx])
            except (ValueError, IndexError):
                val = None
        if val is not None:
            return numeric_formats[feature].format(val)

    # Categorical
    val = apt.get(feature)
    if val is not None:
        return str(val).replace("_", " ").title()

    return "—"


def prepare_features(apt: dict, plz: int | None = None,
                     lat: float | None = None, lon: float | None = None,
                     gemini_features: dict | None = None,
                     nlp_features: dict | None = None) -> pd.DataFrame:
    """Build a single-row DataFrame with all 75 model features.

    Args:
        apt: structural features (livingSpace, noRooms, etc.)
        plz: postal code for PLZ-level fallback
        lat, lon: coordinates for unit-level spatial features
        gemini_features: dict from Gemini image analysis (optional)
        nlp_features: dict from NLP title extraction (optional)
    """
    row = {}
    feature_groups = MODEL_CONFIG.get("feature_groups", {})

    # --- Structural numeric ---
    structural_numeric = ["livingSpace", "noRooms", "yearConstructed", "floor",
                          "numberOfFloors", "thermalChar", "sqm_per_room"]
    for f in structural_numeric:
        if f == "sqm_per_room":
            row[f] = apt.get("livingSpace", 60) / max(apt.get("noRooms", 2), 1)
        else:
            row[f] = apt.get(f, _FEATURE_DEFAULTS.get(f, 0))

    # Quick numeric features
    row["nebenkosten_sqm"] = apt.get("nebenkosten_sqm", _FEATURE_DEFAULTS["nebenkosten_sqm"])
    row["picturecount"] = apt.get("picturecount", _FEATURE_DEFAULTS["picturecount"])

    # --- Structural binary ---
    structural_binary = ["balcony", "hasKitchen", "lift", "cellar", "garden", "newlyConst"]
    for f in structural_binary:
        row[f] = int(apt.get(f, 0))

    # --- NLP title features (from nlp_features dict or defaults) ---
    nlp_src = nlp_features or {}
    for f in ["is_altbau", "is_neubau", "is_furnished", "is_tauschwohnung",
              "is_renovated", "is_wg", "is_befristet", "has_terrasse", "is_dachgeschoss"]:
        row[f] = int(nlp_src.get(f, _FEATURE_DEFAULTS.get(f, 0)))

    # --- Gemini image features (from gemini_features dict or defaults) ---
    gem_src = gemini_features or {}
    if gem_src:
        print(f"DEBUG prepare_features: gemini_features has {len(gem_src)} keys, "
              f"interior_quality={gem_src.get('interior_quality', 'MISSING')}, "
              f"renovation_level={gem_src.get('renovation_level', 'MISSING')}", file=sys.stderr)
    gemini_numeric = feature_groups.get("gemini_numeric", []) or [
        "interior_quality", "kitchen_quality", "bathroom_quality", "brightness",
        "renovation_level", "bldg_condition", "rooms_shown", "bldg_floors",
    ]
    gemini_binary = feature_groups.get("gemini_binary", []) or [
        "is_render", "has_visible_kitchen", "has_visible_balcony", "bldg_green", "bldg_commercial_gf",
    ]
    for f in gemini_numeric:
        row[f] = gem_src.get(f, _FEATURE_DEFAULTS.get(f, 0))
    for f in gemini_binary:
        row[f] = int(gem_src.get(f, _FEATURE_DEFAULTS.get(f, 0)))

    # --- Categorical ---
    row["condition"] = apt.get("condition", "unknown")
    row["interiorQual"] = apt.get("interiorQual", "unknown")
    row["typeOfFlat"] = apt.get("typeOfFlat", "apartment")
    row["heatingGroup"] = _group_heating(apt.get("heatingType", "unknown"))
    row["building_era"] = apt.get("building_era", "unknown")
    row["bezirk"] = apt.get("bezirk", "Mitte")
    row["sizeCategory"] = _size_category(apt.get("livingSpace", 60))

    # Gemini categorical — check both feature_groups and categorical_features list
    gemini_cats = feature_groups.get("gemini_categorical", [])
    if not gemini_cats:
        # v4.3+ stores all categoricals in one list — Gemini cats are those in the encoder but not structural
        structural_cats = {"condition", "interiorQual", "typeOfFlat", "heatingGroup", "building_era", "bezirk", "sizeCategory"}
        all_cats = set(MODEL_CONFIG.get("categorical_features", []))
        gemini_cats = [f for f in all_cats - structural_cats if f not in row]
    for f in gemini_cats:
        row[f] = gem_src.get(f, _FEATURE_DEFAULTS.get(f, "unknown"))

    # Encode all categoricals
    cat_features = feature_groups.get("categorical", []) or MODEL_CONFIG.get("categorical_features", [])
    cat_values = [str(row.get(f, "unknown")).lower().strip() for f in cat_features]
    cat_encoded = _encoder.transform([cat_values])[0]
    for f, val in zip(cat_features, cat_encoded):
        row[f] = val

    # --- Spatial features ---
    if lat is not None and lon is not None and _kdtrees:
        spatial = compute_spatial_features(lat, lon)
    elif plz is not None:
        spatial = get_spatial_from_plz(plz)
    else:
        spatial = {}

    for f in MODEL_CONFIG.get("features", []):
        if f.startswith(("dist_", "count_", "nd", "avg_rent_", "rent_dispersion_", "n_listings_")):
            if f not in row:
                row[f] = spatial.get(f, 0)

    # PLZ median rent (v4.3)
    plz_median = compute_rent_plz_median(plz) if plz else 0
    row["median_rent_plz"] = plz_median

    # Fallback: if no coords, use PLZ median for rent neighbor features
    if row.get("avg_rent_500m", 0) == 0 and plz_median > 0:
        row["avg_rent_500m"] = plz_median
        row["avg_rent_1km"] = plz_median

    # Fill any remaining missing features with 0
    for f in MODEL_CONFIG.get("features", []):
        if f not in row:
            row[f] = 0

    return pd.DataFrame([row])[MODEL_CONFIG["features"]]


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict(apt: dict, plz: int | None = None,
            lat: float | None = None, lon: float | None = None,
            gemini_features: dict | None = None,
            nlp_features: dict | None = None) -> dict:
    """Predict rent and compute SHAP explanation.

    Args:
        apt: structural apartment features
        plz: postal code (fallback for spatial)
        lat, lon: coordinates (preferred for spatial)
        gemini_features: Gemini image analysis results (optional)
        nlp_features: NLP title features (optional)

    Returns:
        dict with predicted_rent_sqm, base_value, shap_top_features, enrichment_level
    """
    X = prepare_features(apt, plz=plz, lat=lat, lon=lon,
                         gemini_features=gemini_features, nlp_features=nlp_features)
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

    # Layer 2: Feature worth table — SHAP translated into money language
    living_space = apt.get("livingSpace", 75)
    feature_worth = []
    for f, v in feat_shap[:10]:
        shap_val = round(float(v), 2)
        monthly = round(shap_val * living_space)
        # Determine what the user has for this feature
        has_value = _describe_feature_value(f, apt, X)
        # Actionability
        actionable = f in ("hasKitchen", "balcony", "lift", "garden", "cellar",
                           "newlyConst", "condition", "interiorQual", "thermalChar")
        feature_worth.append({
            "feature": f,
            "label": FEATURE_LABELS.get(f, f),
            "shap_sqm": shap_val,
            "monthly_eur": monthly,
            "you_have": has_value,
            "actionable": actionable,
        })

    # Enrichment level indicator
    enrichment = "basic"
    if lat is not None and lon is not None:
        enrichment = "spatial"
    if gemini_features:
        enrichment = "full"

    # Prediction intervals (conformal, from model_config)
    pi = MODEL_CONFIG.get("prediction_intervals", {})
    hw80 = pi.get("half_width_80", 4.50)
    hw50 = pi.get("half_width_50", 2.24)

    return {
        "predicted_rent_sqm": round(pred, 2),
        "base_value": round(base_value, 2),
        "shap_top_features": top_features,
        "feature_worth": feature_worth,
        "prediction_interval_80": [round(pred - hw80, 2), round(pred + hw80, 2)],
        "prediction_interval_50": [round(pred - hw50, 2), round(pred + hw50, 2)],
        "model_r2": MODEL_CONFIG.get("metrics", {}).get("r2_regular", MODEL_CONFIG.get("metrics", {}).get("r2", 0)),
        "model_version": MODEL_CONFIG.get("model_version", "unknown"),
        "enrichment_level": enrichment,
    }
