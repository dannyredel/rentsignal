# Compliance Engine — How It Works

## Overview

The compliance engine answers two questions:
1. **"What is the maximum rent I can legally charge?"** — Rent law (Mietpreisbremse, §558, §559)
2. **"How much CO2 cost am I liable for?"** — Energy/climate law (CO2KostAufG)

It implements five pieces of German law:
1. **§556d BGB** — The Mietpreisbremse (rent brake) — new leases
2. **§558 BGB** — Rent increases on existing tenants (Mieterhöhung)
3. **§559 BGB** — Modernization rent increases
4. **§559e BGB** — Heating replacement under the GEG (new since Jan 2024)
5. **CO2KostAufG** — Carbon cost-sharing between landlord and tenant (since Jan 2023)

All rent calculations use the **Berlin Mietspiegel 2024** as the reference for "local comparative rent" (ortsübliche Vergleichsmiete).

---

## Part 1: The Mietpreisbremse (§556d BGB)

### What it is
In cities with "tight housing markets" (angespannter Wohnungsmarkt), landlords cannot charge more than **110% of the local comparative rent** when signing a new lease.

Berlin has been designated as a tight housing market continuously and this was extended to **December 31, 2029**.

### The formula

```
legal_max_rent = ortsübliche_Vergleichsmiete × 1.10
```

That's it. The hard part is figuring out the ortsübliche Vergleichsmiete — which is what the Mietspiegel does.

### How we calculate the ortsübliche Vergleichsmiete

The Mietspiegel is a giant lookup table. You need three inputs:

#### Input 1: Building year → Building year category
| Category | Years | Label |
|----------|-------|-------|
| pre_1918 | ≤ 1918 | Altbau (vor 1918) |
| 1919_1949 | 1919–1949 | Zwischenkrieg/Nachkrieg |
| 1950_1964 | 1950–1964 | Nachkrieg |
| 1965_1972 | 1965–1972 | Spätmoderne |
| 1973_1990 | 1973–1990 | Plattenbau-Ära |
| 1991_2002 | 1991–2002 | Nachwendezeit |
| 2003_2013 | 2003–2013 | Neuzeit |
| 2015+ | ≥ 2015 | Neubau (EXEMPT — see exceptions) |

#### Input 2: Living space → Size category
| Category | Size |
|----------|------|
| under_40 | < 40 m² |
| 40_60 | 40–60 m² |
| 60_90 | 60–90 m² |
| over_90 | ≥ 90 m² |

#### Input 3: Location quality (Wohnlage)
| Quality | Description | Example districts |
|---------|-------------|-------------------|
| Einfach (simple) | Basic residential area | Spandau, Neukölln, Marzahn, Lichtenberg |
| Mittel (average) | Average residential area | Friedrichshain-Kreuzberg, Pankow, Tempelhof-Schöneberg |
| Gut (good) | Good residential area | Mitte, Charlottenburg-Wilmersdorf, Steglitz-Zehlendorf |

Each district is mapped to a default location quality. In reality, the Mietspiegel uses sub-district zones (Wohnlagenkarte), but we simplify to district level for the demo.

#### The lookup result

For any combination of (building year, size, location), the Mietspiegel gives three values:

```
lower — mid — upper    (all in €/m² nettokalt)
```

Example: Pre-1918 Altbau, 60–90 m², mittlere Wohnlage → **5.88 — 7.57 — 10.03 €/m²**

The **mid** value is the "ortsübliche Vergleichsmiete" — the local comparative rent.

#### Equipment adjustments (Spanneneinordnung)

The mid value assumes an average apartment. If yours has better or worse equipment, we adjust:

| Feature | If present | If absent |
|---------|-----------|-----------|
| Modern bathroom (Modernes Bad) | +€0.35/m² | −€0.20/m² |
| Fitted kitchen (Einbauküche) | +€0.28/m² | €0 |
| Balcony/terrace | +€0.23/m² | €0 |
| Elevator (Aufzug) | +€0.22/m² | €0 |
| Modern heating (Zentralheizung) | +€0.18/m² | −€0.15/m² |
| Good insulation (Wärmedämmung) | +€0.20/m² | €0 |
| Parquet flooring (Parkettboden) | +€0.15/m² | €0 |
| Basement storage (Keller) | +€0.08/m² | €0 |

These are summed and added to the mid value. The result is clamped to the [lower, upper] range — you can't adjust beyond the Mietspiegel range.

```
adjusted_mid = clamp(mid + equipment_adjustments, lower, upper)
legal_max = adjusted_mid × 1.10
```

### Exceptions — when the Mietpreisbremse does NOT apply

Three situations where the 110% cap is lifted:

#### Exception 1: New build (Neubau, §556f BGB)
If the apartment was **first used and rented after October 1, 2014**, the Mietpreisbremse does not apply. The landlord can charge whatever the market will bear.

In our code, we use `building_year >= 2015` as a safe proxy. Buildings from exactly 2014 are edge cases that need manual date verification.

#### Exception 2: Comprehensive modernization (§556f BGB)
If the apartment is being rented for the **first time after a comprehensive modernization** (umfassende Modernisierung), it's treated like a new build. The modernization must be extensive enough to equal roughly one-third of new-build costs.

#### Exception 3: Previous tenant's rent (Vormiete, §556e BGB)
If the previous tenant legally paid more than the Mietspiegel+10% limit, the landlord can charge up to the previous rent level. The logic:

```python
if previous_rent > legal_max:
    legal_max = previous_rent  # Previous rent becomes the new floor
```

This prevents landlords from being forced to lower rent between tenants.

### The compliance check

Once we know the legal max, the compliance check is simple:

```python
if current_rent <= legal_max:
    # Compliant — report headroom (room to increase)
    headroom = legal_max - current_rent
else:
    # Non-compliant — report overpayment
    overpayment = current_rent - legal_max
    # Tenant can retroactively reclaim the overpayment!
```

---

## Part 2: Modernization Rent Increase (§559 BGB)

### What it is
When a landlord modernizes an apartment (not just repairs it), they can pass part of the cost to the tenant through a permanent rent increase.

### The formula

```
annual_rent_increase = eligible_cost × 0.08   (8% of cost per year)
monthly_increase_per_sqm = annual_rent_increase / 12 / living_space_sqm
```

### What counts as "eligible cost"

Only **modernization** costs count. **Maintenance** (Instandhaltung) does not.

| Counts as modernization | Does NOT count |
|------------------------|----------------|
| Energy efficiency (insulation, windows, heating) | Repairing broken heating |
| Water/resource savings | Fixing leaky pipes |
| New amenities (fitted kitchen, balcony) | Repainting walls |
| Structural improvements | Replacing worn-out fixtures |
| Climate adaptation | Cosmetic repairs |

When a measure is both (e.g., replacing old windows = maintenance + insulation improvement), the maintenance share must be estimated and deducted.

```python
eligible_cost = total_cost × (1 - maintenance_share)
```

### The caps (Kappungsgrenze)

To protect tenants, the law caps how much rent can increase from modernization within a rolling 6-year period:

| Current rent | Maximum increase in 6 years |
|-------------|---------------------------|
| ≤ €7.00/m² | +€2.00/m² |
| > €7.00/m² | +€3.00/m² |

This is a **rolling 6-year window**. If the landlord already increased rent by €1.50/m² via §559 in the past 6 years, the remaining headroom is:

```python
remaining = max_cap - prior_increases_6yr
actual_increase = min(calculated_increase, remaining)
```

### Why payback is always 12.5 years (when uncapped)

An interesting property of the 8% rule: if the cap doesn't bind, the payback period is always the same regardless of renovation cost:

```
payback = cost / (0.08 × cost / 12) = 12 / 0.08 = 150 months = 12.5 years
```

