# RentSignal — Product & Commercial Strategy
## Regulated Rent Intelligence — From Unit-Level Tool to Portfolio Platform

*Last updated: 2026-03-16*

---

## 1. What RentSignal Is

**Category we own: Regulated Rent Intelligence**

No one occupies the intersection of *ML-powered rent prediction* + *legal compliance automation* + *causal renovation economics* for regulated European markets. Conny does enforcement. Rentana does US free-market pricing. Predium does ESG snapshots. RentSignal is the intelligence layer that connects all three — for markets where the law constrains every pricing decision.

### Positioning Evolution

| Phase | Positioning | Tagline |
|-------|------------|---------|
| **Phase 1: Launch** (May–Aug 2026) | Rent intelligence platform | "Rent intelligence for the German rental market" |
| **Phase 2: Portfolio** (Sep 2026+) | Portfolio rent intelligence | "Portfolio rent intelligence for property managers" |
| **Phase 3: Scale** (2027+) | Intelligence layer for regulated markets | "The intelligence layer for regulated rental markets" |

**Today:** A unit-level rent intelligence platform built around three pillars — Comply, Optimize, Act — with portfolio monitoring from day one.

**Tomorrow:** A portfolio intelligence platform that optimizes pricing, renovations, vacancy, and compliance risk across thousands of units — "Bloomberg Terminal for property managers."

**The demand cycle:**
```
COMPLY (what's the legal position?) → OPTIMIZE (what's the unit worth?) →
ACT (what should I do?) → MONITOR (is anything changing?) → COMPLY...
```

### The Three Pillars

**Comply · Optimize · Act**

| Pillar | What it answers | Core tools |
|--------|----------------|-----------|
| **Comply** | What is my legal position — now and going forward? | Mietpreisbremse check (§556d), Mieterhöhung limits (§558), Modernization passthrough (§559/§559e), Energy compliance (CO2KostAufG, GEG), ESG risk flags (Phase 2) |
| **Optimize** | What is every unit worth — and what am I leaving on the table? | Rent prediction (37 features + satellite), feature contribution breakdown (SHAP), portfolio rent gap analysis, market monitoring + alerts, comparable benchmarking |
| **Act** | What should I do next — renovation, rent increase, or new acquisition? | Renovation ROI simulator (dual-method), Mieterhöhung wizard + letter generation, Neighborhood Investment Intelligence, budget-constrained acquisition analysis |

### What We Sell

1. **Compliance intelligence** — Real-time legal position across rent law (§556d, §558, §559/§559e BGB) and energy/climate law (CO2KostAufG, GEG). Covers both new leases and existing tenants. Prevents the Conny complaint and the energy penalty before either happens.

2. **Rent optimization** — XGBoost prediction with 37 features including satellite spatial indices. R²=0.749 on 10,275 Berlin listings. Unit-specific prediction with feature contribution breakdown showing exactly why. Portfolio monitoring that alerts when market conditions change.

3. **Decision intelligence** — Dual-method renovation ROI (observational matching + demand-side estimation, 3% convergence). Mieterhöhung wizard with formal letter generation. Neighborhood Investment Intelligence for acquisition due diligence.

### Validation Evidence

| Claim | Evidence | Source |
|-------|----------|--------|
| Prediction accuracy | R²=0.749, RMSE=2.59 €/m² | XGBoost v3, 37 features, 10,275 listings |
| Spatial improvement | +2.4% R² over baseline | OSM + Sentinel-2 vs structural-only model |
| Causal convergence | Kitchen renovation impact: 3% apart across two independent methods | Observational matching (2,288 matched pairs) vs demand-side estimation (75 respondents) |
| Renovation insight | Balcony renovation impact = -€0.72/m² (negative) | Robust across 3 caliper specifications |
| Legal compliance | 3 exemption types, §559 + §559e BGB | Validated against Berlin Mietspiegel 2024 |

---

## 2. Product Layers

```
┌───────────────────────────────────────────────────────────┐
│  PORTFOLIO INTELLIGENCE (Enterprise — Phase 2+)           │
│                                                           │
│  • Cross-unit pricing with demand substitution (IO/BLP)   │
│  • Renovation budget allocation (constrained optimization)│
│  • Vacancy prediction & lease coordination                │
│  • Compliance risk aggregation (portfolio VaR)            │
│  • Geographic strategy (satellite temporal analysis)      │
│  • ESG risk scoring + EU EPBD deadline flags              │
│                                                           │
│  ← Requires enterprise client data + time-series data     │
└──────────────────────────┬────────────────────────────────┘
                           │ feeds on
                           ▼
┌───────────────────────────────────────────────────────────┐
│  PORTFOLIO MONITORING (Pro/Business — Phase 1) 🔨 BUILD   │
│                                                           │
│  • Portfolio watchdog — nightly re-check on all units     │
│  • Market drift alerts (rent gap changes, new comparables)│
│  • Monthly portfolio health report (PDF, client-ready)    │
│  • Compliance risk dashboard (€/year exposure, ranked)    │
│  • Revenue gap dashboard (underpriced units, ranked)      │
│                                                           │
│  ← Light versions of Phase 2 features, available now     │
└──────────────────────────┬────────────────────────────────┘
                           │ feeds on
                           ▼
┌───────────────────────────────────────────────────────────┐
│  UNIT-LEVEL INTELLIGENCE (Free + Pro — Phase 1) ✅ BUILT  │
│                                                           │
│  • COMPLY  — Mietpreisbremse (§556d) + energy compliance  │
│  • OPTIMIZE — Rent prediction + SHAP + monitoring alerts  │
│  • ACT     — Renovation ROI + Mieterhöhung wizard +       │
│              Neighborhood Investment Intelligence          │
│  • SPATIAL — Satellite + OSM neighborhood features        │
│                                                           │
│  ← This is the launch product & landing page              │
└───────────────────────────────────────────────────────────┘
```

