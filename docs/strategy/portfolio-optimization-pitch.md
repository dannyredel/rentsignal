# Portfolio Optimization — Pitch & Strategy Notes

## Core Framing

**One-liners (pick per audience):**

| Context | Line |
|---------|------|
| General | "RentSignal: the first tool that prices apartments as a portfolio, not in isolation." |
| Technical | "We don't just tell you what to charge. We tell you which units need to be more different from each other — and how to price the differences." |
| Provocative | "You're competing with yourself and you don't even know it." |
| ROI-focused | "Airlines found 3-7%. Hotels found 2-5%. Property management is still at 0%. Until now." |
| Investor | "Rentana prices units. We optimize portfolios. That's the difference between a tool and a platform." |

**Problem statement:** Every property manager prices each apartment independently — "what's this unit worth?" But when you own 50 units in Neukölln, pricing unit A affects demand for unit B. You're competing with yourself and you don't even know it. And worse — your renovation strategy might be making two units MORE similar instead of more differentiated.

---

## Language We Own

These are concepts we introduce to the proptech vocabulary:

- **"You're competing with yourself"** — the core insight. Multiple units in the same area cannibalize each other's demand.
- **"Portfolio-optimal vs unit-optimal"** — the gap between pricing each unit independently and pricing them as a system. This gap = our value proposition.
- **"Self-cannibalization"** — when your cheap unit steals applicants from your premium unit.
- **"One unit is subsidizing its neighbor"** — the most powerful demo moment. Unit A is underpriced, propping up demand for unit B. Raise A, total portfolio revenue goes up.
- **"Substitution matrix"** — the heatmap showing which of your units compete with which. Visual, intuitive, unique.
- **"Constrained optimization"** — we maximize revenue WITHIN Mietpreisbremse limits. Not just compliance, not just optimization — both simultaneously.
- **"The 2% that matters"** — small percentage, massive absolute value at portfolio scale.
- **"Optimize differentiation, not just price"** — the deepest insight. Don't just ask "what should I charge?" Ask "which units need to be MORE different from each other — and how to price the differences."
- **"The optimal price GAP, not just the optimal price LEVEL"** — what matters is relative pricing between your own units, not absolute pricing of each.
- **"Close substitutes limit your pricing power"** — when two units are interchangeable, raising one just pushes demand to the other. No revenue gained. The solution: differentiate them through targeted renovation, then price the gap.
- **"Renovation as differentiation strategy"** — portfolio-aware renovation advice is fundamentally different: "Don't renovate A's kitchen — B already has one. Add a balcony to A instead. Now they serve different segments and you can charge a premium on BOTH."

---

## Economic Intuition: Close vs Distant Substitutes

The portfolio pricing insight comes from understanding substitution:

```
Unit A: 65m², 2R, Altbau, kitchen        → €13.00/m²
Unit B: 68m², 2R, Altbau, kitchen        → €12.50/m²  ← CLOSE substitute to A
Unit C: 45m², 1R, Neubau, balcony        → €18.00/m²  ← DISTANT substitute
```

**Close substitutes (A ↔ B):** Same tenant type. Raise A → demand moves to B. You just shuffled revenue between pockets. Pricing power between them is LOW.

**Distant substitutes (A/B ↔ C):** Different tenant types (couples vs singles). Raise C independently — its demand doesn't leak to A/B. Pricing power is HIGH.

**The strategic implication:**

| Position | What you are | Pricing power | Strategy |
|----------|-------------|---------------|----------|
| Own 1 unit | Price taker | Low | Price to market |
| Own 2 close substitutes | Competing with yourself | Low between them | Differentiate → then price the gap |
| Own 2 distant substitutes | Multi-segment monopolist | High | Price each segment independently |

**The portfolio manager's goal:** Transform close substitutes into distant substitutes through targeted renovation, then price the differentiation.

**Why this changes renovation advice:**
- **Unit-level advice:** "Renovate A's kitchen — ROI is €2.91/m²"
- **Portfolio advice:** "Don't renovate A's kitchen — B already has one. Add a balcony to A. Now A=balcony-seekers, B=kitchen-seekers. You charge a premium on BOTH because they stopped cannibalizing each other."

**The airline analogy:** Economy and Premium Economy are close substitutes. Airlines don't just optimize the price of each — they optimize the **product gap** (legroom, boarding priority) AND the **price gap** simultaneously. The optimal gap depends on cross-elasticity. RentSignal does the same for apartments.

---

## Cross-Industry Validation

These industries already prove that portfolio pricing beats independent pricing:

| Industry | Method | Revenue uplift | Source |
|----------|--------|---------------|--------|
| **Airlines** | Revenue management with fare class substitution | 3-7% | American Airlines pioneered 1980s, now universal |
| **Hotels** | Multi-property pricing with cannibalization modeling (Marriott, IHG) | 2-5% | Cornell Hospitality Research |
| **Grocery retail** | Category management with cross-elasticity matrices (Walmart, Tesco) | 2-4% | Dolan & Simon, "Power Pricing" |
| **Car rental** | Fleet allocation + dynamic pricing across locations (Enterprise, Hertz) | 3-6% | Talluri & van Ryzin, "Revenue Management" |
| **SaaS** | Multi-tier pricing with cannibalization between plans | 5-15% | Price Intelligently research |
| **Ride-sharing** | Surge pricing with spatial demand substitution (Uber) | 8-12% | Uber engineering blog |

