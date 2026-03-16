# Spatial Feature Pipeline — Technical Notes
## MietOptimal / RentSignal

---

## Overview

The spatial pipeline extracts neighborhood-level features to augment the XGBoost rent prediction model. Three distinct data categories, each with different sources and methods.

---

## 1. Vector/POI Features (coordinates + attributes)

**Sources:** OpenStreetMap (Overpass API), Berlin Open Data, BVG GTFS
**Method:** Download coordinates → geopandas spatial joins → compute distances and counts per listing
**Effort:** ~3-4h total

| Feature | Source | Method | Notes |
|---------|--------|--------|-------|
| U-Bahn/S-Bahn distance | OSM Overpass API | Nearest station distance per listing | Key rent driver |
| Bus/tram stop distance | OSM or BVG GTFS feed | Nearest stop distance | Secondary transit |
| Restaurant/cafe density | OSM (amenity=restaurant/cafe) | Count within 500m radius | Walkability proxy |
| Shop/supermarket density | OSM (shop=supermarket/convenience) | Count within 500m radius | Daily needs access |
| School/kindergarten distance | OSM or Berlin Open Data | Nearest facility distance | Family appeal |
| Park distance | OSM (leisure=park polygons) | Distance to nearest park edge | Green access |
| Water body distance | OSM (natural=water, waterway) | Distance to nearest river/canal/lake | Amenity premium |
| Parking area proximity | OSM (amenity=parking) | Area within 500m | Car accessibility |

**All features are:**
- Quantitative and reproducible
- Free, no API keys needed
- Computed per listing using PLZ centroid or geocoded coordinates

---

## 2. Raster/Satellite-Derived Features (pixel-level)

### 2a. Sentinel-2 — DIY Computation

