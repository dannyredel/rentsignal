# RentSignal Feature Specs v2
## Next Build Sprint — Property Manager Intelligence Features

> Created: 2026-03-20. Build target: next session.
> All features use existing data, models, and infrastructure. No new data collection required.

---

## Feature 1: URL Wizard (Paste & Predict)

**Pain point:** Property managers waste time manually entering apartment details. Most listings already exist on ImmoScout24.

**User flow:**
```
1. User pastes: https://immobilienscout24.de/expose/166409657
2. Backend scrapes listing data (address, sqm, rooms, amenities, photos)
3. Backend auto-fills form + geocodes address + runs Gemini on photos
4. User reviews pre-filled form, edits if needed
5. Click "Analyze" → full 75-feature prediction with image features
```

**Technical approach:**
- New endpoint: `POST /listing/import` accepts ImmoScout24 URL
- Scrape listing via Apify single-expose scraper or direct HTTP (same structure as batch scrape)
- Extract from `adTargetingParameters` (same as notebook 13 pipeline)
- Download photos → Gemini analysis (same as notebook 19 pipeline)
- Return pre-filled `ApartmentInput` + `gemini_features` + `nlp_features`
- Frontend: new "Paste URL" tab on the Add Unit page

**Validation:** Our Apify scraper already extracts this exact data structure. The only new part is single-listing scraping instead of batch.

**Implementation options:**
- **Option A (recommended): Apify actor** — call same ImmoScout scraper with single URL. ~€0.01/scrape, reliable, ~10 sec. We already have Apify set up.
- **Option B: Direct HTTP scrape** — parse listing page HTML/JSON. Free but fragile, risk of IP blocking.
- **Option C: Hybrid** — try direct scrape first, fall back to Apify if blocked.

**Effort:** ~4h (backend endpoint + frontend tab)

