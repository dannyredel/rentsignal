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

### Data

- [ ] **Scrape current listing data (Apify ImmoScout24)** (~3h)
  - Replace 2018-2019 Kaggle data with current Berlin listings
  - Retrain XGBoost model on fresh data (removes inflation adjustment hack)
  - Re-run spatial pipeline for new PLZs if needed
  - See `docs/technical/DATA-SOURCES.md` for Apify actor URLs

- [ ] **Design ML training workflow** (~2h)
  - Define train/test/validation split strategy
  - Prevent data contamination (never predict on training data)
  - Define retraining cadence (quarterly? on new data arrival?)
  - Document data lineage: which data → which model version → which predictions
  - Version control for model artifacts (model_config.json tracks this)

### Frontend → Backend Integration

- [ ] **Onboarding flow** (~2h)
  - First login → redirect to Add units page (not empty Portfolio)
  - "Welcome to RentSignal" state with "Add your first apartment" CTA
  - Option: "Try with demo data" button loads 5 demo apartments into view (not saved to DB)

- [ ] **Real CRUD — Add units saves to Supabase** (~2h)
  - Add units form submits to `POST /portfolio/units` (backend already built)
  - Lovable sends auth token with request
  - Form shows success/error state
  - After save, redirect to unit detail page

- [ ] **Auto-analysis on unit creation** (~2h)
  - After `POST /portfolio/units`, auto-call `POST /predict` + `POST /compliance` + `POST /renovate`
  - Store results in `analyses` table via backend
  - Unit detail page shows live results immediately

- [ ] **Portfolio shows real user data** (~1h)
  - Portfolio page calls `GET /portfolio/units` (not `/demo/apartments`)
  - Stats, table, revenue gap chart all use real data
  - If 0 units → show empty state with CTA

- [ ] **Empty states for all pages** (~1h)
  - Portfolio: "No units yet — add your first apartment"
  - Comply: "Add units to see compliance risk"
  - Optimize: "Add units to see revenue gaps"

### Admin & Demo

- [ ] **Admin role for Daniel** (~15min)
  - Set `plan_tier = 'enterprise'` in Supabase profiles table for your user_id
  - Full access to all features, no limits

- [ ] **Demo mode toggle** (~1h)
  - "Try demo data" button on Portfolio loads 5 demo apartments in read-only view
  - Separate from real portfolio — doesn't pollute user data
  - Demo badge visible when in demo mode

### Bug Fixes

- [x] **Address autocomplete fix** ✅ 2026-03-16 (pushed, deploying)
  - Removed osm_tag filter, added error handling
- [ ] **Inflation adjustment on demo endpoint** (~30min)
  - Demo apartments show raw 2019 prices — apply ×1.378 in demo router
- [ ] **Optimize page Gap % display** (~15min)
  - Currently shows 1790% instead of 17.9% — Lovable display bug

### Basic Tier Enforcement

- [ ] **Unit counter in Add units** (~30min)
  - Show "1/3 units" for Free, "5/15 units" for Pro
  - Disable "Add unit" button when at limit
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

- [ ] **Portfolio map (Leaflet)** (~2h)
  - Compliance-colored pins on Berlin map
  - Click pin → navigate to unit detail
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

- [ ] **SEO content — first 3 blog posts** (~3h)
  - "Mietpreisbremse Rechner 2026 — Kostenlos prüfen" (DE)
  - "Berlin Rent Brake Calculator — Free Check" (EN)
  - "Lohnt sich die Küchenrenovierung? Daten statt Bauchgefühl" (DE)
- [ ] **LinkedIn company page + first 5 posts** (~2h)
  - Data insights from our analysis (restaurant density, balcony ROI, CO2 stats)
- [ ] **Product Hunt launch** (~1h)
  - "Rent Intelligence for Germany" listing
- [ ] **Landlord forum posts** (~1h)
  - vermieter-forum.com, immobilienscout24.de community
- [ ] **Newsletter setup (Substack)** (~1h)
  - "Berlin Rent Intelligence" weekly brief

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
- [ ] Per-listing lat/lon spatial features (requires coordinate data)
- [ ] European expansion (Austria, Netherlands, France, Sweden)

---

## 🎯 Hackathon-Specific (April 25-26, 2026)

*Separate track — these enhance the demo, not the product.*

- [ ] Gemini API integration (spatial extraction + NL→structured)
- [ ] Gradium API integration (German STT voice input)
- [ ] Entire CLI setup (build process tracking)
- [ ] Pitch deck in Gamma (content ready at `pitch/PITCH-DECK.md`)
- [ ] Record backup demo video
