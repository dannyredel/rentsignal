# Data Architecture & Management

> Source of truth for RentSignal's relational data model, data flows, and management conventions.

---

## Raw Data Inventory

| Source | File | Records | Size | Date | Key Fields |
|--------|------|---------|------|------|------------|
| Kaggle ImmoScout24 | `data/raw/listings/immo_data.csv` | 268,850 (→10,275 Berlin) | ~150 MB | 2018–2020 | scoutId, all features, NO lat/lon |
| Apify Scrape 1 | `data/raw/scraping/dataset_...-2026-03-17.json` | 568 | 28.6 MB | 2026-03-17 | 54 ATP fields, basicInfo.address |
| Apify Scrape 2 | `data/raw/scraping/dataset_...-2026-03-18.json` | 8,335 | 397.7 MB | 2026-03-18 | 54 ATP fields, basicInfo.address |
| OSM Features | `data/processed/spatial_osm_features.csv` | 190 PLZs | ~30 KB | 2025 | 9 distance/count features |
| Satellite Features | `data/processed/spatial_satellite_features.csv` | 190 PLZs | ~40 KB | Aug 2024 | 9 NDVI/NDWI/NDBI stats |
| Conjoint Survey | `data/conjoint/berlin_rental/survey_responses.csv` | 750 | ~200 KB | 2026-03 | 20 cols, LLM-simulated CBC |
| Mietspiegel | `data/reference/mietspiegel_simplified.json` | 96 cells | ~5 KB | 2024 | era×size×location→rent |
| PLZ Intelligence | `data/processed/plz_intelligence.json` | 190 PLZs | ~80 KB | 2019 | Market aggregates |

### Address & Coordinate Coverage (Apify 2026 Data)

| Field | Scrape 2 (8,335 records) | Coverage |
|-------|--------------------------|----------|
| `obj_zipCode` (PLZ) | 8,335 | **100%** |
| `obj_street` (street name) | 5,136 | **61.6%** |
| `obj_houseNumber` | 5,136 | **61.6%** |
| `basicInfo.address.lat/lon` | 5,123 | **61.4%** |
| `obj_regio3` (bezirk) | 8,335 | **100%** |
| `obj_regio4` (neighborhood) | 8,335 | **100%** |

**Implication:** 5,123 units are immediately ready for unit-level spatial features without geocoding. The remaining 3,212 need geocoding via Berlin Address Register or Nominatim.

---

## Design Principles

1. **Entity-centric** — Every physical rental unit gets a stable ID. Observations (listings, prices) reference that ID.
2. **Panel-ready** — The same unit observed at different dates produces multiple rows in `listings`, not duplicate units.
3. **Source-agnostic** — Kaggle 2019 and Apify 2026 data flow through the same schema. The `source` column tracks provenance.
4. **Spatial joins are layered** — PLZ-level features exist today; unit-level (lat/lon) features slot in without schema changes.
5. **No duplication of truth** — Derived features (rent_sqm, building_era, sqm_per_room) are computed once, stored once, recomputed on rebuild.

---

## Entity-Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         MASTER TABLES                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐         ┌──────────────┐                        │
│  │   units      │ 1───M  │  listings     │                       │
│  │─────────────│         │──────────────│                        │
│  │ unit_id (PK) │         │ listing_id    │                       │
│  │ plz (FK)     │◄────┐   │ unit_id (FK)  │                       │
│  │ lat, lon     │     │   │ observed_date │                       │
│  │ physical     │     │   │ rent fields   │                       │
│  │ amenities    │     │   │ source        │                       │
│  │ categorical  │     │   └──────────────┘                        │
│  └──────┬──────┘     │                                           │
│         │            │                                           │
│         │ FK: plz    │                                           │
│         ▼            │                                           │
│  ┌──────────────┐    │   ┌──────────────────┐                    │
│  │ spatial_plz   │    │   │ spatial_unit      │                    │
│  │──────────────│    │   │──────────────────│                    │
│  │ plz (PK)     │    │   │ unit_id (FK, PK)  │                    │
│  │ osm_features │    │   │ osm_point_feats   │                    │
│  │ sat_features │    │   │ sat_buffer_feats  │                    │
│  └──────────────┘    │   │ noise, air, lor   │                    │
│                      │   └──────────────────┘                    │
│                      │                                           │
├──────────────────────┼───────────────────────────────────────────┤
│                      │    REFERENCE TABLES                       │
│                      │                                           │
│  ┌──────────────┐    │   ┌──────────────────┐                    │
│  │ mietspiegel   │    │   │ causal_estimates  │                    │
│  │──────────────│    │   │──────────────────│                    │
│  │ era × size ×  │    │   │ treatment         │                    │
│  │ location →    │    │   │ method            │                    │
│  │ rent limits   │    │   │ effect, CI        │                    │
│  └──────────────┘    │   └──────────────────┘                    │
│                      │                                           │
│  ┌──────────────┐    │   ┌──────────────────┐                    │
│  │ plz_stats     │◄───┘   │ model_registry    │                    │
│  │──────────────│        │──────────────────│                    │
│  │ plz (PK)     │        │ version           │                    │
│  │ market aggs  │        │ trained_on        │                    │
│  │ building     │        │ features, metrics │                    │
│  │ stock stats  │        │ artifacts path    │                    │
│  └──────────────┘        └──────────────────┘                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Table Definitions

