# BeeSignal Product Reference

What the product does, what it produces, how studies work, and where the platform is heading.

*Evolved from study-centric "pricing decision system" to Continuous Pricing Intelligence platform (March 2026). Updated March 2026 to reflect vocabulary decisions, framing framework (A/B), and category naming from the positioning session.*

---

## 1. What BeeSignal Is

BeeSignal is a **Continuous Pricing Intelligence platform for SaaS**. It answers the question every $1M-$50M ARR company asks but has no rigorous tool to answer:

> *What should we charge — and what actually happens when we change it?*

### Three Core Capabilities

| Capability | What It Does | Status |
|-----------|-------------|--------|
| **A. Simulate the Market** | Choice experiments on simulated demand map the full willingness-to-pay landscape across segments, features, and price points. Forward-looking: works before launch, before data exists. | Built (P0 + P0.5) |
| **B. Track Causal Impact** | DiD event studies, synthetic control, and quasi-experimental methods measure what *actually happened* after a pricing change — separating price effects from confounders. | Planned (P2) |
| **C. Recalibrate** | Live tracking of pricing performance against predictions. Pricing Health Score, drift detection, and signal-triggered demand recalibration when the market shifts. | Planned (P2-P3) |

### The Demand Cycle (4-Node Loop)

```
SIMULATE → PRICE → TRACK → RECALIBRATE → SIMULATE...
```

| Node | Name | What It Does | Method |
|------|------|-------------|--------|
| 1 | **Simulate the Market** | Choice-based experiments on simulated demand. Real choices, not stated preferences. | Experimental |
| 2 | **Price with Confidence** | Demand curves + tier architecture. Validated at r=0.80 against actual purchases. | Strategic |
| 3 | **Track Causal Impact** | Live Pricing Health Score via Stripe + Amplitude. Isolates true revenue effect from noise. | Causal |
| 4 | **Recalibrate** | Signal-triggered demand recalibration seeded from real behavioral data. Each cycle sharpens the model. | Continuous |

**Today:** BeeSignal covers nodes 1-2 (simulate + price with confidence).
**Vision:** BeeSignal owns the entire demand cycle.

### The Long-Term Position

BeeSignal is the **intelligence layer above any billing stack**. We don't process payments — Stripe does. But we tell you what your pricing should be, whether it's still optimal, and exactly when and how to adjust. Think Amplitude for pricing: Amplitude doesn't store your data, but it tells you what's happening in your product.

---

## 2. Study Types & Methods

### Two Methods

| Method | Elicitation | Design | Best For |
|--------|-------------|--------|----------|
| **Conjoint (CBC)** | SSR preference over product profiles | D-optimal, 2-3 alternatives per task | Price discovery, feature importance, willingness to pay, demand curves |
| **Experimental (Vignette RCT)** | SSR + choice + numeric | Between-subjects, stratified randomization | Causal effects of messaging, framing, pricing model on preference |

### Phase Structure

```
Phase 0 (Market Diagnostic) ---- descriptive, no randomization
    |
    +--- Phase 1a (Pricing Model Selection) ---- vignette RCT
    |         |
    |         +--- Phase 1b (Pricing Discovery) ---- conjoint (CBC)
    |         |         |
    |         +-----+---+
    |               |
    |               v
    |        Phase 2 (Tier Design) ---- REQUIRES 1a + 1b
    |               |
    |               v
    +----  Phase 3 (Stress Test / CI / Launch Sim) ---- dual-mode
```

### Study Type Matrix

| Study Type | Method | Standalone? | Client-Facing Name |
|-----------|--------|-------------|-------------------|
| Pricing Discovery | **CBC** (always) | Yes | Optimal Pricing |
| Pricing Model Selection | **RCT** (always) | Yes | Pricing Model |
| Tier Design | **RCT** (always) | No (requires 1a+1b) | Tier Design |
| Price Change Impact | **Dual** (CBC or RCT) | Yes | Price Change Impact |
| Competitive Intelligence | **Dual** (CBC or RCT) | Yes | Competitive Intelligence |
| Launch Simulation | **Dual** (CBC or RCT) | Yes | Launch Simulation |
| Market Diagnostic | **Descriptive** | Yes | Market Diagnostic |
| Validation | **CBC** (always) | Yes | Validation Study |

### CBC vs RCT Decision Logic

**Use CBC when:**
- Continuous demand curve needed (simulate any price)
- Feature-level WTP required
- Many scenarios to explore from one study
- Cross-elasticities needed
- Discovery study already done (marginal cost = 0)

**Use RCT when:**
- Few features / simple question ("Should we raise by 10%?")
- Fewer assumptions wanted (no utility function spec, no IIA)
- Standalone study (no prior Discovery)
- Concrete scenarios to compare (2-3 specific options)
- Testing framing, messaging, or pricing model (not attribute tradeoffs)

---

## 3. Study Deliverables

### 3.1 Pricing Discovery (CBC)

The core study. "What's the right price?"