**Reference:** [AI for Rental Properties 2025](https://www.styldod.com/blog/ai-for-rental-properties) — "AI can automatically assess property value, analyze trends, and forecast demand instead of relying on manual research."

---

## Feature 2: Mieterhöhung Calculator (Rent Increase Wizard)

**Pain point:** Property managers don't know the maximum legal rent increase for each unit. The calculation involves §558 BGB, Mietspiegel comparison, Kappungsgrenze (15% cap over 3 years), and various exceptions.

**What it computes:**
```
Input: current rent, last increase date, prior increases in 6 years, unit features
Output:
  - Maximum allowable increase: +€1.23/m² (to €9.73/m²)
  - Legal basis: §558 BGB, Kappungsgrenze 15%
  - Mietspiegel comparison: your rent is at 72nd percentile
  - Timeline: eligible for increase after [date]
  - Letter template (§558a BGB formal request)
```

**Technical approach:**
- Backend endpoint already exists: `POST /rent-increase/calculate` (built in notebook 09)
- Logic: `current_rent + min(Kappungsgrenze_cap, Mietspiegel_mid - current_rent)`
- Constrained by: 15% Kappungsgrenze over 3 years, Mietspiegel upper bound
- Add: portfolio-wide view ("which units are eligible for increase NOW?")

**Validation:** §558 BGB is the primary legal framework. [Kautionskasse 2025](https://www.kautionskasse.de/ratgeber/artikel/was-sich-fur-mieter-jetzt-bei-der-nebenkostenabrechnung-andert) confirms ongoing regulatory changes requiring automated tracking.

**Effort:** ~2h (connect existing backend to frontend, add portfolio view)

---

## Feature 3: Portfolio Renovation Optimizer (Budget-Constrained)

**Pain point:** "I have €50K renovation budget. Which units/renovations maximize total portfolio rent uplift?"

**What it computes:**
```
Input: renovation budget (€), portfolio units with current features
Output:
  - Optimal renovation plan:
    "Unit A kitchen (+€261/mo, €15K) → Unit C garden (+€82/mo, €5K) → Unit B elevator (+€130/mo, €45K)"
  - Total uplift: €473/mo = €5,676/yr
  - Budget used: €45K of €50K
  - ROI: 11.4% annual
  - Compare vs naive: "If you just picked top-ROI per unit, you'd get €410/mo — our optimizer finds €473/mo (+15%)"
```

**Technical approach:**
- 0-1 knapsack problem: maximize Σ(CATE_i × sqm_i × 12) subject to Σ(cost_i) ≤ budget
- Items: each (unit, renovation_type) pair that the unit doesn't already have
- Solver: `scipy.optimize.linprog` or `PuLP` for integer programming
- Account for §559 BGB modernization passthrough limits
- Complementarity effects (future): facade renovation increases kitchen ROI

**Validation:** [Knapsack-based portfolio optimization (PLOS ONE)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213652) validates the framework. [Gurobi knapsack guide](https://www.gurobi.com/resources/solving-the-knapsack-problem-a-classic-challenge-in-optimization/) provides implementation reference.

**Effort:** ~3h (optimizer logic + API endpoint + frontend visualization)

---

## Feature 4: Portfolio Health Score

**Pain point:** No single metric tells a property manager "how healthy is my portfolio?"

**Score components (weighted):**

| Component | Weight | Source | Metric |
|-----------|--------|--------|--------|
| Pricing efficiency | 30% | Prediction gap | % of units within 50% PI of market |
| Compliance safety | 25% | Compliance engine | % units compliant + aggregate exposure |
| Renovation opportunity | 20% | CATE estimates | Total unrealized rent uplift |
| Occupancy risk | 15% | Vacancy proxy | Units priced >20% above market |
| Data quality | 10% | Enrichment level | % units with photos, coordinates, full data |

**Output:**
```
Portfolio Health Score: 72/100 (Good)
  ✅ Pricing: 85/100 — most units fairly priced
  ⚠️ Compliance: 45/100 — 3 units at high risk (€26K/yr exposure)
  🔧 Renovation: 78/100 — €5,676/yr unrealized from 2 kitchen renovations
  📊 Occupancy: 90/100 — no units significantly overpriced
  📷 Data quality: 60/100 — 2 units missing photos
```

**Technical approach:**
- Aggregate existing per-unit metrics into weighted composite
- Track score over time (store in Supabase per analysis date)
- Show trend: "Your score improved from 68 to 72 this month"

**Validation:** [NetSuite 2025 real estate metrics](https://www.netsuite.com/portal/resource/articles/business-strategy/real-estate-metrics.shtml) — "Individual metrics are valuable data points, but they become most meaningful when analyzed together to evaluate overall business health." [KRS Holdings KPI guide](https://www.krsholdings.com/articles/kpi-property-management) provides the standard landlord dashboard framework.

**Effort:** ~2h (backend computation + frontend score card)

---

## Feature 5: Comparable Listings

**Pain point:** "How does my unit compare to what's currently on the market?"

**What it shows:**
```
Your unit: 75m², 3R, Kreuzberg, kitchen+balcony, €18.00/m²

5 Most Similar Listings (scraped March 2026):
  1. Oranienstr. 42    72m² 3R  €17.50/m² (listed)  Model: €16.80  → fairly priced
  2. Kottbusser Str. 8  78m² 3R  €19.20/m² (listed)  Model: €17.10  → overpriced
  3. Adalberstr. 15     68m² 2R  €15.80/m² (listed)  Model: €15.40  → fair
  4. Graefestr. 22      80m² 3R  €22.00/m² (listed)  Model: €18.50  → overpriced
  5. Görlitzer Str. 31  70m² 3R  €14.20/m² (listed)  Model: €16.00  → underpriced

  Median comp listing: €17.50/m²  |  Median model prediction: €16.80/m²
  Your position: 68th percentile of comparable listings

  ⚠️ Data freshness: listings scraped March 18, 2026
```

**Technical approach:**
- KNN on feature space: `(plz, livingSpace ±20%, noRooms ±1, building_era)`
- Search across our 8,256-unit database (`units.parquet` + `listings.parquet`)
- Return K=5-10 nearest neighbors with both listed price AND predicted price
- Include data freshness warning (scrape date)
- Future: with more frequent scrapes, show "this listing was active X days ago"

**Both current and predicted prices shown** — current prices answer "what are landlords asking?" and predicted prices answer "what should they be asking?" The gap between the two identifies market mispricing.

**Validation:** [Apartment rent prediction using KNN (arXiv)](https://arxiv.org/pdf/1906.11099) — "rent predictions improve when historical rent data for nearby properties are included using the k-nearest neighbors approach."

**Effort:** ~2h (backend endpoint + frontend comparison table)

---

## Feature 6: Scenario Simulator (Simplified)

**Pain point:** "What happens if I change X? I want to explore options before committing."

**Priority scenarios (based on property manager frequency of use):**

### Scenario A: Rent Adjustment
```
"What if I change the rent from €18 to €X?"
Slider: €10 ────●──── €25

At €18.00: Compliance ⚠️ exceeds max | Market position: 68th pctile | Vacancy risk: Low
At €16.00: Compliance ✅ compliant   | Market position: 45th pctile | Vacancy risk: Very Low
At €20.00: Compliance ⚠️ exceeds max | Market position: 82nd pctile | Vacancy risk: Medium
```

### Scenario B: Renovation Impact
```
"What if I add a kitchen?"
Toggle: Kitchen [ON] → Predicted rent changes from €15.20 to €18.68 (+€3.48/m²)
  Monthly gain: +€261  |  Cost: €15,000  |  Payback: 57 months  |  Legal passthrough: €1.19/m²
```

### Scenario C: Mietspiegel Update
```
"What if the Mietspiegel increases by 5%?"
Your current compliance status: Non-compliant (€9.66 over)
After 5% Mietspiegel increase: Non-compliant (€8.93 over) — exposure drops by €548/yr
After 10% increase: Non-compliant (€8.20 over) — exposure drops by €1,095/yr
```

**Technical approach:**
- Rent slider: re-run compliance check with modified `current_rent_per_sqm`, compute vacancy risk from prediction interval position
- Renovation toggle: use CATE estimates (already in renovation service)
- Mietspiegel update: re-run compliance with scaled Mietspiegel values
- All computations use existing endpoints with modified inputs — no new models needed

**Effort:** ~3h (backend parameter variations + frontend interactive sliders)

---

## Feature 7: Vacancy Duration Prediction (Future — needs 2+ scrapes)

**Pain point:** "How long will my vacant unit sit empty? What can I do to lease faster?"

**Method:** Survival analysis on time-on-market data.

**Approaches (ranked):**
1. **Cox Proportional Hazards** — semi-parametric, most interpretable
2. **Gradient-boosted survival trees** (scikit-survival) — highest accuracy
3. **Kaplan-Meier curves** — non-parametric, good for segment comparisons

**Data requirement:** Minimum 2 scrapes to identify which listings disappeared (leased) vs persisted (still vacant). With quarterly scrapes:
- March 2026 scrape (done): 8,335 listings
- June 2026 scrape (planned): compare → identify leased/persisted
- Duration = days between scrapes for leased units (right-censored for persisted)

**Output:**
```
Your unit: 75m², Kreuzberg, kitchen, balcony, €18/m²
Predicted time to lease: 14 days (median)
  Survival curve: 50% leased by day 14, 80% by day 28, 95% by day 45
  Key factors: price (if lowered to €16 → 8 days), photos (+3 days without)
  Comparable units: median 12-22 days in PLZ 10961
```

**Milestone:** Schedule next Apify scrape for June 2026 → enables survival analysis.

**Validation:** [JLL Germany Housing Market H2 2025](https://www.jll.com/en-de/insights/market-perspectives/germany-living) — "The discrepancy between existing and new contract rents has widened, creating lock-in effects affecting mobility rates."

**Effort:** ~4h (after second scrape is available)

---

## Feature 8: Compliance Risk Scoring (Enhanced)

**Pain point:** "Which of my units are most likely to get a Mietpreisbremse complaint?"

**Risk factors:**
```
Risk Score = f(
  overpayment_amount,       # higher overcharge = higher risk
  district_conny_activity,  # Kreuzberg/Neukölln = Conny is actively advertising there
  tenant_demographics,      # young/expat tenants more aware of rights
  listing_visibility,       # if listing was public, price is documented
  time_since_lease,         # recent leases = fresh complaint window
)
```

**Risk tiers:**
- 🔴 **High** (>70): >€5/m² over max + central district + high Conny activity
- 🟡 **Medium** (40-70): €2-5/m² over max or moderate risk factors
- 🟢 **Low** (<40): <€2/m² over max, suburban, exempt categories

**Uses existing data:** Compliance engine + spatial features (district, food density as urbanization proxy) + prediction intervals.

**Effort:** ~1h (scoring function + frontend risk badges)

---

## Build Priority

| # | Feature | Effort | Impact | Priority |
|---|---------|--------|--------|----------|
| 1 | URL Wizard | 4h | 🔴 High (UX revolution) | **P0** |
| 2 | Mieterhöhung Calculator | 2h | 🔴 High (top PM pain point) | **P0** |
| 3 | Portfolio Renovation Optimizer | 3h | 🟡 High (portfolio value) | **P1** |
| 4 | Portfolio Health Score | 2h | 🟡 Medium (retention) | **P1** |
| 5 | Comparable Listings | 2h | 🟡 High (market context) | **P1** |
| 6 | Scenario Simulator | 3h | 🟡 Medium (engagement) | **P2** |
| 7 | Vacancy Prediction | 4h | 🟡 High (needs 2nd scrape) | **P2** (June) |
| 8 | Compliance Risk Scoring | 1h | 🟡 Medium (enhances existing) | **P1** |

**Recommended build order:** 1 → 2 → 5 → 3 → 8 → 4 → 6 → 7

---

## References

- [NetSuite: 33 Real Estate Metrics 2025](https://www.netsuite.com/portal/resource/articles/business-strategy/real-estate-metrics.shtml)
- [Knapsack Portfolio Optimization (PLOS ONE)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213652)
- [KNN Rent Prediction (arXiv)](https://arxiv.org/pdf/1906.11099)
- [Property Manager Pain Points (Beagle)](https://www.joinbeagle.com/post/10-property-manager-pain-points)
- [Gurobi Knapsack Problem](https://www.gurobi.com/resources/solving-the-knapsack-problem-a-classic-challenge-in-optimization/)
- [AI in Real Estate 2025 (RTS Labs)](https://rtslabs.com/ai-in-real-estate/)
- [JLL Germany Housing Market H2 2025](https://www.jll.com/en-de/insights/market-perspectives/germany-living)
- [Buena €49M raise for property management](https://www.eu-startups.com/2025/07/berlin-based-buena-raises-e49-million-to-digitise-property-management/)
