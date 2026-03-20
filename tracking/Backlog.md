# Backlog
## RentSignal — Task Queue

*Restructured around MVP milestones. See `docs/PRODUCT.md` for full product spec.*

---

## ✅ Completed (Foundation + Infrastructure)

- [x] **Source Berlin rental listing data** ✅ 2026-03-15
  - 10,275 clean Berlin listings → `data/processed/listings_clean.parquet`
- [x] **Train XGBoost rent prediction model** ✅ 2026-03-15
  - R²=0.749, RMSE=2.59 €/m², 37 features (19 structural + 9 OSM + 9 satellite)
- [x] **Spatial feature pipeline (OSM + Sentinel-2)** ✅ 2026-03-15
- [x] **Mietpreisbremse compliance engine** ✅ 2026-03-15
- [x] **Matching estimator (observational CATE)** ✅ 2026-03-15
- [x] **BeeSignal conjoint calibration** ✅ 2026-03-15
- [x] **Demo apartments + narratives** ✅ 2026-03-15
- [x] **Product strategy, Marketing, Positioning** ✅ 2026-03-16
- [x] **FastAPI backend — 28 endpoints** ✅ 2026-03-16
  - predict, comply, renovate, spatial, demo, portfolio CRUD, batch analysis, CSV import, address autocomplete, rent-increase, energy, neighborhood
- [x] **Supabase schema — 8 migrations deployed** ✅ 2026-03-16
  - profiles, units, analyses, import_jobs, alerts, batch_jobs + views + functions
- [x] **Railway deployment** ✅ 2026-03-16
  - `https://web-production-f2b2f.up.railway.app` · Python 3.11 · Auto-deploy from GitHub
- [x] **Google OAuth + Supabase auth** ✅ 2026-03-16
- [x] **Lovable frontend — dashboard + landing page** ✅ 2026-03-16
  - Portfolio, Unit detail (4 tabs), Comply, Optimize, Act, Neighborhoods all working with live API
  - Domain: `rentsignal.de`
- [x] **Notebooks 09 (Mieterhöhung), 10 (CO2), 11 (Neighborhoods)** ✅ 2026-03-16
- [x] **Pitch deck content (Gamma-ready)** ✅ 2026-03-16
- [x] **Docs reorg** ✅ 2026-03-16
  - core / technical / strategy / _archive / blog

---

## 🔴 MVP v1 — "A real user can sign up, add units, and see results"

*Minimum to launch and get first users. Everything below must work end-to-end.*

### Data & ML Pipeline (see `docs/technical/DATA-ARCHITECTURE.md`)

- [x] **Scrape current listing data (Apify ImmoScout24)** ✅ 2026-03-18
  - 8,335 Berlin listings scraped (Mar 18 batch); 568 test batch (Mar 17, superseded)
  - Raw data in `data/raw/scraping/`

- [x] **Design data architecture & ML training workflow** ✅ 2026-03-19
  - Relational schema: `units` (master) + `listings` (panel) + `spatial_plz` + `spatial_unit`
  - Documented in `docs/technical/DATA-ARCHITECTURE.md`

- [x] **Phase 1: Ingest Apify 2026 data into unified schema** ✅ 2026-03-19
  - 8,335 → 8,256 clean units after quality filters + dedup
  - Pipeline: `data/pipelines/ingestion.py`, Notebook: `13_data_ingestion_pipeline.ipynb`
  - Output: `data/processed/units.parquet` + `data/processed/listings.parquet`
  - Key finding: implied inflation factor is 1.145× (not 1.378×)

- [x] **Phase 2: Geocode missing coordinates** ✅ 2026-03-19
  - 5,081 from Apify (61.5%) + 770 geocoded (title mining + Kaggle cross-match) + 2,399 centroid fallback
  - Final: 99.9% coverage (8,250/8,256), only 6 unresolved
  - Added `cross_match_addresses()` to pipeline for future scrapes
  - Notebook: `14_geocoding_and_spatial_features.ipynb`

- [x] **Phase 3: Unit-level spatial features** ✅ 2026-03-19
  - 24 features: 15 OSM (dist_cbd, dist_ubahn, count_cafe, count_building, etc.) + 9 satellite (NDVI/NDWI/NDBI × 100m/250m/500m buffers)
  - All computed from actual unit coordinates, not PLZ centroids
  - count_food_1000m: unit median=111 vs PLZ median=20 (5.5× better signal)
  - OSM POIs cached in `data/processed/osm_pois/` for reuse
  - Notebook: `15_unit_spatial_features.ipynb`
  - Output: `data/processed/spatial_unit.parquet` (8,250 × 24 features)

