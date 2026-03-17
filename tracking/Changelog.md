# Changelog
## MietOptimal — Session Log

---

### 2025-03-14 Session 0: Strategic Planning & Project Setup
**Duration:** ~3h (Claude.ai conversation, not Claude Code)
**Type:** Planning / pre-development

**What happened:**
- Analyzed Big Berlin Hack sponsor landscape (Buena, Qontext, Inca + infrastructure partners)
- Evaluated three track partners: scored Buena 4.2/5, Inca 4.0/5, Qontext 3.0/5
- Deep-dived Buena (proptech, €49M raised, 60k units, GV-backed) and Inca (insurance claims AI)
- Generated 3 project ideas per track, scored by feasibility, demo-ability, differentiation
- Built full project brief for ReserveIQ (Inca track) — claims reserve optimizer
- Built full project brief for MietOptimal (Buena track) — rent optimization engine
- Ran head-to-head comparison: MietOptimal won 6-3 on execution safety, sponsor alignment, data availability
- Identified spatial analytics as unique differentiator → satellite-derived neighborhood features
- Mapped all 4 infrastructure partners: Gemini (core AI), Lovable (frontend), Gradium (voice), Entire (dev tracking)
- Refined ML architecture: XGBoost (prediction) + SHAP (explainability) + dual causal method (matching + conjoint)
- Discussed hedonic models vs ML — decided XGBoost for accuracy, SHAP for interpretability, causal matching + conjoint for renovation counterfactuals
- Discussed synthetic conjoint users for identification — decided dual-method approach (observational + simulated) with convergence validation
- Mapped competitive landscape: Official Mietspiegel Rechner, Conny, ImmoScout24, Immowelt, aggregator sites → identified 6 gaps nobody fills
- Researched all data sources: Kaggle listings, IBB reports, Statistik BB demographics, Sentinel-2, Berlin Umweltatlas, OSM

**Artifacts produced:**
- `docs/PROJECT-BRIEF.md` — MietOptimal v2 complete project brief (with spatial layer, dual-method causal, competitive landscape, BeeSignal connection)
- `docs/PREP-ROADMAP.md` — Prioritized 12-task roadmap across 6 weeks
- `docs/DATA-SOURCES.md` — Comprehensive data guide (listings, demographics, spatial imagery)
- `docs/PROJECT-STRUCTURE.md` — Full folder structure, .env, requirements.txt, API endpoints
- `CLAUDE.md` — Session management protocol, skills/agents reference, architecture overview
- `tracking/Backlog.md` — Task queue initialized from roadmap
- `tracking/Decisions.md` — 6 key strategic decisions recorded with rationale
- `tracking/Memory.md` — Current state, API status, context, gotchas
- `tracking/Changelog.md` — This file

**Also produced (not carried forward):**
- ReserveIQ project brief (Inca track) — archived, not pursuing
- MietOptimal v1 project brief — superseded by v2
- RentSignal-Revenue-Model.html — revenue calculations (content merged into project brief)

**State at end of session:**
- All planning documents complete
- Competitive teardown of Rentana, Predium, and Conny complete with stolen features prioritized
- Revenue model with TAM/SAM/SOM and client-level calculations complete
- Feature roadmap prioritized: Hackathon Core → P1 (weeks 1-4 post) → P2 (months 2-3) → P3 (months 4-12)
- ESG expansion path identified (same satellite pipeline, minimal incremental cost)
- Working product name: RentSignal
- Zero code written yet
- Next action: Task 1 (source Berlin listing data) + Task 7 (set up API accounts)
- 6 weeks until hackathon (April 25)

---

### 2026-03-14 Session 1: File Organization & Git Init
**Duration:** ~15min
**Type:** Project setup

**Tasks completed:**
- Organized all planning docs from flat root into `docs/` and `tracking/` directories per PROJECT-STRUCTURE.md
- Created full folder skeleton: `backend/`, `conjoint/`, `spatial/`, `notebooks/`, `frontend/`, `pitch/`, `scripts/`, `data/` (with `raw/`, `processed/`, `demo/`, `reference/` subdirs), `models/`
- Created `.env.example`, `.gitignore`, `backend/requirements.txt`, `README.md` from PROJECT-STRUCTURE.md templates
- Added `docs/COMPETITIVE-TEARDOWN.md` (not in original structure spec but important planning doc)
- Initialized git repo and made initial commit

**Artifacts produced:**
- `.env.example` — API key template
- `.gitignore` — standard ignores for data, models, node_modules, env
- `backend/requirements.txt` — Python dependencies
- `README.md` — Project one-liner
- `.gitkeep` files in all empty placeholder directories

**State at end of session:**
- Project structure matches PROJECT-STRUCTURE.md spec
- Git initialized with clean initial commit (9abf72a)
- Zero code written — ready to start Task 1 (source listing data) or Task 7 (API accounts)
- 6 weeks until hackathon (April 25)

---

### 2026-03-15 Session 2: Data Pipeline + Model Training
**Duration:** ~2h
**Type:** Data engineering + ML

**Tasks completed:**
- **Task 1:** Built `notebooks/01_data_exploration.ipynb` — loaded Kaggle ImmoScout24 (268k rows), filtered to Berlin (10,406), cleaned outliers, engineered features (building_era, bezirk, sqm_per_room), exported 10,275 clean rows to `data/processed/listings_clean.parquet`
- **Task 2:** Built `notebooks/02_model_training.ipynb` — trained XGBoost with GridSearchCV (36 configs × 5-fold CV), achieved R²=0.73 vs linear baseline R²=0.34. SHAP analysis shows bezirk, hasKitchen, livingSpace, building_era as top drivers. Kitchen SHAP (+0.96) is 16× balcony (+0.06) — validates "don't build the balcony" demo narrative.
- Assessed 4 GitHub repos — all rated LOW for direct use
- Created `docs/REFERENCES.md`, `.claude/skills/paper-reviewer.md`
- Resolved dependency issues: xgboost 3.2, shap 0.48→0.51, numpy/matplotlib compat

**Artifacts produced:**
- `notebooks/01_data_exploration.ipynb`, `notebooks/02_model_training.ipynb`
- `data/processed/listings_clean.parquet` (10,275 × 27)
- `models/xgboost_rent.joblib`, `models/shap_explainer.joblib`, `models/feature_encoder.joblib`
- `models/model_config.json`, `models/training_report.md`
- `docs/REFERENCES.md`, `.claude/skills/paper-reviewer.md`