### Dashboard Structure (Maps to Three Pillars)

Sidebar navigation: **Portfolio** → **Add units** → **Comply** → **Optimize** → **Act** → **Neighborhoods**

Each unit has a detail view with 4 tabs: **Optimize** (prediction + feature breakdown) · **Comply** (Mietpreisbremse + §558 + CO2) · **Act** (renovation ROI + Mieterhöhung) · **Spatial** (neighborhood map + features)

Portfolio page includes: stat cards (total units, avg predicted rent, compliance exposure, revenue gap) + portfolio map + units table + revenue gap breakdown chart.

See `frontend/rentsignal_dashboard_v3.html` for the interactive prototype and `frontend/TIER-GATING-SPEC.md` for the complete tier gating matrix per page/element.

---

## 3. Customer Segments & ICP Prioritization

### Segment Analysis

| Segment | Size (Germany) | Pain Point | Willingness to Pay | Acquisition Difficulty | **Priority** |
|---------|---------------|------------|-------------------|----------------------|-------------|
| **A. Property management companies (Hausverwaltungen)** | ~24,000 companies managing 15M+ units | Pricing across portfolios, compliance risk, renovation ROI at scale, client reporting | High (€2-5/unit/month) | Medium (B2B sales, conference-driven) | **#1 — Enterprise** |
| **B. Professional landlords (5-50 units)** | ~800,000 individuals | Setting correct rent, avoiding Mietpreisbremse complaints, renovation decisions, annual rent reviews | Medium (€29/month flat) | Low (SEO, content marketing) | **#2 — Pro** |
| **C. Small landlords (1-4 units)** | ~3.9M individuals | "Am I charging the right rent?" + compliance anxiety | Low (free → conversion) | Very low (freemium, word-of-mouth) | **#3 — Freemium funnel** |
| **D. PropTech platforms (Buena, ImmoScout24)** | ~50 relevant platforms | Need intelligence layer for their existing tools | Very high (API licensing, €0.10-0.50/query) | High (partnership/BD) | **#1b — API/White-label** |
| **E. Institutional investors / REITs** | ~200 active in Germany | Portfolio-level analytics, geographic strategy, ESG | Very high (€10K+/month) | Very high (long sales cycles) | **Phase 2+** |

### Realistic Usage Patterns by ICP

Understanding *how often* each ICP actually uses the product is critical for retention design.

| ICP | Natural trigger events | Frequency | Retention risk | Fix |
|-----|----------------------|-----------|----------------|-----|
| **Small landlord (1-4 units)** | Tenant moves out, Mietspiegel update, Conny letter | 2-4× per year | "I've run my checks, why keep paying?" | Free tier only — no subscription needed |
| **Professional landlord (5-50 units)** | Turnover (~10%/year across portfolio = 1-5 events/year), annual rent reviews, renovation decisions | 8-15× per year | Seasonal spikes, off-season silence | Portfolio Monitor provides passive engagement; monthly digest keeps them subscribed |
| **Hausverwaltung (50-500 units)** | Turnover (50-75 units/year for 500-unit manager), annual review season (Jan-Mar), client reporting | 20-40× per year | Tool vs. platform perception | Monthly client report PDF — canceling means losing a professional deliverable |
| **PropTech API partner** | Always on | Continuous | N/A | Per-query pricing |

**Key retention insight:** The subscription is justified not by session frequency but by the *monitoring relationship* (Pro) and *client deliverables* (Business). Even if a Pro user doesn't log in for 6 weeks, the platform is watching their portfolio and will email them when something changes. Cancel, and nobody is watching.

### Early Adopter Focus

**Primary target: Segment B (Professional landlords, 5-50 units)**
- Most likely to find us via SEO ("Miete berechnen Berlin", "Mietpreisbremse Rechner")
- Large enough to value renovation simulator and portfolio monitoring
- Small enough to self-serve — no enterprise sales needed
- Annual rent review season (Jan-Mar) is a natural activation moment

**Secondary target: Segment D (PropTech platforms)**
- Buena manages 60,000+ units — a single partnership is transformative
- API integration = instant scale without our own user acquisition
- Buena alone at €2/unit/month = €1.44M ARR