### 1. `units` — Master Unit Registry

Every physical rental unit gets exactly one row. Deduplication key: `(plz, street, house_number)` or `scout_id` within the same source.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `unit_id` | VARCHAR(12) | NO | **PK.** Generated: `RS-{zero-padded seq}` e.g. `RS-000001` |
| `scout_id` | VARCHAR(20) | YES | Original ImmoScout24 listing ID (scoutId) |
| `source` | ENUM | NO | `kaggle_2019` \| `apify_2026_03` \| `apify_2026_03_18` |
| `first_seen` | DATE | NO | Earliest observed_date for this unit |
| `last_seen` | DATE | NO | Latest observed_date for this unit |
| `plz` | VARCHAR(5) | NO | **FK → spatial_plz.plz, plz_stats.plz** |
| `bezirk` | VARCHAR(30) | NO | Berlin district (Mitte, Kreuzberg, ...) |
| `neighborhood` | VARCHAR(50) | YES | Ortsteil / sub-district |
| `street` | VARCHAR(100) | YES | Street name (for geocoding) |
| `house_number` | VARCHAR(10) | YES | House number (for geocoding) |
| `lat` | FLOAT | YES | Latitude WGS84 (NULL until geocoded) |
| `lon` | FLOAT | YES | Longitude WGS84 (NULL until geocoded) |
| `geocode_source` | VARCHAR(20) | YES | `berlin_register` \| `nominatim` \| `google` \| `listing` |
| `living_space_sqm` | FLOAT | NO | Living area m² |
| `n_rooms` | FLOAT | NO | Number of rooms |
| `year_constructed` | INT | YES | Year built (NULL → unknown) |
| `floor` | INT | YES | Floor level (0 = ground) |
| `n_floors` | INT | YES | Total floors in building |
| `thermal_char` | FLOAT | YES | Energy consumption kWh/m²/year |
| `has_balcony` | BOOL | NO | Balcony or terrace |
| `has_kitchen` | BOOL | NO | Fitted kitchen included |
| `has_elevator` | BOOL | NO | Elevator in building |
| `has_cellar` | BOOL | NO | Basement storage |
| `has_garden` | BOOL | NO | Garden access |
| `is_new_construction` | BOOL | NO | Newly constructed |
| `condition` | VARCHAR(40) | NO | Physical condition (or `unknown`) |
| `interior_quality` | VARCHAR(20) | NO | Interior quality (or `unknown`) |
| `type_of_flat` | VARCHAR(20) | NO | apartment, loft, maisonette, ... |
| `heating_type` | VARCHAR(40) | NO | Heating system type (or `unknown`) |
| `building_era` | VARCHAR(15) | NO | **Derived** from year_constructed |
| `sqm_per_room` | FLOAT | NO | **Derived:** living_space_sqm / n_rooms |

**Indexes:**
- `PRIMARY KEY (unit_id)`
- `UNIQUE (scout_id, source)` — no duplicate listings from same source
- `INDEX (plz)` — spatial join
- `INDEX (lat, lon)` — point-level spatial queries
- `INDEX (bezirk)` — district filtering

**Deduplication rules:**
- Within same source: match on `scout_id`
- Cross-source (Kaggle ↔ Apify): match on `(plz, street, house_number, living_space_sqm, n_rooms)` with fuzzy tolerance on sqm (±2m²). Given the 6-year gap, true duplicates are rare — most matches are re-listings of the same physical unit.
- When a cross-source match is found: keep both `listings` rows (different dates/prices) but assign the same `unit_id`.

