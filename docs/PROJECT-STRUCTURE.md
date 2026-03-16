# RentSignal — Project Structure

*Last updated: 2026-03-16*

---

## Root

```
rentsignal/
├── CLAUDE.md                     # Claude Code session protocol + architecture overview
├── README.md                     # Project overview
├── .env.example                  # API key template (never commit .env)
├── .gitignore
├── Procfile                      # Railway: uvicorn backend.main:app
├── railway.toml                  # Railway deployment config
├── nixpacks.toml                 # Nixpacks build (Python 3.11)
├── requirements-api.txt          # Lean API deps (no geopandas/rasterio)
```

## Documentation

```
docs/
├── PRODUCT.md                    # Product & commercial strategy (source of truth)
├── POSITIONING-EVOLUTION.md      # Phase 1→2→3 positioning + copy reference
├── MARKETING.md                  # SEO, channels, Conny positioning, brand identity
├── PROJECT-BRIEF.md              # Founding brief: problem, persona, Q&A prep, pitch narrative
├── PROJECT-STRUCTURE.md          # This file
├── LOVABLE-PROMPT.md             # Lovable frontend generation prompt
├── blog-synthetic-users-validation.md  # Blog draft: "We Ran the Same Experiment Two Ways"
│
├── technical/                    # Implementation specs
│   ├── COMPLIANCE-ENGINE.md      # §556d/§559 BGB rules, Mietspiegel lookup, decision trees
│   ├── SPATIAL-TECHNICAL-NOTES.md # Sentinel-2 + OSM pipeline, Gemini prompts
│   └── DATA-SOURCES.md           # All datasets, URLs, APIs, field specs
│
├── strategy/                     # Strategic planning
│   ├── COMPETITIVE-TEARDOWN.md   # Rentana/Predium/Conny analysis + stolen features
│   └── PREP-ROADMAP.md           # Pre-hackathon task list (mostly complete)
│
├── _archive/                     # Superseded docs
│   └── REFERENCES.md             # External resources (merged into DATA-SOURCES.md)
│
├── ideas/                        # Research & inspiration
│   ├── rental-price-variables-research.md   # Exotic spatial features roadmap
│   ├── RentSignal-Portfolio-Optimization.md  # Portfolio intelligence proposal
│   └── inspo/                    # BeeSignal docs used as templates
│       ├── STRATEGY.md
│       ├── COMMERCIAL.md
│       ├── PRODUCT.md
│       └── ARCHITECTURE.md
│
└── papers/                       # Academic references (PDFs + summaries)
```

## Backend (FastAPI)

```
backend/
├── __init__.py
├── main.py                       # FastAPI app + CORS middleware
├── models/                       # Pydantic schemas
│   ├── apartment.py              # ApartmentInput, PredictionResult, RenovationResult
│   └── compliance.py             # ComplianceInput, ComplianceResult, ModernizationResult
├── routers/                      # API endpoints
│   ├── comply.py                 # POST /compliance
│   ├── demo.py                   # GET /demo/apartments, GET /demo/apartments/{id}
│   ├── predict.py                # POST /predict
│   ├── renovate.py               # POST /renovate
│   └── spatial.py                # GET /spatial/{plz}, GET /spatial
├── services/                     # Business logic
│   ├── compliance_service.py     # Mietpreisbremse rules engine
│   ├── ml_service.py             # XGBoost prediction + SHAP
│   └── renovation_service.py     # Dual-method CATE + WTP + ROI
└── utils/
```

### Planned backend additions (see Backlog.md)

```
backend/
├── auth.py                       # P0: Supabase JWT validation middleware
├── routers/
│   ├── portfolio.py              # P0: CRUD, CSV import, batch analysis
│   ├── address.py                # P0: autocomplete + resolve (OSM Photon)
│   ├── neighborhood.py           # P1: PLZ intelligence + compare
│   ├── rent_increase.py          # P1: §558 calculator + letter PDF
│   └── monitor.py                # P2: alerts + digest
├── services/
│   ├── portfolio_service.py      # P0: portfolio CRUD, batch, CSV import
│   ├── energy_compliance_service.py  # P1: CO2KostAufG
│   ├── neighborhood_service.py   # P1: PLZ-level aggregation
│   ├── rent_increase_service.py  # P1: §558 BGB rules
│   └── monitor_service.py        # P2: nightly watchdog, alerts
```

## Supabase (Database)

