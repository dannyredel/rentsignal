# MietOptimal — Project Structure
## VSCode Workspace Reference

---

## Root Structure

```
mietoptimal/
├── README.md                          # Project overview (Devpost/hackathon submission)
├── .gitignore
├── .env.example                       # Template for API keys (never commit .env)
├── .entire/                           # Entire CLI config (auto-generated)
│
├── docs/                              # Project documentation
│   ├── PROJECT-BRIEF.md               # Full project brief (from hackathon OS)
│   ├── PREP-ROADMAP.md                # Pre-hackathon task roadmap
│   ├── DATA-SOURCES.md                # Data acquisition guide
│   ├── PITCH-NOTES.md                 # Speaker notes + Q&A prep
│   └── DEMO-SCRIPT.md                 # Click-by-click demo walkthrough
│
├── data/                              # All data assets (gitignored except small reference files)
│   ├── raw/                           # Original downloaded data (gitignored)
│   │   ├── listings/                  # ImmoScout24 Kaggle data
│   │   │   └── immo_data_berlin.csv
│   │   ├── spatial/                   # Satellite + aerial tiles
│   │   │   ├── sentinel2/             # Sentinel-2 GeoTIFF (10m NDVI)
│   │   │   ├── aerial_tiles/          # Google Maps Static or Berlin Orthophotos
│   │   │   └── osm/                   # OpenStreetMap Berlin extract
│   │   ├── geodata/                   # Berlin administrative boundaries
│   │   │   ├── lor_planungsraeume.geojson
│   │   │   ├── bezirke.geojson
│   │   │   └── plz_berlin.geojson
│   │   └── umweltatlas/               # Environmental atlas layers
│   │       ├── green_spaces.shp
│   │       ├── impervious_surface.shp
│   │       └── noise_immission.shp
│   │
│   ├── processed/                     # Cleaned, feature-engineered datasets
│   │   ├── listings_clean.parquet     # Cleaned Berlin listings with features
│   │   ├── spatial_features.json      # Pre-computed spatial features per neighborhood
│   │   ├── ndvi_by_lor.csv            # NDVI aggregated to LOR planning areas
│   │   ├── transit_proximity.csv      # Distance to nearest station per PLZ
│   │   ├── poi_density.csv            # Amenity counts per grid cell
│   │   └── noise_by_lor.csv           # Noise levels aggregated to LOR
│   │
│   ├── demo/                          # Pre-loaded demo data (committed to repo)
│   │   ├── demo_apartments.json       # 5 demo apartments with all features
│   │   ├── demo_spatial_cards.json    # Spatial feature cards for demo neighborhoods
│   │   ├── demo_shap_values.json      # Pre-computed SHAP for demo apartments
│   │   ├── demo_renovation_results.json # Pre-computed renovation estimates
│   │   └── demo_satellite_tiles/      # Cached aerial images for demo neighborhoods
│   │       ├── kreuzberg.png
│   │       ├── wedding.png
│   │       ├── mitte.png
│   │       ├── lichtenberg.png
│   │       └── prenzlauer_berg.png
│   │
│   └── reference/                     # Small reference tables (committed)
│       ├── mietspiegel_simplified.json # Simplified Mietspiegel lookup table
│       ├── renovation_costs.json      # Average renovation costs by type
│       ├── berlin_districts.json      # District metadata (name, avg income, demographics)
│       └── bvg_stations.json          # U-Bahn/S-Bahn station coordinates
│
├── models/                            # Trained ML model artifacts
│   ├── xgboost_rent.joblib            # Trained XGBoost rent prediction model
│   ├── shap_explainer.joblib          # SHAP TreeExplainer for the model
│   ├── feature_encoder.joblib         # Label encoders / one-hot for categorical features
│   ├── scaler.joblib                  # Feature scaler (if used)
│   └── training_report.md             # Model performance metrics (R², RMSE, MAE)
│
├── backend/                           # FastAPI backend
│   ├── main.py                        # App init, CORS, router mounting
│   ├── config.py                      # Settings, API keys from env
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── routers/
│   │   ├── predict.py                 # POST /predict — rent prediction + SHAP
│   │   ├── compliance.py              # POST /compliance — Mietpreisbremse check
│   │   ├── renovate.py                # POST /renovate — renovation impact simulator
│   │   ├── spatial.py                 # GET /spatial/{neighborhood} — spatial features
│   │   └── demo.py                    # GET /demo/apartments — pre-loaded demo data
│   │
│   ├── services/
│   │   ├── ml_service.py              # Load model, run prediction, compute SHAP
│   │   ├── compliance_service.py      # Mietpreisbremse rules engine
│   │   ├── renovation_service.py      # Dual-method renovation estimator
│   │   │                              #   ├── observational matching (CATE)
│   │   │                              #   └── conjoint simulation (WTP)
│   │   ├── spatial_service.py         # Load/serve pre-computed spatial features
│   │   ├── gemini_service.py          # Gemini API: image→features, NL→structured
│   │   └── gradium_service.py         # Gradium STT: voice→text
│   │
│   ├── models/                        # Pydantic schemas (not ML models)
│   │   ├── apartment.py               # ApartmentInput, ApartmentFeatures
│   │   ├── prediction.py              # PredictionResult, SHAPBreakdown
│   │   ├── compliance.py              # ComplianceResult, LegalMaximum
│   │   ├── renovation.py              # RenovationScenario, DualEstimate, ROI
│   │   └── spatial.py                 # SpatialFeatures, NeighborhoodCard
│   │
│   └── utils/
│       ├── feature_engineering.py     # Transform raw input → model features
│       └── data_loader.py             # Load demo data, reference tables
│
├── conjoint/                          # BeeSignal conjoint engine (adapted for rental)
│   ├── README.md                      # How the conjoint module works
│   ├── config.py                      # Conjoint attribute definitions + levels
│   ├── personas.py                    # Synthetic tenant persona generator
│   │                                  #   calibrated to Berlin demographics
│   ├── simulation.py                  # CBC simulation engine
│   │                                  #   (imported from BeeSignal, adapted)
│   ├── calibration.py                 # Calibrate preferences to market data
│   ├── wtp_estimator.py               # Extract WTP per renovation type
│   └── data/
│       ├── persona_distributions.json # Berlin demographic distributions per district
│       └── conjoint_results_cache.json # Pre-computed results for demo scenarios
│
├── spatial/                           # Spatial analytics pipeline
│   ├── README.md                      # Spatial pipeline documentation
│   ├── ndvi_pipeline.py               # Sentinel-2 → NDVI → aggregate to LOR
│   ├── osm_features.py                # OSM → transit proximity + POI density
│   ├── gemini_extraction.py           # Aerial image → Gemini → structured features
│   ├── noise_processing.py            # Umweltatlas noise → aggregate to LOR
│   ├── validation.py                  # Compare extracted features vs ground truth
│   ├── aggregate.py                   # Combine all spatial layers → feature matrix
│   └── prompts/
│       └── spatial_extraction.txt     # Gemini prompt template for aerial imagery
│
├── notebooks/                         # Jupyter notebooks for exploration + prep
│   ├── 01_data_exploration.ipynb      # EDA on listing data
│   ├── 02_model_training.ipynb        # XGBoost training + evaluation + SHAP
│   ├── 03_spatial_pipeline.ipynb      # NDVI computation + spatial feature assembly
│   ├── 04_conjoint_calibration.ipynb  # Persona calibration + conjoint validation
│   ├── 05_matching_estimator.ipynb    # Observational CATE estimation
│   ├── 06_demo_data_prep.ipynb        # Generate demo apartment outputs
│   └── 07_gemini_testing.ipynb        # Test Gemini spatial + NL extraction prompts
│
├── frontend/                          # Lovable-generated React app (or manual)
│   ├── README.md                      # Frontend setup instructions
│   ├── lovable_prompt.md              # The prompt used to generate the app
│   └── src/                           # (Generated by Lovable, exported to GitHub)
│       └── ...                        # React + Tailwind + Supabase connector
│
├── pitch/                             # Presentation materials
│   ├── gamma_content.md               # Slide content for Gamma.app
│   ├── demo_script.md                 # Second-by-second demo walkthrough
│   ├── backup_screenshots/            # Static screenshots in case demo fails
│   │   ├── screen1_input.png
│   │   ├── screen2_dashboard.png
│   │   └── screen3_renovation.png
│   └── backup_video.mp4              # Screen recording of working demo
│
└── scripts/                           # Utility scripts
    ├── setup.sh                       # Install deps, download data, train model
    ├── seed_supabase.py               # Upload demo data to Supabase
    ├── precompute_demo.py             # Run all predictions for demo apartments
    ├── download_tiles.py              # Fetch Google Maps Static tiles for demo
    └── deploy.sh                      # Deploy backend to Railway, frontend to Vercel
```