**Freemium funnel: Segment C (Small landlords)**
- Free compliance check = acquisition wedge, no login required
- Converts to Pro when they want monitoring + renovation simulator

---

## 4. Product Format: SaaS Dashboard + API

**Decision: Web-first SaaS dashboard + API for platform partners.**

The dashboard serves Segments B and C directly. The API serves Segment D. Both share the same FastAPI backend.

---

## 5. Data Ingestion — How Users Get Their Properties In

A Business-tier user with 200 units will not fill 200 forms. Ingestion design is a retention problem, not just a UX problem: if onboarding is painful, activation never happens.

### Ingestion Methods by Tier

| Tier | Primary method | Secondary | Notes |
|------|---------------|-----------|-------|
| **Free** | Single-unit form with address autocomplete | — | No bulk needed |
| **Pro** | Address autocomplete + guided unit-by-unit entry | CSV upload (our template, up to 20 units) | Most Pro users have ≤20 units in a spreadsheet |
| **Business** | Intelligent CSV mapper — upload any format, map columns visually | Assisted onboarding call (we do the mapping) | Assisted onboarding is a retention mechanism |
| **Enterprise** | objego API sync (Phase 2) | Intelligent CSV mapper | objego integration unlocks all Hausverwaltungen using it |

### Address Autocomplete
User types a partial address → we resolve via OSM Photon API (free, self-hostable) → auto-populate PLZ, district, and inferred building year from OSM tags. User confirms/corrects rather than filling from scratch.

### Intelligent CSV Mapper (Business tier)
User uploads any CSV or Excel export from their existing system (objego, DOMUS, their own spreadsheet). We detect column headers and show a visual mapping interface: "Your column 'Wohnfläche' → Living Space (m²)". User confirms, import runs as an async job. Result: their entire portfolio is onboarded in under 10 minutes, regardless of their source format.

### Assisted Onboarding (Business tier)
A 30-minute onboarding call where we take the client's export file, clean it, and upload it for them. Cost: 30 minutes of our time. Benefit: dramatically higher activation rate, early relationship with the account, clean data from day one. Offered as standard for all new Business subscribers.

### Listing URL Auto-fill (Pro tier, Phase 2)
User pastes an ImmoScout24 listing URL → we parse the listing and pre-populate the form. Legally gray, implement defensively with fallback to manual entry.

### PM Software Integration (Enterprise, Phase 2)
Direct sync with objego (market leader in German property management software). One-click export → RentSignal import. Eliminates onboarding friction entirely for enterprise clients.

---

## 6. Pricing & Tiers

### Tier Structure

The tiers represent different *relationships* with the platform, not just feature gates.

| | **Free** | **Pro** | **Business** | **Enterprise** |
|--|---------|---------|-------------|---------------|
| **Price** | €0 | €29/month | €99/month or €2/unit/month | Custom (min €500/month) |
| **Target** | Small landlords (1-3 units) | Professional landlords (5-15 units) | Property managers (15-500 units) | Large managers + platforms (500+ units) |
| **Units** | Max 3 | Max 15 | Unlimited | Unlimited |
| **Relationship** | One-time checks | Your portfolio is being watched | Your clients get monthly reports | Full intelligence infrastructure |
| **Comply** | Mietpreisbremse check (unlimited, no login for first) | + Mieterhöhung calculation + CO2KostAufG energy exposure | + Full portfolio compliance risk table (sortable, all units ranked by €/year exposure) | + ESG risk scoring, EU EPBD deadline flags (Phase 2) |
| **Optimize** | 3 predictions/month, feature breakdown top 3 only (rest blurred) | Unlimited predictions + full feature breakdown (all 37) + portfolio monitoring alerts + weekly digest email | + Batch analysis + full revenue gap ranking + comparable benchmarking | + API access, custom integrations |
| **Act** | 🔒 Visible but locked (preview with "don't build the balcony" chart) | ✅ Renovation simulator + Neighborhood Intelligence + Mieterhöhung wizard + letter PDF | + Acquisition comparison (up to 5 candidates) + Neighborhood PDF export | + Portfolio renovation budget allocation (Phase 2) |
| **Neighborhoods** | 🔒 Visible but locked | ✅ Full access | + PDF export | + Custom reporting |
| **Ingestion** | Manual form + address autocomplete | + CSV upload (template, max 15) | + Intelligent CSV mapper (any format, unlimited) + assisted onboarding | + PM software sync (Phase 2) |
| **Reporting** | — | PDF per-unit reports | Monthly portfolio health PDF (client-ready, brandable) | Custom reporting + SLA |

### Gating Philosophy

**Show value before gating.** Never hide a feature entirely — hidden features can't sell themselves. Show locked features with blurred/dimmed results or a preview, then gate the full output.

**Gate outputs, not inputs.** Let any user fill out any form. Gate the *result*, not the *form*. A Free user who fills out a renovation form should see a teaser of the result with an upgrade prompt — they've invested effort; reward that with a glimpse, then convert.

**Upgrade prompts are contextual, not generic.** "Upgrade to Pro" is weak. "This unit is underpriced by €1.67/m² — unlock the full breakdown for €29/month" is strong. Every prompt references the specific value the user is about to unlock, using their own data.