---

### 2. `listings` — Price Observations (Panel)

One row per (unit × date). This is the training dataset. A unit listed in Oct 2019 and again in Mar 2026 produces two rows here.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `listing_id` | VARCHAR(15) | NO | **PK.** `{source_prefix}-{seq}` e.g. `KG-000001`, `AP-000001` |
| `unit_id` | VARCHAR(12) | NO | **FK → units.unit_id** |
| `observed_date` | DATE | NO | When the listing was active / scraped |
| `source` | ENUM | NO | `kaggle_2019` \| `apify_2026_03` |
| `base_rent_eur` | FLOAT | NO | Monthly base rent (Nettokaltmiete) |
| `total_rent_eur` | FLOAT | YES | Gross rent incl. Nebenkosten |
| `service_charge_eur` | FLOAT | YES | Monthly service charge |
| `rent_sqm` | FLOAT | NO | **Derived:** base_rent_eur / living_space_sqm |
| `is_latest` | BOOL | NO | TRUE if this is the most recent observation for this unit_id |

**Indexes:**
- `PRIMARY KEY (listing_id)`
- `INDEX (unit_id)` — join to units
- `INDEX (observed_date)` — time filtering
- `INDEX (is_latest)` — fast "current price" queries

**Panel structure:**
```
unit_id    | observed_date | base_rent | rent_sqm | source
───────────┼───────────────┼───────────┼──────────┼──────────────
RS-000042  | 2019-10-01    | 850.00    | 12.14    | kaggle_2019
RS-000042  | 2026-03-17    | 1120.00   | 16.00    | apify_2026_03
RS-001234  | 2019-05-01    | 620.00    | 10.33    | kaggle_2019
RS-005678  | 2026-03-17    | 980.00    | 14.00    | apify_2026_03
```

**Training strategy:**
- **Current model (v3):** Train on `WHERE source = 'kaggle_2019'` with inflation factor ×1.378
- **Next model (v4):** Train on `WHERE is_latest = TRUE` (prefers 2026 data, fills gaps with inflation-adjusted 2019)
- **Future panel model:** Use all rows with time fixed effects, enabling rent trend estimation

---

### 3. `spatial_plz` — PLZ-Level Spatial Features (Current)

One row per postal code. Computed from PLZ centroid (OSM) and PLZ polygon zonal statistics (Sentinel-2).

| Column | Type | Description |
|--------|------|-------------|
| `plz` | VARCHAR(5) | **PK** |
| `centroid_lat` | FLOAT | PLZ centroid latitude |
| `centroid_lon` | FLOAT | PLZ centroid longitude |
| `dist_transit_m` | FLOAT | Distance to nearest transit stop (m) |
| `dist_park_m` | FLOAT | Distance to nearest park (m) |
| `dist_water_m` | FLOAT | Distance to nearest water body (m) |
| `dist_school_m` | FLOAT | Distance to nearest school (m) |
| `count_food_500m` | INT | Restaurants/cafes within 500m of centroid |
| `count_shop_500m` | INT | Shops within 500m of centroid |
| `count_food_1000m` | INT | Restaurants/cafes within 1km of centroid |
| `count_shop_1000m` | INT | Shops within 1km of centroid |
| `count_transit_1000m` | INT | Transit stops within 1km of centroid |
| `ndvi_mean` | FLOAT | Mean NDVI across PLZ polygon |
| `ndvi_std` | FLOAT | NDVI standard deviation |
| `ndvi_median` | FLOAT | Median NDVI |
| `ndwi_mean` | FLOAT | Mean NDWI (water index) |
| `ndwi_std` | FLOAT | NDWI standard deviation |
| `ndwi_median` | FLOAT | Median NDWI |
| `ndbi_mean` | FLOAT | Mean NDBI (built-up index) |
| `ndbi_std` | FLOAT | NDBI standard deviation |
| `ndbi_median` | FLOAT | Median NDBI |
| `computed_at` | DATE | When these features were last computed |

**Coverage:** 190 / 214 Berlin PLZs (88.8%)

---

### 4. `spatial_unit` — Unit-Level Spatial Features (Future)

One row per geocoded unit. Replaces PLZ-level approximations with point-precise measurements.

