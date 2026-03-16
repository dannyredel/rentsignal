# RentSignal — Project Brief
## Origin: Big Berlin Hack (April 2026) | Buena Track | Solo Build

*Note: This is the founding project brief. For current product strategy, see `PRODUCT.md`. For positioning, see `POSITIONING-EVOLUTION.md`. For marketing, see `MARKETING.md`. The problem statement, Q&A prep, pitch narrative, and BeeSignal connection in this doc remain the canonical references.*

---

## Problem

**Who:** German landlords (private and small-scale) and property managers who manage 5–200 units, including firms being acquired/digitized by Buena.

**Pain:** Setting the right rent in Germany is a legal minefield with real financial consequences on both sides:

1. **Pricing too high** — Violates the Mietpreisbremse (rent brake). Tenants can retroactively demand repayment. ~50% of rental contracts in Germany are technically unlawful, and 83% of expat contracts exceed legal limits. Landlords face financial and legal risk they often don't know about.
2. **Pricing too low** — Leaving money on the table within legal bounds. The Mietspiegel gives a *range*, not a number. A landlord charging €10.50/m² when their legal max is €13.20/m² is losing €2,700/year on a 75m² apartment — and doesn't know it.
3. **Modernization blind spots** — "Should I renovate the kitchen or add a balcony?" Nobody can answer this with data. The actual causal effect of a renovation is confounded by selection bias (nicer buildings get renovated). Landlords fly blind on investment decisions worth tens of thousands of euros.
4. **Location quality is a black box** — The Mietspiegel uses coarse neighborhood categories. But two streets apart can differ dramatically in green space, noise, transit access, and construction activity. These hyper-local spatial signals drive willingness-to-pay but are invisible in the current system.

**Current hack:** Landlords google "Mietspiegel [city]," struggle with the official calculator, or copy neighboring rents. Property managers use spreadsheets. Nobody runs a proper analysis that combines legal compliance, market prediction, spatial intelligence, and renovation ROI.

**Why solvable now:**
- LLMs (Gemini) can analyze apartment photos AND satellite imagery to extract features
- ML models outperform traditional hedonic regression on rent prediction
- Causal ML techniques (DML, matching) enable credible renovation impact estimation
- Geospatial AI can extract neighborhood quality signals from satellite/aerial imagery at scale

---

## Competitive Landscape — What Already Exists (and What Doesn't)

### Existing Tools

| Tool | What it does | Who it serves | What's missing |
|------|-------------|---------------|---------------|
| **Official Berlin Mietspiegel Rechner** (mietspiegel.berlin.de) | Government calculator. Looks up legal comparative rent range by building year, size, location, amenities. The legal reference standard. | Tenants + landlords | Gives a range, not a recommendation. No market prediction. Confusing UX. German only. No renovation analysis. No spatial intelligence. |
| **Conny / wenigermiete.de** | Legal-tech platform. Calculates if rent exceeds Mietpreisbremse, then enforces reduction via lawyers for a success-based commission (~3 months of savings). | Tenants only | Tenant-side only — no landlord optimization. Has been criticized for structurally incorrect Mietspiegel calculations. No market intelligence, no renovation ROI, no spatial features. |
| **ImmoScout24 Mietspiegel** | Germany's largest real estate portal. Shows average asking rents by district and apartment type. Based on 6B+ listing data points. | General public | Aggregated district averages, not apartment-specific. Not the qualified Mietspiegel — can't be used for legal compliance. Informational only. |
| **Immowelt Mietpreisrechner** | Rent calculator based on Immowelt listing data. Considers size, equipment, location. More current than Mietspiegel data. | Landlords | Uses listing data (more current) but explicitly states it can't replace the legal Mietspiegel. No decomposition, no what-if analysis, no spatial layer. |
| **Miet-check / Wohnungsbörse / Miete-aktuell** | Various aggregator sites showing average €/m² per district, sometimes with historical trends. | General public | Pure aggregation. Not apartment-specific. No legal layer. No intelligence. Dashboard displays only. |

### The White Space — What Nobody Does

1. **Market prediction + legal compliance in one tool.** You either get a legal calculator (Mietspiegel Rechner, Conny) OR a market estimate (ImmoScout, Immowelt). Nobody combines both to answer: "your legal max is X, the market will bear Y, here's where to price."
2. **Renovation ROI simulation.** Zero tools answer "should I renovate the kitchen or the bathroom?" with data. Completely unserved.
3. **Spatial intelligence from satellite/aerial imagery.** Nobody extracts neighborhood quality features from imagery. All tools use coarse district-level or Mietspiegel zone categories.
4. **Feature-level price decomposition.** Nobody shows WHY an apartment is worth what it is — which feature adds how much. SHAP waterfall is entirely novel in this space.
5. **Landlord optimization (vs. tenant protection).** Conny is tenant-side. The official calculator is neutral. Nobody explicitly helps landlords optimize within legal bounds.
6. **Causal counterfactual analysis.** Nobody handles the "what if I change X" question with proper causal identification. This is the deepest technical moat.

**RentSignal fills all six gaps in a single product.**

### Positioning Statement (for pitch)
"Existing tools give you either legal compliance OR market averages. RentSignal gives you both — plus spatial intelligence, feature-level price decomposition, and renovation simulations with causal inference. It's the first rent optimization engine that treats pricing as an analytical problem, not a lookup."