### Unit Limits & Rate Limits

| Tier | Units | Predictions/month | CSV rows | API calls/day |
|------|-------|--------------------|----------|---------------|
| Free | 3 | 3 | 0 | 50 |
| Pro | 15 | Unlimited | 15 | 1,000 |
| Business | Unlimited | Unlimited | Unlimited | 10,000 |
| Enterprise | Unlimited | Unlimited | Unlimited | Custom |

### Trial & Conversion

- **Pro trial:** 14 days, no credit card required. Triggered when Free user clicks any upgrade prompt.
- **Downgrade:** Units beyond limit become "archived" — visible but not analyzable. No data deleted. Monitoring stops, alerts stop, digest emails stop.

See `frontend/TIER-GATING-SPEC.md` for complete page-by-page gating matrix, upgrade prompt patterns, and frontend implementation notes.

### Pricing Logic

- **Free = acquisition wedge.** Compliance check is the hook. Free, unlimited, no login for first check. Captures email on second use. Conny's advertising creates the demand — we capture it.
- **Pro = the monitoring relationship.** €29/month is less than one hour of any professional's time. The value is not one session — it's the platform watching your portfolio when you're not.
- **Business = the client deliverable.** The monthly portfolio health PDF is something property managers send to their building owners. Canceling RentSignal means losing a professional deliverable they bill for.
- **Enterprise = the infrastructure.** Buena's 60,000 units at €2/unit = €120K/month = €1.44M ARR. Even 5 enterprise clients = €600K+/month ARR.

### API Pricing (Segment D)

| Endpoint | Per-query price | Notes |
|----------|----------------|-------|
| `/compliance` | €0.05 | High volume, low compute |
| `/predict` | €0.15 | ML inference + SHAP |
| `/renovate` | €0.25 | Dual-method computation |
| Bundle (all 3) | €0.30 | Discount for combined use |
| Monthly minimum | €500 | Ensures commitment |

---

## 7. Neighborhood Investment Intelligence

### Scope Definition

The Neighborhood Investment Intelligence feature answers: *before you invest in or manage in a neighborhood, understand what rents look like, what drives them, and what renovations will pay off there.*

This is the due diligence layer before an acquisition, not a property listing service. We do not recommend specific properties — that is ImmoScout's job. We are the research layer users consult before going to ImmoScout.

### What We Show (PLZ Level)

- Predicted rent range for typical units in this PLZ
- Which features matter most for rent here (SHAP aggregated at PLZ level — e.g., "in PLZ 12049, transit proximity contributes +€0.80/m² vs Berlin average")
- Top renovation ROI in this PLZ (kitchen vs balcony performance varies by neighborhood type)
- Compliance landscape: estimated % of units in this PLZ above legal max (proxy for how tightly the Mietpreisbremse binds)
- Spatial benchmark: how this PLZ scores on NDVI, restaurant density, transit access vs comparable PLZs
- Side-by-side PLZ comparison: "PLZ 12049 vs PLZ 10119 vs PLZ 10437 — which has better fundamentals?"

### What We Explicitly Do Not Show (Yet)

- Neighborhood price trends over time — requires historical listing time-series data (Phase 2)
- Vacancy rates — requires external data source (Phase 2)
- Comparable transaction/sale prices — requires notarial deed data (Phase 2)
- Specific properties for sale or rent — not our product

### Budget-Constrained Acquisition Analysis

When a user provides a list of candidate addresses and a budget ceiling:

- We run the full unit assessment on each candidate (predicted rent, legal max, rent gap, top renovation opportunities)
- We return a ranked list by expected rental yield
- When budget is provided, we identify the optimal subset: "With €500,000, properties A and C together generate €2,400/month estimated — better than property B alone at €1,900/month"
- Phase 1: simple ranking + budget filter. Phase 2: integer programming optimization.

---

## 8. New Feature: Mieterhöhung Wizard

### What It Solves

This is separate from the Mietpreisbremse (which governs new leases). §558 BGB allows landlords to raise rent on *existing tenants* up to the Mietspiegel mid value, capped at 15-20% within any 3-year period, with a formal written request required.

Every professional landlord does this every 2-3 years per unit. A 20-unit landlord has 6-10 of these per year. Many don't know the exact rules and generate the letters incorrectly or miss the optimal timing.

### What It Produces

1. **Calculation:** Can I increase? By how much? When is the earliest legal date? What is the new legal maximum?
2. **Letter (PDF):** A formally compliant Mieterhöhungsverlangen letter in German, pre-filled with the calculation output, ready to sign and send. Must meet §558a BGB formal requirements. *Requires one-time legal review before launch (budget €200-500).*

---

## 9. Comply Pillar: Climate & Energy Compliance Expansion

The Comply pillar expands beyond rent law to cover the growing energy/climate compliance surface. Same engine, new rules.

### Phase 1 (Launch)

