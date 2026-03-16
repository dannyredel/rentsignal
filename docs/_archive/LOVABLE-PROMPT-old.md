# RentSignal — Lovable Frontend Prompt

Paste this into Lovable to generate the MVP frontend.

---

## PROMPT

Build a full-stack React + Tailwind CSS web application for "RentSignal" — a B2B rent intelligence platform for the German rental market. The app has two parts: a **public landing page** and a **dashboard** (behind a simple auth gate via Supabase).

---

### BRAND & DESIGN SYSTEM

**Brand name:** RentSignal
**Tagline:** "Precision Intelligence for the German Rental Market"

**Design direction:**
- Clean, geometric, professional — like Linear.app meets Stripe Dashboard
- Sharp edges, no rounded/bubbly shapes
- Data-dense but elegant — not a consumer app
- Works in both light mode (landing page) and dark mode (dashboard)

**Background texture:**
- Subtle gradient (soft lavender/blue → warm cream/peach, very muted)
- Overlaid with a faint architectural blueprint grid pattern (thin precise lines like construction technical drawings, ~10% opacity)
- This grid texture is the signature brand element — use it on the landing page hero and as a subtle dashboard background

**Typography:**
- Headings: Inter or General Sans (geometric sans-serif, bold weights)
- Body: Inter or DM Sans (clean, readable)
- Data/numbers: JetBrains Mono or IBM Plex Mono (monospace for €/m² values, percentages)
- NO italic or script fonts anywhere

**Color palette:**
- Derive colors from the brand identity screenshots I will share — match the palette closely
- Must include: primary, accent (for CTAs), success (compliant), danger (non-compliant), neutrals
- AVOID: Bright green as primary (competitor Conny uses green)

**Logo:** Use text "RentSignal" with a small signal/pulse icon. Simple geometric mark.

---

### PART 1: LANDING PAGE (public, no auth)

**Route:** `/`

**Hero section:**
- Architectural grid background with subtle gradient
- Headline: "Know what every unit is worth. Stay legal. Renovate smarter."
- Subheadline: "Rent intelligence for the German rental market. Predict fair rent, check Mietpreisbremse compliance, and simulate renovation ROI — from a single apartment to an entire portfolio."
- Two CTAs: "Try Free Compliance Check →" (primary/accent button) and "Request Demo" (outline button)
- Small trust badge in monospace: "Based on 10,275 Berlin apartments • 37 ML features • Satellite spatial data"

**Features section (3 cards):**
1. **Predict** — "Know your apartment's market rent" — "XGBoost model with 37 features including satellite vegetation indices and restaurant density. R²=0.749. See exactly why with SHAP feature breakdown."
2. **Comply** — "Check Mietpreisbremse instantly" — "Real-time §556d BGB compliance check with Mietspiegel 2024 lookup, equipment adjustments, and exemption handling. Bilingual DE/EN."
3. **Renovate** — "See renovation ROI before you spend" — "Dual-method analysis: observational causal matching (10,275 apartments) + synthetic conjoint (75 respondents). Kitchen: +€4.01/m². Balcony: negative ROI."

**Social proof section:**
- "Trusted methodology" — show key numbers: "10,275 apartments analyzed", "37 ML features", "3% convergence between two independent methods", "190 Berlin postal codes"

**Pricing section (3 tiers):**
- **Free:** €0 — Compliance check (unlimited), 3 predictions/month
- **Pro:** €29/month — Unlimited predictions, full SHAP, renovation simulator, spatial features, PDF reports
- **Business:** €99/month — Portfolio dashboard, bulk upload, API access

**Footer:** Links, "Made in Berlin 🇩🇪", copyright

---

### PART 2: DASHBOARD (authenticated via Supabase)

**Route:** `/dashboard`

**Auth:** Use Supabase Auth (email + password signup/login). Simple auth pages at `/login` and `/signup`. After login, redirect to `/dashboard`.

**Layout:**
- Left sidebar navigation (collapsible, dark background):
  - 📊 Overview
  - 🏠 Predict
  - ⚖️ Comply
  - 🔧 Renovate
  - 🗺️ Spatial
  - 📁 Portfolio (greyed out, "Coming Soon" badge)
  - ⚙️ Settings
- Top bar with: RentSignal logo, search bar (placeholder), notification bell, user avatar/menu
- Main content area with the selected page

---

#### Page: Overview (`/dashboard`)

A summary dashboard showing key metrics and quick actions.

**Top stats row (4 cards):**
- "Apartments Analyzed" — count with trend arrow
- "Average Predicted Rent" — €X.XX/m²
- "Compliance Issues Found" — count with red highlight if > 0
- "Potential Revenue Uplift" — €X,XXX/month

**Recent analyses section:**
- Table/list of recent predictions with: apartment name/address, predicted rent, compliance status (green/red badge), date

