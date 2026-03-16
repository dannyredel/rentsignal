# RentSignal — Pitch Deck Content (Gamma-Ready)

*Paste this into Gamma.app. Design direction: deep teal (#004746) + green (#00BC72) + amber (#E8913A) accents. General Sans headings, Inter body, JetBrains Mono for data. Sharp, geometric, no rounded/bubbly. Same aesthetic as rentsignal-landing.html.*

---

## SLIDE 1: TITLE

**RentSignal**
*Rent intelligence for the German rental market*

Comply · Optimize · Act

*Logo: signal waveform mark + "RentSignal" wordmark*

---

## SLIDE 2: THE PROBLEM

**Half of all rental contracts in Germany are illegal.**

Not because landlords are malicious — because the system is impossibly complex.

- **Price too high?** Tenants retroactively reclaim overpayments. €5,000+ per complaint.
- **Price too low?** You're leaving thousands on the table. The Mietspiegel gives a *range*, not a number.
- **Renovate the kitchen or the balcony?** Nobody can answer this with data.
- **CO2 cost-sharing?** 84% of Berlin apartments trigger it. Most landlords don't know.

*Source: 50% of rental contracts are technically unlawful (IVD, 2023). 83% of expat contracts exceed legal limits.*

---

## SLIDE 3: WHAT EXISTS (AND WHAT DOESN'T)

| | Mietspiegel | Conny | ImmoScout | Rentana (US) | **RentSignal** |
|--|--|--|--|--|--|
| Legal compliance | Range only | Tenant-side | — | — | **Full engine** |
| Rent prediction | — | — | District avg | Dynamic | **37-feature ML** |
| Feature breakdown | — | — | — | Basic | **SHAP waterfall** |
| Renovation ROI | — | — | — | — | **Dual-method** |
| Satellite spatial | — | — | — | — | **Sentinel-2** |
| Portfolio monitoring | — | — | — | Portfolio | **Watchdog + alerts** |

**RentSignal fills all six gaps. Nobody else fills more than two.**

---

## SLIDE 4: THE SOLUTION — COMPLY · OPTIMIZE · ACT

**Three pillars. One platform.**

**Comply** — Know your legal position. Always.
Mietpreisbremse check · Mieterhöhung calculator · CO2 cost-sharing · Letter generation

**Optimize** — Know what every unit is worth.
37-feature ML prediction · Feature contribution breakdown · Portfolio monitoring

**Act** — Make the right move.
Renovation ROI simulator · Neighborhood intelligence · Acquisition comparison

---

## SLIDE 5: HOW IT WORKS (DEMO FLOW)

*[Screenshot: dashboard with Kreuzberg Altbau]*

1. Enter apartment details (or autocomplete from address)
2. See predicted rent: **€11.85/m²** (current: €10.50 → underpriced by 13%)
3. Check compliance: legal max **€8.42/m²** → compliant, with €1.43 headroom
4. See why: top features = restaurants (+€2.82), living space (+€2.51), kitchen (+€1.03)
5. Toggle renovations: kitchen +€4.01/m² (54mo payback) vs balcony -€0.72/m² (never pays back)

**"Don't build the balcony."**

---

## SLIDE 6: THE DATA BEHIND IT

| Metric | Value |
|--|--|
| Training data | 10,275 Berlin apartments |
| Features | 37 (structural + OSM + Sentinel-2 satellite) |
| Model accuracy | R² = 0.749 |
| Spatial coverage | 190 Berlin postal codes |
| Renovation validation | Dual-method: 3% convergence |
| Matched apartment pairs | 2,288 |

**Restaurant density is the #1 rent predictor.** Not size. Not location category. Restaurants within 1km.

*Feature contribution breakdown shows exactly why each apartment is worth what it is.*

---

## SLIDE 7: SATELLITE INTELLIGENCE (DIFFERENTIATOR)

**The Mietspiegel says "good residential area." We show you this:**

- NDVI vegetation index from Sentinel-2 (10m resolution, free)
- Restaurant/transit/shop density from OpenStreetMap
- Built-up density index (NDBI)
- All computed for 190 Berlin postal codes

**+2.4% prediction accuracy** over structural features alone.

*"Nobody at a hackathon — or in the German market — has this."*

---

## SLIDE 8: DON'T BUILD THE BALCONY (THE DEMO MOMENT)

**Most landlords assume balconies increase rent.**

We matched 2,288 apartment pairs to test that assumption.

| Renovation | Market Impact | Payback | ROI |
|--|--|--|--|
| **Kitchen** | +€4.01/m² | 54 months | 24.4% |
| **Garden** | +€0.97/m² | 69 months | 17.5% |
| **Elevator** | +€1.45/m² | 412 months | 2.9% |
| **Balcony** | **−€0.72/m²** | **Never** | **Negative** |

Validated: observational matching (+€4.01) vs demand-side estimation (+€4.13) = **3% apart.**

Two independent methods. One answer. **Invest in kitchens, not balconies.**

---

## SLIDE 9: CO2 COMPLIANCE — THE HIDDEN COST

**84% of Berlin apartments trigger CO2 cost-sharing.**

Since 2023, landlords of energy-inefficient buildings pay a share of tenant carbon costs.

| Energy Class | Landlord Share | Avg Annual Cost |
|--|--|--|
| A-B | 0-10% | €0-15 |
| C-D | 20-40% | €15-80 |
| E-F | 50-70% | €80-250 |
| G-H | 80-90% | €250-500+ |

CO2 price trajectory: €45 (2024) → €65 (2026) → €100+ (2030)

**At Buena scale (60,000 units): €1.88M/year in CO2 exposure.**

*Most landlords don't know this cost exists. RentSignal shows it.*

---

## SLIDE 10: PRODUCT TIERS

| | Free | Pro (€29/mo) | Business (€99/mo) |
|--|--|--|--|
| Units | 3 | 15 | Unlimited |
| Comply | Mietpreisbremse | + Mieterhöhung + CO2 | + Portfolio risk table |
| Optimize | 3 predictions/mo, top 3 features | Unlimited + full breakdown | + Batch + revenue gaps |
| Act | Locked (preview) | Full access | + Acquisition comparison |
| Monitoring | — | Portfolio watchdog | + Monthly PDF report |

**Free compliance check = acquisition wedge.**
**Pro monitoring = subscription stickiness.**
**Business PDF = client deliverable they bill for.**

---

## SLIDE 11: MARKET & REVENUE

**TAM: €828M/year** (23M German rental apartments × €3/unit/month)

| Scenario | Year 1 ARR |
|--|--|
| Conservative | €40K (30 Pro + 5 Business + 1 API partner) |
| Optimistic | €149K (100 Pro + 15 Business + 2 platforms) |
| Buena alone | **€1.44M** (60,000 units × €2/unit/month) |

**European expansion:** Austria, Netherlands, France, Sweden — all have rent regulation.
European TAM: **€2B+**

---

## SLIDE 12: COMPETITIVE MOAT

**Why we win:**

1. **Satellite spatial features** — nobody else has Sentinel-2 data in rent prediction
2. **Dual-method causal validation** — not correlation, causation (3% convergence)
3. **Full compliance engine** — Mietpreisbremse + Mieterhöhung + CO2KostAufG + §559
4. **Portfolio monitoring** — the subscription is the watchdog, not the calculation
5. **Three-pillar framework** — Comply·Optimize·Act scales from 1 unit to 60,000

**Conny tells tenants they're overpaying. We tell property managers where the money is — and where the risk is.**

---

## SLIDE 13: TRACTION & STATUS

**Already built:**
- Live API: 28 endpoints on Railway (Python 3.11)
- XGBoost model: R²=0.749, 37 features, SHAP explanations
- Supabase: 6 tables with RLS, Google OAuth ready
- 10 validated notebooks: data → model → spatial → compliance → matching → conjoint → CO2
- Dashboard + landing page prototypes
- Product strategy: 18-section PRODUCT.md

**Next:**
- Lovable frontend generation (prompt ready)
- City expansion: Hamburg, Munich (same engine, new Mietspiegel)
- Portfolio monitoring (nightly watchdog)

---

## SLIDE 14: THE ASK

**For Buena:**
"We help your property managers set compliant, optimized rents across 60,000+ units — with spatial intelligence no competitor has."

**For investors:**
"€828M German TAM. Six gaps nobody fills. Unit-level tool: built. Portfolio intelligence is the moat."

**For the audience:**
"Before you spend €25,000 on a balcony, see the data."

---

## SPEAKER NOTES

**Slide 2 (Problem):** Pause after "half of all rental contracts are illegal." Let it land. Then: "Not because landlords are malicious..."

**Slide 5 (Demo):** This is the live demo slide. Walk through the Kreuzberg apartment. End with "don't build the balcony" — this is the wow moment.

**Slide 8 (Balcony):** This is the punchline. Show the dual-method convergence: "Two completely independent methods, 3% apart. When that happens, the signal is real."

**Slide 9 (CO2):** New territory. Most people in the room won't know about CO2KostAufG. The €1.88M Buena number gets attention.

**Slide 12 (Moat):** The Conny line is the competitor framing. Deliver it exactly: "Conny tells tenants they're overpaying. We tell property managers where the money is — and where the risk is."

**Timing:** 3 minutes total. Slides 1-3: 45 seconds. Slides 4-8: 90 seconds (demo + balcony moment). Slides 9-14: 45 seconds.