- [x] **Phase 4: Retrain XGBoost v4 on 2026 data** ✅ 2026-03-19
  - R²=0.7083, RMSE=4.21 €/m², MAE=3.07 €/m² (on noisier 2026 data)
  - 43 features (19 structural + 24 unit-level spatial)
  - No inflation hack (trained on current data)
  - Spatial contribution: ΔR²=+0.0193 (+2.8%)
  - Top SHAP: condition (2.56), livingSpace (1.26), hasKitchen (1.05), interiorQual (0.79), count_food_1000m (0.53)
  - Early stopping at 193 trees, L1/L2 regularization added
  - Artifacts: xgboost_rent_v4.joblib, shap_explainer_v4.joblib, feature_encoder_v4.joblib
  - Notebook: `17_model_v4_training.ipynb`
  - **Note:** R² appears lower than v3 (0.71 vs 0.75) but data has higher variance (std 7.79 vs ~5.1). Relative error reduction is comparable (~46% vs ~51%).
  - **TODO:** Deploy v4 to Railway backend, update ml_service.py to use new feature set

### R² Improvement Plan (v4.0 → v4.1+, target R² ≈ 0.75-0.78)

- [x] **Steps 1-4: Missing data + feature engineering + NLP + tuning** ✅ 2026-03-19
  - thermalChar 79%→0.2% missing (conditional medians by heatingType)
  - yearConstructed +574 from title keywords, building_era updated
  - heatingType collapsed 49→8 groups, sizeCategory added
  - 9 NLP title features (is_tauschwohnung SHAP #1, picturecount SHAP #6)
  - RandomizedSearchCV 30 iterations, best: max_depth=6, lr=0.03
  - Model v4.1: R²=0.736 (+0.028 over v4.0)
  - Notebook: `18_model_v4_improvements.ipynb`

- [x] **Step 4.5: Image-based features via Gemini** ✅ 2026-03-20
  - 54,866 photos downloaded locally (9.4 GB), 6,997/7,291 listings processed (96%)
  - 21 features per listing: interior quality, kitchen/bathroom quality, brightness, renovation level, floor type, ceiling height, style, staging, view, building condition/style/floors, etc.
  - renovation_level (r=+0.50) and interior_quality (r=+0.46) are strongest image correlations
  - Model v4.2: R²=0.761, RMSE=3.81 — **surpassed v3 (0.749)** on noisier 2026 data
  - 5 image features in SHAP top 20, renovation_level is SHAP #4 overall
  - Notebooks: 19a (test), 19 (batch), 20 (training)

- [~] **Step 5: External data sources** (~2h)
  - Berlin Umweltatlas noise map (WMS, proven rent predictor)
  - LOR block statistics (income/demographics from daten.berlin.de)
  - VIIRS nighttime lights (one raster download)

### Post-Model Tasks

### Deployment & Product (priority order)

- [~] **Step 1: Deploy v4.2 to Railway (form mode)** (~2h)
  - Update `ml_service.py` for 75-feature set
  - Spatial features computed from address (KDTree + raster), not PLZ lookup
  - Gemini/NLP features filled with defaults when not available
  - Update SHAP feature labels for new features
  - Update model artifacts on Railway

- [ ] **Step 2: Photo upload in prediction form** (~3h)
  - Optional photo section: "Add photos for better accuracy (+5-10%)"
  - Backend sends photos to Gemini → adds 21 image features
  - Show confidence indicator (with/without photos)

- [ ] **Step 3: Paste listing URL mode** (~4h)
  - New input mode: paste ImmoScout24 URL
  - Backend scrapes listing → pre-fills form → enriches with NLP + photos
  - User reviews/edits before submitting → full 75-feature prediction
  - "Zero-form" user experience — killer feature

- [ ] **Step 4: Confidence indicator** (~1h)
  - Show which enrichment steps completed (geocoded ✓, photos analyzed ✓, etc.)
  - Nudge: "Paste the ImmoScout URL for even more accurate results"
  - Gamifies data quality — users want to provide more

- [ ] **Re-run matching estimator on 2026 data** (~2h)
  - Update renovation CATE estimates (kitchen/balcony/lift/garden effects)
  - Use v4.2 features for better propensity score matching

- [ ] **Portfolio optimization demo** (~4h)
  - Substitution matrix heatmap, cross-unit pricing with Mietpreisbremse constraints
  - "One unit subsidizing its neighbor" demo moment
  - See `docs/strategy/portfolio-optimization-pitch.md`

- [ ] **Blog: "We analyzed 55,000 apartment photos with AI"** (~2h)
  - Gemini image pipeline methodology + key findings
  - SEO: "AI apartment photo analysis Berlin"

### Frontend → Backend Integration

- [x] **Onboarding flow** ✅ 2026-03-17
  - Empty state on Portfolio serves as onboarding: "Welcome to RentSignal" + "Add your first apartment" CTA
  - "Try demo data" link also available

- [x] **Real CRUD — Add units saves to Supabase** ✅ 2026-03-17
  - Add units form submits to `POST /portfolio/units` with auth token
  - Redirects to unit detail page after save
  - Toast notification shows prediction + compliance status

- [x] **Auto-analysis on unit creation** ✅ 2026-03-17
  - Backend auto-runs predict + comply + renovate on `POST /portfolio/units`
  - Results stored in `analyses` table with denormalized metrics
  - `POST /portfolio/units/{id}/analyze` endpoint for re-running

- [x] **Portfolio shows real user data** ✅ 2026-03-17
  - All pages (Portfolio, Comply, Optimize, Act) use `GET /portfolio/units`
  - Stats, table, gap %, compliance status all from real data

- [x] **Empty states for all pages** ✅ 2026-03-17
  - Shared EmptyState component across Portfolio, Comply, Optimize, Act

### Admin & Demo

- [x] **Admin role for Daniel** ✅ 2026-03-17
  - Set `plan_tier = 'enterprise'` in Supabase profiles table

- [x] **Demo mode toggle** ✅ 2026-03-17
  - "Try demo data" link on empty Portfolio, DEMO banner, read-only mode

### Bug Fixes

- [x] **Address autocomplete fix** ✅ 2026-03-16 (pushed, deploying)
  - Removed osm_tag filter, added error handling
- [x] **Inflation adjustment on demo endpoint** ✅ 2026-03-17
  - Applied ×1.378 to all rent/SHAP values in demo router
- [x] **Optimize page Gap % display** ✅ 2026-03-17
  - Fixed by switching to `rent_gap_pct` from analyses table
- [x] **Debug endpoint removed** ✅ 2026-03-17
  - Removed `/debug/token` from main.py

### Basic Tier Enforcement

- [x] **Unit counter in Add units** ✅ 2026-03-17
  - Shows "1 of 3 units (free)" / "Unlimited (enterprise)" from real /profile API
  - Disabled submit + upgrade CTA when at limit
- [ ] **Prediction counter** (~30min)
  - Show "2 of 3 predictions remaining" for Free tier

---

## 🟡 MVP v2 — "Polish + Conversion"

*Makes users want to stay and upgrade.*

### Tier Gating UI

- [ ] **Full tier gating per TIER-GATING-SPEC.md** (~4h)
  - Lock icons + "Pro" badge on Act and Neighborhoods for Free users
  - Blurred feature breakdown below top 3 features
  - Locked page with preview for Act (show "don't build the balcony" chart)
  - Upgrade prompt cards with contextual value messaging
  - Pro trial (14 days, no credit card)
  - Downgrade handling (units archived, not deleted)

### UI Polish

- [~] **Portfolio map (Leaflet)** (~1h remaining)
  - Map tiles + zoom rendering, boundaries + data loading (200 OK)
  - **Bug:** choropleth polygons not visually colored, markers not appearing
  - Likely frontend rendering issue (data joins work server-side)
  - Debug: inspect SVG/Canvas layer in browser dev tools
- [ ] **CSV import UI** (~2h)
  - Drag-and-drop upload zone
  - Column mapping interface (German column auto-detection)
- [ ] **Settings page** (~1h)
  - Profile info (name, email, company)
  - Current plan tier + upgrade CTA
  - Logout button
- [ ] **Landing page refinement** (~1h)
  - Match final brand colors (Nano Banana round 2)
  - Responsive mobile optimization

### New Features

- [ ] **Mieterhöhung letter PDF** (~2h)
  - `POST /rent-increase/letter` → formal §558a BGB letter
  - Needs one-time legal review (budget €200-500)
- [ ] **CO2 compliance in unit detail Comply tab** (~1h)
  - Show CO2KostAufG exposure on the Comply tab when energy data available

---

## 🟢 P1 — Growth & Retention

### SEO & Promotion Launch

- [x] **Blog infrastructure** ✅ 2026-03-17
  - Quarto blog at `blog.rentsignal.de`, GitHub Pages + GitHub Actions auto-deploy
  - First article: "Küche oder Balkon?" published
- [x] **SEO strategy docs** ✅ 2026-03-17
  - `docs/strategy/rentsignal-seo-strategy.md` — keywords, 12-week content calendar, link building
  - `docs/strategy/rentsignal-seo-tracking-setup.md` — GA4, GSC, UTM, schema markup, GDPR

#### SEO Technical Setup
- [x] **Google Analytics 4** ✅ 2026-03-18
  - Property: RentSignal, Measurement ID: G-85X4K34WMV
  - Blog: Quarto cookie-consent + google-analytics in _quarto.yml
  - Main site: Lovable added react-ga4 with GDPR consent banner
- [x] **Google Search Console** ✅ 2026-03-18
  - Domain property `rentsignal.de` verified via DNS TXT
  - Blog sitemap submitted (4 pages discovered)
  - Indexing requested for landing page + 3 blog articles
- [x] **robots.txt** ✅ 2026-03-17 (blog)
- [x] **Request indexing** ✅ 2026-03-18 (5 URLs submitted)

#### SEO Content — 12-Week Calendar
- [x] **Wk 0:** "Küche oder Balkon?" (data insight) ✅ 2026-03-17
- [x] **Wk 1:** "Mietpreisbremse Rechner 2026" (DE) + "Berlin Rent Brake Calculator" (EN) ✅ 2026-03-18
- [ ] **Wk 2:** "Mietspiegel Berlin 2024 erklärt" (DE) + "Lohnt sich Küchenrenovierung?" (DE, expanded)
- [ ] **Wk 3:** "Berlin Mietspiegel Explained" (EN) + "Mietpreisbremse Ausnahmen" (DE)
- [ ] **Wk 4:** "Mieterhöhung berechnen 2026" (DE) + "§559 Modernisierung" (DE)
- [ ] **Wk 5:** "Warum der Balkon sich nicht lohnt" (DE, viral) + "Rent Increase Rules" (EN)
- [ ] **Wk 6:** "How We Predict Rents: 37 Features" (EN, technical) + "CO2 Kostenaufteilung" (DE)
- [ ] **Wk 7-12:** See `docs/strategy/rentsignal-seo-strategy.md` §2

#### SEO Polish
- [ ] **Article hero images (og:image)** (~2h)
  - Generate branded OG images for each article (Quarto `image:` frontmatter)
  - Needed for social sharing previews (LinkedIn, Twitter)
- [ ] **FAQ schema (JSON-LD)** per compliance article (~30min each)
  - Enables Google rich snippets (FAQ dropdowns in search results)
  - Add to Mietpreisbremse Rechner + Berlin Rent Brake Calculator first
- [ ] **Hreflang tags** for DE/EN article pairs (~30min)

#### Promotion
- [ ] **LinkedIn company page + first 5 posts** (~2h)
- [ ] **Product Hunt launch** (~1h)
- [ ] **Landlord forum posts** (vermieter-forum.com) (~1h)
- [ ] **Newsletter setup (Substack)** (~1h)

### Retention Features

- [ ] **Portfolio monitoring — nightly watchdog** (~4h)
  - Background job: re-run predict+comply on all monitored units
  - Alert system (compliance_change, rent_gap_change, mieterhoehung_eligible)
- [ ] **Weekly digest email** (~2h)
  - Monday 8:00 AM CET, Resend/SendGrid
- [ ] **Monthly portfolio PDF report** (~3h)
  - Client-ready, brandable PDF

### Expansion

- [ ] **City expansion: Hamburg** (~4h)
  - New Mietspiegel lookup table
  - Retrain/transfer model
  - Spatial pipeline for Hamburg PLZs
- [ ] **City expansion: Munich** (~4h)
  - Same as Hamburg

### Billing

- [ ] **Stripe integration** (~4h)
  - Pro (€29/month) and Business (€99/month) plans
  - Webhook → update plan_tier in Supabase profiles
  - 14-day trial flow

---

## ⚪ P2+ — Differentiation & Scale

- [ ] Acquisition analysis endpoints (compare properties by yield)
- [ ] Listing URL auto-fill (ImmoScout24 → pre-populate form)
- [ ] Public API with docs + API key management
- [ ] Intelligent CSV mapper (auto-detect any spreadsheet format)
- [ ] Neighborhood trend analysis (requires historical time-series data)
- [ ] Portfolio renovation budget allocation (integer programming)
- [ ] EU EPBD deadline flags + ESG scoring
- [ ] objego PM software integration
- [ ] Cross-unit pricing (IO/BLP demand models)
- [x] Per-listing lat/lon spatial features — **promoted to MVP v1 Phase 2-3** ✅
- [ ] European expansion (Austria, Netherlands, France, Sweden)

---

## 🎯 Hackathon-Specific (April 25-26, 2026)

*Separate track — these enhance the demo, not the product.*

- [ ] Gemini API integration (spatial extraction + NL→structured)
- [ ] Gradium API integration (German STT voice input)
- [ ] Entire CLI setup (build process tracking)
- [ ] Pitch deck in Gamma (content ready at `pitch/PITCH-DECK.md`)
- [ ] Record backup demo video