---

## Target User Persona

**Name:** Thomas
**Role:** Private landlord, owns 3 apartments in Berlin (Kreuzberg, Wedding, Lichtenberg). Day job is in consulting.
**Goal:** Maximize rental income without legal risk, make smart renovation decisions
**Pain:** He knows the Mietpreisbremse exists but has never calculated his legal maximum. He suspects one apartment is underpriced and another might be over the limit. He's been thinking about renovating the Wedding apartment but has no idea if it's worth it.
**Trigger moment:** His tenant in Kreuzberg moves out. He needs to set rent for the new listing. The online Mietspiegel calculator confused him last time.

---

## Solution

### UVP

**For the pitch (Before-After):**
"Before: you guess your rent, risk violating the Mietpreisbremse, and have no idea if renovations are worth it. After: you see your exact legal maximum, where your apartment sits in the market based on satellite-derived neighborhood intelligence, and which renovations give the highest rent uplift per euro — backed by causal inference, not guesswork."

**For the README (technical):**
"RentSignal combines Mietpreisbremse compliance checking with ML-powered rent prediction, satellite-derived spatial features, and dual-method renovation impact estimation (observational matching + synthetic conjoint). Four layers: XGBoost for prediction accuracy, SHAP for explainability, causal matching for observational treatment effects, and BeeSignal-style conjoint simulation for WTP estimation. No existing Berlin rent tool offers any of these capabilities."

---

## The Three-Layer Architecture

This is the intellectual core of the project. Each layer uses the right tool for the right job.

