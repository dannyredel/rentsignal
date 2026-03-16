# Backlog
## RentSignal — Task Queue

*Organized by product roadmap priority (P0→P4). See `docs/PRODUCT.md` §12-13 for full roadmap and API spec.*

---

## ✅ Completed (Foundation)

These tasks built the core ML + compliance + causal engine that everything else depends on.

- [x] **Source Berlin rental listing data** ✅ 2026-03-15
  - 10,275 clean Berlin listings → `data/processed/listings_clean.parquet`
- [x] **Train XGBoost rent prediction model** ✅ 2026-03-15
  - R²=0.749, RMSE=2.59 €/m², 37 features (19 structural + 9 OSM + 9 satellite)
- [x] **Spatial feature pipeline (OSM + Sentinel-2)** ✅ 2026-03-15
  - 18 spatial features for 190 Berlin PLZs
- [x] **Mietpreisbremse compliance engine** ✅ 2026-03-15
  - §556d + §559 + §559e BGB, Berlin Mietspiegel 2024, 3 exemptions
- [x] **Matching estimator (observational CATE)** ✅ 2026-03-15
  - PSM: Kitchen +2.91, Balcony -0.72 €/m²
- [x] **BeeSignal conjoint calibration** ✅ 2026-03-15
  - Kitchen WTP +€4.13/m², 3% convergence with CATE
- [x] **Demo apartments + narratives** ✅ 2026-03-15
  - 5 apartments, charts, JSON, speaker notes
- [x] **FastAPI backend v1 (unit-level endpoints)** ✅ 2026-03-15
  - 8 endpoints: health, demo×2, predict, comply, renovate, spatial×2
- [x] **Product strategy (PRODUCT.md)** ✅ 2026-03-16
  - 18 sections, Comply · Optimize · Act framework
- [x] **Marketing strategy (MARKETING.md)** ✅ 2026-03-15
  - SEO, channels, Conny positioning, brand name locked: RentSignal
- [x] **Positioning evolution** ✅ 2026-03-16
  - 3-phase positioning with copy reference

---

## 🔴 P0 — Nothing Else Works Without These

### Infrastructure

- [ ] **Deploy backend to Railway** (~1h)
  - Push to GitHub, connect Railway, set env vars, test live endpoints
  - Deployment files ready: `Procfile`, `railway.toml`, `nixpacks.toml`, `requirements-api.txt`
  - Consider computing SHAP explainer on-the-fly to avoid 26MB file in repo

- [ ] **Supabase schema: users, units, analyses, import_jobs** (~2h)
  - `units` table: user_id, address, plz, living_space, building_year, features JSON, created_at
  - `analyses` table: unit_id, type (predict/comply/renovate), result JSON, analyzed_at
  - `import_jobs` table: user_id, status, row_count, error_log, created_at
  - Row-level security policies per user
  - Dependencies: none

### Portfolio CRUD

- [ ] **Portfolio unit endpoints** (~3h)
  - `POST /portfolio/units` — create unit
  - `GET /portfolio/units` — list all for authenticated user
  - `GET /portfolio/units/{unit_id}` — get with latest cached analysis
  - `PUT /portfolio/units/{unit_id}` — update
  - `DELETE /portfolio/units/{unit_id}` — remove
  - Dependencies: Supabase schema

- [ ] **CSV import pipeline** (~3h)
  - `POST /portfolio/import/csv` — upload CSV, return detected columns
  - `POST /portfolio/import/confirm` — submit column mapping, start async job
  - `GET /portfolio/import/{job_id}` — poll job status
  - Dependencies: Portfolio CRUD

- [ ] **Batch analysis job** (~2h)
  - `POST /portfolio/analyze` — trigger predict+comply on all/selected units
  - `GET /portfolio/analyze/{job_id}` — poll status
  - Reuses existing predict + comply logic, runs async
  - Dependencies: Portfolio CRUD, existing predict/comply endpoints

### Address Resolution

- [ ] **Address autocomplete endpoint** (~2h)
  - `GET /address/autocomplete?q=` — wraps OSM Photon API (free, self-hostable)
  - `POST /address/resolve` — full address → PLZ, district, lat/lon, inferred building year
  - Dependencies: none

---

## 🟡 P1 — Core Value (Delivers the Three-Pillar UVP)

### Comply Pillar

- [ ] **Mieterhöhung calculator** (~3h)
  - `POST /rent-increase/calculate` — §558 BGB: can I increase? by how much? earliest legal date?
  - Rules: Mietspiegel mid cap, 15-20% Kappungsgrenze over 3 years, formal requirements
  - Dependencies: existing compliance service (reuse Mietspiegel lookup)

- [ ] **Mieterhöhung letter PDF** (~2h)
  - `POST /rent-increase/letter` — same input + tenant details → formal Mieterhöhungsverlangen PDF
  - Must meet §558a BGB formal requirements
  - **Needs one-time legal review before launch (budget €200-500)**
  - Dependencies: Mieterhöhung calculator

- [ ] **CO2KostAufG energy compliance** (~2h)
  - `POST /compliance/energy` — building energy class + specs → landlord CO2 share % + annual € exposure
  - CO2 price: €55/tonne (2025), €65/tonne (2026)
  - Dependencies: none (new rules engine)

### Optimize Pillar

- [ ] **Portfolio summary endpoint** (~1h)
  - `GET /portfolio/summary` — total units, avg rent gap, total compliance exposure €/year
  - Dependencies: batch analysis

- [ ] **Compliance risk ranking** (~1h)
  - `GET /portfolio/compliance-risk` — all units with status + €/year exposure, sorted by risk
  - Dependencies: batch analysis

- [ ] **Revenue gap ranking** (~1h)
  - `GET /portfolio/revenue-gaps` — units sorted by rent gap (underpriced first)
  - Dependencies: batch analysis