**The pitch line:** "Airlines figured this out in the 1980s. Hotels in the 2000s. Grocery in the 2010s. Property management still prices apartments like it's 1995 — one unit at a time. We're bringing portfolio intelligence to the last major industry that hasn't adopted it."

**The math that sells:** For a 5,000-unit Berlin portfolio at avg €12/m² × 65m²:
- Monthly revenue: ~€3.9M
- 2% uplift: **€78K/month = €936K/year**
- RentSignal cost at €2/unit/month: €120K/year
- **ROI: 7.8:1**

---

## Demo Flow (Hackathon — 5 minutes)

### Slide 1: The Problem (30 sec)
> "When you manage 200 apartments in Kreuzberg, you're not just competing with the market. You're competing with yourself."

### Slide 2: The Substitution Matrix (60 sec)
- Upload 15 units across 3 buildings
- Show heatmap: which units are substitutes (same bezirk, similar size, similar rooms)
- Red cells = high substitution risk ("these two units are cannibalizing each other")

### Slide 3: Current vs Optimized (90 sec)
- Left: current independent pricing → total revenue €18,400/mo
- Right: portfolio-optimized pricing → €19,200/mo (+4.3%)
- Arrows showing which units go up, which go down, and WHY
- All prices still within Mietpreisbremse limits (compliance overlay)

### Slide 4: The "Aha" Moment (60 sec)
- Click on the unit that went DOWN in price
- SHAP waterfall shows: "This unit was overpriced relative to its neighbor. Lowering it by €0.80/m² redirects demand to the premium unit next door, which can now sustain €1.50/m² more."
- **"One unit was subsidizing its neighbor. Now both are priced optimally."**

### Slide 5: Why This Works (30 sec)
- "Airlines: 3-7%. Hotels: 2-5%. Property management: 0%. Until now."
- "€936K/year for a 5,000-unit portfolio. 7.8:1 ROI."

### Slide 6: The Moat (30 sec)
- IO demand estimation (Berry-Levinsohn-Pakes)
- Mietpreisbremse as constraint (uniquely German, uniquely hard)
- Satellite spatial features for neighborhood trajectory
- "Rentana prices units. Predium does ESG. Conny does compliance. Nobody does portfolio optimization."

---

## Technical Architecture for Portfolio Optimization

```
INPUT: Portfolio of N units
  ↓
STEP 1: Cluster substitutes
  - Same bezirk, ±20% sqm, ±1 room, ±500m distance
  - Output: substitute clusters + substitution scores
  ↓
STEP 2: Estimate demand model
  - Phase 1 (simple): time-on-market as demand proxy
  - Phase 2 (BLP): discrete choice with random coefficients
  - Output: cross-price elasticity matrix
  ↓
STEP 3: Constrained optimization
  - Maximize: Σ(rent_i × occupancy_prob_i) across all units
  - Subject to: rent_i ≤ Mietpreisbremse_max_i for all i
  - Subject to: portfolio vacancy rate ≤ target
  - Solver: scipy.optimize or OR-Tools
  ↓
OUTPUT:
  - Optimal price vector [rent_1*, rent_2*, ..., rent_N*]
  - Revenue uplift vs independent pricing
  - Per-unit explanation (why each price changed)
  - Substitution heatmap visualization
```

---

## Implementation Phases

### Phase 0 — Hackathon Demo (can build now)
- Hard-code a demo portfolio (15 units, 3 buildings)
- Simple substitution scoring (distance + similarity)
- Optimization with assumed elasticities (calibrated from literature)
- Beautiful heatmap + before/after visualization
- **No real demand estimation yet** — use reasonable assumptions

### Phase 1 — MVP with Simple Demand Model
- Use time-on-market from scraped listing data as demand proxy
- Logit model: P(leased within 30 days) = f(price, features, competition)
- Cross-elasticities from coefficient estimates
- Works with public data (no client data needed)

### Phase 2 — Full BLP with Client Data
- Requires: applicant counts, showing requests, actual lease dates from clients (Buena has this)
- Random coefficients logit (heterogeneous tenant preferences)
- Instruments: construction cost index, Mietspiegel updates, regulatory changes
- Full substitution matrix with confidence intervals

---

## Key References

- Berry, S., Levinsohn, J., & Pakes, A. (1995). "Automobile prices in market equilibrium." Econometrica.
- Talluri, K. & van Ryzin, G. (2004). "The Theory and Practice of Revenue Management." Springer.
- Bayer, P., Ferreira, F., & McMillan, R. (2007). "A unified framework for measuring preferences for schools and neighborhoods." JPE.
- Diamond, R. (2016). "The determinants and welfare implications of US workers' diverging location choices." AER.
- Conlon, C. & Gortmaker, J. (2020). "Best practices for differentiated products demand estimation with PyBLP." RAND.

---

*This document captures strategic ideas from the 2026-03-19 session. Cross-reference with `docs/ideas/RentSignal-Portfolio-Optimization.md` for the full five-pillar framework.*