This means the legal mechanism treats all renovations equally. A €5,000 kitchen and a €50,000 balcony both "pay back" in 12.5 years via the legal passthrough. **The differentiation comes from the market** (SHAP values show tenants value kitchens much more than balconies).

---

## Part 3: GEG Heating Replacement (§559e BGB) — New since Jan 2024

### What it is
When a landlord replaces a heating system to comply with the Gebäudeenergiegesetz (Building Energy Act), a special modernization path applies with a higher passthrough rate but a tighter cap.

### The formula

```
eligible_cost = (total_cost - maintenance_share) - public_subsidies
annual_increase = eligible_cost × 0.10   (10% — higher than standard 8%)
monthly_increase_per_sqm = annual_increase / 12 / living_space_sqm
```

### The cap

Hard cap: **€0.50/m² per month**, regardless of rent level. No 6-year rolling window — this is a flat per-project cap.

### When to use §559e vs §559

§559e is specifically for GEG-compliant heating replacements where public subsidies are used. The landlord can choose either path (§559 or §559e), but §559e is usually better when subsidies are available because:
- Higher passthrough rate (10% vs 8%)
- But subsidies are deducted from the eligible cost
- And the €0.50/m²/month cap is quite tight

---

## Code Architecture

```
data/reference/mietspiegel_simplified.json
    └── Lookup table: building_year × size × location → (lower, mid, upper)
    └── Equipment adjustment factors
    └── District-to-location mapping
    └── §559 cap rules

backend/models/compliance.py
    └── ComplianceInput (Pydantic)  — apartment features + current rent
    └── ComplianceResult           — legal max, compliance status, recommendation
    └── ModernizationInput         — renovation cost + context
    └── ModernizationResult        — increase amount, cap status, new rent

backend/services/compliance_service.py
    └── lookup_mietspiegel()                  — table lookup + equipment adjustment
    └── check_mietpreisbremse()               — §556d + exceptions
    └── check_compliance()                    — full check with recommendation
    └── calculate_modernization_increase()    — §559 or §559e calculation
```

---

## Decision Rules Summary

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: district, sqm, building_year, equipment, current_rent│
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │ building_year >= 2015?   │
            └──────┬───────────────────┘
                   │
         yes ◄─────┴─────► no
         │                 │
    ┌────▼─────┐    ┌──────▼──────────────────────────┐
    │ EXEMPT   │    │ first_rental_after_modernization?│
    │ No cap   │    └──────┬──────────────────────────┘
    └──────────┘           │
                  yes ◄────┴────► no
                  │               │
             ┌────▼─────┐  ┌─────▼────────────────────────┐
             │ EXEMPT   │  │ Mietspiegel lookup            │
             │ No cap   │  │ year_cat × size_cat × location│
             └──────────┘  │ + equipment adjustments       │
                           │ = adjusted_mid                │
                           └─────┬────────────────────────┘
                                 │
                                 ▼
                     legal_max = adjusted_mid × 1.10
                                 │
                                 ▼
                     ┌───────────────────────────┐
                     │ previous_rent > legal_max? │
                     └─────┬─────────────────────┘
                           │
                  yes ◄────┴────► no
                  │               │
         legal_max = previous_rent│
                  │               │
                  └───────┬───────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │ current_rent <= legal_max│
              │ → COMPLIANT (headroom)  │
              │ current_rent > legal_max │
              │ → NON-COMPLIANT (overpay)│
              └─────────────────────────┘


§559 MODERNIZATION:
┌───────────────────────────────────────────────────┐
│ INPUT: cost, maintenance_share, current_rent,     │
│        prior_increases_6yr, is_geg_heating        │
└──────────────────────┬────────────────────────────┘
                       │
                       ▼
        eligible = cost × (1 - maintenance_share)
        [if GEG: also subtract public subsidies]
                       │
                       ▼
          ┌────────────────────────────┐
          │ GEG heating (§559e)?       │
          └─────┬──────────────────────┘
                │
       yes ◄────┴────► no
       │               │
  rate = 10%      rate = 8%
  cap = €0.50/m²  │
  per month        ▼
       │     ┌──────────────────┐
       │     │ rent ≤ €7/m²?    │
       │     └──┬───────────────┘
       │        │
       │   yes ◄┴► no
       │   │      │
       │   cap    cap
       │   €2/m²  €3/m²
       │   6yr    6yr
       │   │      │
       └───┴──┬───┘
              │
              ▼
  increase = min(eligible × rate / 12 / sqm, remaining_cap)
  new_rent = current_rent + increase
