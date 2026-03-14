# MietOptimal — Pre-Hackathon Prep Roadmap
## Prioritized by dependency chain and risk

---

## Your Starting Position

| Asset | Status | Notes |
|-------|--------|-------|
| BeeSignal conjoint engine (CBC + RCT) | ✅ Working | Needs calibration for property/rental context |
| Python / FastAPI skills | ✅ Ready | Your strongest stack |
| Spatial analytics / remote sensing | ✅ Ready | Need to apply to Berlin specifically |
| XGBoost / SHAP experience | ✅ Ready | Standard tooling |
| Berlin rental listing data | ❌ Need to source | Critical dependency |
| Satellite/aerial imagery for Berlin | ❌ Need to source | Can use Google Maps Static API |
| Gemini API access | ❌ Need to set up | Free tier available |
| Gradium API access | ❌ Need to set up | Free tier available |
| Lovable account | ❌ Need to set up | Free tier for testing |
| Entire CLI | ❌ Need to install | Quick setup |

---

## Priority Tiers

### 🔴 P0 — BLOCKING (do these first — everything else depends on them)

#### Task 1: Source Berlin rental listing data
**Time estimate:** 2-3 hours
**Why P0:** The XGBoost model, the matching estimator, AND the conjoint calibration all depend on having real listing data. Without this, you can't build anything.

**Options (try in order):**
1. **Kaggle Berlin datasets** — Search for "Berlin rental" or "ImmoScout24". There are several scraped datasets with apartment features and prices.
2. **OpenImmo / public data portals** — Berlin Open Data (daten.berlin.de) has housing-related datasets. Check for rental price surveys.
3. **Web scraping ImmoScout24/Immowelt** — Last resort. Use Firecrawl or a simple Python scraper. Note: ImmoScout may block. Consider using their API if available.
4. **Fallback: generate synthetic listing data** — If you can't get real data in time, generate a realistic synthetic dataset calibrated to known Berlin rent statistics (average €13.11/m² in Q1 2026, variation by district from ImmoScout published stats). This is less impressive but functional.

**Minimum viable dataset:** 1,000+ listings with: neighborhood/district, m², building year, floor, number of rooms, amenities (balcony, elevator, fitted kitchen, central heating, etc.), Kaltmiete (cold rent).

**Deliverable:** Clean CSV/parquet file with Berlin apartment listings, features, and rents. Saved to project repo.

---

#### Task 2: Train XGBoost rent prediction model
**Time estimate:** 3-4 hours (after Task 1)
**Why P0:** This is the core "Layer 1 — PREDICT" engine. Every other layer builds on top of it.

**Steps:**
1. Load listing data, clean and feature-engineer
2. Create Mietspiegel-relevant features: building year brackets, district dummies, amenity binary flags
3. Split train/test (80/20), train XGBoost with hyperparameter tuning (grid search over max_depth, n_estimators, learning_rate)
4. Evaluate: RMSE, MAE, R² on test set. Compare to a simple linear model to quantify the nonlinearity advantage.
5. Compute SHAP values on test set. Generate waterfall plots for 5 demo apartments. Verify they make intuitive sense.
6. Save: model artifact (.joblib), SHAP explainer, scaler/encoder objects

