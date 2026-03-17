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
- [ ] **Google Analytics 4** (~30min)
  - Create property, add to Quarto blog (`_quarto.yml`) + Lovable app
  - Cookie consent banner (GDPR)
- [ ] **Google Search Console** (~20min)
  - Domain property for `rentsignal.de`, DNS TXT verification
  - Submit sitemaps (blog + main site)
- [ ] **robots.txt** for both properties (~10min)
- [ ] **Request indexing** for landing page + first articles (~10min)

#### SEO Content — 12-Week Calendar
- [x] **Wk 0:** "Küche oder Balkon?" (data insight) ✅ 2026-03-17
- [ ] **Wk 1:** "Mietpreisbremse Rechner 2026" (DE, P0) + "Berlin Rent Brake Calculator" (EN, P0)
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