---

## Key Dependency Flows

```
notebooks/01 → data/processed/listings_clean.parquet
notebooks/02 → models/*.joblib
notebooks/03 → data/processed/spatial_features.json, ndvi_by_lor.csv
notebooks/04 → conjoint/data/persona_distributions.json
notebooks/05 → (uses listings_clean.parquet → matching estimates)
notebooks/06 → data/demo/*.json (assembles everything for demo)
notebooks/07 → spatial/prompts/spatial_extraction.txt (refined prompt)

backend/ ← models/*.joblib (prediction)
backend/ ← data/demo/*.json (demo apartments)
backend/ ← data/reference/*.json (Mietspiegel, renovation costs)
backend/ ← conjoint/ (renovation WTP estimation)
backend/ ← data/processed/spatial_features.json (spatial)

frontend/ → backend/ (API calls)
frontend/ → Supabase (demo apartment data)
```

---

## .env.example

```bash
# Google / Gemini
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_MAPS_API_KEY=your_maps_api_key

# Gradium (Voice)
GRADIUM_API_KEY=your_gradium_api_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# Backend
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# Railway (deploy)
RAILWAY_TOKEN=your_railway_token
```

---

## .gitignore

```
# Environment
.env
venv/
__pycache__/
*.pyc

# Data (large files)
data/raw/
data/processed/*.parquet
*.tif
*.tiff
*.pbf

# Models (large binaries)
models/*.joblib

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/settings.json
*.code-workspace

# Node (frontend)
frontend/node_modules/
frontend/.next/
frontend/dist/

# Misc
*.log
.entire/checkpoints/
```