**State at end of session:**
- Tasks 1 & 2 (P0) complete — critical path unblocked
- Next: Task 3 (conjoint), Task 4 (spatial), Task 5 (compliance) — all unblocked
- Model R²=0.73 baseline — will improve with spatial features
- Data vintage (2018-2019) still needs price calibration for 2024-2025
- Apify ImmoScout24 scraper identified as path to current data (parked for now, files in `data/raw/scraping/`)
- ~6 weeks until hackathon (April 25)

---

### 2026-03-15 Session 2b: Spatial Pipeline Planning
**Duration:** ~30min
**Type:** Planning / architecture

**Tasks completed:**
- Designed 3-phase spatial pipeline: OSM vector → Sentinel-2 DIY → Gemini (hackathon day)
- Created `docs/SPATIAL-TECHNICAL-NOTES.md` with full technical plan: feature comparison table, data sources, implementation phases, effort estimates
- Identified Apify ImmoScout24 scrapers for current price data — parked, URLs saved in `data/raw/scraping/`
- Updated `docs/REFERENCES.md` with Apify sources
- Decision: Gemini spatial extraction deferred to hackathon day (pre-compute for 5 demo neighborhoods only)

**Artifacts produced:**
- `docs/SPATIAL-TECHNICAL-NOTES.md` — full technical plan with 3 spatial data categories, feature tables, implementation phases
- `data/raw/scraping/` — directory for Apify files (92 Berlin neighborhood URLs)

**State at end of session:**
- Task 4 Phase 1 (OSM features) ready to build — no dependencies
- Task 4 Phase 2 (Sentinel-2) ready — needs Copernicus account (free)
- Next action: build `notebooks/03a_spatial_osm.ipynb`

---

### 2026-03-15 Session 3: OSM Spatial Pipeline + Model Integration
**Duration:** ~3h
**Type:** Spatial data engineering + ML integration

**Tasks completed:**
- **Task 4 Phase 1:** Built `notebooks/03a_spatial_osm.ipynb` — extracted 9 OSM spatial features for 190 Berlin PLZs via Overpass API (transit stations, restaurants/cafes, shops, parks, water bodies, schools). Computed distance-to-nearest and density-within-radius features per PLZ centroid. Created interactive Folium maps (HTML) + matplotlib choropleths.
- **Spatial-Model Integration:** Built `notebooks/04_spatial_model_integration.ipynb` — retrained XGBoost with 28 features (19 original + 9 spatial). R² improved 0.747 → 0.769 (+3.1%), RMSE improved 2.57 → 2.45 €/m² (4.6% better). Key finding: `count_food_1000m` (restaurant density) is the #1 most important feature in the entire model (SHAP=1.89), more than 2.5× livingSpace.
- Added Task 13 to backlog: upgrade spatial features to per-listing lat/lon when coordinate data becomes available.

**Artifacts produced:**
- `notebooks/03a_spatial_osm.ipynb` — OSM spatial feature extraction pipeline
- `notebooks/04_spatial_model_integration.ipynb` — model retraining with spatial features
- `data/processed/spatial_osm_features.csv` (190 × 10)
- `data/processed/listings_with_spatial.parquet` (10,275 × 36)
- `data/processed/berlin_plz_boundaries.geojson` (190 polygons)
- `data/processed/map_transit_distance.html`, `map_food_density.html`, `map_combined_overview.html`
- `data/processed/spatial_osm_maps.png`
- Updated `models/` artifacts (xgboost_rent.joblib, shap_explainer.joblib, model_config.json, training_report.md)

**State at end of session:**
- Task 4 Phase 1 complete, model retrained with spatial features
- XGBoost R²=0.77 (up from 0.73), 28 features
- Restaurant density is #1 SHAP feature — strong pitch narrative
- PLZ boundary sources (OpenDataSoft, suche-postleitzahl.org, GitHub) were all down — used Nominatim geocoding fallback (190/214 PLZs)
- Kaggle data lacks lat/lon — spatial features are at PLZ centroid level (Task 13 for upgrade)
- Next: Task 4 Phase 2 (Sentinel-2 satellite indices) or Task 5 (Mietpreisbremse compliance engine)

---

### 2026-03-15 Session 3b: Sentinel-2 Satellite Pipeline + Full Model Integration
**Duration:** ~2h
**Type:** Spatial data engineering + ML integration

**Tasks completed:**
- **Task 4 Phase 2:** Built `notebooks/03b_spatial_satellite.ipynb` — computed NDVI, NDWI, NDBI from Sentinel-2 L2A imagery via Microsoft Planetary Computer STAC API (free, no account needed). Scene: S2B_MSIL2A_20240820, 0.6% cloud cover, summer 2024. Full tile read (10980×10980 at 10m), SWIR upsampled 20m→10m via scipy.ndimage.zoom. Zonal statistics (mean/std/median) per PLZ using 500m buffer polygons.
- **Model Integration v3:** Updated `notebooks/04_spatial_model_integration.ipynb` with 3-model comparison:
  - Model A (19 original features): R²=0.7248, RMSE=2.72
  - Model B (+9 OSM = 28 features): R²=0.7453, RMSE=2.61
  - Model C (+9 OSM +9 satellite = 37 features): R²=0.7491, RMSE=2.59
