# MietOptimal — Data Sources Guide
## For Pre-Hackathon Prep (Claude Code Reference)

---

## 1. Rental Listing Data (for XGBoost model + matching estimator)

### 1A. Best Option: Kaggle — ImmoScout24 Germany Apartments

**URL:** https://www.kaggle.com/datasets/corrieaar/apartment-rental-offers-in-germany
**What it is:** Scraped rental offers from ImmoScout24 (Germany's largest real estate portal, ~60% market share). Three snapshots: 2018-09, 2019-05, 2019-10.
**Fields likely included:** regio (region/city), livingSpace (m²), totalRent (warm), baseRent (Kaltmiete), noRooms, balcony, hasKitchen, cellar, condition, yearConstructed, floor, numberOfFloors, garden, lift, typeOfFlat, geo_plz (postal code), and more.
**Action:** Download, filter to Berlin (regio1 = "Berlin"), clean. This gives you several thousand Berlin listings.
**Limitation:** Data is from 2018-2019, not 2025. Fine for model architecture and demo — just adjust price levels by applying a scalar (Berlin rents up ~40-50% since 2019). Alternatively, use as training data and note the vintage in Q&A.

### 1B. Alternative: GitHub — Berlin House Prices Prediction

**URL:** https://github.com/MoMkhani/Berlin-House-Prices-Prediction
**What it is:** Pre-filtered Berlin subset of the Kaggle ImmoScout24 data with some feature engineering already done.
**Action:** Check if the repo has the cleaned CSV directly — saves preprocessing time.

### 1C. Academic: RWI-GEO-RED (Research-grade ImmoScout24 data)

**URL:** https://www.rwi-essen.de/en/research-advice/further/research-data-center-ruhr-fdz/data-sets/rwi-geo-red
**What it is:** The official research dataset of ALL ImmoScout24 listings 2007-2020. Monthly data, geo-coded, with ~49 variables per listing. Covers apartments for rent, apartments for sale, houses for rent, houses for sale.
**Access:** Requires signed data use agreement with FDZ Ruhr. Available to researchers at scientific institutions. Takes days-weeks to process the application.
**Action:** If you have academic affiliation, apply NOW. This is the gold standard dataset. But don't wait for it — use Kaggle as primary, RWI as upgrade path.
**For the pitch:** Mention this exists: "In production, we'd train on the RWI-GEO-RED dataset with 13 years of geo-coded listing history."

### 1D. Fallback: Scrape current listings

**Tool:** Python (requests + BeautifulSoup) or Firecrawl
**Target:** ImmoScout24 Berlin rental listings (immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten)
**Warning:** ImmoScout actively blocks scrapers. Consider:
- WG-gesucht.de (less protected, good for shared apartments)
- Immowelt.de (alternative portal)
- kleinanzeigen.de (formerly eBay Kleinanzeigen, classifieds)
**Action:** Only if Kaggle data is insufficient. Budget 3-4 hours including anti-blocking workarounds.

### 1E. Fallback of fallback: Generate synthetic listing data

If all else fails, generate a realistic synthetic dataset:
- Use known Berlin rent statistics to calibrate distributions:
  - Average Kaltmiete Q1 2026: ~€13.11/m² (ImmoScout24 data)
  - Range: €8.50/m² (Marzahn) to €22/m² (Mitte Neubau)
  - Size distribution: 30-70m² most common
  - Building year: heavy clusters at pre-1918 (Altbau), 1950-70 (post-war), 1970-90 (Plattenbau), 2014+ (Neubau)
- Add realistic feature correlations (newer buildings have kitchens + elevators, Altbau has high ceilings but no elevator, etc.)
- 2,000+ synthetic listings should be enough for XGBoost + matching

**Minimum fields needed for the model:**

| Field | Type | Example |
|-------|------|---------|
| district | categorical | Kreuzberg, Wedding, Mitte... |
| plz | string | 10999 |
| livingSpace_sqm | float | 65.0 |
| baseRent_eur | float | 780.0 |
| noRooms | float | 2.5 |
| yearConstructed | int | 1968 |
| floor | int | 3 |
| numberOfFloors | int | 5 |
| balcony | bool | false |
| hasKitchen | bool | true |
| lift | bool | false |
| garden | bool | false |
| cellar | bool | true |
| condition | categorical | well_kept / renovated / first_time_use |
| heatingType | categorical | central / district / gas |
| typeOfFlat | categorical | Etagenwohnung / Dachgeschoss / Erdgeschoss |
| lat | float | 52.4951 |
| lon | float | 13.4232 |

---

## 2. Tenant Demographic Data (for synthetic conjoint calibration)

The goal here is to calibrate synthetic tenant personas to real Berlin demographic distributions. You need: income, household size, age, migration background, and ideally housing cost burden — all by district.

### 2A. IBB Wohnungsmarktbericht (Housing Market Report)

**URL:** https://www.ibb.de/en/publications/publications.html (English summary available)
**Full report (German):** https://www.ibb.de/wohnungsmarktbericht
**What it contains:**
- Asking rents by district and building type
- New construction analysis
- Vacancy rates (citywide ~1.5%, central <1%)
- Tenant profile segmentation by neighborhood
- Supply-demand dynamics
**Key stats for calibration:**
- Average asking rent: €15.78/m² (2024)
- BBU (public housing) new contract rents: €9.54/m² (40% below market)
- Existing tenant average: ~€7.67/m² (2022 Census)
- New contract average: €16.35/m²
**Action:** Download the summary PDF. Extract district-level rent data and tenant segmentation.

### 2B. Amt für Statistik Berlin-Brandenburg (Official Statistics)

**URL:** https://www.statistik-berlin-brandenburg.de/
**Key datasets:**

| Dataset | URL / Reference | What it gives you |
|---------|----------------|-------------------|
| Population by district | statistik-berlin-brandenburg.de/a-i-5-hj/ | 3.91M residents. Population per district (Pankow: 427k, Mitte: 397k, Spandau: 259k). Age, gender, nationality by district. |
| Household structure | Pressemitteilung 186-2025 | 2.22M households. 56.5% are single-person households. Average household size: 1.77 persons. |
| Income per capita | statistik-berlin-brandenburg.de/p-i-10-j/ | Disposable income: €26,209/person (2023). 92.1% of national average. Primary income: €32,466/person. |
| Population forecast 2024-2040 | berlin.de → Bevölkerungsprognose | +109,000 by 2040. Growth concentrated in outer districts. |
| Social monitoring (LOR level) | Monitoring Soziale Stadtentwicklung | Social status index by planning area (LOR). Unemployment rates, child poverty, transfer payment recipients — by sub-district. |

**Action:** Download the district-level demographic tables. The key variables for tenant persona calibration are:
- Income distribution by district (approximate from disposable income + SGB II rates)
- Household size by district
- Age distribution by district
- Migration background share by district (Mitte: 59%, Neukölln: 52.2%, vs Treptow-Köpenick: ~25%)

### 2C. Berlin Open Data Portal

**URL:** https://daten.berlin.de/
**ODIS Geoexplorer:** https://daten.odis-berlin.de
**Key datasets available for direct download (GeoJSON, CSV, Shapefile):**
- LOR (Lebensweltlich orientierte Räume) — planning areas with social indicators
- Block-level geographic boundaries
- Building footprints
- Street segments

**Action:** Download LOR boundaries (GeoJSON) — these are the planning-area polygons you'll use to match spatial features to demographic data.

### 2D. Mietspiegel Berlin 2024 (Official Qualified Rent Index)

**URL:** https://mietspiegel.berlin.de/
**What it is:** The legally binding rent reference standard for Berlin. A qualified Mietspiegel based on scientific methodology.
**What it contains:**
- Rent ranges by: building year bracket × equipment level × residential area class
- Detailed amenity classification (Sondermerkmale)
- Residential area maps (Wohnlagenkarte)
**Action:** Access the online query tool. Note the category structure — this is what your compliance engine needs to replicate (simplified). The printed brochure is available for free pickup at various Berlin offices.

### 2E. Micro Census (Mikrozensus) — Household Net Income

**Reference:** Statistischer Bericht, Table 4.1 — Household net income by household size
**What it gives:** Income distribution brackets by household size for Berlin. More granular than the per-capita figures.
**Action:** Find via statistik-berlin-brandenburg.de under Mikrozensus publications.

### Calibration Summary for Synthetic Tenant Personas:

| Persona parameter | Source | Key values |
|-------------------|--------|-----------|
| Income distribution by district | IBB + Statistik BB (P I 10) | €26,209/person avg. Use SGB II rates to estimate low-income share per district. |
| Household size | Statistik BB Pressemitteilung 186-2025 | 56.5% single, avg 1.77 persons |
| Age distribution | Statistik BB A I 5 | Youngest: Friedrichshain-Kreuzberg (39.3yr), Oldest: Steglitz-Zehlendorf (46.6yr) |
| Migration background | Statistik BB 132-2025 | Citywide 41.7%. Mitte: 59%, Neukölln: 52%, Steglitz-Zehl: ~25% |
| Rent burden (rent/income ratio) | IBB Wohnungsmarktbericht | Estimate from avg rent ÷ avg income per district |
| Tenant type | IBB + GUTHMANN report | Long-term (avg rent €7.67/m²) vs. new contract (€16.35/m²). Turnover <2%/year |

---

## 3. Spatial / Satellite / Aerial Imagery Data

### The question: What resolution and source do you actually need?

For the MietOptimal use case, you need **neighborhood-level** spatial features, not building-level. You're extracting covariates like green space ratio, building density, and construction activity for a ~250m radius around an apartment. This means:

- **You DON'T need:** Sub-meter satellite imagery (expensive, overkill)
- **You DO need:** Medium-resolution imagery (~10-30m) for NDVI/vegetation analysis + high-resolution aerial/map imagery for visual feature extraction via Gemini

### 3A. Sentinel-2 (Free, 10m resolution, ESA)

**What:** European Space Agency's Copernicus Sentinel-2 satellites. 10m/pixel multispectral imagery. Freely available.
**Why useful:** Compute NDVI (Normalized Difference Vegetation Index) per grid cell → green space ratio. This is YOUR remote sensing bread and butter.
**Access:**
- Copernicus Open Access Hub: https://scihub.copernicus.eu/ (soon migrating to Copernicus Data Space: https://dataspace.copernicus.eu/)
- Google Earth Engine (GEE): Search "Sentinel-2 Berlin" — free for research/non-commercial
- Sentinel Hub EO Browser: https://apps.sentinel-hub.com/eo-browser/ (quick visual preview + download)
**Resolution:** 10m bands (B2-B4, B8), 20m bands (B5-B7, B11-B12)
**Temporal:** Revisit every ~5 days. Get a cloud-free composite for Berlin (summer 2024 or 2025 for best vegetation signal).
**Action:** Download a Berlin-wide Sentinel-2 tile. Compute NDVI per pixel. Aggregate to neighborhood-level (LOR or PLZ polygons). This gives you a validated, quantitative green space ratio per area.
**For the pitch:** "We compute vegetation indices from Sentinel-2 satellite imagery at 10m resolution — the same data ESA uses for climate monitoring."

### 3B. Google Maps Static API (High-res aerial view for Gemini)

**What:** Download satellite/aerial view tiles centered on specific coordinates.
**Why useful:** Feed these into Gemini for visual feature extraction (building density, construction activity, street quality, commercial presence). Gemini is better at interpreting high-res aerial imagery than Sentinel-2's 10m pixels.
**Access:** Google Maps Static API — requires API key, free tier: 28,000 loads/month.
**URL format:** `https://maps.googleapis.com/maps/api/staticmap?center=52.4951,13.4232&zoom=17&size=640x640&maptype=satellite&key=YOUR_KEY`
**Resolution:** ~0.5-1m at zoom 17-18. Excellent for visual analysis.
**Action:** Pre-download tiles for 5-10 demo neighborhoods. Feed into Gemini for structured feature extraction.

### 3C. Berlin Open Geodata — Orthophotos (Free, Official)

**What:** Official aerial orthophotos of Berlin, published by the Berlin Senate.
**Access:** Berlin Geoportal FIS-Broker: https://fbinter.stadt-berlin.de/fb/
- WMS service: Digitale farbige Orthophotos (DOP20)
- Resolution: 20cm/pixel — extremely high res
- Updated every 2-3 years
**Why useful:** Higher resolution than Google Maps, freely available, official data. Can feed into Gemini or do your own image processing.
**Formats:** WMS (streaming), or you can request tiles.
**Action:** Access via QGIS or direct WMS calls. Download tiles for demo neighborhoods. This is the best free source for high-res aerial imagery of Berlin.

### 3D. Berlin Umweltatlas (Environmental Atlas — Ground Truth)

**URL:** https://www.berlin.de/umweltatlas/en/
**FIS-Broker portal:** https://fbinter.stadt-berlin.de/fb/
**What it contains (key layers for your project):**

| Layer | What it measures | Use for MietOptimal |
|-------|-----------------|-------------------|
| **Actual Use of Built-up Areas (06.01)** | Land use classification per block | Ground truth for building density, green space |
| **Green and Open Spaces (06.02)** | Public and private green spaces | Validate Gemini green space extraction |
| **Impervious Soil Coverage (01.02)** | % sealed surface per block | Proxy for building density |
| **Noise Immission (07.05)** | Noise levels from traffic | Noise is a rent-relevant factor invisible to Mietspiegel |
| **Air Quality (03.xx)** | Pollution levels | Potential health-related WTP factor |
| **Biotope Types (05.08)** | Vegetation classification | Detailed green space typology |

**Formats:** WMS, WFS, downloadable shapefiles for some layers.
**Action:** Download green space + impervious coverage layers as validation for your Sentinel-2 NDVI and Gemini extraction. Also download noise data — it's a powerful rent predictor that nobody else uses.

### 3E. OpenStreetMap Berlin (Free, Community-Maintained)

**URL:** https://download.geofabrik.de/europe/germany/berlin.html
**What it contains:** Buildings, roads, transit stations, POIs (shops, restaurants, parks), land use.
**Formats:** PBF, Shapefile
**Action:** Download Berlin OSM extract. Extract:
- U-Bahn/S-Bahn station locations → compute transit proximity per apartment
- POI density (shops, restaurants, cafes) per grid cell → walkability/amenity score
- Building footprints → building density validation
- Park polygons → green space validation

### 3F. UP42 / Commercial Satellite Providers (If you want to go premium)

**URL:** https://up42.com/
**What:** Marketplace for commercial satellite imagery from Airbus, Vexcel, Maxar, etc.
**Resolution:** 30cm-50cm, much higher than Sentinel-2.
**Cost:** Varies, but free trials available. UP42 has a developer tier.
**Action:** Only if you want extra wow factor. For the hackathon, Sentinel-2 + Google Maps Static + Berlin Orthophotos are more than sufficient.

### Recommended Spatial Stack (pick this):

| Layer | Source | Resolution | What you extract | How |
|-------|--------|-----------|-----------------|-----|
| **NDVI / Green space** | Sentinel-2 | 10m | Quantitative vegetation index per neighborhood | Python (rasterio, geopandas) — YOUR skillset |
| **Visual features** | Google Maps Static API OR Berlin Orthophotos | 0.5-1m | Building density, construction, street quality, commercial density | Feed into Gemini multimodal → structured JSON |
| **Transit proximity** | OpenStreetMap | Vector | Distance to nearest U-Bahn/S-Bahn | Geopandas spatial join |
| **POI / amenity density** | OpenStreetMap | Vector | Shops, restaurants per grid cell | OSM Overpass API + spatial aggregation |
| **Noise levels** | Umweltatlas | Raster/WMS | Traffic noise immission | WMS download + spatial join |
| **Ground truth** | Umweltatlas green space + impervious | Block-level | Validate NDVI and Gemini extraction | Download shapefiles, compute correlation |

**This gives you a multi-layered spatial feature set that is:**
1. Quantitatively rigorous (Sentinel-2 NDVI, not just Gemini's visual guess)
2. Validated against official data (Umweltatlas)
3. Visually impressive in the demo (satellite imagery + map overlays)
4. Technically deep (shows real spatial analytics skills, not just API calls)
5. Novel in the rental pricing context (nobody else does this)

---

## 4. Quick Reference: All URLs

### Listing Data
- Kaggle ImmoScout24: https://www.kaggle.com/datasets/corrieaar/apartment-rental-offers-in-germany
- GitHub Berlin filtered: https://github.com/MoMkhani/Berlin-House-Prices-Prediction
- RWI-GEO-RED (academic): https://www.rwi-essen.de/en/research-advice/further/research-data-center-ruhr-fdz/

### Demographic / Tenant Data
- IBB Wohnungsmarktbericht: https://www.ibb.de/en/publications/publications.html
- Statistik Berlin-Brandenburg: https://www.statistik-berlin-brandenburg.de/
- Berlin Mietspiegel 2024: https://mietspiegel.berlin.de/
- Berlin Open Data: https://daten.berlin.de/
- ODIS Geoexplorer: https://daten.odis-berlin.de

### Spatial / Imagery
- Sentinel-2 (Copernicus Data Space): https://dataspace.copernicus.eu/
- Sentinel Hub EO Browser: https://apps.sentinel-hub.com/eo-browser/
- Google Maps Static API: https://developers.google.com/maps/documentation/maps-static
- Berlin Geoportal FIS-Broker: https://fbinter.stadt-berlin.de/fb/
- Berlin Umweltatlas: https://www.berlin.de/umweltatlas/en/
- OpenStreetMap Berlin: https://download.geofabrik.de/europe/germany/berlin.html
- Geofabrik OSM extracts: https://download.geofabrik.de/europe/germany/berlin.html

### Infrastructure Partner APIs
- Gemini API: https://ai.google.dev/
- Gradium API: https://gradium.ai/api_docs.html
- Lovable: https://lovable.dev/
- Entire CLI: https://github.com/entireio/cli
- Supabase: https://supabase.com/

---

## 5. Priority Order for Data Acquisition

```
Day 1:
├── Download Kaggle ImmoScout24 dataset → filter to Berlin  [30 min]
├── Download Berlin LOR boundaries (GeoJSON) from ODIS      [15 min]
├── Download OSM Berlin extract from Geofabrik               [15 min]
└── Get Gemini API key + Google Maps Static API key           [15 min]

Day 2:
├── Download Sentinel-2 Berlin tile (cloud-free summer)       [30 min]
├── Compute NDVI per pixel, aggregate to LOR polygons         [1-2 hr]
├── Download Umweltatlas green space layer for validation      [30 min]
└── Download IBB Wohnungsmarktbericht summary PDF             [15 min]

Day 3:
├── Extract demographic stats from Statistik BB publications  [1 hr]
├── Build tenant persona calibration table (income, HH size,  [1 hr]
│   age, migration background — per district)
├── Download Google Maps Static tiles for 5 demo neighborhoods [30 min]
└── Test Gemini spatial extraction on the tiles                [1 hr]

Day 4+:
├── Extract transit stations + POIs from OSM                   [1 hr]
├── Download noise data from Umweltatlas                       [30 min]
├── Assemble complete spatial feature matrix per neighborhood  [1-2 hr]
└── Validate spatial features against ground truth             [1 hr]
```

Total data acquisition + processing: ~12-15 hours across 4-5 sessions.