**CO2KostAufG (CO2 cost-sharing law, in force since 2023)**
Landlords of energy-inefficient buildings pay a share of tenant carbon costs. This directly reduces net rental income and scales with the CO2 price (currently €55/tonne, rising to €65 in 2026). We calculate: building energy class → landlord CO2 cost share % → annual cost exposure in €. Already financially material for EPC class E, F, G buildings.

**§559e BGB (GEG heating replacement)**
Already in the compliance engine. Surface more prominently in the UI as a distinct compliance scenario.

### Phase 2

**EU EPBD mandatory renovation deadlines**
Under the EU Energy Performance of Buildings Directive, worst-performing buildings (EPC class F and G) must reach class E by 2030, class D by 2033. Flag affected units: "Your building is EPC class G — mandatory renovation required by 2030. Estimated cost: €X. Available KfW subsidies: €Y. Without action: stranded asset risk."

**ESG risk scoring (Enterprise)**
Aggregate ESG exposure across a portfolio, prioritized by regulatory deadline and estimated cost. Positions RentSignal as "Rentana + Predium" — rent optimization and ESG intelligence in one platform.

---

## 10. Go-to-Market Strategy

### Phase 1: Launch (May-June 2026)

**Goal:** First 100 registered users, 10 paying Pro subscribers, 1 platform partnership conversation.

| Channel | Action | Cost | Expected Result |
|---------|--------|------|----------------|
| **SEO/Content** | Blog articles: "Mietpreisbremse Rechner 2026", "Lohnt sich Küche renovieren?", "Miete berechnen Berlin" | €0 | Organic traffic, 500+ monthly visitors in 60 days |
| **Big Berlin Hack** | Demo at hackathon → press, Buena relationship | €0 | Buena partnership lead, press mentions |
| **Product Hunt** | Launch "Rent Intelligence for Germany" | €0 | 200+ signups in first week |
| **Landlord forums** | Post on immobilienscout24.de forum, wohnen-im-eigentum.de, vermieter-forum.com | €0 | 50+ early adopters |
| **LinkedIn** | Daniel's network + PropTech Berlin community | €0 | Warm leads for Pro tier |

### Phase 2: Growth (July-Dec 2026)

- Expand to other German cities (Hamburg, Munich, Frankfurt)
- Launch Business tier with full portfolio features
- Close first enterprise/API partnership
- Target: 500 users, 50 Pro, 5 Business, 1 Enterprise

### Phase 3: Scale (2027)

- Portfolio optimization pillars
- European expansion (Austria, Netherlands)
- Raise seed round if traction supports it

---

## 11. Competitive Positioning

### The Landscape

| Competitor | What They Do | Their Gap | Our Advantage |
|-----------|-------------|-----------|---------------|
| **Conny** | Tenant-side enforcement | No landlord product, calculations documented as structurally incorrect | We're landlord-side AND more accurate. We prevent the Conny complaint before it happens. |
| **Rentana** | US dynamic pricing for multifamily | No German market, no Mietpreisbremse, no renovation analysis | We handle regulated markets. Feature contribution breakdown is our version of their "why" explanations. |
| **Predium** | ESG for real estate (satellite-based) | No pricing, no compliance, no renovation ROI | Same satellite pipeline, different application. ESG is our expansion path, not our starting point. |
| **ImmoScout24 Preisatlas** | Market-level price maps | No unit-level prediction, no compliance, no renovation analysis | We go from "average price in this area" to "your specific apartment should charge €X because of these 10 factors." |
| **Official Mietspiegel** | Government reference table | Static, no ML, no spatial, no renovation, published every 2 years | We enhance the Mietspiegel with 37 features + satellite + causal renovation effects. |

### Our Positioning Statement

> **For property managers and landlords in Germany** who need to optimize rental income within legal constraints, **RentSignal** is a regulated rent intelligence platform built around three pillars: Comply, Optimize, and Act. **Unlike** Conny (tenant-side only), Rentana (US, no regulation), or the official Mietspiegel (static, no ML), **RentSignal** delivers unit-level intelligence, portfolio monitoring, and decision support — for the world's most regulated rental market.

### The Six Gaps Nobody Fills

1. ✅ ML-powered unit prediction with feature contribution breakdown (SHAP)
2. ✅ Real-time Mietpreisbremse + energy compliance checking
3. ✅ Satellite-derived spatial features (NDVI, NDWI, NDBI + OSM)
4. ✅ Causal renovation impact estimation (not just correlation)
5. ✅ Dual-method validation (observational + demand-side)
6. ✅ Portfolio monitoring with automated alerts and client-ready reporting

---

## 12. Product Roadmap