**Deliverable:** Trained model + SHAP explainer + evaluation metrics saved to repo. Model should achieve R² > 0.7 on test data (Berlin rental data is noisy, so don't expect 0.95).

---

### 🟡 P1 — HIGH PRIORITY (do these next — major differentiators)

#### Task 3: Calibrate BeeSignal conjoint for rental context
**Time estimate:** 3-4 hours
**Why P1:** This is the "Approach B" of your renovation simulator and the BeeSignal connection. Since the engine already works, this is mostly configuration.

**Steps:**
1. **Define apartment attributes and levels for conjoint:**
   - Kitchen quality: basic (pre-1990) / standard (1990-2010) / modern (post-2010) / premium
   - Bathroom: basic / modernized / premium
   - Flooring: laminate / parquet / premium hardwood
   - Balcony: none / small / large
   - Energy rating: poor (pre-insulation) / average / good (post-renovation)
   
2. **Define synthetic tenant personas calibrated to Berlin:**
   - Use IBB Wohnungsmarktbericht data for calibration:
     - Income distribution by district (Wedding ≠ Mitte)
     - Household composition (single, couple, family)
     - Age distribution
     - Tenure type (long-term resident vs. new arrival vs. expat)
   - Each persona has a utility function over apartment attributes with noise
   - Price sensitivity parameter calibrated to observed rent elasticities in listing data
   
3. **Run conjoint simulation on demo apartments:**
   - Generate WTP estimates for each renovation type
   - Produce demand curves ("at +€X/m², Y% of tenants prefer renovated")
   - Sanity check: do estimates roughly align with observed price differentials in the listing data?

4. **Build convergence comparison:**
   - For each renovation type, compute both the observational matching CATE (from Task 2 data) and the conjoint WTP estimate
   - Visualize side-by-side with CI bars and convergence indicator

**Deliverable:** Conjoint config file, synthetic tenant generator calibrated to Berlin, pre-computed WTP estimates for 5 renovation scenarios on 5 demo apartments, convergence comparison data.

---

#### Task 4: Spatial feature extraction pipeline
**Time estimate:** 3-4 hours
**Why P1:** This is your unique differentiator and the core Gemini integration.

**Steps:**
1. **Get Gemini API key** — Sign up at ai.google.dev, get free tier access
2. **Download satellite/aerial tiles for demo neighborhoods:**
   - Use Google Maps Static API (satellite view) for 5 Berlin locations: Kreuzberg, Wedding, Prenzlauer Berg, Lichtenberg, Mitte
   - Download at zoom level ~16-17 (neighborhood scale, ~250m tiles)
   - Also grab street-level imagery if possible
   
3. **Build Gemini spatial extraction prompt:**
   - Design a structured output prompt that takes a satellite image and returns:
     ```json
     {
       "green_space_ratio": 0.35,
       "building_density": 0.72,
       "construction_activity": false,
       "visible_cranes": 0,
       "tree_coverage": "moderate",
       "building_condition": "mixed",
       "street_width": "medium",
       "commercial_presence": "low"
     }
     ```
   - Test on 5+ tiles, iterate on prompt until outputs are consistent and sensible
   
4. **Validate against ground truth:**
   - Berlin Umweltatlas (umweltatlas.berlin.de) has official green space data
   - OpenStreetMap has transit station locations and commercial POIs
   - Compare Gemini-extracted features to official data. Compute correlation.
   - Prepare one slide-ready comparison: "Gemini says green_space = 0.38, official data says 0.41 — strong correlation"
   
5. **Pre-compute and cache for demo neighborhoods:**
   - Store spatial features as JSON per neighborhood tile
   - These get loaded into the model at demo time — no live API calls for spatial during the pitch

**Deliverable:** Satellite tiles for 5 neighborhoods, validated spatial features JSON, Gemini prompt template, ground truth comparison data.

---

#### Task 5: Build Mietpreisbremse compliance engine
**Time estimate:** 2 hours
**Why P1:** Straightforward rules engine, but needed for the "three-number dashboard" (legal max vs. market vs. current).

**Steps:**
1. Implement the legal calculation:
   - Input: building year, district, size, amenities
   - Lookup ortsübliche Vergleichsmiete from simplified Mietspiegel table
   - Apply +10% cap for Mietpreisbremse areas
   - Handle exceptions: post-2014 new builds (exempt), comprehensive modernization (exempt)
   
2. Implement §559 BGB renovation rules:
   - Max 8% of modernization cost added to annual rent
   - Cap: €2/m² increase within 6 years (for rents up to €7/m²), €3/m² otherwise
   - This feeds into the "legal ceiling shift" number in the renovation simulator

3. Use simplified Mietspiegel reference table — you don't need the full 200-page document, just the major bands:
   - Building year brackets × residential area class × equipment level → reference rent range
   - Can extract from the official Mietspiegel PDF or approximate from public sources

**Deliverable:** Python module: `compliance.py` with functions `get_legal_max(apartment_features)` and `get_renovation_ceiling_shift(renovation_type, renovation_cost, current_rent)`.

---

### 🟢 P2 — IMPORTANT (do these if time allows — they make the demo shine)

#### Task 6: Build matching estimator for observational CATE
**Time estimate:** 2 hours (after Tasks 1-2)
**Why P2:** "Approach A" of the renovation simulator. If you have the conjoint already (Task 3), this is the complementary estimate.

**Steps:**
1. From the listing dataset, create binary treatment variables: has_modern_kitchen (yes/no), has_balcony (yes/no), etc.
2. Implement nearest-neighbor matching: for each treated apartment, find 3-5 nearest untreated neighbors on covariates (building year, district, size, floor)
3. Estimate ATE and CATE with bootstrap confidence intervals
4. Compare to conjoint estimates — prepare convergence visualization

**Deliverable:** Matching estimator function + pre-computed treatment effects for 5 renovation types.

---

#### Task 7: Set up infrastructure partner accounts
**Time estimate:** 1-2 hours total
**Why P2:** Quick wins, but don't need deep testing until closer to the event.

- [ ] **Gradium:** Sign up at gradium.ai, get API key, test German STT with one apartment description (10 minutes)
- [ ] **Lovable:** Create account, test generating a simple dashboard from a prompt (30 minutes)
- [ ] **Entire:** `brew install entireio/tap/entire`, run `entire enable` in your project repo (10 minutes)
- [ ] **Supabase:** Create project, set up a demo apartments table, test connection (20 minutes)

**Deliverable:** All API keys in .env file, basic connectivity tested.

---

#### Task 8: Prepare demo apartments and narratives
**Time estimate:** 2 hours
**Why P2:** This is what makes the pitch land. Do it after the model is trained so you can use real predictions.

**5 demo apartments:**

| Name | Neighborhood | Story | Demo purpose |
|------|-------------|-------|-------------|
| "Thomas's Altbau" | Kreuzberg | 75m², 1968, no balcony, basic kitchen. Tenant just moved out. | Underpriced — show revenue opportunity + spatial green space premium |
| "The Wedding Dilemma" | Wedding | 60m², 1975, ground floor, needs renovation. | Renovation ROI star — "kitchen yes, balcony no" + dual-method convergence |
| "Marina's Neubau" | Mitte | 45m², 2018, modern everything. | Correctly priced — model confirms. Shows Mietpreisbremse exemption for post-2014 |
| "The Plattenbau" | Lichtenberg | 55m², 1980, unrenovated DDR-era block. | Overpriced — compliance risk flagged. Spatial features show limited amenity access |
| "Prenzlauer Gold" | Prenzlauer Berg | 80m², 1910 renovated in 2019, full amenities. | Show how modernization shifted category + gentrification satellite signal |

For each, prepare:
- Input features (exact values for the form)
- Expected model output (prediction, SHAP top factors, compliance status)
- Demo narrative (2-3 sentences of what you say while showing this apartment)
- The "insight moment" (what surprised the landlord)

**Deliverable:** Demo data JSON file with 5 apartments, pre-computed outputs, and speaker notes.

---

#### Task 9: Draft pitch deck content (Gamma-ready)
**Time estimate:** 1.5 hours
**Why P2:** Can be done at the hackathon too, but having a draft saves 30+ minutes under pressure.

Follow the Pitch Content Generator framework from the project brief:
- 7-8 slides: Title → Problem → Insight → Demo → How it Works → Impact → Team → Close
- Paste into Gamma for auto-design
- Font recommendation: Space Grotesk (headings) + Inter (body) — Modern Tech palette
- Color: #1a1a2e primary, #00d4aa accent (Fintech/Pricing palette from the skill)

**Deliverable:** Gamma-ready text file with slide content and speaker notes.

---

### ⚪ P3 — NICE TO HAVE (only if everything above is done)

#### Task 10: Test Lovable end-to-end with full prompt
**Time estimate:** 1-2 hours
**Why P3:** You'll be doing this at the hackathon anyway, but a test run de-risks it.

Write the full Lovable prompt for all 3 screens. Generate the app. Note what Lovable gets wrong and what you need to manually fix. This becomes your "known issues" list for hackathon day.

#### Task 11: Record backup demo video
**Time estimate:** 30 minutes (after everything else works)
**Why P3:** Insurance against live demo failure. Screen-record yourself clicking through the app with narration.

#### Task 12: Prepare "what we'd do with Buena's data" slide
**Time estimate:** 30 minutes
**Why P3:** For Q&A. Shows you've thought about the production path: diff-in-diff with their longitudinal data, real conjoint surveys with their tenant applicant pool, spatial features at portfolio scale.

---

## Dependency Graph

```
Task 1 (data) ──────┬──→ Task 2 (XGBoost + SHAP)
                     │        │
                     │        ├──→ Task 6 (matching CATE)
                     │        │         │
                     │        │         ├──→ Task 8 (demo apartments)
                     │        │         │         │
                     │        │         │         └──→ Task 9 (pitch deck)
                     │        │         │                  │
                     │        │         │                  └──→ Task 11 (backup video)
                     │        │
                     ├──→ Task 3 (conjoint calibration) ──→ Task 6 (convergence)
                     │
Task 4 (spatial) ────┤  [independent — can run in parallel]
                     │
Task 5 (compliance) ─┘  [independent — can run in parallel]

Task 7 (accounts) ──────→ [independent, do anytime]
Task 10 (Lovable test) ──→ [depends on knowing what the screens look like]
Task 12 (Buena slide) ──→ [depends on nothing, do anytime]
```

---

## Suggested Schedule

**Assuming hackathon is ~1-2 weeks away:**

### Week 1: Foundation (critical path)

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|-----------|
| Day 1 | Task 1 (source data) + Task 7 (accounts setup) | 3-4h | 4h |
| Day 2 | Task 2 (train XGBoost + SHAP) | 3-4h | 8h |
| Day 3 | Task 3 (calibrate conjoint for Berlin) | 3-4h | 12h |
| Day 4 | Task 4 (spatial pipeline + Gemini testing) | 3-4h | 16h |
| Day 5 | Task 5 (compliance engine) + Task 6 (matching CATE) | 3-4h | 20h |

### Week 2: Polish (make it demo-ready)

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|-----------|
| Day 6 | Task 8 (demo apartments + narratives) | 2h | 22h |
| Day 7 | Task 9 (pitch deck draft) + Task 10 (Lovable test) | 2-3h | 25h |
| Day 8 | Buffer / fix issues found in testing | 2h | 27h |
| Eve of hackathon | Task 12 (Buena slide) + final check all APIs work | 1h | 28h |

**Total pre-hackathon prep: ~28 hours across 8-10 sessions**

---

## What You Build AT the Hackathon (with all prep done)

| Hour | Activity |
|------|----------|
| 0-1 | Opening, matchmaking, scope confirmation |
| 1-2 | FastAPI backend: wire XGBoost model + compliance engine + conjoint as API endpoints |
| 2-4 | Lovable: generate frontend from prepared prompt, connect to Supabase |
| 4-6 | Integration: connect frontend → backend API, test full flow |
| 6-8 | Gemini integration: spatial features displayed in UI, voice input with Gradium |
| 8-10 | Demo data: load 5 apartments, verify all outputs look right |
| 10-14 | Polish: fix bugs, improve UI, test edge cases |
| 14-16 | Feature freeze. Generate Gamma pitch deck. |
| 16-18 | Rehearse pitch 2x. Record backup video. |
| 18-20 | Final polish, deploy, submit |
| 20+ | Present |

With prep done, the hackathon itself is primarily **integration and polish** — not building from scratch. That's how a solo builder wins.