| Column | Type | Description |
|--------|------|-------------|
| `unit_id` | VARCHAR(12) | **PK, FK → units.unit_id** |
| — | — | **Point-level OSM (from actual lat/lon)** |
| `dist_transit_m` | FLOAT | Exact distance to nearest transit stop |
| `dist_park_m` | FLOAT | Exact distance to nearest park |
| `dist_water_m` | FLOAT | Exact distance to nearest water body |
| `dist_school_m` | FLOAT | Exact distance to nearest school |
| `count_food_500m` | INT | Restaurants within 500m of unit |
| `count_shop_500m` | INT | Shops within 500m of unit |
| `count_food_1000m` | INT | Restaurants within 1km of unit |
| `count_shop_1000m` | INT | Shops within 1km of unit |
| `count_transit_1000m` | INT | Transit stops within 1km of unit |
| — | — | **Multi-scale satellite buffers** |
| `ndvi_100m` | FLOAT | Mean NDVI in 100m buffer (immediate surroundings) |
| `ndvi_250m` | FLOAT | Mean NDVI in 250m buffer (block-level) |
| `ndvi_500m` | FLOAT | Mean NDVI in 500m buffer (neighborhood) |
| `ndwi_100m` | FLOAT | Mean NDWI in 100m buffer |
| `ndwi_250m` | FLOAT | Mean NDWI in 250m buffer |
| `ndwi_500m` | FLOAT | Mean NDWI in 500m buffer |
| `ndbi_100m` | FLOAT | Mean NDBI in 100m buffer |
| `ndbi_250m` | FLOAT | Mean NDBI in 250m buffer |
| `ndbi_500m` | FLOAT | Mean NDBI in 500m buffer |
| — | — | **New fine-grained sources** |
| `noise_traffic_db` | FLOAT | Traffic noise level dB(A) — Berlin Umweltatlas |
| `noise_rail_db` | FLOAT | Rail noise level dB(A) |
| `air_no2` | FLOAT | NO₂ concentration µg/m³ |
| `air_pm25` | FLOAT | PM2.5 concentration µg/m³ |
| `lor_pop_density` | FLOAT | Population density per km² (LOR block) |
| `lor_avg_income` | FLOAT | Avg household income index (LOR block) |
| `isochrone_alex_min` | INT | Minutes to Alexanderplatz by transit (OSRM) |
| `isochrone_hbf_min` | INT | Minutes to Hauptbahnhof by transit |
| `walk_score` | FLOAT | Walkability score 0–100 |
| `computed_at` | DATE | When these features were last computed |

**Fallback logic at query time:**
```python
def get_spatial_features(unit_id, plz):
    """Try unit-level first, fall back to PLZ-level."""
    unit_feats = spatial_unit.get(unit_id)
    if unit_feats and unit_feats.is_complete():
        return unit_feats
    else:
        return spatial_plz.get(plz)  # current behavior
```

---

### 5. `plz_stats` — Market Aggregates per PLZ

Pre-computed market intelligence. Refreshed whenever listings table is updated.

| Column | Type | Description |
|--------|------|-------------|
| `plz` | VARCHAR(5) | **PK** |
| `n_listings` | INT | Total listings observed |
| `n_listings_latest` | INT | Listings from most recent source |
| `rent_sqm_median` | FLOAT | Median rent €/m² |
| `rent_sqm_p25` | FLOAT | 25th percentile |
| `rent_sqm_p75` | FLOAT | 75th percentile |
| `rent_sqm_mean` | FLOAT | Mean rent €/m² |
| `avg_sqm` | FLOAT | Average living space |
| `avg_year_built` | FLOAT | Average year constructed |
| `pct_with_kitchen` | FLOAT | % units with fitted kitchen |
| `pct_with_balcony` | FLOAT | % units with balcony |
| `pct_with_elevator` | FLOAT | % units with elevator |
| `updated_at` | DATE | Last recomputed |

---

### 6. `mietspiegel` — Legal Rent Limits

Lookup table for §556d BGB Mietpreisbremse compliance.

| Column | Type | Description |
|--------|------|-------------|
| `building_era` | VARCHAR(15) | Era category (pre_1918, ..., 2014_plus) |
| `size_category` | VARCHAR(15) | under_40, 40_60, 60_90, over_90 |
| `location_quality` | VARCHAR(10) | einfach, mittel, gut |
| `rent_lower` | FLOAT | Lower bound €/m² |
| `rent_mid` | FLOAT | Midpoint €/m² (ortsübliche Vergleichsmiete) |
| `rent_upper` | FLOAT | Upper bound €/m² |
| `legal_max` | FLOAT | **Derived:** rent_mid × 1.10 (Mietpreisbremse cap) |
| `year` | INT | Mietspiegel edition year (2024) |