| Deliverable | Output |
|-------------|--------|
| Feature Importance | Attribute importance shares (horizontal bar chart) |
| Willingness to Pay | Willingness-to-pay per attribute level with delta method CIs |
| AMCE Detail | Forest plot with coefficients, CIs, p-values |
| Demand Curve | Revenue by price point, optimal price marker, elasticity |
| Segment Analysis | Preference-based clusters with segment-specific willingness to pay |
| Recommendations | Prioritized action cards (Do Now / Explore / Monitor) |

### 3.2 Tier Design (RCT)

"How should we structure tiers?" Requires prior discovery data.

| Deliverable | Output |
|-------------|--------|
| Feature Gating Table | Which features in which tier, based on willingness to pay |
| Tier Architecture | Recommended structure with pricing |
| Self-Selection Chart | Predicted tier choice distribution |
| Value Audit | Feature-value mapping per segment |

### 3.3 Price Change Impact (Dual)

"What if we raise prices?"

| Deliverable | CBC Mode | RCT Mode |
|-------------|----------|----------|
| Price sensitivity | Continuous demand curve | ATE point estimates |
| Revenue impact | Simulated at any price point | Implied revenue per arm |
| Break-even | Volume loss threshold | N/A (direct measurement) |
| Competitor response | 3 scenario models | N/A |

### 3.4 Competitive Intelligence (Dual)

"How do we compare?"

| Deliverable | CBC Mode | RCT Mode |
|-------------|----------|----------|
| Market shares | Predicted share per product | N/A |
| Head-to-head | Diversion ratios (IIA caveat) | Win/lose/tie verdicts with lift % |
| Switching drivers | Attribute-level analysis | ATE by outcome |
| Ranking | Optimal product design | Arm ranking by intent |

### 3.5 Launch Simulation (Dual)

"Will this new product succeed?"

| Deliverable | CBC Mode | RCT Mode |
|-------------|----------|----------|
| Entry share | Simulated at any price/feature combo | ATE on purchase intent |
| Cannibalization | Own vs competitor sourcing | N/A |
| Revenue | Net incremental with portfolio impact | N/A |
| Go/no-go | N/A | Threshold-based recommendation |

### 3.6 Pricing Model Selection (RCT)

"Which pricing model works best?" Vignette experiment.

| Deliverable | Output |
|-------------|--------|
| ATE | Treatment effect of pricing model on purchase intent |
| HTE | Heterogeneous effects by segment (causal forests) |
| Ranking | Arm ranking by implied outcome |

---

## 4. Monitoring & Continuous Intelligence (Roadmap)

### Three Rings of Monitoring Data

| Ring | Data Source | What It Reveals |
|------|-----------|----------------|
| 1. Billing & Subscription | Stripe, Chargebee | MRR waterfall, churn rate, ARPU, tier distribution — lagging indicators |
| 2. Product Analytics | Amplitude, Mixpanel, PostHog | Feature usage, paywall encounters, engagement by tier — packaging alignment |
| 3. External/Market | Competitor scraping, G2/Capterra | Competitor pricing changes, sentiment shifts — leading indicators |

### Pricing Health Score

Composite metric benchmarked against demand model predictions:

| Signal | Weight | Threshold |
|--------|--------|-----------|
| Plan mix deviation from prediction | High | >15% deviation |
| Tier conversion rate trend (30-day) | High | >20% decline |
| Feature-tier alignment score | Medium | <60% alignment |
| Competitive pricing gap change | Medium | >15% relative change |
| Time since last demand study | Low | >6 months |

**Green** = Pricing performing as predicted.
**Yellow** = Signals drifting. Review recommended.
**Red** = Significant drift. Re-optimization study recommended.

### The Calibration Moat

Every study + monitoring cycle generates (demand model prediction, real outcome) pairs. This data systematically improves the demand simulation model. Compounding data advantage that competitors cannot replicate without the same installed base.

### Phased Rollout

| Phase | Timeline | Product |
|-------|----------|---------|
| 1 | Month 1-6 | Manual 90-day scorecard (post-study check-in) |
| 2 | Month 6-12 | Lightweight pricing signal feed (Ring 1 + 2) |
| 3 | Month 12-18 | Smart alerts + drift detection + competitor monitoring (all rings) |
| 4 | Month 18-24 | Full automated loop + A/B test design engine + scenario simulator |

---

## 5. Analysis Modules (Code Mapping)

### CBC Pipeline

| Module | File | Key Class |
|--------|------|-----------|
| Market Simulator | `analysis/simulator.py` | `MarketSimulator` |
| Pricing | `analysis/pricing.py` | `PricingAnalyzer` |
| Tier Design | `analysis/tiers.py` | `TierDesigner` |
| Price Change | `analysis/price_change.py` | `PriceChangeAnalyzer` |
| Competitive | `analysis/competitive.py` | `DiversionAnalysis`, `OptimalProductDesign` |
| Launch | `analysis/launch.py` | `ProductLaunchSimulator` |
| Segments | `analysis/segments.py` | Preference-based clustering |

### RCT Pipeline

