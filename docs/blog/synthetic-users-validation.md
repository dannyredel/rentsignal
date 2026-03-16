# We Ran the Same Experiment Two Ways. The Results Were 3% Apart.

**How synthetic conjoint with LLM respondents reproduced causal estimates from 10,275 real apartments**

*By Daniel · BeeSignal Research · March 2026*

---

## The Question Nobody Asks

Every pricing and product team runs surveys. Conjoint analysis, MaxDiff, willingness-to-pay studies — the machinery of stated preference research. The unspoken assumption is that what people *say* they'd pay maps to what they *actually* pay.

But does it? And if you replace human respondents with LLM-simulated personas, does that introduce another layer of divergence — or does it somehow cancel out?

We tested this. Not with a toy example, but with a real market: Berlin rental apartments, 10,275 real listings, and 75 synthetic tenants.

The headline result: for kitchen renovations, our observational causal estimate was **+€4.01/m²**. Our synthetic conjoint estimate was **+€4.13/m²**. A 3% difference across two methods that share zero data, zero assumptions, and zero methodology.

---

## The Setup: Two Independent Methods, One Market

We chose the Berlin rental market because it's data-rich, economically significant, and has a clear policy question: *which apartment renovations actually increase rent?*

Property managers in Germany face this constantly. Should they invest €15,000 in a modern kitchen, €8,000 in a balcony, or €40,000 in an elevator? The wrong answer wastes capital. The right answer requires causal reasoning, not just correlation.

### Method A: Observational Matching (Revealed Preference)

We started with 10,275 Berlin apartment listings from ImmoScout24 (2018-2020). Each listing includes the rent per square meter, apartment features (kitchen, balcony, elevator, garden), and confounders (district, building era, living space, floor, condition, interior quality, energy rating).

The naive comparison is tempting: apartments with modern kitchens rent for +€4.02/m² more. But this is confounded — kitchen apartments tend to be newer, in better districts, and better maintained. The raw premium conflates the kitchen effect with everything else.

To isolate the causal effect, we used **propensity score matching (PSM)** — a standard technique in causal inference. For each apartment with a kitchen, we found the most similar apartment *without* a kitchen (matching on all 14 confounders via logit propensity score, 1:1 nearest-neighbor with caliper = 0.2 SD). Then we compared rents within these matched pairs.

![Propensity Score Distributions](../data/processed/ps_distribution_kitchen.png)
*Figure 1: Propensity score distributions for treated (kitchen) and control (no kitchen) apartments. Good overlap in the common support region enables reliable matching.*

The matching quality was strong: all 14 confounders balanced after matching (standardized mean differences < 0.1), meaning our matched pairs are genuinely comparable.

![Love Plot — Balance Diagnostics](../data/processed/love_plot_kitchen.png)
*Figure 2: Love plot showing covariate balance before (red) and after (blue) matching. All confounders fall within the ±0.1 threshold after matching — the gold standard for PSM balance.*

The result: **kitchen renovation CATE = +€2.91/m² (95% CI: €2.65–€3.18)** in 2019 prices. Adjusted for Berlin rent inflation to 2025 (IBB data: median asking rent rose from €11.45 to €15.78/m², a 37.8% increase): **+€4.01/m²**.

We ran the same pipeline for balcony, elevator, and garden access:

![CATE All Treatments](../data/processed/cate_all_treatments.png)
*Figure 3: Causal treatment effects (ATT) for four renovation types, estimated via propensity score matching on 10,275 Berlin listings. Kitchen dominates. Balcony is negative — a surprising but robust finding.*

| Renovation | CATE (2019) | CATE (2025 adj.) | 95% CI | Matched Pairs |
|-----------|-------------|-------------------|--------|---------------|
| Kitchen | +€2.91/m² | +€4.01/m² | [3.65, 4.39] | 2,288 |
| Elevator | +€1.09/m² | +€1.50/m² | [0.98, 1.96] | 3,847 |
| Garden | +€0.93/m² | +€1.27/m² | [0.67, 1.86] | 1,142 |
| Balcony | -€0.72/m² | -€1.00/m² | [-1.48, -0.56] | 1,896 |

*Table 1: Observational CATE estimates for four renovation types. Balcony has a negative causal effect — apartments with balconies rent for less after controlling for all confounders.*