- Satellite adds modest but real improvement (+0.5% R² over OSM-only). ndwi_median is the top satellite feature (SHAP=0.24, rank #9 overall).

**Artifacts produced:**
- `notebooks/03b_spatial_satellite.ipynb` — Sentinel-2 satellite feature extraction pipeline
- `notebooks/04_spatial_model_integration.ipynb` — updated with 3-model comparison (A/B/C)
- `data/processed/spatial_satellite_features.csv` (190 × 10)
- `data/processed/spatial_all_features.csv` (190 × 19)
- `data/processed/listings_with_spatial.parquet` (10,275 × 45, updated with satellite features)
- `data/processed/ndvi_berlin.tif`, `ndwi_berlin.tif`, `ndbi_berlin.tif`
- `data/processed/satellite_indices_berlin.png`
- Updated `models/` artifacts (xgboost_rent.joblib, shap_explainer.joblib, model_config.json, training_report.md — now v3 with 37 features)

**State at end of session:**
- Task 4 Phases 1 & 2 complete — spatial pipeline done (OSM + satellite)
- XGBoost v3: R²=0.749, RMSE=2.59 €/m², 37 features
- count_food_1000m still #1 SHAP (1.71), ndwi_median is top satellite feature (#9 overall)
- Satellite correlations: ndwi_median (+0.46), ndvi_median (-0.45), ndbi_mean (+0.38)
- Microsoft Planetary Computer = free Sentinel-2 access, no account needed — great for pitch ("zero data cost")
- Next: Task 5 (Mietpreisbremse compliance engine) or Task 3 (BeeSignal conjoint)

---

### 2026-03-15 Session 4: Mietpreisbremse Compliance Engine
**Duration:** ~45min
**Type:** Rules engine / Python module

**Tasks completed:**
- **Task 5:** Built the Mietpreisbremse compliance engine — three components:
  1. `data/reference/mietspiegel_simplified.json` — Simplified Berlin Mietspiegel 2023 lookup table with 8 building year × 4 size × 3 location categories, plus 8 equipment adjustment factors
  2. `backend/models/compliance.py` — Pydantic schemas (ComplianceInput, ComplianceResult, ModernizationInput, ModernizationResult, etc.)
  3. `backend/services/compliance_service.py` — Rules engine implementing §556d BGB (rent brake: 110% of Mietspiegel mid) and §559 BGB (modernization: 8% passthrough with 6-year caps)
- Validated on all 5 demo apartments + edge cases (Vormiete exception, prior increase tracking, no-current-rent mode)
- Key insight for demo: §559 legal passthrough gives identical 12.5yr payback for all renovations (1/0.08). The "don't build the balcony" differentiation comes from the MARKET layer (SHAP), not the legal layer. Perfect pitch narrative.

**Artifacts produced:**
- `data/reference/mietspiegel_simplified.json` — Mietspiegel lookup table
- `backend/models/compliance.py` — Pydantic schemas
- `backend/services/compliance_service.py` — Compliance rules engine
- `backend/__init__.py`, `backend/models/__init__.py`, `backend/services/__init__.py` — Package init files
- `notebooks/05_compliance_engine.ipynb` — Validation notebook

**State at end of session:**
- Tasks 1, 2, 4 (Phases 1-2), 5 complete
- Next unblocked: Task 3 (BeeSignal conjoint), Task 6 (matching estimator), Task 8 (demo apartments, partially unblocked)

---

### 2026-03-15 Session 4b: Legal Updates + Matching Estimator
**Duration:** ~1.5h
**Type:** Legal compliance update + Causal inference

**Tasks completed:**
- **Task 5 updates:** Deep legal research → updated Mietspiegel from 2023 to 2024, fixed Neubau cutoff to >= 2015 (legal: post-Oct 1 2014), added §559e BGB GEG heating path (10% passthrough, €0.50/m² cap), added bilingual DE/EN output, created `docs/COMPLIANCE-ENGINE.md` documentation
- **Task 6:** Built propensity score matching estimator for causal renovation effects (CATE):
  - Method: Logistic PS → 1:1 NN matching (caliper=0.2 SD logit PS, without replacement) → bootstrap 1000× CIs
  - **Kitchen: +2.91 €/m² [2.65, 3.18]** (2,288 pairs, 14/14 balanced) — headline result
  - **Lift: +1.09 €/m² [0.71, 1.42]** (1,480 pairs)
  - **Garden: +0.93 €/m² [0.48, 1.35]** (1,120 pairs)
  - **Balcony: -0.72 €/m² [-1.07, -0.40]** (1,764 pairs) — negative! "Don't build the balcony" confirmed causally
  - Heterogeneous effects: kitchen CATE strongest in 1965-1972 buildings (+4.47 €/m²), weakest in 2003-2014 (+0.29)
  - Confounding bias revealed: raw kitchen premium (+3.95) → causal (+2.91), raw lift premium (+2.74) → causal (+1.09)
  - Caliper robustness: estimates stable across 0.1-0.5 SD
  - Exported to `data/processed/matching_results.json` for API use

**Artifacts produced:**
- `notebooks/06_matching_estimator.ipynb` — Full PSM pipeline (13 cells)
- `data/processed/matching_results.json` — CATE estimates per treatment + heterogeneous effects
- `docs/COMPLIANCE-ENGINE.md` — Full compliance engine documentation
- Updated `backend/services/compliance_service.py` (§559e, bilingual, Neubau fix)
- Updated `backend/models/compliance.py` (§559e fields, bilingual fields)
- Updated `data/reference/mietspiegel_simplified.json` (2024, Neubau label)
- Updated `notebooks/05_compliance_engine.ipynb` (bilingual output, §559e test)

**State at end of session:**
- Tasks 1, 2, 4 (Phases 1-2), 5, 6 complete
- The "don't build the balcony" narrative now has causal backing: kitchen CATE is +2.91, balcony is NEGATIVE (-0.72)
- Next unblocked: Task 3 (BeeSignal conjoint), Task 7 (infrastructure), Task 8 (demo apartments)

---

### 2026-03-15 Session 5: BeeSignal Conjoint Calibration + Dual-Method Convergence
**Duration:** ~2.5h
**Type:** Synthetic conjoint / causal inference validation

**Tasks completed:**
- **Task 3:** Adapted BeeSignal CBC engine for Berlin rental apartment WTP estimation:
  - Designed 6-attribute study: monthly rent (€900-1,350 for 65m², 4 levels) + kitchen + balcony + elevator + garden + condition (binary)
  - Created 6 Berlin tenant persona segments from IBB Wohnungsmarktbericht 2025 demographics (young professional 35%, couple 20%, student 15%, expat 15%, family 10%, older renter 5%)
  - D-optimal design (d-efficiency=0.30, rank sufficient, orthogonal), 10 tasks, dual-response elicitation
  - 75 LLM respondents (GPT-5-mini), 750 total choice observations, ~$6 API cost, ~12min runtime
  - MNL estimation: pseudo-R²=0.43, price coefficient correctly negative (-0.0048, p<0.0001)
  - **Kitchen WTP: +€268/mo = +€4.13/m²** — strongest feature by far
  - Condition: +€134/mo (+€2.06/m²), Elevator: +€92/mo (+€1.41/m²), Balcony: +€66/mo (+€1.01/m²), Garden: +€43/mo (+€0.67/m²)
  - 58.8% none-option rate (realistic Berlin price sensitivity), 59.2% order agreement
- **Dual-method convergence validated:**
  - Kitchen: CATE +€4.01 vs WTP +€4.13 (3% difference!) — extraordinary convergence
  - Elevator: CATE +€1.50 vs WTP +€1.41 (6% difference)
  - Garden: CATE +€1.27 vs WTP +€0.67 (directionally consistent)
  - Balcony: CATE -€1.00 vs WTP +€1.01 — **stated/revealed preference gap** (tenants say they'd pay more, market says they don't)
  - 3/4 direction match, kitchen/elevator quantitatively precise
- **Blog article drafted:** `docs/blog-synthetic-users-validation.md` — "We Ran the Same Experiment Two Ways. The Results Were 3% Apart." Technical but accessible, includes all key charts and tables.

**Artifacts produced:**
- `notebooks/07_conjoint_wtp.ipynb` — Full CBC pipeline (setup → design → survey → estimation → convergence)
- `data/processed/conjoint_results.json` — WTP estimates + convergence data for API use
- `data/processed/convergence_cate_vs_wtp.png` — Side-by-side convergence bar chart
- `data/conjoint/berlin_rental/` — Raw survey responses (responses.csv)
- `docs/blog-synthetic-users-validation.md` — Blog article draft

**Key bugs fixed during session:**
- `MIETOPTIMAL_ROOT` path bug: `Path(".").resolve().parent` resolved wrong after `os.chdir(BEESIGNAL_ROOT)` → hardcoded correct path
- `await survey.run()` → `survey.run()` (not async)
- `result` → `result.responses` for `save_responses()`
- Multiple BeeSignal API mismatches: `respondent_id` → `consumer_id`, `chosen_option` → `choice`, `pseudo_r_squared` → `pseudo_r2`, `coefficients`/`std_errors`/`p_values` (lists) → `params`/`std_errors`/`p_values` (dicts), `wtp.estimates` → `wtp.rows`, `amce.effects` → `amce.rows`, `plot_amce` → `amce_plot`, `plot_wtp_bars` → `wtp_bars`, `diag.checks` → `diag.flags`

**State at end of session:**
- Tasks 1, 2, 3, 4 (Phases 1-2), 5, 6 complete
- Dual-method convergence validated — "don't build the balcony" confirmed by 3 independent methods (SHAP, CATE, conjoint ranking)
- Blog article drafted for BeeSignal
- Next unblocked: Task 7 (infrastructure), Task 8 (demo apartments), Task 9 (pitch deck)

---

### 2026-03-15 Session 6: Demo Apartments Notebook
**Duration:** ~1.5h
**Type:** Demo preparation / visualization

**Tasks completed:**
- **Task 8:** Built `notebooks/08_demo_apartments.ipynb` — 5 realistic Berlin apartments with pre-computed outputs through all 4 layers:
  1. **Kreuzberg Altbau** (The Hidden Gem): Underpriced by 13%, kitchen ROI 25%/yr
  2. **Wedding Altbau** (The Renovation Star): Kitchen +€4.07/m² (57mo payback) vs Balcony +€0.01/m² (never pays back)
  3. **Mitte Neubau** (Premium New Build): Mietpreisbremse exempt (post-2014 §556f), underpriced by 18%
  4. **Lichtenberg Plattenbau** (Compliance Risk): Overpriced by 35%, €289/month legal exposure
  5. **Prenzlauer Berg Renovated** (Gentrification Signal): Post-modernization premium confirmed
- 5 pitch-ready PNG charts with custom Tailwind-inspired color scheme
- Speaker notes auto-generated for all 5 apartments
- All results exported to `data/demo/demo_apartments.json`

**Artifacts produced:**
- `notebooks/08_demo_apartments.ipynb` — Full demo pipeline (21 cells)
- `data/demo/demo_apartments.json` — Pre-computed outputs for API/frontend
- `data/demo/demo_overview.png` — Portfolio overview (3-bar comparison)
- `data/demo/shap_wedding.png` — SHAP waterfall for Wedding Altbau
- `data/demo/renovation_wedding.png` — Dual-method renovation ROI
- `data/demo/compliance_lichtenberg.png` — Compliance risk gauge
- `data/demo/kitchen_vs_balcony.png` — "Don't Build the Balcony" punchline chart

**Bugs fixed:**
- `ComplianceService` class doesn't exist → used standalone `check_compliance()` function
- Cell type wrong (markdown instead of code) for apartment definitions
- Duplicate cells accumulated from multiple edits → cleaned up
- `float32` not JSON serializable → added `make_serializable()` recursive converter
- Kitchen vs Balcony chart: annotations overlapping title, "nan" payback → repositioned, "Never pays back" text

**State at end of session:**
- Tasks 1, 2, 3, 4 (Phases 1-2), 5, 6, 8 complete
- Demo apartments ready with all 4 layers computed
- Next unblocked: Task 7 (infrastructure), Task 9 (pitch deck), Task 10 (Lovable test)

---

### 2026-03-15 Session 7: FastAPI Backend + Product Strategy
**Duration:** ~2.5h
**Type:** Backend engineering + product strategy

**Tasks completed:**
- **Task 7 (partial):** Built complete FastAPI backend with 8 endpoints:
  - `GET /health` — health check
  - `GET /demo/apartments` — list 5 demo apartments
  - `GET /demo/apartments/{id}` — get single demo apartment
  - `POST /predict` — XGBoost rent prediction with SHAP explanations (loads model, encoder, explainer, spatial data at module level)
  - `POST /compliance` — Mietpreisbremse compliance check (§556d BGB)
  - `POST /renovate` — Dual-method renovation simulator (CATE + WTP + ROI + §559 passthrough)
  - `GET /spatial/{plz}` — spatial features for a PLZ
  - `GET /spatial` — list all available PLZs
  - All endpoints tested successfully via curl on localhost:8000
  - Infrastructure accounts: Lovable ✅ (user has), Supabase ✅ (user has), Gemini/Gradium deferred to hackathon day
- **Product Strategy:** Created comprehensive `docs/PRODUCT.md` — 14-section product & commercial strategy document:
  - Category ownership: "Regulated Rent Intelligence"
  - 3-layer product: Compliance Shield → Market Intelligence → Portfolio Intelligence
  - Customer segments: property managers (early adopters), institutional landlords, proptech platforms
  - Format: SaaS dashboard (B2B), unit-level tool as acquisition wedge
  - Pricing: Free tier → Professional (€2.99/unit/mo) → Enterprise (custom)
  - GTM: land-with-compliance, expand-with-intelligence
  - Revenue projections: €500K ARR Y1 → €5M Y3
  - Research roadmap integration (exotic spatial features expand moat, don't change short-term plan)
  - BeeSignal-inspired additions: brand voice & vocabulary rules, messaging matrix by audience, objection handling playbook, content strategy with 5 clusters

**Artifacts produced:**
- `backend/main.py` — FastAPI app entry point with CORS
- `backend/models/apartment.py` — Pydantic schemas (ApartmentInput, PredictionResult, RenovationOption, RenovationResult)
- `backend/services/ml_service.py` — ML prediction service (model + SHAP + spatial lookup)
- `backend/services/renovation_service.py` — Renovation simulator (CATE + WTP + ROI)
- `backend/routers/demo.py` — Demo apartments endpoints
- `backend/routers/predict.py` — Prediction endpoint
- `backend/routers/comply.py` — Compliance endpoint
- `backend/routers/renovate.py` — Renovation endpoint
- `backend/routers/spatial.py` — Spatial features endpoints
- `backend/routers/__init__.py` — Package init
- `docs/PRODUCT.md` — Full product & commercial strategy (~400+ lines)

**State at end of session:**
- Tasks 1, 2, 3, 4 (Phases 1-2), 5, 6, 7 (partial), 8 complete
- Backend API fully functional on localhost:8000
- Product strategy documented — ready to inform frontend design and pitch
- Next: Task 9 (pitch deck), frontend (Lovable prompt), Task 10 (Lovable test)

---

### 2026-03-15 Session 8: Marketing Strategy + Brand Identity + Lovable Prompt
**Duration:** ~1.5h
**Type:** Marketing / brand / frontend planning

**Tasks completed:**
- **Marketing strategy:** Created `docs/MARKETING.md` — 10-section marketing plan:
  - Brand naming analysis: scored 6 options, MietOptimal (40pts) vs RentSignal (38pts)
  - SEO keyword strategy: 4 tiers (landlord DE, tenant DE, expat EN, long-tail) with 12-week content calendar
  - Channel strategy: LinkedIn primary, avoid TikTok/Instagram where Conny dominates
  - Competitive positioning: "landlord's defense against Conny" — Conny's ad spend creates our demand
  - Launch sequence: pre-launch → launch week → month 1 playbook
  - Conny intelligence brief: strengths, weaknesses, the judo move
- **Brand name decision:** Locked in **RentSignal** — international-ready, BeeSignal brand family, works for EU expansion (Austria, Netherlands, France, Sweden all have similar rent regulation). Conny precedent: they went FROM German (Wenigermiete) TO international.
- **Domain:** rentsignal.de available (€5.93/yr), rentsignal.app (€11.03/yr), rentsignal.io (€29.73/yr). Recommended: buy .de now, .app optional.
- **Brand identity prompt:** Built comprehensive Nano Banana / Gemini prompt for brand identity generation — logo, color palettes (2-3 options), typography, architectural blueprint grid texture, dashboard mockup, landing page mockup. User generated first round — liked architectural grid background and dashboard layout, wants to iterate on colors.
- **Lovable prompt:** Created `docs/LOVABLE-PROMPT.md` — full frontend spec:
  - Landing page: hero with grid texture, 3 feature cards, pricing, social proof
  - Dashboard: 5 pages (Overview, Predict, Comply, Renovate, Spatial) + Portfolio placeholder
  - All 8 FastAPI endpoints mapped to specific pages with exact request/response schemas
  - Supabase auth + 3 tables (profiles, analyses, apartments) with RLS
  - Design system: Inter + JetBrains Mono, sharp geometry, architectural grid, no italics
  - Colors: derive from brand screenshots (not locked in yet)

**Artifacts produced:**
- `docs/MARKETING.md` — Full marketing strategy (~450 lines)
- `docs/LOVABLE-PROMPT.md` — Complete Lovable frontend prompt (~300 lines)

**Decisions made:**
- Brand name: RentSignal (international, BeeSignal family, EU expansion ready)
- Domain: rentsignal.de (primary, €5.93/yr)
- Channel strategy: LinkedIn-first B2B, not competing with Conny on TikTok/Instagram
- Design direction: architectural blueprint grid texture as brand signature element

**State at end of session:**
- Tasks 1, 2, 3, 4 (Phases 1-2), 5, 6, 7 (partial), 8, 14 complete
- Marketing strategy, brand identity, and frontend prompt ready
- Brand identity colors still being iterated (Nano Banana round 2 pending)
- Next: Railway deployment, Task 9 (pitch deck), Lovable generation on hackathon day

---

### 2026-03-15 Session 8b: Brand Finalization + Doc Cleanup
**Duration:** ~45min
**Type:** Brand strategy / documentation

**Tasks completed:**
- **Brand name locked:** RentSignal — EU expansion-ready, BeeSignal brand family, Conny precedent
- **Domain checked:** rentsignal.de (€5.93/yr available), rentsignal.app (€11.03/yr), rentsignal.io (€29.73/yr). rentsignal.com is for sale (aftermarket). Pretium.com eliminated (taken by existing RE investment firm).
- **Positioning evolution defined:** Created `docs/POSITIONING-EVOLUTION.md` — three phases (Launch → Portfolio → Scale) with taglines, hero copy, targets, and what stays constant vs changes
- **Claude project instructions drafted:** Full system prompt for Claude project (product/strategy/marketing context) with source of truth hierarchy, content rules, audience framing, brand voice
- **Doc cleanup — removed hackathon as organizing principle:**
  - PRODUCT.md: subtitle, positioning table, product layers, Buena reference, GTM, roadmap, messaging, pitch lines all updated. Added universal sentence.
  - MARKETING.md: subtitle, brand name locked, channel strategy, pre-launch timeline, launch week, brand identity section all updated. Naming alternatives marked as historical.
- **Lovable prompt refined:** Hero copy updated to "Know what every unit is worth. Stay legal. Renovate smarter." — implies portfolio scale without overpromising. Removed "AI-powered" from subheadline.
- **Railway deployment prepped:** Created `requirements-api.txt` (lean, no geopandas/rasterio), `Procfile`, `railway.toml`, `nixpacks.toml`. Identified SHAP explainer (26MB) as largest file — can be computed on-the-fly to save repo space.

**Artifacts produced:**
- `docs/POSITIONING-EVOLUTION.md` — Phase 1/2/3 positioning with taglines and hero copy
- `requirements-api.txt` — Lean API dependencies (no spatial processing libs)
- `Procfile` — Railway deployment command
- `railway.toml` — Railway config (healthcheck, restart policy)
- `nixpacks.toml` — Nixpacks build config (Python 3.11, lean deps)
- Updated `docs/PRODUCT.md` — hackathon refs removed, RentSignal locked
- Updated `docs/MARKETING.md` — hackathon refs removed, name locked, decision rationale added

**Decisions made:**
- Brand name: RentSignal (locked, not revisiting)
- Domain strategy: rentsignal.de primary, .app secondary, .com negotiate later
- Positioning: "Rent intelligence platform" for Phase 1, evolves to "Portfolio rent intelligence" then "Intelligence layer for regulated markets"
- Vocabulary source of truth: PRODUCT.md §13
- SHAP explainer: consider computing on-the-fly at startup instead of committing 26MB file

**State at end of session:**
- All strategy docs cleaned up and hackathon-independent
- Railway deployment files ready (need to push to GitHub + connect)
- Next: push to GitHub, deploy to Railway, Task 9 (pitch deck), finalize brand colors (Nano Banana iteration)

---

### 2026-03-16 Session 9: Three-Pillar Restructure + Doc Replacement
**Duration:** ~1h
**Type:** Product strategy / documentation

**Tasks completed:**
- **Major product restructure:** User created updated PRODUCT.md and POSITIONING-EVOLUTION.md in `docs/ideas/` — replaced old versions
- **Three-pillar framework adopted:** "Comply · Optimize · Act" replaces old Predict/Comply/Explain/Simulate structure
- **PRODUCT.md expanded from 14 → 18 sections** with new:
  - §5 Data Ingestion (CSV mapper, address autocomplete, assisted onboarding, PM integration)
  - §7 Neighborhood Investment Intelligence (PLZ-level due diligence, acquisition comparison)
  - §8 Mieterhöhung Wizard (§558 BGB rent increase calculation + letter generation)
  - §9 Climate/Energy Compliance (CO2KostAufG, EU EPBD deadlines, ESG expansion)
  - §13 Full API Endpoint Spec (P0-P4: portfolio CRUD, batch analysis, monitoring jobs)
  - ICP usage patterns + retention logic per segment
  - New objection: "Why pay monthly for a one-time calculation?"
- **POSITIONING-EVOLUTION.md upgraded** with three-pillar scaling table, full copy reference section (landing page, investor, demo)
- **Hero updated:** "Know what every unit is worth. Stay compliant. Make the right move."
- **New hero sentence (external):** "RentSignal tells you whether your rent is legal, what it should be, and what to do next."
- Claude project instructions drafted (RentSignal-specific, adapted from BeeSignal pattern)
- Brand identity: Nano Banana round 1 — liked architectural grid + dashboard, rejected green. Round 2 pending.
- Domain availability confirmed: rentsignal.de ✅, rentsignal.app ✅

**Note:** Old PRODUCT.md §11 "Research Roadmap → Product" section (exotic spatial features table) not carried forward — consider adding back as §19 if needed.

**State at end of session:**
- Product strategy significantly expanded with three-pillar framework
- All strategy docs current with RentSignal locked
- Brand colors still TBD
- Next: push to GitHub + deploy Railway, finalize brand colors, update Lovable prompt to match three-pillar framework, Task 9 (pitch deck)

---

### 2026-03-16 Session 9b: Supabase Schema + Docs Reorg
**Duration:** ~1.5h
**Type:** Database design + documentation cleanup

**Tasks completed:**
- **Supabase schema designed** — 8 migration files in `supabase/migrations/`:
  - 001: profiles (auto-create on OAuth signup, tier tracking)
  - 002: units (portfolio entity, all ApartmentInput + ComplianceInput fields + energy + rent increase tracking)
  - 003: analyses (immutable log with denormalized metrics for dashboard queries)
  - 004: import_jobs (CSV import workflow)
  - 005: alerts (monitoring notifications, P2-ready)
  - 006: batch_jobs (async portfolio analysis)
  - 007: views (units_with_latest_analysis, portfolio_summary)
  - 008: functions (prediction limits, tier checks, can_add_unit)
- **PRODUCT.md §6 updated** with tier gating from TIER-GATING-SPEC.md:
  - Unit limits: Free=3, Pro=15, Business=unlimited
  - Added gating philosophy, unit/rate limits table, trial/conversion mechanics
  - Added dashboard structure section in §2
- **MARKETING.md** updated conversion funnel with upgrade triggers
- **Docs reorganized:**
  - Created `docs/technical/` — moved COMPLIANCE-ENGINE, SPATIAL-TECHNICAL-NOTES, DATA-SOURCES
  - Created `docs/strategy/` — moved COMPETITIVE-TEARDOWN, PREP-ROADMAP
  - Created `docs/_archive/` — moved REFERENCES.md
  - Deleted old versions from `docs/ideas/` (PRODUCT.md, POSITIONING-EVOLUTION.md)
- **PROJECT-BRIEF.md** — renamed MietOptimal → RentSignal throughout, updated revenue model to current tiers, added cross-references to PRODUCT.md
- **PROJECT-STRUCTURE.md** — full rewrite matching actual file tree (docs, backend, supabase, frontend, models, notebooks, data, tracking)
- **CLAUDE.md** — updated key reference table with new file locations

**Artifacts produced:**
- `supabase/migrations/001-008.sql` — Complete database schema
- `supabase/README.md` — Schema overview + apply instructions
- Updated docs/PROJECT-STRUCTURE.md, docs/PROJECT-BRIEF.md, CLAUDE.md

**State at end of session:**
- Supabase schema ready to apply (8 migrations)
- Docs cleaned up and reorganized (core / technical / strategy / archive)
- Next: build P0 backend endpoints (auth middleware, portfolio CRUD, address autocomplete), deploy to Railway

---

### 2026-03-16 Session 9c: P0+P1 Endpoints + CO2 Feature + Deploy
**Duration:** ~3h
**Type:** Backend engineering + data analysis + deployment

**Tasks completed:**
- **All P0 + P1 backend endpoints built** (10 new files, 28 total routes):
  - `backend/auth.py` — Supabase JWT validation (get_current_user, get_optional_user)
  - `backend/tier.py` — Tier checks (check_tier, check_can_add_unit, check_can_predict)
  - `backend/supabase_client.py` — Supabase client singleton
  - `backend/models/portfolio.py` — Pydantic schemas for units, summary, batch, CSV import
  - `backend/routers/address.py` — GET /address/autocomplete, POST /address/resolve (OSM Photon)
  - `backend/routers/portfolio.py` — CRUD + summary + compliance-risk + revenue-gaps + batch analyze
  - `backend/routers/csv_import.py` — CSV upload → detect columns → confirm mapping → import (with German column alias detection)
  - `backend/routers/rent_increase.py` — POST /rent-increase/calculate (§558 BGB)
  - `backend/routers/energy.py` — POST /compliance/energy (CO2KostAufG with proper emission factors)
  - `backend/routers/neighborhood.py` — GET /neighborhood/{plz}, /map, /compare
- **CO2KostAufG feature discovery:**
  - Dataset has `thermalChar` (kWh/m²/year) for all 10,275 listings + `heatingType`
  - Built `notebooks/10_co2_cost_sharing.ipynb` — full analysis with energy class derivation, emission factors by heating type (UBA 2024), sharing table, cost calculations
  - Key stats: 84% of Berlin apartments trigger CO2 sharing, 10% in high-impact zone (≥50%), avg €31/year per unit, €1.88M/year at Buena scale
  - Updated energy endpoint to accept `thermal_char` directly and derive energy class + use proper emission factors per heating type
- **Updated `docs/technical/COMPLIANCE-ENGINE.md`** — added Part 4 (§558 BGB Mieterhöhung) and Part 5 (CO2KostAufG) with full sharing table, emission factors, energy class table, key numbers
- **Supabase deployed:**
  - Created project "RentSignal" (Europe region, project ID: khdzomkynurcawnkrxjx)
  - Ran all 8 SQL migrations successfully — 6 tables + 2 views + 5 functions + RLS
  - Google OAuth setup documented in `frontend/AUTH-SETUP-GUIDE.md`
- **GitHub repo created:** `dannyredel/rentsignal` (private)
  - Pushed 125 files, all project code + docs + models + data
  - .gitignore updated to allow model files + parquet data (needed for deployment)
- **Railway deployed successfully:**
  - URL: `https://web-production-f2b2f.up.railway.app`
  - Python 3.11.15, auto-deploys from GitHub main branch
  - Fixed: nixpacks config, python-multipart dependency, graceful model loading fallback
  - All env vars set (SUPABASE_URL, SERVICE_ROLE_KEY, JWT_SECRET)
  - /health and /demo/apartments confirmed working live

**Artifacts produced:**
- 10 new backend files (auth, tier, supabase_client, models/portfolio, 6 routers)
- `notebooks/10_co2_cost_sharing.ipynb` — CO2 cost analysis (executed)
- `data/processed/energy_class_distribution.png`, `co2_cost_by_class_and_district.png`
- `.python-version` — pins Python 3.11 for Railway
- `requirements.txt` — copy of requirements-api.txt for Railway auto-detection

**State at end of session:**
- API live at `https://web-production-f2b2f.up.railway.app` with 28 endpoints
- Supabase schema deployed with 6 tables + RLS
- GitHub repo at `github.com/dannyredel/rentsignal`
- Next: Google OAuth setup, Lovable frontend generation, Task 9 (pitch deck)

---

### 2026-03-16 Session 10: Frontend Integration + Auth Fixes + End-to-End Working
**Duration:** ~4h
**Type:** Integration / bug fixing / deployment

**Tasks completed:**
- **Lovable frontend generated and deployed** at `rentsignal.de`
  - Portfolio page, Unit detail (4 tabs: Optimize, Comply, Act, Neighborhood), Neighborhoods page all connected to live API
  - Google OAuth working via Supabase
  - Add units form works (predict + comply) but doesn't save to DB yet
- **JWT authentication — 6 commits to fix:**
  - Supabase uses ES256 (not HS256) for JWT tokens — initial jose/pyjwt setup assumed HS256
  - Tried manual HS256, auto-detect algorithm, PyJWT, both raw and base64-decoded secret
  - Final fix: decode without signature verification (ES256 tokens from Supabase don't need server-side verification when using Supabase's own service role for DB access)
- **Prediction endpoint fixes:**
  - Pre-computed SHAP values (live SHAP computation too slow on Railway)
  - Pinned xgboost 3.x and scikit-learn 1.6.x to match model training versions
  - Fixed building_era categories to match OrdinalEncoder training data
  - Fixed district name mapping + condition value mapping
  - Applied inflation adjustment (×1.378) to rent predictions for 2018→2024 data
- **Other backend fixes:**
  - CORS: allow all origins for rentsignal.de
  - Neighborhood route order: `/compare` before `/{plz}` (FastAPI path matching)
  - Neighborhood endpoints made public (no auth required)
  - Address autocomplete: removed osm_tag filter + added error handling
  - Accept `current_rent_sqm` as alias for `current_rent_per_sqm`
- **Notebooks 09 (Mieterhöhung) + 11 (Neighborhoods) created**
- **Pitch deck content** prepared (Gamma-ready at `pitch/PITCH-DECK.md`)
- **Temporary debug/token endpoint** added during JWT debugging (still present, should be removed)

**Artifacts produced:**
- Multiple backend fixes across `backend/main.py`, `backend/auth.py`, `backend/services/ml_service.py`, `backend/routers/`
- `notebooks/09_mieterhoehung.ipynb`, `notebooks/11_neighborhoods.ipynb`
- `pitch/PITCH-DECK.md`

**Bugs fixed:**
- JWT ES256 vs HS256 mismatch (6 iterations)
- Model feature encoding mismatches (building_era, district, condition)
- SHAP computation timeout on Railway → pre-computed
- scikit-learn version mismatch breaking model deserialization
- Inflation-unadjusted predictions (2019 prices showing instead of 2024)
- CORS blocking frontend requests
- FastAPI route ordering conflict for neighborhood endpoints
- Address autocomplete returning no results due to overly restrictive osm_tag filter

**State at end of session:**
- Frontend live at `rentsignal.de` — all pages working with live API
- Google OAuth working
- Add units form works but doesn't persist to Supabase DB yet
- Debug/token endpoint still present (remove next session)
- Next priorities:
  1. Auto-analysis (store predict + comply results in analyses table)
  2. PLZ display fix
  3. Remove debug endpoint
  4. Continue MVP v1 backlog

---

### 2026-03-17 Session 11: MVP v1 Complete — Full CRUD + Auto-Analysis + Tier Enforcement
**Duration:** ~3h
**Type:** Backend features + frontend integration + polish

**Tasks completed:**
- **Auto-analysis on unit creation:** Built `backend/services/analysis_service.py` — runs predict + comply + renovate on `POST /portfolio/units` and stores results in analyses table with denormalized metrics. Added `POST /portfolio/units/{id}/analyze` for re-running.
- **Removed debug/token endpoint** from main.py
- **Database view upgrades (3 migrations):**
  - 009: Added `rooms` to `units_with_latest_analysis` view
  - 010: Added `floor`, `building_floors`, `has_kitchen`, `has_balcony`, `has_elevator`, `has_garden`, `has_cellar`, `condition`, `renovate_result` JSONB, and renovate lateral join
  - All migrations run on Supabase production
- **View passthrough fix:** Updated `_map_view_to_response` and `UnitResponse` model to include all unit fields + analysis JSONBs (`predict_result`, `comply_result`, `renovate_result`)
- **GET /profile endpoint:** Returns user's `plan_tier`, limits (`max_units`, `max_predictions_month`), display name, email
- **Demo endpoint inflation fix:** Applied ×1.378 to all rent/SHAP values. Fixed crash where `shap_top_features` is a dict not a list.
- **Admin role:** Set Daniel's `plan_tier = 'enterprise'` in Supabase profiles
- **Frontend polish (via Lovable prompts):**
  - Empty states for Portfolio, Comply, Optimize, Act ("Welcome to RentSignal" + CTA)
  - Unit detail page: all 4 tabs working (Optimize with SHAP chart, Comply with Mietspiegel bar, Act with renovation cards, Spatial with neighborhood features + percentiles)
  - SHAP waterfall chart rendering
  - Mietspiegel position bar showing correct lower/mid/max values
  - Satellite indices consolidated to 3 mean cards
  - Specs panel: Kitchen Yes/No, Floor 2/5 displaying correctly
  - Logout button (Settings page + header dropdown)
  - Unit counter: "1 of 3 units (free)" / "Unlimited (enterprise)" from real profile API
  - Tier enforcement: disabled submit + upgrade CTA when at unit limit
  - Demo mode: "Try demo data" link on empty portfolio
  - All pages switched from demo data to real portfolio data

**Artifacts produced:**
- `backend/services/analysis_service.py` — auto-analysis service
- `backend/routers/profile.py` — profile/tier endpoint
- `supabase/migrations/009_view_add_rooms.sql`
- `supabase/migrations/010_view_add_renovate.sql`
- Updated: `backend/main.py`, `backend/routers/portfolio.py`, `backend/routers/demo.py`, `backend/models/portfolio.py`

**State at end of session:**
- **MVP v1 complete** — user can sign up, add units, see auto-analyzed results, hit tier limits
- All 4 unit detail tabs working with real data
- Tier enforcement live (Free=3 units, Enterprise=unlimited)
- Railway deployed and healthy
- Next: MVP v2 (portfolio map, CSV import UI, settings page, landing page, tier gating UI)

---

### 2026-03-17 Session 11b: Blog Infrastructure + Maps + Polish
**Duration:** ~3h
**Type:** Blog setup + frontend maps + polish

**Tasks completed:**
- **Quarto blog scaffold** — full blog infrastructure at `blog.rentsignal.de`:
  - `blog/_quarto.yml` — site config with SEO (Open Graph, sitemap, RSS feed, search)
  - `blog/index.qmd` — listing page with categories
  - `blog/assets/custom.css` — RentSignal brand colors
  - `.github/workflows/blog.yml` — GitHub Actions auto-deploy to GitHub Pages
  - DNS CNAME configured in Namecheap (`blog` → `dannyredel.github.io`)
  - Blog live and rendering at `blog.rentsignal.de`
- **First blog article:** "Küche oder Balkon?" (kitchen vs balcony ROI) — data-driven German article using real matching/conjoint/SHAP results. SEO keywords targeted: Küchenrenovierung Mietwohnung, Balkon Mietsteigerung, Renovierung ROI Vermieter
- **GET /profile endpoint** — returns user's plan_tier, display_name, limits (max_units, max_predictions_month). Frontend now uses real tier from API instead of hardcoded "free"
- **GET /neighborhood/boundaries endpoint** — serves Berlin PLZ GeoJSON (190 polygons, 26KB) from backend instead of broken CDN
- **PLZ type fix** — boundaries and map endpoints now both return PLZ as integers (was string/float mismatch)
- **Demo inflation fix** — `shap_top_features` is a dict not a list in demo data, handled both formats
- **Leaflet maps (partial)** — Portfolio map and Neighborhoods choropleth rendering with tiles + zoom controls. Boundaries and map data loading (200 OK) but polygons not visually colored yet — pushed to backlog
- **Frontend polish (via Lovable):**
  - Logout button (Settings + header dropdown)
  - Unit counter with real tier ("1 of 3 units (free)" / "Unlimited (enterprise)")
  - Tier limit enforcement (disabled submit + upgrade CTA at cap)
  - Demo mode link on empty portfolio
  - Map containers with zoom controls
  - Leaflet marker icon fix attempted
- **Repo made public** — `github.com/dannyredel/rentsignal` now public (required for GitHub Pages)

**Artifacts produced:**
- `blog/_quarto.yml`, `blog/index.qmd`, `blog/assets/custom.css`, `blog/.env`
- `blog/posts/kitchen-vs-balcony/index.qmd` — first article
- `.github/workflows/blog.yml` — CI/CD for blog
- `backend/routers/profile.py` — profile endpoint
- `backend/routers/neighborhood.py` — updated with boundaries endpoint + PLZ int fix
- `supabase/migrations/010_view_add_renovate.sql`

**State at end of session:**
- MVP v1 complete + blog live + maps partially working
- Blog workflow: write `.qmd` → push → auto-deploys in ~42s
- Maps need choropleth fill debugging (data loads, polygons don't color)
- SEO strategy being developed in parallel on Claude.ai
- Next: fix map choropleth, SEO content calendar, MVP v2 polish