| Priority | Timeline | What | Commercial Impact |
|----------|----------|------|-------------------|
| **P0** | April 2026 | Portfolio CRUD + CSV import + batch analysis job | Nothing else works without this |
| **P0** | April 2026 | Address autocomplete (OSM Photon) | Dramatically reduces unit entry friction |
| **P1** | May 2026 | Public launch: Free + Pro tiers, SEO content | First users, first revenue |
| **P1** | May 2026 | Mieterhöhung wizard + letter generation (§558) | High-frequency, high-value tool for Pro users |
| **P1** | May 2026 | Portfolio summary + compliance risk + revenue gap dashboards | Delivers the monitoring value proposition |
| **P1** | May 2026 | CO2KostAufG energy compliance engine | Expands Comply pillar, differentiates from pure rent tools |
| **P1** | May 2026 | Neighborhood Investment Intelligence (PLZ-level) | Powers the Act pillar, acquisition use case |
| **P2** | June 2026 | Portfolio Monitor — nightly watchdog + alert system | The core retention mechanism for Pro tier |
| **P2** | June 2026 | Monthly portfolio health report PDF | The core retention mechanism for Business tier |
| **P2** | June 2026 | Intelligent CSV mapper | Unlocks Business tier onboarding at scale |
| **P2** | June 2026 | City expansion: Hamburg, Munich | 3× addressable market |
| **P3** | Aug 2026 | Public API with docs + pricing page | Platform partnership revenue |
| **P3** | Aug 2026 | Budget-constrained acquisition comparison | Differentiates Neighborhood Intelligence from static map |
| **P3** | Sep 2026 | Listing URL auto-fill (ImmoScout) | Pro tier friction reduction |
| **P4** | 2027 | Neighborhood trend analysis (time-series) | Requires historical listing data |
| **P4** | 2027 | Portfolio renovation budget allocation (integer programming) | Crown jewel Phase 2 feature |
| **P4** | 2027 | EU EPBD deadline flags + ESG scoring | Enterprise value prop |
| **P4** | 2027 | objego PM software integration | Enterprise onboarding unlock |

---

## 13. New API Endpoints

### P0 — Build First (nothing else works without these)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/portfolio/units` | Create a single unit in user's portfolio |
| GET | `/portfolio/units` | List all units for authenticated user |
| GET | `/portfolio/units/{unit_id}` | Get single unit with latest cached analysis |
| PUT | `/portfolio/units/{unit_id}` | Update unit data |
| DELETE | `/portfolio/units/{unit_id}` | Remove unit |
| POST | `/portfolio/import/csv` | Upload any CSV → returns detected columns for mapping UI |
| POST | `/portfolio/import/confirm` | Submit column mapping → execute import as async job |
| GET | `/portfolio/import/{job_id}` | Poll import job status |
| POST | `/portfolio/analyze` | Trigger batch predict+comply on all/selected units |
| GET | `/portfolio/analyze/{job_id}` | Poll batch analysis job status |
| GET | `/address/autocomplete?q=` | Partial address → suggestions with PLZ + district (wraps OSM Photon) |
| POST | `/address/resolve` | Full address → PLZ, district, lat/lon, inferred building year |

### P1 — Core Value (delivers the three-pillar UVP)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/portfolio/summary` | Aggregate metrics: total units, avg rent gap, total compliance exposure €/year |
| GET | `/portfolio/compliance-risk` | All units with compliance status + €/year exposure, sorted by risk |
| GET | `/portfolio/revenue-gaps` | Units sorted by rent gap, underpriced first |
| POST | `/rent-increase/calculate` | §558 BGB: can I increase? by how much? earliest date? Reuses compliance logic. |
| POST | `/rent-increase/letter` | Same input + tenant details → PDF Mieterhöhungsverlangen letter |
| POST | `/compliance/energy` | Building energy class + specs → CO2KostAufG landlord share + annual exposure € |
| GET | `/neighborhood/{plz}` | Extends existing `/spatial/{plz}`: add rent range, PLZ benchmark vs Berlin avg |
| GET | `/neighborhood/map` | All Berlin PLZs with summary metrics for frontend map rendering |
| GET | `/neighborhood/compare?plz=` | Compare 2-3 PLZs side by side |

### P2 — Retention (drives subscription stickiness)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/monitor/subscribe` | Subscribe units to nightly market monitoring |
| GET | `/monitor/alerts` | Get pending alerts (type, unit_id, message, detected_at) |
| POST | `/monitor/alerts/{id}/dismiss` | Mark alert as seen |
| GET | `/monitor/digest` | Preview of weekly digest email content |
| GET | `/portfolio/report/monthly` | Generate monthly portfolio health report PDF |
| GET | `/neighborhood/{plz}/report` | PDF export of neighborhood intelligence |

### P3 — Differentiation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/acquisition/analyze` | Full assessment for one candidate property (composes predict + comply + renovate + neighborhood) |
| POST | `/acquisition/compare` | List of addresses + optional budget ceiling → ranked list + budget-optimal subset |
| POST | `/address/from-url` | ImmoScout listing URL → pre-populated ApartmentInput. Implement defensively. |

### P4 — Phase 2 (defer — requires new data or significant new compute)

| Method | Endpoint | Description | Blocker |
|--------|----------|-------------|---------|
| GET | `/neighborhood/{plz}/trend` | Rent trend over time for a PLZ | Needs historical listing time-series data |
| POST | `/portfolio/optimize` | Budget-constrained renovation allocation (integer programming) | Needs client portfolio data at scale |
| POST | `/compliance/esg` | ESG risk scoring + EU EPBD deadline flags | Needs EPC data pipeline |