The balcony result is counterintuitive but robust: it survived three different caliper specifications (0.1, 0.2, 0.5 SD) with stable estimates.

![Robustness — Caliper Sensitivity](../data/processed/robustness_caliper.png)
*Figure 4: CATE estimates across three caliper specifications. Kitchen and balcony effects are remarkably stable — the estimates aren't artifacts of matching parameters.*

We also found heterogeneous effects: kitchen renovation adds the most value in older Plattenbau buildings (+€4.47/m²) and the least in post-2003 construction (+€0.29/m²). This makes intuitive sense — a modern kitchen in a 1960s building is a bigger upgrade than one in an already-modern apartment.

![Kitchen CATE by Building Era](../data/processed/cate_kitchen_by_era.png)
*Figure 5: Heterogeneous treatment effects — kitchen CATE by building era. Older buildings benefit dramatically more from kitchen renovation.*

### Method B: Synthetic Conjoint (Stated Preference)

Completely independently, we ran a Choice-Based Conjoint (CBC) study using BeeSignal's synthetic respondent engine. No listing data was used. No matching was performed. The only shared element was the question: *how much more would Berlin tenants pay for a renovated kitchen?*

**Study design:**
- 6 attributes: monthly rent (€900/€1,050/€1,200/€1,350 for 65m²) + kitchen + balcony + elevator + garden + building condition
- D-optimal experimental design (10 choice tasks per respondent, 2 alternatives + none option)
- 2×2 counterbalancing to control for presentation order effects
- Dual-response elicitation for more precise utility estimation

**Respondents:** 75 LLM-simulated Berlin tenant personas across 6 segments, calibrated from IBB Wohnungsmarktbericht 2025 demographics:

| Segment | Weight | Budget (mean) | Price Sensitivity |
|---------|--------|---------------|-------------------|
| Young professional | 35% | €1,000/mo | 35% High |
| Couple, no kids | 20% | €1,300/mo | 20% High |
| Student/early career | 15% | €650/mo | 70% High |
| Expat professional | 15% | €1,400/mo | 15% High |
| Family with kids | 10% | €1,500/mo | 30% High |
| Older renter | 5% | €950/mo | 45% High |

*Table 2: Synthetic persona segments — weighted by actual Berlin apartment-seeker demographics, not general population.*

Each persona was given realistic Berlin-specific traits, pain points, and priorities. The student segment, for example, has experienced "almost everything listed is above budget" and "landlords prefer employed applicants with higher income proof." These are real Berlin rental market dynamics, not generic descriptions.

**Estimation:** Multinomial Logit (MNL) with effects coding. WTP = -β_feature / β_price (delta method CIs).

**Results:**

| Feature | MNL Coefficient | p-value | WTP (€/month) | WTP (€/m²) |
|---------|----------------|---------|---------------|------------|
| Kitchen (renovated) | +1.300 | <0.0001 | +€268/mo | **+€4.13/m²** |
| Condition (well maintained) | +0.649 | <0.0001 | +€134/mo | +€2.06/m² |
| Elevator | +0.444 | <0.0001 | +€92/mo | +€1.41/m² |
| Balcony (small) | +0.318 | 0.0011 | +€66/mo | +€1.01/m² |
| Garden | +0.210 | 0.0554 | +€43/mo | +€0.67/m² |

*Table 3: Synthetic conjoint WTP estimates. Kitchen is the dominant feature, with WTP more than double the next strongest (building condition). Model pseudo-R² = 0.43, all price coefficients negative.*

The model fit is strong (pseudo-R² = 0.43), the price coefficient is correctly negative (-0.0048, p < 0.0001), and the AMCE analysis (a non-parametric safety net) confirms the same ranking.

---

## The Convergence

Here's the money chart:

![Dual-Method Convergence](../data/processed/convergence_cate_vs_wtp.png)
*Figure 6: Side-by-side comparison of observational CATE (blue, from 10,275 real listings) and synthetic conjoint WTP (coral, from 75 LLM respondents). Kitchen estimates are nearly identical. Balcony diverges — and that divergence is the most interesting finding.*

