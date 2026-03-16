# XGBoost Rent Prediction — Training Report (v3: Full Spatial Features)
## Generated: 2026-03-15 15:48

### Dataset
- Source: Kaggle ImmoScout24 (Berlin subset) + OSM + Sentinel-2 spatial features
- Training samples: 8,179
- Test samples: 2,045
- Features: 37 (19 original + 9 OSM + 9 satellite)
- Target: rent per m² (baseRent / livingSpace)

### Model Comparison (Test Set)

| Model | R² | RMSE (€/m²) | MAE (€/m²) |
|-------|-----|-------------|------------|
| Ridge (original) | 0.3214 | 4.26 | 3.14 |
| Ridge (+ OSM) | 0.4693 | 3.77 | 2.72 |
| Ridge (+ OSM + sat) | 0.4807 | 3.73 | 2.69 |
| XGBoost (original) | 0.7248 | 2.72 | 1.83 |
| XGBoost (+ OSM) | 0.7453 | 2.61 | 1.72 |
| **XGBoost (+ OSM + sat)** | **0.7491** | **2.59** | **1.70** |

### Spatial Feature Impact
- OSM alone: R² 0.7248 → 0.7453 (+0.0205)
- OSM + Satellite: R² 0.7248 → 0.7491 (+0.0243)
- RMSE: 2.72 → 2.59 €/m² (4.5% better)

### Spatial Features
**OSM (9):** dist_transit_m, dist_park_m, dist_water_m, dist_school_m, count_food_500m, count_shop_500m, count_food_1000m, count_shop_1000m, count_transit_1000m
**Satellite (9):** ndvi_mean, ndvi_std, ndvi_median, ndwi_mean, ndwi_std, ndwi_median, ndbi_mean, ndbi_std, ndbi_median

### Best Hyperparameters
{
  "colsample_bytree": 0.8,
  "learning_rate": 0.05,
  "max_depth": 8,
  "min_child_weight": 5,
  "n_estimators": 800,
  "subsample": 0.8
}

### Notes
- Sentinel-2 scene: 2024-08-20, 0.6% cloud cover (summer composite)
- Spatial features at PLZ centroid level (190 PLZs, 500m buffer for zonal stats)
- Data vintage: 2018-2019 listings