### Act Pillar

- [ ] **Neighborhood Intelligence endpoints** (~3h)
  - `GET /neighborhood/{plz}` — extends existing `/spatial/{plz}`: add rent range, SHAP by PLZ, renovation ROI by area, compliance landscape
  - `GET /neighborhood/map` — all Berlin PLZs with summary metrics for map rendering
  - `GET /neighborhood/compare?plz=12049,10119` — side-by-side PLZ comparison
  - Dependencies: existing spatial data + model

---

## 🟢 P2 — Retention (Drives Subscription Stickiness)

- [ ] **Portfolio Monitor — nightly watchdog** (~4h)
  - Background job: re-runs predict+comply on all monitored units
  - Writes alerts when rent gap or compliance status changes beyond threshold
  - `POST /monitor/subscribe` — subscribe units
  - `GET /monitor/alerts` — get pending alerts
  - `POST /monitor/alerts/{id}/dismiss` — mark seen
  - Dependencies: batch analysis, Supabase alerts table

- [ ] **Weekly digest email** (~2h)
  - Background job: Monday 8:00 AM CET
  - `GET /monitor/digest` — preview digest content
  - Dependencies: monitor alerts, email service (Resend / SendGrid)

- [ ] **Monthly portfolio PDF report** (~3h)
  - `GET /portfolio/report/monthly` — generate client-ready PDF
  - Compliance summary, revenue gaps, renovation opportunities, market changes
  - Dependencies: portfolio summary endpoints

- [ ] **Intelligent CSV mapper** (~3h)
  - Upgrade CSV import: auto-detect column headers from any format (objego, DOMUS, custom spreadsheets)
  - Visual mapping UI: "Your column 'Wohnfläche' → Living Space (m²)"
  - Dependencies: CSV import pipeline (P0)

- [ ] **City expansion: Hamburg, Munich** (~4h per city)
  - New Mietspiegel lookup tables (JSON)
  - Retrain model or transfer-learn with new city data
  - Spatial features: run OSM + satellite pipelines for new city
  - Dependencies: parameterized compliance engine

---

## ⚪ P3 — Differentiation

- [ ] **Acquisition analysis endpoints** (~3h)
  - `POST /acquisition/analyze` — full unit assessment (predict + comply + renovate + neighborhood)
  - `POST /acquisition/compare` — list of addresses + budget → ranked by yield, budget-optimal subset
  - Dependencies: all P1 endpoints

- [ ] **Listing URL auto-fill** (~2h)
  - `POST /address/from-url` — ImmoScout24 listing URL → pre-populated ApartmentInput
  - Implement defensively with fallback to manual entry
  - Dependencies: none

- [ ] **Public API with docs + pricing page** (~2h)
  - API key management, rate limiting, usage tracking
  - Swagger/Redoc public docs
  - Dependencies: all P1 endpoints stable

---

## 🔵 P4 — Phase 2+ (Deferred — requires new data or significant compute)

- [ ] **Neighborhood trend analysis** — requires historical listing time-series data
- [ ] **Portfolio renovation budget allocation** — integer programming, requires client data at scale
- [ ] **EU EPBD deadline flags + ESG scoring** — requires EPC data pipeline
- [ ] **objego PM software integration** — requires partnership/API access
- [ ] **Cross-unit pricing (IO/BLP demand models)** — crown jewel, requires client portfolio data
- [ ] **Upgrade spatial features to per-listing lat/lon** — requires listing data with coordinates

---

## 🎯 Hackathon-Specific (April 25-26, 2026)

*These are hackathon-day tasks, not product backlog. Separate track.*

- [ ] Gemini API integration (spatial extraction + NL→structured)
- [ ] Gradium API integration (German STT voice input)
- [ ] Entire CLI setup (build process tracking)
- [ ] Gemini visual extraction for 5 demo neighborhoods
- [ ] Pitch deck content (Gamma-ready slides + speaker notes)
- [ ] Record backup demo video
- [ ] "Scale with Buena" Q&A slide

---

## 📊 Scripts & Analysis Needed

*New notebooks/scripts required by the expanded product scope.*

- [ ] **`notebooks/09_mieterhoehung_rules.ipynb`** — Validate §558 BGB rules engine against edge cases (Kappungsgrenze, Staffelmiete exclusion, timing calculations)
- [ ] **`notebooks/10_co2_cost_sharing.ipynb`** — CO2KostAufG calculation validation (energy class → landlord share %, CO2 price schedule, annual cost)
- [ ] **`notebooks/11_neighborhood_intelligence.ipynb`** — PLZ-level aggregations: rent range, SHAP by PLZ, renovation ROI variation, compliance landscape
- [ ] **`backend/services/rent_increase_service.py`** — §558 BGB rules engine (Mieterhöhung wizard)
- [ ] **`backend/services/energy_compliance_service.py`** — CO2KostAufG + GEG compliance
- [ ] **`backend/services/neighborhood_service.py`** — PLZ-level intelligence aggregation
- [ ] **`backend/services/portfolio_service.py`** — Portfolio CRUD, batch analysis, CSV import
- [ ] **`backend/services/monitor_service.py`** — Nightly watchdog, alert generation, digest composition
- [ ] **`backend/routers/portfolio.py`** — All /portfolio/* endpoints
- [ ] **`backend/routers/neighborhood.py`** — All /neighborhood/* endpoints
- [ ] **`backend/routers/rent_increase.py`** — Mieterhöhung calculator + letter
- [ ] **`backend/routers/monitor.py`** — Monitoring + alerts
- [ ] **`backend/routers/acquisition.py`** — Acquisition analysis (P3)
- [ ] **`backend/routers/address.py`** — Autocomplete + resolve