**Source:** ESA Copernicus Sentinel-2 (free, 10m resolution, multispectral)
**Access:** Copernicus Data Space (https://dataspace.copernicus.eu/) or Sentinel Hub EO Browser
**Method:** Download cloud-free Berlin summer composite → compute indices with rasterio → aggregate to PLZ/LOR polygons

| Index | Formula | What it measures | Bands |
|-------|---------|-----------------|-------|
| **NDVI** | (NIR - Red) / (NIR + Red) | Vegetation density / green space | B8 (NIR) + B4 (Red) |
| **NDWI** | (Green - NIR) / (Green + NIR) | Water bodies | B3 (Green) + B8 (NIR) |
| **NDBI** | (SWIR - NIR) / (SWIR + NIR) | Built-up / impervious surface | B11 (SWIR) + B8 (NIR) |

**Workflow:**
1. Download Sentinel-2 L2A tile (atmospherically corrected) for Berlin, summer 2024/2025
2. Load bands with rasterio
3. Compute NDVI, NDWI, NDBI per pixel
4. Load PLZ or LOR polygon boundaries (GeoJSON from Berlin Open Data)
5. Zonal statistics: mean, std, percentiles per polygon
6. Join to listings by PLZ/LOR

**Key notes:**
- Summer months (June-August) give best vegetation signal
- Need cloud-free composite — may need to composite multiple dates
- 10m resolution is sufficient for neighborhood-level aggregation
- Validate against Umweltatlas ground truth (see 2b)

### 2b. Berlin Umweltatlas — Pre-Computed Official Data

**Source:** Berlin Environmental Atlas (https://www.berlin.de/umweltatlas/en/)
**Access:** FIS-Broker portal (https://fbinter.stadt-berlin.de/fb/), WMS/WFS/Shapefile downloads
**Method:** Download official layers → spatial join to listings

| Layer | Code | What it measures | Use for MietOptimal |
|-------|------|-----------------|-------------------|
| Green and Open Spaces | 06.02 | Public/private green areas | Validate NDVI, green space % |
| Impervious Soil Coverage | 01.02 | % sealed surface per block | Building density proxy |
| Noise Immission (traffic) | 07.05 | dB(A) noise levels from traffic | **Powerful rent predictor nobody uses** |
| Biotope Types | 05.08 | Vegetation classification | Detailed green typology |
| Actual Land Use | 06.01 | Land use per block | Ground truth for satellite |

**Key advantage:** Official, validated data. Use as ground truth to validate our Sentinel-2 computations.

---

## 3. Visual/AI-Extracted Features (Gemini multimodal)

**Source:** Google Maps Static API or Berlin Orthophotos → Gemini API
**Method:** Feed aerial image + structured prompt → receive JSON with visual features
**When:** Hackathon day, for 5 demo neighborhoods only

| Feature | Extractable otherwise? | Gemini adds |
|---------|:---------------------:|------------|
| Construction activity / cranes | No | Detects active construction sites |
| Building facade condition | No | Estimates building age/quality |
| Street quality / maintenance | No | Subjective assessment |
| Neighborhood "vibe" / character | No | Demo wow factor |
| Solar panel presence | No | Visible on rooftops |

**Notes:**
- Pre-compute and cache for demo — no live API calls during pitch
- Qualitative, not fully reproducible — complement, don't replace quantitative features
- Maximizes Google DeepMind infrastructure prize scoring (multimodal = 5/5)

---

## Efficiency vs. Robustness Matrix

| Approach | Effort | # Features | Robustness | Hackathon value |
|----------|--------|-----------|------------|-----------------|
| **OSM + geopandas only** | ~4h | 8-10 | High — reproducible | Good but not unique |
| **OSM + Sentinel-2 DIY** | ~6-8h | 12-14 | Very high — MSc-grade | Shows real RS skills |
| **OSM + Umweltatlas pre-computed** | ~3h | 12-14 | High — official data | Efficient but less impressive |
| **OSM + Sentinel-2 + Gemini** | ~8-10h | 16-18 | Mixed | Maximum demo impact |

---

## Implementation Plan

### Phase 1: OSM Vector Features (~3-4h) — `notebooks/03a_spatial_osm.ipynb`
- Download Berlin OSM extract or use Overpass API
- Extract: transit stations, POIs (shops, restaurants, schools), parks, water bodies
- Compute distance/density features per listing PLZ centroid
- Output: `data/processed/spatial_osm_features.csv`

### Phase 2: Sentinel-2 NDVI + Indices (~2-3h) — `notebooks/03b_spatial_satellite.ipynb`
- Download cloud-free summer Sentinel-2 tile from Copernicus
- Compute NDVI, NDWI, NDBI with rasterio
- Aggregate to PLZ polygons (zonal statistics)
- Validate against Umweltatlas green space layer
- Output: `data/processed/spatial_satellite_features.csv`

### Phase 3: Gemini Visual Extraction (~2h, hackathon day)
- Download aerial tiles for 5 demo neighborhoods
- Run Gemini multimodal extraction → structured JSON
- Cache results in `data/demo/demo_spatial_cards.json`

### Integration: Merge all spatial features → retrain XGBoost
- Join OSM + satellite features to listings by PLZ
- Retrain model with expanded feature set
- Measure R² improvement: "spatial features add X points to R²"
- Update SHAP to show spatial feature importance

---

## Data Access Quick Reference

| Data | URL | Format | Auth needed |
|------|-----|--------|-------------|
| OSM Berlin | https://download.geofabrik.de/europe/germany/berlin.html | PBF/Shapefile | No |
| OSM Overpass API | https://overpass-turbo.eu/ | JSON/XML | No |
| Sentinel-2 | https://dataspace.copernicus.eu/ | GeoTIFF | Free account |
| Sentinel Hub EO Browser | https://apps.sentinel-hub.com/eo-browser/ | Preview + download | Free account |
| Berlin LOR boundaries | https://daten.berlin.de/ | GeoJSON | No |
| Berlin PLZ boundaries | https://daten.berlin.de/ | GeoJSON | No |
| Umweltatlas | https://fbinter.stadt-berlin.de/fb/ | WMS/WFS/Shapefile | No |
| Google Maps Static API | https://developers.google.com/maps/documentation/maps-static | PNG tiles | API key (free tier) |
| Gemini API | https://ai.google.dev/ | JSON | API key (free tier) |