| Feature | CATE (obs., 2025 adj.) | Conjoint WTP | Difference | Direction Match |
|---------|----------------------|--------------|------------|-----------------|
| **Kitchen** | **+€4.01/m²** | **+€4.13/m²** | **3%** | **Yes** |
| Elevator | +€1.50/m² | +€1.41/m² | 6% | Yes |
| Garden | +€1.27/m² | +€0.67/m² | 47% | Yes |
| Balcony | -€1.00/m² | +€1.01/m² | — | **No** |

*Table 4: Dual-method convergence. Kitchen and elevator show remarkable agreement. Garden agrees in direction but differs in magnitude. Balcony diverges — and that's the most informative result.*

Three things to notice:

### 1. Kitchen convergence is extraordinary

+€4.01 vs +€4.13. Two methods, zero shared data, zero shared assumptions, and they land within 3% of each other. The confidence intervals overlap substantially (CATE: [3.65, 4.39], WTP: [2.65, 5.60]).

This is not a coincidence. Both methods are measuring the same underlying economic reality — the marginal value of a modern kitchen in the Berlin rental market — just through different lenses. The observational method captures *revealed preference* (what landlords actually charge and tenants actually pay). The conjoint captures *stated preference* (what tenants say they'd pay in a controlled experiment).

When these converge, it means the stated preferences of our synthetic respondents are economically calibrated to real market dynamics. That's a strong external validity signal.

### 2. Elevator convergence is tight

+€1.50 vs +€1.41 (6% difference). Again, confidence intervals overlap. Elevators have a clear, well-understood utility — mobility, convenience, accessibility — and both methods capture it similarly.

### 3. The balcony divergence is the most interesting finding

The observational data says balconies are associated with **-€1.00/m²** in rent (causal, after matching). The conjoint says tenants would pay **+€1.01/m²** more for a balcony.

This is a textbook **stated-versus-revealed preference gap**, and it's exactly what behavioral economists have documented for decades:

- **Stated preference** (conjoint): Tenants *think* they value balconies. When presented with two apartments side-by-side in a choice task, they prefer the one with the balcony and indicate willingness to pay ~€66/month more for it.

- **Revealed preference** (market data): In practice, apartments with balconies don't command higher rents after controlling for confounders. Why? Several possible mechanisms:
  - **Supply effect:** Balconies are common in Berlin (73% of our sample). Abundant supply depresses the premium.
  - **Selection effect:** Older buildings with balconies may have other unobserved drawbacks (noise exposure, smaller rooms to accommodate the balcony footprint).
  - **Capitalization gap:** Landlords may not price-discriminate on balconies as effectively as on kitchens (which are immediately visible and functional).

This divergence is not a failure of the synthetic conjoint — it's a *feature*. It reveals something that neither method alone could show: **the gap between what tenants say they want and what the market actually prices.** For a property manager deciding where to invest renovation capital, this is critical intelligence: *don't build the balcony*.

---

## What This Means for Synthetic Users

This experiment provides one of the first external validations of LLM-based conjoint against real-world causal estimates. The implications:

**1. Synthetic respondents produce economically meaningful WTP estimates.**
The kitchen WTP from 75 LLM respondents (€4.13/m²) matched the causal estimate from 10,275 real listings (€4.01/m²) to within 3%. This isn't just directionally correct — it's quantitatively precise.

**2. The method correctly captures preference heterogeneity.**
Our 6 persona segments — from budget-constrained students to high-earning expats — produced varied but internally consistent responses. The 58.8% none-option rate (respondents rejecting both apartments) reflects realistic Berlin price sensitivity, especially among student and older renter segments.

**3. Stated/revealed preference gaps appear where theory predicts them.**
The balcony divergence isn't noise — it's a well-documented behavioral phenomenon that the synthetic respondents reproduced faithfully. They *stated* a balcony preference (as real humans would), while the market data *revealed* that this preference doesn't translate to rent premiums.

**4. The approach is fast and cheap.**
The entire synthetic conjoint — design, simulation, estimation — took ~15 minutes and ~$6 in API costs. The observational matching required access to a proprietary listing dataset and several hours of statistical work. For rapid market sizing and feature prioritization, synthetic conjoint offers a compelling cost-benefit ratio, especially when calibrated against market data.

---

## The Three Layers of Rent Estimation

This work demonstrates a hierarchy of increasingly sophisticated rent estimation:

| Layer | Method | What It Measures | Example: Kitchen |
|-------|--------|-----------------|-----------------|
| **Naive** | Mean comparison | Correlation (confounded) | +€4.02/m² |
| **Causal** | Propensity score matching | Revealed preference (causal effect) | +€2.91/m² → +€4.01 adj. |
| **Synthetic** | CBC conjoint with LLM | Stated preference (willingness-to-pay) | +€4.13/m² |

The naive estimate (+€4.02) is close to the causal estimate (+€4.01 adjusted) by coincidence — the confounders approximately cancel in this case. But for other features, naive estimates can be wildly wrong. The naive balcony premium is +€0.42/m², while the causal estimate is -€0.72/m². Trusting the naive number would lead to a bad investment decision.

The synthetic conjoint adds a complementary perspective: it measures what tenants *would* pay in a hypothetical market, unbounded by current supply constraints. When it converges with the causal estimate (kitchen, elevator), we have high confidence. When it diverges (balcony), we've identified a stated/revealed gap worth investigating.

---

## Limitations and Honest Caveats

We're not claiming synthetic conjoint replaces real surveys or real data. Several limitations apply:

- **LLM training data leakage:** GPT-5-mini may have been trained on Berlin rental data, potentially biasing WTP estimates toward "correct" market values. We can't fully rule out this confound, though the persona-level heterogeneity (varying budgets, priorities, pain points) makes direct memorization unlikely.

- **Sample size:** 75 synthetic respondents is below the Orme (2010) minimum of 100 for CBC. Our observations-per-parameter ratio (93.8) is comfortable, but a larger sample would tighten confidence intervals.

- **Single market:** We tested in Berlin, a well-documented rental market. Performance in less-studied markets (smaller German cities, emerging markets) may differ.

- **Inflation adjustment:** Comparing 2019 observational data with 2025 conjoint prices required a blanket 37.8% inflation adjustment. Feature-specific inflation rates may vary.

- **Unobserved confounders:** PSM controls for observed confounders but cannot rule out unobserved ones. Apartments with kitchens may differ in ways not captured by our 14 matching variables.

---

## Try This With Your Product

The convergence we found isn't unique to rental markets. The same dual-method validation can be applied to any pricing or feature prioritization decision:

1. **Run a synthetic conjoint** with BeeSignal to estimate WTP for your features
2. **Compare against observational data** — transaction logs, A/B test results, or market benchmarks
3. **Look for convergence** (validates the synthetic approach) and **divergence** (reveals stated/revealed gaps worth investigating)

The cost is ~$6 and 15 minutes. The alternative — running a traditional conjoint with 300+ human respondents — costs $15,000–50,000 and takes 4–6 weeks.

[Try BeeSignal →](https://beesignal.com)

---

## Technical Appendix

**Observational method:** Propensity Score Matching with logistic regression. 1:1 nearest-neighbor matching on logit propensity score, caliper = 0.2 SD, without replacement. 14 confounders: livingSpace, noRooms, yearConstructed, floor, numberOfFloors, thermalChar, building_era (dummies), bezirk (dummies), condition (ordinal), interiorQual (ordinal), plus other amenities as cross-confounders. Bootstrap 95% CIs (1,000 resamples).

**Synthetic conjoint:** Choice-Based Conjoint with D-optimal design (d-efficiency = 0.30). Effects coding for all non-price attributes. MNL estimation via maximum likelihood (conditional logit). WTP = -β_attribute / β_price with delta method standard errors. AMCE computed as non-parametric robustness check.

**Data:** 10,275 Berlin listings from ImmoScout24 (2018-2020) via Kaggle. Synthetic respondents simulated via GPT-5-mini with BeeSignal's CBC engine (dual-response elicitation, 2×2 counterbalancing).

**Reproducibility:** All code available in Jupyter notebooks. Observational: `06_matching_estimator.ipynb`. Synthetic conjoint: `07_conjoint_wtp.ipynb`.

---

*This research was conducted as part of the RentSignal project — an AI-powered rent optimization engine for the German rental market. Built with [BeeSignal](https://beesignal.com) for synthetic conjoint and open-source tools (scikit-learn, XGBoost, SHAP) for causal inference.*