**Composite PK:** `(building_era, size_category, location_quality, year)`

---

### 7. `causal_estimates` — Treatment Effect Registry

| Column | Type | Description |
|--------|------|-------------|
| `treatment` | VARCHAR(20) | Feature toggled (hasKitchen, balcony, lift, garden) |
| `method` | VARCHAR(15) | `matching` \| `conjoint` |
| `subgroup` | VARCHAR(20) | `overall` \| building_era value (for heterogeneous effects) |
| `effect_sqm` | FLOAT | Estimated effect €/m² |
| `ci_lower` | FLOAT | 95% CI lower bound |
| `ci_upper` | FLOAT | 95% CI upper bound |
| `n_obs` | INT | Sample size (matched pairs or survey responses) |
| `data_vintage` | VARCHAR(15) | Which listings data was used |
| `computed_at` | DATE | When this estimate was produced |

**Composite PK:** `(treatment, method, subgroup, data_vintage)`

---

### 8. `model_registry` — ML Model Versions

| Column | Type | Description |
|--------|------|-------------|
| `version` | VARCHAR(10) | **PK.** Semantic version (v3.0.0, v4.0.0) |
| `trained_at` | DATETIME | Training timestamp |
| `training_query` | TEXT | SQL/filter that produced the training set |
| `n_train` | INT | Training set size |
| `n_test` | INT | Test set size |
| `features` | JSON | Ordered list of feature names used |
| `hyperparams` | JSON | XGBoost hyperparameters |
| `r2` | FLOAT | Test R² |
| `rmse` | FLOAT | Test RMSE |
| `mae` | FLOAT | Test MAE |
| `inflation_factor` | FLOAT | Applied inflation multiplier (1.0 if trained on current data) |
| `artifacts_path` | VARCHAR(100) | Path to model .joblib files |
| `data_sha256` | VARCHAR(64) | Hash of training data for reproducibility |
| `spatial_level` | VARCHAR(10) | `plz` \| `unit` — which spatial table was used |
| `notes` | TEXT | Free-form notes |

---

## Data Flow Diagram

```
                    RAW SOURCES
                    ══════════
    ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
    │ Kaggle CSV    │  │ Apify JSON (×N)  │  │ Future scrapes│
    │ 268K rows     │  │ 568+ rows each   │  │ ...           │
    │ 2018-2020     │  │ 2026-03          │  │               │
    └──────┬───────┘  └────────┬─────────┘  └──────┬───────┘
           │                   │                    │
           ▼                   ▼                    ▼
    ┌──────────────────────────────────────────────────────┐
    │              INGESTION PIPELINE                       │
    │  1. Parse & normalize schema (27 columns)            │
    │  2. Type casting (bool, float, categorical)          │
    │  3. Derive: rent_sqm, building_era, sqm_per_room    │
    │  4. Outlier filtering (rent, sqm, year bounds)       │
    │  5. Assign source tag                                │
    └──────────────────────┬──────────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────────┐
    │              DEDUPLICATION ENGINE                     │
    │  Within-source: scout_id match                       │
    │  Cross-source: (plz, street, house_no, sqm) fuzzy   │
    │  Output: unit_id assignment                          │
    └──────────────────────┬──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────┐           ┌──────────────┐
    │    units      │           │   listings    │
    │  (master)     │           │   (panel)     │
    │  ~10,500      │           │   ~11,000     │
    │  unique apts  │           │   price obs   │
    └──────┬───────┘           └──────────────┘
           │
           │  geocode (lat/lon)
           ▼
    ┌──────────────────────────────────────────────────────┐
    │              GEOCODING PIPELINE                       │
    │  1. Berlin Address Register (primary)                │
    │  2. Nominatim / Photon (fallback)                    │
    │  3. Google Geocoding API (last resort)               │
    │  Output: lat, lon, geocode_source in units table     │
    └──────────────────────┬──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────┐           ┌──────────────────┐
    │ spatial_plz   │           │ spatial_unit      │
    │ (190 PLZs)    │           │ (per geocoded     │
    │ centroid-     │           │  unit, point-     │
    │ based)        │           │  level features)  │
    └──────────────┘           └──────────────────┘

              ┌──────────────────────────────────┐
              │         TRAINING PIPELINE         │
              │  1. Join: listings × units        │
              │  2. Join: × spatial (plz or unit) │
              │  3. Filter: training query        │
              │  4. Encode categoricals           │
              │  5. Train XGBoost                 │
              │  6. Compute SHAP                  │
              │  7. Register in model_registry    │
              └──────────────────────────────────┘
```