```

---

## Legal Sources

| Law | Section | What it governs |
|-----|---------|----------------|
| BGB §556d | Mietpreisbremse | Max 110% of Mietspiegel in designated areas |
| BGB §556e | Vormiete exception | Previous rent as floor |
| BGB §556f | Neubau + modernization exemptions | When the rent brake doesn't apply |
| BGB §559 | Modernization passthrough | 8% of costs to annual rent |
| BGB §559e | GEG heating replacement | 10% with €0.50/m² cap (since Jan 2024) |
| BGB §558d | Qualified Mietspiegel | Legal standard for determining local rent |
| MietpreisbremsenVO Berlin | Berlin designation | Entire Berlin designated until Dec 31, 2029 |
| Berliner Mietspiegel 2024 | Rent table | Current qualified Mietspiegel for Berlin |

### Key recent developments
- **June 2025:** Bundestag extended Mietpreisbremse to December 31, 2029
- **January 2026:** Bundesverfassungsgericht confirmed constitutionality (1 BvR 183/25)
- **January 2024:** §559e BGB (GEG heating path) entered into force
- **February 2026:** Draft Mietrechtsreform proposed (index rent caps, furnished rental rules) — **not yet law**, ignored in our engine

### Simplifications in our implementation
1. **Mietspiegel values are approximated** — production version would use the official qualified Mietspiegel with all sub-categories
2. **Location quality mapped at district level** — the real Mietspiegel uses a Wohnlagenkarte with sub-district zones
3. **Equipment adjustments simplified** — the real Spanneneinordnung has more granular factors
4. **Neubau cutoff uses building_year >= 2015** — the actual cutoff is "first used after October 1, 2014" which requires the exact first-use date
5. **Size categories simplified to 4 brackets** — the 2024 Mietspiegel uses more granular size brackets that vary by building age class

---

## Part 4: Rent Increases on Existing Tenants (§558 BGB)

### What it is
Separate from the Mietpreisbremse (which governs **new** leases), §558 BGB governs rent increases on **existing** tenants. A landlord can raise rent up to the Mietspiegel mid value, subject to caps.

### Rules
1. **Mietspiegel cap:** New rent cannot exceed the Mietspiegel mid value (ortsübliche Vergleichsmiete Mittelwert)
2. **Kappungsgrenze:** Maximum 15% increase within any 3-year period (Berlin uses the stricter 15%; federal default is 20%)
3. **15-month minimum** between rent increase requests
4. **Formal written request** required (Mieterhöhungsverlangen, §558a BGB) — must reference Mietspiegel or comparable apartments
5. **Tenant consent required** — tenant has 2 months to agree; if they refuse, landlord can sue for consent (Zustimmungsklage)

### Calculation
```
effective_max = min(mietspiegel_mid, current_rent * 1.15)  # lower of the two caps
max_increase = max(0, effective_max - current_rent)
```

### Exclusions
- Staffelmiete (graduated rent) and Indexmiete (index-linked rent) contracts — §558 does not apply, increases follow the contract terms
- First 12 months after last increase — no new request allowed

### Implementation
- Endpoint: `POST /rent-increase/calculate`
- Reuses the Mietspiegel lookup from the Mietpreisbremse engine
- Accepts `last_increase_date` and `rent_3_years_ago` for Kappungsgrenze check
- Returns: can_increase (bool), max_increase_sqm, effective_max_rent, earliest_increase_date

### Phase 2: Letter Generation
`POST /rent-increase/letter` will generate a §558a-compliant Mieterhöhungsverlangen PDF. Requires one-time legal review (budget €200-500).

---

## Part 5: CO2 Cost-Sharing (CO2KostAufG)

### What it is
Since January 2023, the **Kohlendioxidkostenaufteilungsgesetz** (CO2KostAufG) requires landlords of energy-inefficient buildings to share CO2 costs with tenants. The worse the building's energy performance, the more the landlord pays — up to 90%.

This directly reduces net rental income and scales with the rising CO2 price.

### Why it matters
- **84% of Berlin apartments trigger some CO2 cost-sharing** (based on our 10,275 listings)
- **10% are in the high-impact zone** (landlord pays ≥50%)
- CO2 price is rising: €45/tonne (2024) → €55 (2025) → €65 (2026) → projected €100+ by 2030
- Most landlords don't know this cost exists — it's deducted from their Nebenkostenabrechnung

### The 10-Step Sharing Table (§5 Abs. 1 CO2KostAufG)

| CO2 Emissions (kg/m²/year) | Landlord Share | Tenant Share |
|---|---|---|
| < 12 | 0% | 100% |
| 12 – 17 | 10% | 90% |
| 17 – 22 | 20% | 80% |
| 22 – 27 | 30% | 70% |
| 27 – 32 | 40% | 60% |
| 32 – 37 | 50% | 50% |
| 37 – 42 | 60% | 40% |
| 42 – 47 | 70% | 30% |
| 47 – 52 | 80% | 20% |
| ≥ 52 | 90% | 10% |

### How We Calculate It

1. **Energy consumption** → from `thermalChar` (kWh/m²/year), available in our dataset for all 10,275 listings
2. **Emission factor** → depends on heating type (gas: 0.201, oil: 0.266, district: 0.130, heat pump: 0.045 kg CO2/kWh). Source: UBA 2024
3. **CO2 per m²** = thermalChar × emission_factor (kg CO2/m²/year)
4. **Sharing lookup** → find the row in the table above
5. **Annual cost** = (CO2/m² × living_space / 1000) × CO2_price × landlord_share_%

### Energy Class Derivation

We derive the Energieausweis class from `thermalChar`:

| Class | kWh/m²/year | Dataset % |
|---|---|---|
| A+ | ≤ 30 | 0.7% |
| A | 30 – 50 | 3.3% |
| B | 50 – 75 | 14.5% |
| C | 75 – 100 | 13.9% |
| D | 100 – 130 | 46.1% |
| E | 130 – 160 | 11.6% |
| F | 160 – 200 | 6.9% |
| G | 200 – 250 | 2.3% |
| H | > 250 | 0.7% |

### Key Numbers (Berlin, 2026 @ €65/tonne)

- Average landlord CO2 cost: **€31/year** per apartment
- Hausverwaltung (500 units): **€15,687/year**
- Buena-scale (60,000 units): **€1.88M/year**
- Berlin-wide estimate (23M rental apartments): **€722M/year**

### CO2 Price Schedule

| Year | Price (€/tonne) | Status |
|---|---|---|
| 2023 | €30 | Historical |
| 2024 | €45 | Historical |
| 2025 | €55 | Current |
| 2026 | €65 | Projected |
| 2027+ | €55-65 (ETS corridor) | Market-based from 2027 |

### Implementation
- Endpoint: `POST /compliance/energy`
- Input: energy_class, living_space_sqm, heating_fuel (optional: co2_kg_per_sqm override)
- Output: landlord_share_pct, landlord_cost_annual, landlord_cost_monthly, severity, recommendation
- Tier: Pro+ (energy compliance is a Pro feature)
- Notebook: `notebooks/10_co2_cost_sharing.ipynb`

### Phase 2: EU EPBD Deadline Flags
Under the EU Energy Performance of Buildings Directive, worst-performing buildings (EPC class F and G) must reach class E by 2030, class D by 2033. We will flag affected units with renovation deadlines and estimated costs.