### Layer 1 — PREDICT: "What is this apartment worth?"
**Method:** XGBoost (gradient-boosted trees)
**Why not linear hedonic:** Captures nonlinearities (5th-floor premium doesn't scale linearly), interactions (balcony matters more in Prenzlauer Berg than Marzahn), and complex spatial patterns automatically. Better out-of-sample prediction accuracy.
**Features:**
- Standard: m², building year, floor, amenities (balcony, elevator, fitted kitchen, etc.)
- Mietspiegel category variables (equipment level, residential area class)
- **Spatial features from satellite imagery** (see below)

**Output:** Predicted market rent (€/m²) with prediction interval.

### Layer 2 — EXPLAIN: "Why is it worth that?"
**Method:** SHAP values (SHapley Additive exPlanations)
**Why:** The landlord needs to understand the decomposition — not just "€12.40" but "location contributes +€2.80, building age costs you -€1.20, no balcony costs -€0.60, above-average green space adds +€0.35."
**Output:** Waterfall chart showing each feature's contribution to the predicted rent. Visual, intuitive, actionable.

**Honest framing:** SHAP decomposes the *prediction*, not the *causal effect*. It tells you what drives the model's estimate for this apartment, not what would happen if you changed a feature. That's Layer 3.

### Layer 3 — SIMULATE: "What if I renovate?"

This layer uses two complementary estimation approaches to triangulate renovation impact. Each addresses different identification challenges.

#### Approach A — Observational: Matching on Observables

**Method:** Propensity score matching / nearest-neighbor matching + partial linear model (DML-lite)
**When it works:** When you have enough comparable apartments in the listing data that vary on the renovation variable while being similar on confounders.
**Identification assumption:** Selection on observables (conditional independence) — after matching on building year, neighborhood, size, floor, and other amenities, remaining variation in renovation status is as-if random.

**Approach:**
1. Match the target apartment to comparable units (same building year bracket, same neighborhood tier, similar size, same floor range) that differ only on the renovation variable
2. Estimate the conditional average treatment effect (CATE) of the renovation
3. Combine with the legal ceiling shift (§559 BGB: max 8% of modernization cost added to annual rent, capped at €2-3/m² over 6 years)

**Strengths:** Uses real market data, captures actual revealed preferences.
**Weaknesses:** Selection on observables may not hold (unobservable landlord quality, building condition). Limited by data availability — some renovation types may have too few comparable pairs.

#### Approach B — Simulated Conjoint: Synthetic WTP Estimation (BeeSignal Method)

**Method:** AI-powered conjoint analysis with synthetic respondent profiles, calibrated to market data.
**When it works:** When observational identification is weak — small sample of comparables, likely unobserved confounders, or renovation types rarely observed in data.
**Identification:** Comes from the experimental design of the conjoint itself, not from observational variation. Sidesteps selection bias entirely.

**How it works:**
1. **Define apartment profiles:** Create conjoint-style choice sets varying the renovation attribute (e.g., "same apartment with/without modern kitchen, at different price points")
2. **Generate synthetic tenant profiles:** Using LLM + market calibration, create synthetic tenant personas with realistic preference distributions — income level, family status, location preferences, feature sensitivity. Calibrate to known Berlin rental market demographics (e.g., average household income by district, tenant composition data from IBB Wohnungsmarktbericht).
3. **Run conjoint simulation:** Each synthetic tenant evaluates the apartment profiles and makes a choice. Aggregate across N synthetic tenants (e.g., 1,000) to estimate the WTP distribution for the renovation feature.
4. **Extract WTP and price sensitivity:** The conjoint yields a marginal WTP for each renovation type, plus the demand curve — "at €1.50/m² premium, 70% of tenants prefer the renovated unit; at €2.50/m², only 35% do."

**Strengths:** Clean identification from experimental design. Works even when observational data is sparse. Produces demand curves, not just point estimates. Directly connects to BeeSignal's methodology.
**Weaknesses:** Relies on calibration quality — synthetic preferences are only as good as the market data they're anchored to. Judges may question "fake respondents" — need to frame clearly.

#### Dual-Method Convergence (The Killer Demo Moment)

In the demo, show BOTH estimates side by side for the same renovation:

"Our observational estimate based on 847 matched Berlin apartments: kitchen renovation uplift = +€1.30/m² (CI: €0.80–€1.70).
Our synthetic conjoint simulation calibrated to Berlin tenant demographics: kitchen renovation WTP = +€1.40/m² (CI: €0.95–€1.85).
The estimates converge — landlords can invest with confidence."

When both methods agree, it's powerful validation. When they disagree, it reveals where selection bias matters — which is itself an insight.

**For the pitch:** *"We validate renovation estimates two ways: from real market data using causal matching, and from simulated preference data using conjoint analysis. When both methods agree, you invest with confidence. When they disagree, we tell you why — and that's even more valuable."*

#### Combined Output per Renovation Scenario:
- Legal ceiling shift (deterministic, from Mietpreisbremse §559 BGB rules)
- Observational WTP uplift (CATE from matching, with confidence interval)
- Simulated WTP uplift (conjoint estimate, with confidence interval)
- Convergence indicator (green if methods agree within CI overlap, amber if divergent)
- Effective uplift = min(legal ceiling shift, average of both WTP estimates) — because you can't charge above the law
- Payback period = renovation cost ÷ (effective monthly uplift × 12)
- Demand curve snippet: "At this price point, estimated X% of prospective tenants would prefer the renovated unit"

#### Production-Grade Upgrades (mention in Q&A):
- **Diff-in-diff with Buena's longitudinal data:** Track the same apartments before and after renovation against matched controls. This is the gold standard for causal identification.
- **Double/Debiased ML (Chernozhukov et al., 2018):** Use ML to flexibly control confounders while estimating the treatment effect with valid inference.
- **Real conjoint surveys:** Replace synthetic respondents with actual tenant survey data to calibrate preferences directly.
- **Heterogeneous treatment effects:** CATE by neighborhood — a kitchen renovation has different WTP in Mitte vs. Marzahn. The model can estimate this heterogeneity.

---

## The Spatial Intelligence Layer (Your Differentiator)

This is what makes RentSignal unique — nobody else at the hackathon will have this.

### What it does:
Feed Gemini satellite/aerial imagery of a Berlin neighborhood and extract quantitative spatial features that the Mietspiegel doesn't capture:

| Feature | How extracted | Why it matters for rent |
|---------|-------------|----------------------|
| Green space ratio | Vegetation index from satellite/aerial imagery | Higher green space → higher WTP, especially in dense areas |
| Building density | Built-up area ratio from aerial view | Very high density → noise/crowding discount |
| Construction activity | Detection of cranes, scaffolding, new construction | Proxy for gentrification → future price appreciation |
| Transit proximity | Distance to U-Bahn/S-Bahn stations (from map data) | Major rent driver, nonlinear (diminishing returns past 500m) |
| Commercial density | Shops, restaurants, cafes per street segment | Walkability/amenity score → WTP premium |
| Street-level quality | Gemini analysis of street-view imagery — trees, condition, cleanliness | Micro-location quality invisible to Mietspiegel categories |

### How it enters the model:
These spatial features become covariates in the XGBoost model alongside traditional apartment features. The hypothesis: adding spatial features significantly improves prediction accuracy over Mietspiegel categories alone.

If confirmed, this demonstrates that the current system underprices location quality — a direct insight for Buena, who manages 60,000+ units and needs granular location intelligence.

### Demo implementation:
- Pre-compute spatial features for 5-10 Berlin neighborhoods (Kreuzberg, Wedding, Prenzlauer Berg, Lichtenberg, Mitte, etc.)
- Use Google Maps Static API or pre-downloaded satellite tiles
- Gemini multimodal extracts features from the imagery
- Features are cached and fed into the model in real-time during the demo

### What to say in the pitch:
"The Mietspiegel says Kreuzberg is 'good residential area.' But two blocks apart, the green space ratio varies from 0.15 to 0.45, and our model shows that's worth €0.80/m². We use Gemini's multimodal capabilities to extract these spatial signals from satellite imagery — turning every neighborhood into a quantified feature set that the current system ignores."

---

## Infrastructure Partner Integration

### Google DeepMind (Gemini) — CORE
1. **Satellite/aerial imagery → spatial features** (multimodal vision, primary integration)
2. **Apartment photo → amenity extraction** (upload a photo, Gemini identifies: kitchen age, flooring type, bathroom condition, window quality)
3. **Natural language → structured features** ("2-room Altbau in Kreuzberg, wooden floors, no elevator" → Mietspiegel categories)

### Lovable — FRONTEND
- Full React frontend from prompts
- Supabase integration for demo apartment data
- One-click deploy to Vercel
- SHAP waterfall chart visualization

### Gradium — VOICE INTERFACE
- Voice-powered apartment description: landlord speaks apartment details, Gradium STT transcribes in German, Gemini extracts features, model runs prediction
- "Walk-through mode": describe the apartment as you walk through it, features accumulate in real-time
- Demo moment: speak into the mic in German, watch the rent estimate update live

### Entire — BUILD PROCESS
- Use Entire CLI during the hackathon to track AI-assisted development
- Mention in pitch: "We used Entire to capture our development process — you can see the full reasoning chain"
- Shows awareness of the partner ecosystem even for tools that aren't product-facing

**Partner score:** 4/4 infrastructure partners integrated (3 in the product, 1 in the build process). Maximum impression.

---

## One Feature (MVP)

**The one feature:** Apartment-level rent optimization with spatial intelligence and renovation simulator.

**User flow:**
1. User inputs apartment details (address/neighborhood, size, year, floor, amenities) — via form, natural language, OR voice
2. Gemini extracts satellite-derived spatial features for the neighborhood
3. XGBoost predicts market rent; SHAP decomposes the prediction
4. Mietpreisbremse engine calculates legal ceiling
5. User sees: market estimate, legal max, gap, feature decomposition
6. User toggles renovation scenarios → causal estimator shows impact + ROI

**The wow moment:**
Landlord inputs a Wedding apartment. RentSignal shows: "Your legal max is €11.90/m². Market prediction: €10.80/m². But our satellite analysis shows your block has a green space ratio of 0.42 (above Berlin median) and active construction 200m away — gentrification signal. Your apartment is underpriced by ~€0.70/m²."

Then they toggle "modernize kitchen" → "Legal ceiling shifts to €13.10/m². Market WTP uplift: €1.30/m² (CI: €0.80–€1.70). Effective uplift: €1.20/m². Payback: 54 months. Compare: 'add balcony' → ceiling shift €0.40/m², market uplift €0.50/m², payback: 312 months. **Don't build the balcony.**"

---

## MVP Scope

### ✅ BUILD:
- Apartment input form (neighborhood selector, size, year, amenities checklist)
- Voice input via Gradium (German STT → feature extraction)
- Satellite spatial feature extraction via Gemini (pre-computed for demo neighborhoods)
- XGBoost rent prediction with SHAP waterfall visualization
- Mietpreisbremse legal maximum calculation
- Rent gap visualization (legal max vs. market estimate vs. current rent)
- Renovation impact simulator (toggle 4-5 types, see causal uplift + payback)

### ⏳ NICE TO HAVE (after hour 16):
- Apartment photo upload → Gemini amenity extraction
- Portfolio view for multiple apartments
- Neighborhood comparison map
- Export: rent justification letter

### ❌ CUT:
- User authentication
- Real Mietspiegel API integration (use simplified model)
- Tenant-facing features / PDF generation
- Mobile responsive / multi-city support
- Settings / preferences

### Demo Data Strategy:
5 pre-loaded Berlin apartments:
- **Kreuzberg Altbau** (underpriced — show revenue opportunity + spatial green space premium)
- **Wedding Altbau** (renovation ROI analysis star — "kitchen yes, balcony no")
- **Mitte Neubau** (correctly priced — model confirms, shows Mietpreisbremse exemption for post-2014)
- **Lichtenberg Plattenbau** (overpriced — compliance risk flagged, spatial features show limited amenity access)
- **Prenzlauer Berg renovated** (show how modernization shifted the Mietspiegel category + gentrification signal from satellite)

Pre-computed spatial features for each neighborhood. Pre-trained XGBoost on Berlin rental listing dataset.

---

## Screens

### Screen 1: Apartment Input
**Hero element:** Clean form with Berlin neighborhood map selector
**Components:** Address/neighborhood, m² slider, building year, floor, amenity toggles
**Alternative inputs:** "Describe in natural language" text box, "Speak" button (Gradium)
**Pre-loaded demo:** 5 clickable apartment cards for instant demo

### Screen 2: Rent Analysis Dashboard
**Hero element:** Three-number comparison — Legal Max | Market Estimate | Current Rent
**Left panel:**
- Compliance indicator (green/amber/red)
- Revenue gap ("You could charge €X more" or "You're €X over the legal limit")
**Center panel:**
- SHAP waterfall chart showing feature decomposition (the explainability layer)
- Satellite-derived features highlighted with a different color in the waterfall
**Right panel:**
- Neighborhood spatial card: satellite thumbnail + extracted features (green space %, density, transit score, construction activity)

### Screen 3: Renovation Simulator
**Hero element:** Toggle switches for 5 renovation types
**Per renovation:**
- Legal ceiling shift (deterministic bar)
- Dual WTP estimates side by side: observational CATE (blue) + conjoint WTP (teal) with CI bars
- Convergence badge: green checkmark if CIs overlap, amber warning if divergent
- Effective uplift and payback period
**Chart:** Cumulative cash flow comparison across renovation options over 10 years
**Detail panel:** Click a renovation to see: demand curve from conjoint ("at +€1.50/m², 70% of tenants prefer this; at +€2.50, only 35% do")
**Highlight:** Best ROI renovation has a visual badge, worst ROI has a warning

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Frontend** | Lovable → React + Tailwind | Solo build, fast generation, Supabase connector |
| **Backend** | FastAPI (Python) | ML model + spatial processing run in Python |
| **AI — Spatial** | Gemini API (multimodal) | Satellite image → spatial features extraction |
| **AI — NLP** | Gemini API (text) | Natural language apartment description → structured features |
| **Voice** | Gradium API (STT) | German speech → text for voice input mode |
| **ML — Prediction** | XGBoost (scikit-learn) | Best accuracy for tabular rent data |
| **ML — Explainability** | SHAP | Feature decomposition waterfall charts |
| **ML — Causal (Obs.)** | Matching + partial linear model | Observational renovation treatment effect estimation |
| **ML — Causal (Sim.)** | Synthetic conjoint engine | BeeSignal-method WTP estimation with calibrated synthetic tenants |
| **Database** | Supabase | Demo apartments + Berlin reference data |
| **Hosting** | Railway (API) + Vercel (frontend) | Quick deploy, free tier |
| **Dev tracking** | Entire CLI | Capture AI-assisted build process |
| **Pitch deck** | Gamma.app | Professional slides, fast iteration |

---

## Prize Strategy

**Primary target:** Buena track — "Prosperity through Property"
- Frame: "RentSignal helps your property managers set compliant, optimized rents across 60,000+ units — with spatial intelligence no competitor has."

**Secondary target:** Google DeepMind infrastructure prize
- Frame: "We use Gemini's multimodal capabilities to extract neighborhood quality signals from satellite imagery — a novel spatial AI pipeline that outperforms traditional location categories."

**Dual-prize framing:** Same project, emphasize different layers for each prize. Buena judges see the property management value; Google judges see the multimodal AI innovation.

---

## Pitch Narrative Arc (3 minutes)

**[0:00–0:15] HOOK**
"Half of all rental contracts in Germany are illegal. Not because landlords are malicious — because the system is so complex that most people get it wrong. And the ones who get it right? They're still leaving thousands on the table."

**[0:15–0:45] PROBLEM**
"If you charge too much, your tenant can retroactively reclaim the difference. If you charge too little, you're losing real money. And if you're thinking about renovating — good luck. The Mietspiegel tells you a range, but nobody tells you where in that range to price. And nobody can tell you whether that kitchen renovation will actually pay for itself."

**[0:45–1:00] INSIGHT**
"The data exists — in market listings, in building characteristics, and even in satellite imagery of your neighborhood. The problem isn't data. It's that nobody has combined it into a single, intelligent system."

**[1:00–2:15] DEMO**
"Let me show you. Here's a typical Wedding apartment... [input details, or speak them via Gradium]. The model says: legal max €11.90, market estimate €10.80. But look at the spatial analysis — [show satellite card] — your block has above-average green space and active construction nearby. Our model captures this; the Mietspiegel doesn't.

Now watch what happens when I toggle 'modernize kitchen'... legal ceiling jumps to €13.10. And here's where it gets interesting — we estimate the market impact two ways. Our observational model, matching against 847 comparable Berlin apartments, says +€1.30/m². Our synthetic conjoint simulation, using calibrated tenant preferences, says +€1.40/m². The estimates converge — you can invest with confidence. Payback: 54 months.

But toggle 'add balcony' instead... both methods agree it's barely worth anything. Payback: 312 months. Don't build the balcony.

Under the hood: XGBoost for prediction, SHAP for explainability, and dual causal estimation — observational matching plus simulated conjoint — for the renovation counterfactuals. Four layers, each with the right tool for the job."

**[2:15–2:40] IMPACT**
"Germany has 23 million rental apartments. Property management is a €13.6 billion industry. For a company like Buena managing 60,000 units, this analysis at portfolio scale translates directly to revenue optimization and compliance risk reduction."

**[2:40–2:55] TECH**
"We built this with Gemini for spatial and multimodal intelligence, Gradium for voice input, Lovable for the frontend, and Entire to track our build process. Four partner integrations, built solo in 24 hours."

**[2:55–3:00] CLOSE**
"RentSignal: the rent optimization engine that sees what the Mietspiegel can't. Thank you."

---

## Q&A Preparation

**Q: "Is the hedonic model causal?"**
A: "Deliberately not — the prediction layer uses XGBoost for accuracy, not causal claims. The causal estimation lives in the renovation simulator, where we use two complementary approaches: observational matching that estimates treatment effects from real market data, and synthetic conjoint simulation that estimates WTP from an experimental design. When both methods converge, you can trust the estimate. In production with Buena's longitudinal data, we'd upgrade to diff-in-diff or Double/Debiased ML for even cleaner identification."

**Q: "How do you handle the selection bias in renovation effects?"**
A: "That's exactly why we use two methods. The observational approach uses matching on observables — finding like-for-like apartments that differ only on the renovation. This handles selection IF the matching covariates capture the relevant confounders. The synthetic conjoint sidesteps selection entirely — it estimates WTP from an experimental design with calibrated synthetic tenants. Together, they triangulate the true effect. If they disagree, we flag it and explain which assumptions are driving the divergence."

**Q: "Aren't the synthetic conjoint respondents just... fake?"**
A: "The respondents are synthetic, but the preferences are calibrated to real data. We anchor the preference distributions to Berlin rental market demographics — income levels by district, tenant composition from the IBB Wohnungsmarktbericht, observed price elasticities from listing data. This is the same methodology used in marketing science for conjoint analysis when running a real survey isn't feasible. The key is calibration quality, and we're transparent about that."

**Q: "How is this different from the Mietspiegel Rechner or Conny?"**
A: "The Mietspiegel Rechner gives you a legal range — it doesn't tell you where in that range to price, or whether a renovation is worth it. Conny helps tenants reclaim overcharges — it's a legal enforcement tool, not an optimization engine. Nobody combines legal compliance, ML-based market prediction, satellite spatial intelligence, price decomposition, and renovation counterfactuals in one tool. We fill six gaps that no existing tool addresses."

**Q: "How accurate is the satellite feature extraction?"**
A: "For the demo, we validate Gemini's spatial feature extraction against known ground truth — official Berlin green space data, construction permits. The key insight is that even approximate spatial features improve prediction accuracy over coarse Mietspiegel categories. The signal is real; the measurement can be refined."

**Q: "Isn't this just a calculator?"**
A: "The compliance check is a calculator. But the ML prediction with satellite features, the SHAP decomposition, and the dual-method renovation simulator — that's four layers of intelligence that go far beyond what any calculator offers. Immowelt and ImmoScout give you averages. Conny gives you legal enforcement. We give you optimization."

**Q: "What about data privacy? Satellite imagery of neighborhoods?"**
A: "We use publicly available satellite/aerial imagery and extract aggregate features — green space ratio, building density. No individual identification, no personal data. The spatial features are neighborhood-level covariates, same as the Mietspiegel's 'residential area' classification but more granular."

**Q: "How would this work at scale with Buena?"**
A: "Buena manages 60,000+ units. At scale, the spatial features are pre-computed per neighborhood tile and cached. The ML model re-trains quarterly on new listing data. The renovation simulator improves dramatically with Buena's internal data — they can observe actual rent changes pre/post renovation across their portfolio, which is the diff-in-diff panel data we need for truly causal identification. And the synthetic conjoint gets calibrated to real tenant preferences from Buena's applicant data."

**Q: "What if the Mietspiegel changes?"**
A: "The compliance engine is a modular rules layer — updating it for a new Mietspiegel release is a configuration change, not a model retrain. The ML prediction layer adapts automatically as new listing data comes in."

**Q: "Why XGBoost and not a linear hedonic model?"**
A: "For prediction accuracy, XGBoost outperforms linear hedonic regression on rental data because it captures nonlinearities — the 5th-floor premium doesn't scale linearly — and interactions — a balcony matters more in Prenzlauer Berg than in Marzahn. We use SHAP to recover the interpretability that a linear model gives you for free. Best of both worlds: ML accuracy with hedonic-style decomposition."

---

## Risk Flags & Mitigations

1. **"It's just a calculator"** → Mitigation: the satellite layer and SHAP visualization immediately show it's not. Lead the demo with the spatial insight, not the compliance check.

2. **Mietspiegel data simplification** → Mitigation: use simplified but realistic model based on public Berlin listing data. Acknowledge: "For production, we'd integrate the official qualified Mietspiegel."

3. **Satellite feature extraction quality** → Mitigation: pre-compute and validate before the hackathon. Show known ground truth comparison in demo.

4. **Solo build ambition** → Mitigation: strict scope control. Lovable handles frontend. Pre-train the model. Pre-compute spatial features. Your hackathon time is spent on integration and demo polish, not building from scratch.

5. **Voice input reliability** → Mitigation: have it as a demo bonus, not the primary input path. If Gradium's German STT hiccups, the form input works perfectly. Show voice as a "look what's also possible" moment.

---

## Pre-Hackathon Prep Checklist

### Data & Models (do before the event)
- [ ] Download/scrape Berlin rental listing dataset (ImmoScout24 historical, public Kaggle datasets, or similar)
- [ ] Feature-engineer Mietspiegel-relevant variables from the data
- [ ] Train XGBoost model, validate prediction accuracy, save the model artifact
- [ ] Compute SHAP values for demo apartments, verify the waterfall chart makes sense
- [ ] Build the matching estimator for renovation treatment effects on the training data
- [ ] Map §559 BGB modernization rent increase rules into a rules engine

### Synthetic Conjoint Engine (do before the event)
- [ ] Design apartment profile conjoint: define attributes (kitchen quality, bathroom, balcony, flooring, heating) and levels
- [ ] Build synthetic tenant profile generator: define demographic distributions calibrated to Berlin data (IBB Wohnungsmarktbericht — income by district, household size, age distribution)
- [ ] Implement conjoint simulation engine: synthetic tenants evaluate apartment profiles, aggregate to WTP estimates
- [ ] Calibrate synthetic preferences to match observed rental market patterns (sanity check: do the synthetic WTP estimates roughly align with market price differentials?)
- [ ] Pre-compute conjoint results for the 5 demo renovation scenarios
- [ ] Build the convergence visualization: observational CATE vs. conjoint WTP side-by-side with CI overlap indicator

### Spatial Layer (do before the event)
- [ ] Download satellite/aerial tiles for 5-10 Berlin neighborhoods
- [ ] Test Gemini multimodal on satellite imagery → spatial feature extraction prompts
- [ ] Validate extracted features against known ground truth (Berlin Umweltatlas green space data, OSM transit data)
- [ ] Pre-compute and cache spatial features for demo neighborhoods
- [ ] Prepare one compelling side-by-side: "Mietspiegel says X, satellite says Y, and Y is more accurate"

### Infrastructure Partners (do before the event)
- [ ] Get Gemini API key, test multimodal endpoints
- [ ] Get Gradium API key, test German STT with apartment descriptions
- [ ] Test Lovable with a sample dashboard prompt
- [ ] Install Entire CLI, verify it captures sessions correctly
- [ ] Prepare Lovable prompt for the three screens (input, dashboard, renovation simulator)

### Pitch & Demo (do before the event)
- [ ] Prepare 5 demo apartments with realistic Berlin attributes
- [ ] Write 3 compelling demo narratives (one underpriced, one overpriced, one renovation analysis)
- [ ] Draft Gamma slide content using Pitch Content Generator framework
- [ ] Record backup demo video
- [ ] Read up on Buena's product to nail the integration angle in Q&A

### Tech Setup (do before the event)
- [ ] Set up GitHub repo with FastAPI boilerplate
- [ ] Test Railway deployment for the API
- [ ] Test Supabase for demo data storage
- [ ] Prepare .env.example with all API keys

---

## Competitive Intelligence & Stolen Ideas

### Key Competitors Analyzed

**Rentana (US, $5M seed):** AI rent optimization for US multifamily. Dynamic pricing, Copilot with explained recommendations, amenity-level pricing, portfolio dashboards. No regulatory compliance layer — US doesn't need one. No spatial features.

**Predium (Munich, €13M Series A):** ESG management for real estate using AI, satellite imagery, and 3D models. Energy performance analysis, renovation roadmaps with subsidy calculations, CSRD reporting. Institutional clients (Deutsche Investment, Colliers). No rent optimization, no pricing intelligence.

**Conny / wenigermiete (Berlin, legal-tech):** Tenant-side Mietpreisbremse enforcement. Free calculator → auto-generated legal complaint letters → lawyer escalation. Success-based fee (5-6× monthly savings). Despite claiming "modernste Algorithmen," their tech is a rules engine with template letters. Has been documented to systematically miscalculate Mietspiegel ranges. Moat is legal infrastructure, not technology.

### Positioning
"Conny tells tenants they're overpaying. Rentana optimizes for the US free market. Predium handles ESG for institutional investors. RentSignal is the first platform that combines compliance, market intelligence, spatial analytics, and ESG for German property managers."

### Prioritized Feature Roadmap (Stolen + Original)

#### HACKATHON CORE (build this)
| Feature | Stolen from | Our edge |
|---------|-------------|----------|
| SHAP-powered "why" explanations | Rentana Copilot | Grounded in econometric decomposition, not black-box |
| Amenity-level WTP via conjoint | Rentana amenity pricing | Causal identification, not just correlation |
| Mietpreisbremse compliance check | Conny (improved) | More accurate — implements qualified Mietspiegel correctly |
| Photo-based apartment classification | Fixes Conny's tenant self-classification problem | Gemini vision replaces 30-50 manual questions |
| Satellite spatial features | Predium's satellite approach (different outputs) | Rent-relevant features, not ESG metrics |
| Dual-method renovation simulator | Original (matching + conjoint) | Nobody does this anywhere |
| Confidence intervals (not point estimates) | Fixes Conny's overestimation bias | Builds trust, under-promise/over-deliver |
| Free tier as growth engine | Conny's viral calculator mechanic | But for landlords, not just tenants |

#### POST-HACKATHON P1 (build in weeks 1-4 after event)
| Feature | Source | Value |
|---------|--------|-------|
| Energy class as model feature | Predium EPC parsing | Improves rent prediction + enables ESG angle |
| CO2 cost-sharing calculator | German CO2KostAufG regulation | Shows landlords hidden cost of inefficient buildings |
| KfW subsidy integration in renovation ROI | Predium subsidy calculation | Dramatically changes payback periods ("without subsidy: 90 months, with KfW: 52 months") |
| Market comp benchmarking dashboard | Rentana public market intelligence | "Your apartment vs. similar listings in your PLZ" in real time |
| English language support | Conny's expat accessibility | Berlin has ~1M foreign residents, 83% of expat contracts are illegal |
| Rent justification letter generation | Conny letter automation (flipped for landlords) | Auto-generate legally compliant Mieterhöhungsverlangen |

#### POST-HACKATHON P2 (build in months 2-3)
| Feature | Source | Value |
|---------|--------|-------|
| Portfolio-level dashboard | Rentana portfolio view | Enterprise feature for Buena-scale clients |
| Vacancy/churn prediction | Rentana lease expiration management | "If you raise rent by X, probability tenant leaves is Y%" |
| ESG risk scoring per building | Predium stranding risk | Which buildings will lose value from non-compliance |
| Nebenkostenabrechnung anomaly detection | Conny's adjacent service | Upload utility bill, AI flags overcharges |
| Tenant-side compliance check | Conny's core product (rebuilt better) | Same tool, tenant-facing version, with accurate calculations |
| Lease expiration strategy | Rentana renewal optimization | Adapted for German context: when to invoke Staffelmiete steps |

#### LONG-TERM P3 (months 4-12, product maturity)
| Feature | Source | Value |
|---------|--------|-------|
| Automated CSRD/ESG reporting | Predium reporting | Enterprise compliance requirement, high willingness to pay |
| 3D building model integration | Predium 3D models | Building condition assessment from imagery |
| Buy/renovate/sell decision engine | Predium transaction support | "10-year NPV for each scenario" |
| Multi-city expansion | Original | Same engine, different Mietspiegel. Hamburg, Munich, Frankfurt |
| European expansion | Original | Austria, Switzerland, Netherlands — all have rent regulation |

### ESG Expansion — Why It's Nearly Free

The satellite pipeline we build for rent optimization (Sentinel-2 NDVI, Gemini aerial analysis, Umweltatlas data) is the SAME infrastructure Predium uses for ESG analysis. Adding ESG outputs requires:
1. Adding energy class as an XGBoost feature (one column in the dataset)
2. A CO2 cost-sharing rules engine (simple lookup table based on building energy class)
3. KfW subsidy lookup in the renovation simulator (another lookup table)
4. A Gemini prompt variant that assesses building envelope quality from the same aerial images

Predium raised €13M for ESG alone. We deliver rent optimization AND ESG intelligence from the same pipeline. That's the post-hackathon expansion story.

---

## Revenue Model

*See `PRODUCT.md` §6 for current tier structure and §15 for revenue projections.*

### Current Pricing (updated 2026-03-16)
| Tier | Target | Price | Units |
|------|--------|-------|-------|
| Free | Small landlords (1-3 units) | €0 | Max 3 |
| Pro | Professional landlords (5-15 units) | €29/month | Max 15 |
| Business | Property managers (15-500 units) | €99/month or €2/unit/month | Unlimited |
| Enterprise | Large managers + platforms (500+) | Custom (min €500/month) | Unlimited |

### TAM/SAM/SOM
- **TAM (Germany):** 23M rental apartments × €3/unit/month = **€828M/year**
- **SAM:** ~5M units in firms actively digitizing = **€180M/year**
- **SOM (Year 2):** 190k units = **€6.7M/year** (0.8% market penetration)
- **European expansion:** Austria, Netherlands, France, Sweden = **TAM €2B+**

---

## BeeSignal Connection — The Bigger Picture

RentSignal is not just a hackathon project. It's a vertical proof-of-concept for BeeSignal's core methodology applied to real estate.

### What transfers from BeeSignal:
- **Synthetic conjoint engine** — Same AI-powered WTP estimation, different domain. PriceShift did it for SaaS pricing; RentSignal does it for apartment features.
- **Causal pricing intelligence** — The dual-method approach (observational + simulated) is the BeeSignal philosophy: don't guess what a price change will do, estimate it with rigor.
- **Feature-level price decomposition** — SHAP waterfall for apartments is the same concept as showing which SaaS features drive WTP.

### What's new (and feeds back to BeeSignal):
- **Regulatory constraint layer** — The Mietpreisbremse ceiling creates a constrained optimization problem (maximize revenue subject to legal bounds) that generalizes to any regulated market (energy, healthcare, financial products).
- **Spatial intelligence from satellite** — Novel data source that could apply to any location-dependent pricing problem (retail site selection, logistics, insurance risk by geography).
- **The "convergence" framing** — Showing two independent methods agreeing is a trust mechanism that works universally.

### Post-hackathon path:
1. **LinkedIn content:** "We built an AI rent optimizer at a hackathon — here's what we learned about causal pricing in regulated markets" (fits BeeSignal content calendar)
2. **BeeSignal product:** The synthetic conjoint engine built for RentSignal becomes a reusable module in BeeSignal's toolkit
3. **Vertical expansion narrative:** "BeeSignal started in SaaS pricing. We've proven the methodology in real estate. Next: insurance, energy, financial products."

---

## Competitive Moat Summary

| Capability | Mietspiegel Rechner | Conny | ImmoScout24 | Rentana (US) | Predium | **RentSignal** |
|-----------|---------------------|-------|-------------|-------------|---------|---------------|
| Legal max calculation | ✅ Range | ✅ + enforcement | ❌ | ❌ | ❌ | ✅ Point estimate |
| Market rent prediction | ❌ | ❌ | ⚠️ Averages | ✅ Dynamic | ❌ | ✅ ML per apartment |
| Feature decomposition (WHY) | ❌ | ❌ | ❌ | ⚠️ Basic | ❌ | ✅ SHAP waterfall |
| Renovation ROI simulation | ❌ | ❌ | ❌ | ❌ | ✅ ESG only | ✅ Rent + ESG, dual-method causal |
| Spatial satellite intelligence | ❌ | ❌ | ❌ | ❌ | ✅ ESG focus | ✅ Rent + ESG features |
| Voice input | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Gradium German STT |
| Demand curve / WTP analysis | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Synthetic conjoint |
| ESG/energy scoring | ❌ | ❌ | ❌ | ❌ | ✅ Core | ⚠️ Expansion path (same pipeline) |
| Subsidy integration (KfW) | ❌ | ❌ | ❌ | ❌ | ✅ | ⚠️ Post-hackathon P1 |
| Landlord optimization | ⚠️ Neutral | ❌ Tenant-only | ⚠️ Neutral | ✅ | ⚠️ Investor-facing | ✅ Core purpose |
| German regulatory compliance | ✅ | ✅ | ❌ | ❌ (US only) | ❌ | ✅ |
| Portfolio dashboard | ❌ | ❌ | ❌ | ✅ | ✅ | ⚠️ Enterprise tier |

**RentSignal is the only product that combines compliance + market ML + spatial + causal renovation analysis. Nobody does all four, in any market.**

**The expansion thesis:** Adding ESG (P1 post-hackathon) makes RentSignal = "Rentana + Predium for the German regulated market." That's a €20M+ story from a single platform.