**Quick action cards:**
- "New Prediction" → links to Predict page
- "Compliance Check" → links to Comply page
- "Renovation Analysis" → links to Renovate page

**Demo mode:** On first login (or if user has no saved analyses), pre-populate with 5 demo apartments loaded from the API endpoint `GET /demo/apartments`. Each demo apartment has full data for all 4 layers.

---

#### Page: Predict (`/dashboard/predict`)

**Input form (left panel or top section):**

Form fields matching the API schema:
- District (dropdown): All Berlin Bezirke — Mitte, Friedrichshain-Kreuzberg, Pankow, Charlottenburg-Wilmersdorf, Spandau, Steglitz-Zehlendorf, Tempelhof-Schöneberg, Neukölln, Treptow-Köpenick, Marzahn-Hellersdorf, Lichtenberg, Reinickendorf
- PLZ (number input, optional): 5-digit Berlin postal code
- Living Space (number, m²)
- Rooms (number)
- Year Built (number)
- Floor (number)
- Building Floors (number)
- Condition (dropdown): first_time_use, mint_condition, well_kept, needs_renovation, by_arrangement
- Interior Quality (dropdown): luxury, sophisticated, normal, simple
- Heating Type (dropdown): central_heating, gas, oil, district_heating, floor_heating, self_contained_central_heating, stove_heating, electric, solar, heat_pump, wood_pellet, night_storage
- Energy (kWh/m², number)
- Flat Type (dropdown): apartment, ground_floor, penthouse, maisonette, loft, roof_storey, raised_ground_floor, terraced_flat, other
- Building Era (dropdown): pre_1918, 1919_1949, 1950_1964, 1965_1972, 1973_1990, 1991_2002, 2003_2014, post_2014
- Toggle switches: Modern Kitchen, Balcony, Elevator, Cellar, Garden, New Construction
- Current Rent (€/m², optional — for gap analysis)

**Submit button:** "Predict Rent" → calls `POST /predict` with the form data

**Results panel (right panel or below form):**

After API response, show:

1. **Big number:** Predicted rent €X.XX/m² (large, monospace font)
   - If current rent provided, show gap: "+€1.39/m² UNDERPRICED" (green) or "-€2.10/m² OVERPRICED" (red)
   - Show total monthly: "€927/month for 78m²"

2. **SHAP waterfall chart:**
   - Horizontal bar chart showing top 10 feature contributions
   - Base value (average rent) on the left → predicted rent on the right
   - Positive contributions in blue/teal, negative in red/orange
   - Each bar labeled with feature name (use the `label` field) and value (€/m²)
   - Use the `shap_top_features` array from the API response

3. **Model info badge:** "Model v3 • R²=0.749 • 37 features"

---

#### Page: Comply (`/dashboard/comply`)

**Input form:**

Form fields matching ComplianceInput:
- District (dropdown, same as Predict)
- Living Space (m²)
- Building Year
- Current Rent (€/m², nettokalt)
- Previous Tenant's Rent (€/m², optional)
- Equipment toggles: Modern Bathroom, Fitted Kitchen, Balcony, Elevator, Parquet Flooring, Modern Heating, Good Insulation, Basement Storage
- Location Quality (dropdown): einfach (simple), mittel (medium), gut (good) — or "auto-detect from district"
- Checkbox: "First rental after comprehensive modernization"

**Submit:** "Check Compliance" → calls `POST /compliance`

**Results:**

1. **Compliance status banner:**
   - ✅ COMPLIANT (green): "Your rent is within legal bounds"
   - ❌ NON-COMPLIANT (red): "Your rent exceeds the legal maximum"
   - ⚠️ EXEMPT (amber): "This apartment is exempt from Mietpreisbremse"

2. **Key numbers (card row):**
   - "Legal Maximum" — €X.XX/m² (from `legal_max_rent_per_sqm`)
   - "Your Rent" — €X.XX/m²
   - "Overpayment" — €X.XX/m² (red) OR "Headroom" — €X.XX/m² (green)
   - "Annual Exposure" — €X,XXX/year (if non-compliant)

3. **Mietspiegel breakdown:**
   - Show: building year category, size category, location quality
   - Show: lower / mid / upper Mietspiegel range as a horizontal range bar
   - Show equipment adjustments as a list with +/- €/m² amounts
   - Mark where the legal max falls (110% of adjusted mid)

4. **Recommendation box:**
   - German text in a card
   - English translation below (or toggle DE/EN)

---

#### Page: Renovate (`/dashboard/renovate`)

**Input form (simple):**
- Living Space (m²)
- Toggle switches: Has Kitchen, Has Balcony, Has Elevator, Has Garden

**Submit:** "Simulate Renovations" → calls `POST /renovate`

**Results:**