| Module | File | Key Class |
|--------|------|-----------|
| ATE Estimation | `experimental/ate.py` | `ATEEstimator` (statsmodels OLS + HC3) |
| HTE Estimation | `experimental/hte.py` | `HTEEstimator` (econml CausalForestDML) |
| Price Change (RCT) | `analysis/price_change.py` | `RCTPriceChangeAnalyzer` |
| Competitive (RCT) | `analysis/competitive.py` | `RCTCompetitiveAnalyzer` |
| Launch (RCT) | `analysis/launch.py` | `RCTLaunchAnalyzer` |

### Shared

| Module | File | Key Class |
|--------|------|-----------|
| MNL Estimation | `estimation/mnl.py` | `fit_mnl()` (scipy L-BFGS-B) |
| WTP | `estimation/wtp.py` | `compute_wtp()` (delta method + Krinsky-Robb) |
| AMCE | `estimation/amce.py` | `compute_amce()` (3 inference methods) |
| SSR | `core/ssr.py` | Semantic similarity rating (Maier et al. 2025) |
| Design | `conjoint/design.py` | `DOptimalDesigner` |
| Vignettes | `experimental/vignette.py` | `VignetteEngine` |
| Charts | `viz/charts.py` | 8 chart types, all return `(fig, chart_data)` |

---

## 6. Reporting Standards

### Universal Rules

1. **Finding-as-title pattern** — "Revenue peaks at $106/mo" not "Demand Curve"
2. **Three-layer depth** — Executive (1-page SCQA callouts), Manager (charts + findings), Technical (appendix with coefficients)
3. **Always report AMCE alongside MNL** — AMCE is the safety net when MNL doesn't converge
4. **Always include confidence intervals** on WTP (delta method) and ATE (HC3)
5. **Demand curves show revenue overlay** — max share != max revenue
6. **Revenue = "preference shares"** — label clearly, not absolute market share predictions
7. **Auto-generated recommendations** — Do Now / Explore / Monitor, computed from data

### Chart Types

| Deliverable | Chart Type |
|-------------|-----------|
| Feature Importance | Horizontal bar chart, sorted descending |
| WTP | Bar chart with currency values + CI whiskers |
| AMCE | Forest plot (coefficients with CIs, reference line at 0) |
| Demand Curve | Line chart with optimal price marker + revenue overlay |
| Segments | Cluster cards + heatmap |
| Treatment Effects (ATE) | Forest plot with significance coloring |
| HTE Segments | Grouped bar chart of CATEs by segment x arm |

---

## 7. Section Visibility Matrix

| Section | Pricing (CBC) | Tier Design (RCT) | Price Change (CBC) | Price Change (RCT) | Competitive (CBC) | Competitive (RCT) | Launch (CBC) | Launch (RCT) | Model Selection (RCT) |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Feature Importance | x | x | | | | | | | |
| WTP | x | x | x | | | | | | |
| AMCE Detail | x | x | x | | x | | x | | |
| Demand Curve | x | | x | | | | | | |
| Tier Optimization | | x | | | | | | | |
| Competitive | | | | | x | x | x | x | |
| Segments | x | x | | | x | | | | |
| Treatment Effects (ATE) | | | | x | | x | | x | x |
| HTE (causal forests) | | | | x | | x | | x | x |
| Recommendations | x | x | x | x | x | x | x | x | x |

---

## 8. Case Study Log

| # | Client/Study | Type | Key Finding |
|---|-------------|------|-------------|
| 1 | Notion | tier_design | Value ratios most intuitive metric for stakeholders |
| 2 | Grammarly | pricing + price_change | Price cuts would increase revenue — currently above optimal |
| 3 | Canva | pricing | Never include $0 in price levels (quality signaling artifact) |
| 4 | Spotify | competitive | Diversion ratios reveal competitive structure better than shares |
| 5 | BeeSignal (self) | pricing | Deliverables dominate (38% importance); contract commitment universally negative WTP |
| 6 | BeeSignal (self) | pricing_model | Per-study model preferred over subscription |
| 7 | Peec.ai | tier_design | "Tracked prompts" is #1 driver of tier selection |
| 8 | Mangalitza | validation | Certification WTP matched (738 vs 682 HUF/kg); culturally specific preferences missed |

### Validation Results

| Study | AMCE r | WTP r | Lesson |
|-------|--------|-------|--------|
| Wine (Maier et al.) | 0.631 | — | Persona realism is everything |
| Copyright (Kantorowicz et al.) | 0.916 | — | Abstract policy domains work well |
| Mangalitza (Balogh et al.) | 0.257 | 0.611 | LLMs miss culturally specific preferences |

---

*Last updated: March 2026*
*Synthesized from: PRODUCT.md (original), POSITIONING_EVOLUTION.md, CONTINUOUS_PRICING_INTELLIGENCE.md, beesignal-build-roadmap.md*
*Updated March 2026: aligned with COMMERCIAL.md vocabulary (Continuous Pricing Intelligence, demand cycle naming, no "dashboard", spell out willingness to pay).*