### Background Jobs (scheduled, not request-response)

| Job | Schedule | What it does |
|-----|----------|-------------|
| `portfolio_monitor_job` | Nightly | Re-runs predict+comply on all monitored units. Writes alerts when rent gap or compliance status changes beyond threshold. |
| `market_snapshot_job` | Weekly | Updates neighborhood comparison baselines from model outputs. |
| `digest_email_job` | Monday 8:00 AM CET | Composes and sends weekly portfolio digest to all Pro/Business subscribers with monitored units. |

---

## 14. Key Metrics to Track

### Product Metrics

| Metric | Target (Month 3) | Target (Month 12) |
|--------|------------------|-------------------|
| Registered users | 500 | 5,000 |
| Monthly active users | 200 | 2,000 |
| Predictions run | 1,000/month | 20,000/month |
| Compliance checks | 3,000/month | 50,000/month |
| Free → Pro conversion | 5% | 8% |
| Pro churn (monthly) | <8% | <5% |

### Commercial Metrics

| Metric | Target (Month 6) | Target (Month 12) |
|--------|------------------|-------------------|
| MRR | €2,000 | €12,000 |
| Paying customers | 20 | 100 |
| Enterprise pipeline | 3 conversations | 2 signed |
| API partners | 1 in pilot | 2 live |

---

## 15. Revenue Projections

### Conservative Scenario (Year 1)

| Revenue Stream | Units/Clients | Price | Monthly | Annual |
|---------------|---------------|-------|---------|--------|
| Free → Pro conversion | 30 Pro subscribers | €29/month | €870 | €10,440 |
| Business tier | 5 property managers (avg 100 units) | €200/month avg | €1,000 | €12,000 |
| API partnership | 1 platform (5,000 queries/month) | €0.30/query | €1,500 | €18,000 |
| **Total Year 1** | | | **€3,370/month** | **€40,440** |

### Optimistic Scenario (Year 1)

| Revenue Stream | Units/Clients | Price | Monthly | Annual |
|---------------|---------------|-------|---------|--------|
| Pro subscribers | 100 | €29/month | €2,900 | €34,800 |
| Business tier | 15 (avg 150 units) | €300/month avg | €4,500 | €54,000 |
| API/Enterprise | 2 platforms + 1 enterprise | €5,000/month avg | €5,000 | €60,000 |
| **Total Year 1** | | | **€12,400/month** | **€148,800** |

### The Buena Scenario (Enterprise, Year 2)

60,000 units × €2/unit/month = **€120,000/month = €1.44M ARR**

---

## 16. Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Data vintage** (model trained on 2018-2019) | High | Medium | Transparent about it. Inflation adjustment factor (1.378). Retrain on current data quarterly in production. |
| **Mietspiegel changes** | Medium | High | Engine is parameterized — update JSON lookup table when new Mietspiegel published. |
| **Competitor copies unit-level tool** | Medium | Medium | Portfolio monitoring and client reporting are the real moat. Unit tool is acquisition, not defensibility. |
| **Buena builds internally** | Low | High | Move fast. Show ROI. Be so good it's cheaper to partner than build. |
| **GDPR / data privacy** | Low | High | No personal tenant data. Only apartment features and public market data. |
| **Mieterhöhung letter legal accuracy** | Medium | High | One-time legal review before launch (budget €200-500). |

---

## 17. Brand Voice & Vocabulary

### Voice Rules

- **Confident, not arrogant.** Lead with validation numbers, don't inflate them.
- **Technical credibility without jargon.** Say "we matched 2,288 apartment pairs to isolate the kitchen effect" not "propensity score matching with logit caliper."
- **Outcome-first.** Lead with what the landlord gains/avoids, not methodology. Unlock methodology for technical audiences.
- **Slightly contrarian.** "Most landlords think balconies increase rent. The data says otherwise."
- **Show, don't claim.** Never "best-in-class." Instead: "R²=0.749 on 10,275 Berlin apartments, with satellite spatial features nobody else uses."
- **Bilingual-ready.** German-first for landlords, English-first for investors and tech audiences.

### Vocabulary Rules

**Always use:**
- "Comply · Optimize · Act" as the three-pillar frame
- "rent intelligence" (not "rent calculator")
- "market prediction" (not "AI prediction")
- "legal maximum" (not "Mietpreisbremse limit")
- "renovation impact" or "renovation ROI" (not "CATE" or "treatment effect")
- "spatial features" or "neighborhood intelligence" (not "remote sensing variables")
- "dual-method validation" (not "stated vs revealed preference")
- "compliance risk" (not "overpayment exposure")
- "feature contribution" or "feature contribution breakdown" (not "SHAP value" — unless talking to data scientists)
- "demand-side estimate" (not "WTP" or "willingness to pay" — unless needed for clarity)
- "portfolio monitoring" or "portfolio watchdog" (not "dashboard" as a selling point)