---

## Data Management Conventions

### ID Generation

| Entity | Format | Example | Generator |
|--------|--------|---------|-----------|
| unit_id | `RS-{6-digit seq}` | RS-000001 | Auto-increment at ingestion |
| listing_id | `{src}-{6-digit seq}` | KG-000001, AP-000001 | Per-source counter |

- IDs are stable once assigned — never recycled or reassigned.
- Cross-source matched units share the same `unit_id`.

### Source Tagging

Every record carries a `source` tag for full provenance:

| Source Tag | Description | Date Range | Records |
|------------|-------------|------------|---------|
| `kaggle_2019` | Kaggle ImmoScout24 Berlin subset | Sep 2018 – Feb 2020 | ~10,275 |
| `apify_2026_03` | Apify ImmoScout24 scrape (batch 1) | Mar 17, 2026 | ~568 |
| `apify_2026_03_18` | Apify ImmoScout24 scrape (batch 2) | Mar 18, 2026 | TBD |
| Future sources follow pattern: `{scraper}_{YYYY_MM}` |

### Handling Missing Data

| Strategy | Applied To | Rule |
|----------|-----------|------|
| NULL | year_constructed, floor, n_floors, thermal_char | Genuinely unknown; imputed at training time |
| `'unknown'` | condition, interior_quality, heating_type | Categorical — treated as its own level by encoder |
| Median fill | floor, n_floors, thermal_char | At model training time only, not in stored data |
| 0 fill | spatial features (when PLZ unmatched) | Logged as warning; future: use nearest PLZ |

**Principle:** Store raw truth. Impute at training time, not at ingestion.

### Temporal Management

```
                2018    2019    2020    ...    2026
                 │       │       │              │
Kaggle snapshots ●───────●───────●              │
                Sep     May/Oct  Feb            │
                                                │
Apify scrapes                                   ●── Mar 17-18
                                                │
                                           Future scrapes
                                           (quarterly cadence)
```

**Rules:**
- `observed_date` is the listing date, not the scrape date
- For Kaggle: mapped from snapshot labels (Sep18 → 2018-09-01, etc.)
- For Apify: the scrape timestamp date
- `is_latest` flag is recomputed per unit_id whenever new data arrives
- Inflation adjustment lives in `model_registry`, NOT in the data

### Address Recovery via Cross-Matching

**Principle:** Every new data intake should be cross-matched against ALL previous sources to recover hidden addresses.

Many ImmoScout24 listings hide the address ("incomplete address"), but the same physical apartment may have been listed in a previous scrape with the address visible. By matching on `(plz, livingSpace ±1m², noRooms)`, we can borrow the address from the historical record.

**Validated results (Apify 2026 × Kaggle 2019):**
- 3,175 units missing addresses → 779 matched (24.5%) → 745 successfully geocoded
- This upgraded 9% of all units from PLZ-centroid (~500m) to street-level (~10m) precision

**Implementation:** `data/pipelines/ingestion.py → cross_match_addresses()`

**On each new scrape, run cross-match against:**
1. All previous scrapes (Apify backlog)
2. Kaggle 2019 dataset (8,879 Berlin addresses)
3. Any other address source (Berlin Address Register, etc.)

**Coordinate source hierarchy** (stored in `units.coord_source`):

| Source | Precision | Priority |
|--------|-----------|----------|
| `listing` | ~10m (from scrape) | 1 (best) |
| `kaggle_match` | ~10m (cross-matched) | 2 |
| `title_mining` | ~50-100m (from listing title) | 3 |
| `plz_ortsteil_centroid` | ~200-400m | 4 |
| `plz_centroid` | ~500-800m | 5 (worst) |

### Rebuild & Refresh Protocol

| Trigger | Action |
|---------|--------|
| New scrape ingested | Run ingestion → dedup → cross-match addresses → update units/listings → recompute plz_stats |
| Geocoding completed | Populate lat/lon in units → compute spatial_unit features |
| Spatial data updated | Recompute spatial_plz and/or spatial_unit → retrain model |
| Model retrained | New row in model_registry, update model artifacts |