1. **Renovation options cards (one per available renovation):**
   Each card shows:
   - Renovation name (e.g., "Modern Kitchen")
   - "Already has" badge if `already_has: true` (grey out, no ROI data)
   - For available renovations:
     - Combined uplift: +€X.XX/m² (large number)
     - Monthly uplift: +€XXX/month
     - Payback: XX months
     - ROI: XX%/year
     - Cost: €XX,XXX
     - Dual-method breakdown: CATE €X.XX vs WTP €X.XX (small text showing both methods)
     - Confidence interval from CATE
     - Legal passthrough (§559): €X.XX/m²

2. **Comparison bar chart:**
   - All 4 renovations side by side
   - Y-axis: €/m² uplift
   - Color-code: positive uplift (teal), negative uplift (red)
   - This is the "don't build the balcony" chart — kitchen should be tall and positive, balcony should be short or negative

3. **Key insight box:**
   - "Kitchen renovation: +€4.01/m², 47-month payback, 25% annual ROI"
   - "Balcony: negative market impact despite positive legal passthrough — don't build the balcony"

---

#### Page: Spatial (`/dashboard/spatial`)

**PLZ selector:**
- Dropdown or searchable input with all 190 Berlin PLZs
- OR interactive map of Berlin with PLZ boundaries (stretch goal — if Lovable can handle it, use a simple SVG map or leaflet)

**Results:** Calls `GET /spatial/{plz}`

Show spatial features in categorized cards:

**OSM Features:**
- 🚇 Transit: distance to nearest (m), count within 1km
- 🍽️ Food/Dining: count within 500m, count within 1km
- 🛒 Shopping: count within 500m, count within 1km
- 🌳 Parks: distance to nearest (m)
- 💧 Water: distance to nearest (m)
- 🏫 Schools: distance to nearest (m)

**Satellite Features:**
- 🌿 NDVI (vegetation): mean, std, median
- 💧 NDWI (water): mean, std, median
- 🏗️ NDBI (built-up): mean, std, median

Show each as a metric card with the value and a small visual indicator (e.g., a mini bar showing where this PLZ falls relative to Berlin's range).

---

### BACKEND CONNECTION

**API Base URL:** Configure via environment variable `VITE_API_URL` (default: `http://localhost:8000`)

**Endpoints to connect:**
| Method | Endpoint | Page | Request Body | Response |
|--------|----------|------|-------------|----------|
| GET | `/health` | — | — | `{status, service, version}` |
| GET | `/demo/apartments` | Overview | — | List of 5 demo apartments |
| GET | `/demo/apartments/{id}` | Overview | — | Full apartment with all 4 layers |
| POST | `/predict` | Predict | ApartmentInput JSON | PredictionResult JSON |
| POST | `/compliance` | Comply | ComplianceInput JSON | ComplianceResult JSON |
| POST | `/renovate` | Renovate | RenovationInput JSON | RenovationResult JSON |
| GET | `/spatial/{plz}` | Spatial | — | Spatial features JSON |
| GET | `/spatial` | Spatial | — | `{count, plz_list}` |

**CORS:** The backend already allows `https://*.lovable.app` origins.

**Error handling:** Show toast notifications for API errors. Show a "Backend Offline" banner if `/health` fails.

---

### SUPABASE

**Use Supabase for:**
- Auth (email/password signup + login)
- Storing user's saved analyses (so they persist across sessions)
- User settings/preferences

**Tables to create:**
- `profiles` — user_id (FK to auth.users), display_name, company_name, plan_tier (free/pro/business)
- `analyses` — id, user_id, type (predict/comply/renovate), input_json, result_json, created_at
- `apartments` — id, user_id, name, address, district, plz, specs_json, created_at (user's saved apartments for quick re-analysis)

**Row Level Security:** Users can only see/edit their own data.

---

### RESPONSIVE

- Desktop-first (property managers use desktop)
- Tablet-friendly (sidebar collapses)
- Mobile: landing page must work perfectly, dashboard is acceptable but not primary

---

### TECH STACK

- React 18+ with TypeScript
- Tailwind CSS for styling
- Recharts or Chart.js for data visualizations (SHAP bars, renovation comparison, compliance gauge)
- React Router for navigation
- Supabase JS client for auth + database
- Fetch/axios for API calls to FastAPI backend
- Lucide icons (geometric, matches brand)

---

### IMPORTANT NOTES

- This is a B2B product for property managers, NOT a consumer app. It should feel professional, data-rich, and trustworthy.
- All monetary values should use European format: €X.XX (comma for thousands in German locale, dot for decimals)
- The dashboard should feel like a tool you use daily, not a one-time calculator
- The landing page should feel like a premium SaaS product, not a template
- When no data is available, show the 5 demo apartments as examples with a "Try with demo data" prompt
- The "don't build the balcony" insight is the product's hero moment — make the renovation comparison chart visually impactful