**Never use:**
- "AI-powered" in hero headlines
- "causal inference" in landlord-facing copy (say "two independent methods that agree")
- "CATE", "ATT", "WTP" in external copy
- "synthetic customers" or "AI personas" (say "simulated demand")
- "digital twin", "disrupting", "revolutionizing", "big data"
- "dashboard" as a selling point (it's a delivery format)
- "backed by satellite data and causal inference" in hero or features copy — save for investor/technical audiences and the trust badge

### Messaging by Audience

| Audience | Lead With | Unlock |
|----------|----------|--------|
| **Landlord (1-4 units)** | "Is your rent too high, too low, or just right? Find out in 10 seconds." | Free compliance check → prediction → renovation simulator |
| **Professional landlord (5-50 units)** | "Your portfolio is being watched. We'll tell you when to act." | Portfolio monitoring, renovation ROI, Mieterhöhung wizard |
| **Property manager (Hausverwaltung)** | "340 of your 2,000 units are above the legal max. Annual exposure: €420K. Here's the breakdown." | Compliance risk dashboard, revenue gap ranking, monthly client report |
| **PropTech platform** | "Add rent intelligence to your product. 3 API endpoints, <500ms latency, €0.30/query." | Technical docs, sandbox, white-label options |
| **Investor** | "€828M TAM. 6 gaps nobody fills. Unit-level tool built. Portfolio monitoring is the moat." | Validation evidence, competitive matrix, revenue projections |
| **Event / pitch audience** | "Conny tells tenants they're overpaying. We tell property managers where the money is — and where the risk is." | Live demo, "don't build the balcony" moment, satellite differentiator |

---

## 18. Sales Motion & Objection Handling

### Sales Motion: Land with Compliance, Expand with Intelligence

```
FREE compliance check (no login)
  → email capture on 2nd use
  → show prediction gap ("you're leaving €X on the table")
  → Pro trial (14 days)
  → Pro subscription (€29/month) — monitoring relationship begins
  → Business upgrade when they add more units or need client reports
  → Enterprise when portfolio features ship
```

**Trigger signals to target:**
- New Mietspiegel publication (all landlords need to recheck)
- Conny advertising campaigns (compliance anxiety spikes among landlords)
- Tenant turnover (landlord googles "neue Miete festlegen Berlin")
- Annual rent review season (Jan-Mar)
- Renovation planning season (spring)
- Property acquisition

### Objection Handling

| Objection | Response |
|-----------|----------|
| **"Your model uses 2018 data"** | "Correct — we trained on 10,275 historical listings. The architecture is the product. We apply a validated inflation adjustment (37.8%) and retrain quarterly in production. R²=0.749 reflects model quality, not data recency." |
| **"I can just use the official Mietspiegel"** | "The Mietspiegel uses 4 variables. We use 37, including satellite vegetation indices, restaurant density, and transit proximity. That's why the Mietspiegel says €7.10/m² and we say €8.31/m² — we capture what it misses." |
| **"How do I know the prediction is accurate?"** | "R²=0.749 across 10,275 Berlin apartments. Average error: €1.70/m². The official Mietspiegel explains roughly 30-40% of rent variation. We explain 74.9%. We publish our methodology — nothing is a black box." |
| **"The renovation simulator uses synthetic data"** | "We validate against real market data. Kitchen impact via demand-side estimation: +€4.13/m². Kitchen impact from 2,288 real matched apartment pairs: +€4.01/m². 3% apart. Two independent methods, one answer." |
| **"Conny is free for tenants, why would I pay?"** | "Conny profits from landlord mistakes. We prevent them. One Conny complaint costs €3,000-5,000 in refunds + legal fees. Pro costs €29/month. One prevented complaint pays for 10 years of RentSignal." |
| **"I only have 2 apartments"** | "The compliance check is free, forever. No login. If your apartments are correctly priced, you'll know in 10 seconds." |
| **"Why pay monthly for a one-time calculation?"** | "The compliance check and prediction are instant. The value of the subscription is the monitoring — we watch your portfolio every night and tell you when the market moves, when you're drifting from optimal, or when your legal position changes. You pay for the watchdog, not the calculation." |

---

## Appendix: The Pitch Lines

**For landlords (SEO/content):**
> "Find out if your rent is too high, too low, or just right — in 10 seconds. Free."

**For property managers (B2B):**
> "Your 200 units generate €3.2M/year in rent. We found €180K you're leaving on the table and €95K in compliance risk. Here's how to fix both."

**For events / demos:**
> "Conny tells tenants they're overpaying. Rentana optimizes US free-market rents. Predium handles ESG with satellites. RentSignal combines all three — for Germany's regulated rental market."

**For investors:**
> "We're building the analytics infrastructure for Europe's largest rental market. Unit-level tool: built. Portfolio monitoring: shipping. The moat: satellite spatial features, dual-method validation, and a compliance engine that nobody else has for regulated European markets."

**The universal sentence (internal / investor / technical use only):**
> "RentSignal tells you what your apartment is worth, whether that rent is legal, and which renovations actually pay off — backed by satellite data and causal inference."

**The updated hero sentence (external, landing page):**
> "RentSignal tells you whether your rent is legal, what it should be, and what to do next."
