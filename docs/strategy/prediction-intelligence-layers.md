# Prediction Intelligence — Three Layers
## Beyond Point Estimates: Intervals, Feature WTP, and Segment Demand

> Saved 2026-03-20. Implements on top of v4.2 model (R²=0.761, 75 features).

---

## Layer 1: Prediction Intervals — "What's the plausible range?"

**Method:** Conformal Prediction via MAPIE library (model-agnostic, guaranteed coverage).

**Why conformal over quantile regression:**
- Distribution-free (no Gaussian assumption)
- Wraps existing XGBoost without retraining
- Statistically valid coverage guarantee (e.g., "80% of true rents fall within this range")
- Backed by 2024 Springer paper on automated valuation model uncertainty

**Implementation:**
```python
from mapie.regression import MapieRegressor
mapie = MapieRegressor(model, method="plus", cv=5)
mapie.fit(X_train, y_train)
pred, intervals = mapie.predict(X_new, alpha=0.2)  # 80% interval
```

**Frontend display:**
```
Predicted rent: €15.20/m²
├─ 80% range: €12.40 – €18.60
├─ 50% range: €14.20 – €16.80 (most likely)
└─ Monthly: €960 – €1,395
```

**Interpretation for users:** "We're 80% confident the market rent is between €12.40 and €18.60/m². Your current rent of €22/m² is above even the upper bound — strong evidence of overpricing."

---

## Layer 2: SHAP as "What Each Feature is Worth" (Marginal WTP)

**Econometric basis:** SHAP values are the non-linear, heterogeneous equivalent of hedonic price coefficients (Rosen 1974). In a hedonic model, β_kitchen IS the marginal WTP for a kitchen. In XGBoost + SHAP, SHAP_kitchen is the same thing but non-parametric and instance-specific.

**Current display:** Technical waterfall chart (SHAP values as bars).

**Proposed display:** Actionable feature-value table alongside the waterfall:

```
Feature              You have    Worth         Insight
──────────────────────────────────────────────────────────
Fitted Kitchen       ✅ Yes      +€1.14/m²     "Adds €85/mo to your rent"
Balcony              ✅ Yes      +€0.32/m²     "Modest premium in this area"
Elevator             ❌ No       -€0.45/m²     "Missing €34/mo potential"
Central Location     ✅ 3.7km    +€0.95/m²     "Top 30% centrality in Berlin"
Renovation Level     ⚠️ Default  -€0.65/m²     "Upload photos for accurate score"
```

**Key reframing:** Not "SHAP value = 1.14" but "Your kitchen is worth €85/month in this apartment." Translates technical output into money language that property managers understand.

---

## Layer 3: Segment WTP — "Who Values This Apartment Most?"

**Method:** Combine XGBoost market prediction with BeeSignal conjoint persona utility weights.

**The insight:** The XGBoost gives the MARKET equilibrium price (what the average tenant pays). The conjoint decomposes demand by SEGMENT (what each tenant type WOULD pay based on their preferences).

```
Market prediction (XGBoost): €15.20/m²

Segment WTP breakdown:
├─ Young Professional    €17.50/m²  (+€2.30 above market)
├─ Expat                 €16.90/m²  (+€1.70)
├─ Senior                €14.10/m²  (-€1.10)
├─ Family                €13.80/m²  (-€1.40)
├─ Student               €11.20/m²  (-€4.00)
```

**Strategic value:**
- "Target young professionals for this unit — they'd pay €2.30/m² above market"
- Feeds directly into portfolio optimization: match tenants to units by segment
- The difference between segment WTP and market price = pricing opportunity

**Implementation:**
1. Conjoint utility weights per persona × apartment features → segment WTP
2. Existing BeeSignal conjoint already has 6 Berlin persona segments
3. Validate convergence: conjoint WTP vs matching CATE on 2026 data

**Dependencies:**
- Re-run matching estimator on 2026 data (update CATE)
- Validate conjoint utility weights still hold (preferences stable, only price levels change)

---

## Build Order

1. **Layer 1: Conformal prediction intervals** (~1h) → notebook 23
2. **Layer 2: SHAP as feature WTP table** (~1h) → backend + Lovable prompt
3. **Re-run matching on 2026 data** (~2h) → notebook (update CATE)
4. **Layer 3: Segment WTP integration** (~2h) → after matching validates conjoint

---

## References

- Rosen, S. (1974). "Hedonic Prices and Implicit Markets." JPE. — Foundation for SHAP-as-WTP interpretation
- Springer (2024). "Towards a Better Uncertainty Quantification in AVMs" — Conformal + quantile ensemble for property valuation
- März (2019). "XGBoostLSS — Probabilistic Forecasting" — Distributional XGBoost alternative
- Angelopoulos & Bates (2021). "A Gentle Introduction to Conformal Prediction" — MAPIE theoretical basis
- Lundberg & Lee (2017). "A Unified Approach to Interpreting Model Predictions" — SHAP framework