### File-to-Table Mapping (Current Implementation)

Until we move to a proper database, tables are stored as parquet/CSV:

| Logical Table | Physical File | Format |
|---------------|---------------|--------|
| units + listings (combined) | `data/processed/listings_master.parquet` | Parquet |
| spatial_plz | `data/processed/spatial_osm_features.csv` + `spatial_satellite_features.csv` | CSV |
| spatial_unit | `data/processed/spatial_unit_features.parquet` | Parquet (future) |
| plz_stats | `data/processed/plz_intelligence.json` | JSON |
| mietspiegel | `data/reference/mietspiegel_simplified.json` | JSON |
| causal_estimates | `data/processed/matching_results.json` + `conjoint_results.json` | JSON |
| model_registry | `models/model_config.json` | JSON |

---

## Training Query Examples

### Current: Kaggle-only model (v3)
```python
# All Kaggle listings, PLZ-level spatial
training_data = (
    listings
    .query("source == 'kaggle_2019'")
    .merge(units, on='unit_id')
    .merge(spatial_plz, on='plz', how='left')
)
# Post-prediction: multiply by inflation_factor=1.378
```

### Next: Latest-price model (v4)
```python
# Prefer 2026 data, fill with inflation-adjusted 2019
latest = listings.query("is_latest == True")
training_data = (
    latest
    .merge(units, on='unit_id')
    .merge(spatial_plz, on='plz', how='left')
)
# No inflation factor needed (data is current)
```

### Future: Panel model with time effects
```python
# All observations, year as feature
all_obs = listings.merge(units, on='unit_id')
all_obs['year'] = all_obs['observed_date'].dt.year
training_data = all_obs.merge(spatial_unit, on='unit_id', how='left')
# Model learns rent trends across years
```

### Future: Unit-level spatial model
```python
# Same as v4 but with point-level spatial features
training_data = (
    listings.query("is_latest == True")
    .merge(units, on='unit_id')
    .merge(spatial_unit, on='unit_id', how='left')
    .pipe(lambda df: df.fillna(
        df.merge(spatial_plz, on='plz', how='left', suffixes=('', '_plz'))
    ))  # fallback to PLZ where unit-level missing
)
```

---

## Data Quality Rules

| Rule | Check | Action on Violation |
|------|-------|-------------------|
| rent_sqm ∈ [3, 60] | Ingestion | Drop row, log warning |
| living_space_sqm ∈ [8, 500] | Ingestion | Drop row |
| year_constructed ∈ [1800, current_year+1] | Ingestion | Set NULL |
| floor ∈ [0, 40] | Ingestion | Set NULL |
| PLZ matches `^1[0-4]\d{3}$` | Ingestion | Drop row (not Berlin) |
| No duplicate (scout_id, source) | Dedup | Keep first, log |
| base_rent > 0 | Ingestion | Drop row |
| n_rooms > 0 | Ingestion | Drop row |
| lat ∈ [52.3, 52.7], lon ∈ [13.0, 13.8] | Geocoding | Reject geocode, try fallback |

---

## Migration Path

### Phase 0 (Current State)
- Kaggle + Apify data in separate parquet files
- Spatial features in CSV, joined at query time
- No unit registry, no deduplication

### Phase 1 (This Sprint)
- Build unified `listings_master.parquet` with unit_id assignment
- Ingest both Apify scrapes (568 + 8,335 records) through same pipeline
- Deduplicate within sources
- Compute `is_latest` flag

### Phase 2 (Geocoding + Unit Spatial)
- **5,123 of 8,335 Apify records already have lat/lon** in `basicInfo.address` (61.4%)
- For remaining 3,212: geocode via Berlin Address Register + Nominatim
- For Kaggle data: geocode via address matching (street + PLZ)
- Compute `spatial_unit` features for geocoded units
- Retrain model with unit-level features

### Phase 3 (Panel + New Sources)
- Set up recurring Apify scrapes (quarterly)
- Build panel with time fixed effects
- Add noise, air quality, LOR data to `spatial_unit`

### Phase 4 (Production Database)
- Migrate from parquet files to Supabase/PostgreSQL
- API serves from database instead of in-memory CSV
- Automated ingestion pipeline (Apify webhook → ETL → DB)