---

## requirements.txt (backend)

```
# API
fastapi==0.115.*
uvicorn[standard]==0.34.*
python-dotenv==1.1.*
pydantic==2.10.*

# ML
scikit-learn==1.6.*
xgboost==2.1.*
shap==0.46.*
joblib==1.4.*

# Data
pandas==2.2.*
numpy==2.1.*
pyarrow==18.*

# Spatial
geopandas==1.0.*
rasterio==1.4.*
shapely==2.0.*

# APIs
google-generativeai==0.8.*       # Gemini SDK
httpx==0.28.*                     # Async HTTP for Gradium WebSocket
websockets==14.*                  # Gradium STT streaming

# Utils
orjson==3.10.*                    # Fast JSON serialization
```

---

## Notebook Execution Order (Pre-Hackathon)

```
Week 1-2:
  01_data_exploration.ipynb       → Understand the data, check distributions
  02_model_training.ipynb         → Train XGBoost, evaluate, save artifacts

Week 3:
  03_spatial_pipeline.ipynb       → NDVI, OSM features, Gemini testing
  04_conjoint_calibration.ipynb   → Persona distributions, WTP validation

Week 4:
  05_matching_estimator.ipynb     → Observational CATE for renovations
  07_gemini_testing.ipynb         → Refine spatial extraction prompts

Week 5:
  06_demo_data_prep.ipynb         → Assemble everything for the 5 demo apartments

Hackathon day:
  (No notebooks — everything is in backend/ and served via API)
```

---

## API Endpoint Reference (FastAPI)

```
GET  /health                              → { status: "ok" }

# Demo data
GET  /demo/apartments                     → List of 5 pre-loaded demo apartments
GET  /demo/apartments/{id}                → Single demo apartment with all outputs

# Prediction
POST /predict                             → Rent prediction + SHAP breakdown
     Body: { district, sqm, year, floor, amenities... }
     Returns: { predicted_rent, confidence_interval, shap_values[] }

# Compliance
POST /compliance                          → Mietpreisbremse check
     Body: { district, sqm, year, amenities, current_rent? }
     Returns: { legal_max, is_compliant, gap, exceptions[] }

# Renovation simulator
POST /renovate                            → Dual-method renovation impact
     Body: { apartment_features, renovation_type, renovation_cost }
     Returns: {
       legal_ceiling_shift,
       observational_cate: { estimate, ci_low, ci_high },
       conjoint_wtp: { estimate, ci_low, ci_high },
       convergence: "green" | "amber",
       effective_uplift,
       payback_months,
       demand_curve: [{ price_premium, pct_prefer }]
     }

# Spatial
GET  /spatial/{neighborhood}              → Spatial feature card
     Returns: { green_space_ratio, building_density, transit_score,
                construction_activity, noise_level, poi_density,
                satellite_image_url }

# AI features
POST /extract/image                       → Gemini: apartment photo → features
     Body: { image_base64 }
POST /extract/text                        → Gemini: NL description → features
     Body: { description: "2-room Altbau in Kreuzberg..." }
POST /extract/voice                       → Gradium STT → Gemini → features
     Body: { audio_base64 }
```

---

## Quick Start (Hackathon Day)

```bash
# 1. Clone and setup
git clone https://github.com/your-username/mietoptimal.git
cd mietoptimal
cp .env.example .env  # Fill in API keys

# 2. Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Seed demo data
cd ../scripts
python seed_supabase.py
python precompute_demo.py

# 4. Frontend (Lovable-generated, or manual)
cd ../frontend
npm install && npm run dev

# 5. Enable Entire tracking
cd ..
entire enable
```