```
supabase/
├── README.md                     # Schema overview + apply instructions
└── migrations/                   # Run in order via SQL Editor
    ├── 001_profiles.sql          # User profiles + auto-create trigger
    ├── 002_units.sql             # Portfolio units (core entity)
    ├── 003_analyses.sql          # Cached predict/comply/renovate results
    ├── 004_import_jobs.sql       # CSV import workflow
    ├── 005_alerts.sql            # Monitoring alerts (P2)
    ├── 006_batch_jobs.sql        # Async batch analysis tracking
    ├── 007_views.sql             # Portfolio dashboard views
    └── 008_functions.sql         # Tier checks, prediction limits
```

## Frontend

```
frontend/
├── AUTH-SETUP-GUIDE.md           # Google OAuth + Supabase setup (copy-paste ready)
├── TIER-GATING-SPEC.md           # Page-by-page tier gating matrix
├── DASHBOARD-LOVABLE-PROMPT.md   # Dashboard Lovable prompt
├── LANDING-PAGE-LOVABLE-PROMPT.md # Landing page Lovable prompt
├── rentsignal_dashboard_v3.html  # Interactive dashboard prototype (latest)
├── rentsignal_dashboard_with_maps_v2.html  # Dashboard with Leaflet maps
├── rentsignal_dashboard_design.html        # Early design exploration
└── rentsignal-landing.html       # Landing page prototype
```

## ML Models

```
models/
├── xgboost_rent.joblib           # XGBoost v3 (37 features, R²=0.749)
├── shap_explainer.joblib         # SHAP TreeExplainer (26MB — consider on-the-fly)
├── feature_encoder.joblib        # OrdinalEncoder for categoricals
├── model_config.json             # Feature list, hyperparams, metrics
└── training_report.md            # Training results + validation
```

## Notebooks (execution order)

```
notebooks/
├── 01_data_exploration.ipynb     # Kaggle → 10,275 clean listings
├── 02_model_training.ipynb       # XGBoost + SHAP baseline
├── 03a_spatial_osm.ipynb         # OSM features (9) for 190 PLZs
├── 03b_spatial_satellite.ipynb   # Sentinel-2 NDVI/NDWI/NDBI (9 features)
├── 04_spatial_model_integration.ipynb  # Retrain: 3-model comparison (A/B/C)
├── 05_compliance_engine.ipynb    # Mietpreisbremse validation
├── 06_matching_estimator.ipynb   # PSM causal effects (CATE)
├── 07_conjoint_wtp.ipynb         # BeeSignal CBC + convergence
└── 08_demo_apartments.ipynb      # 5 demo apartments + charts + JSON
```

## Data

```
data/
├── raw/                          # Original downloads (gitignored)
├── processed/                    # Cleaned, feature-engineered
│   ├── listings_clean.parquet    # 10,275 × 27 Berlin listings
│   ├── listings_with_spatial.parquet  # 10,275 × 45 (+ 18 spatial)
│   ├── spatial_osm_features.csv  # 190 PLZs × 9 OSM features
│   ├── spatial_satellite_features.csv  # 190 PLZs × 9 satellite
│   ├── spatial_all_features.csv  # 190 PLZs × 18 combined
│   ├── matching_results.json     # CATE per treatment + heterogeneous effects
│   ├── conjoint_results.json     # WTP estimates + convergence
│   ├── berlin_plz_boundaries.geojson  # 190 PLZ polygons
│   └── *.html, *.png, *.tif     # Maps, charts, satellite rasters
├── demo/                         # Pre-computed demo data (committed)
│   ├── demo_apartments.json      # 5 apartments with all layers
│   └── *.png                     # 5 pitch-ready charts
└── reference/                    # Small lookup tables (committed)
    └── mietspiegel_simplified.json  # Berlin Mietspiegel 2024
```

## Tracking

```
tracking/
├── Backlog.md                    # Task queue (P0→P4 roadmap)
├── Changelog.md                  # Session log
├── Decisions.md                  # Architectural/strategic decision log
└── Memory.md                     # Persistent context across sessions
```

---

## Key Dependencies

```
Notebooks (01-08) → models/*.joblib + data/processed/*
                  ↓
backend/services/ (loads models + data at startup)
                  ↓
backend/routers/  (exposes as HTTP endpoints)
                  ↓
supabase/         (stores user data, analyses, alerts)
                  ↓
frontend/         (React dashboard, consumes API + Supabase)
```

## Quick Start

```bash
# Backend (local)
pip install -r requirements-api.txt
uvicorn backend.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/demo/apartments
```
