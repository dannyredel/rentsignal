# RentSignal Dashboard — Lovable Implementation Prompt

Paste this into Lovable to build the dashboard. Reference the HTML prototype screenshot for visual design.

---

## PROMPT

Update the RentSignal dashboard to match the new design. The dashboard is behind Supabase auth at `/dashboard`. I'm attaching an HTML design prototype as visual reference — match the layout, spacing, and component patterns closely.

---

### DESIGN SYSTEM (match the landing page)

- **Colors:** Deep teal `#004746` for headings/sidebar, bright green `#00BC72` for accents/CTAs/positive values, red `#DC2626` for negative/non-compliant, amber `#E8913A` for labels/warnings
- **Fonts:** General Sans (semibold 600) for headings, Inter for body, JetBrains Mono for all €/m² values, stats, and data
- **Components:** Sharp-cornered cards (no rounded/bubbly), 0.5px borders, pill-shaped buttons with rounded corners (24px radius), monospace for all monetary values
- **Sidebar:** Dark teal background (`#004746`), white text, green active indicator on left border

---

### SIDEBAR NAVIGATION

Left sidebar (collapsible on mobile, always visible on desktop):

1. **Portfolio** — home/default view (`/dashboard`)
2. **Add units** — ingestion flows (`/dashboard/add`)
3. *(separator)*
4. **Comply** — compliance risk view (`/dashboard/comply`)
5. **Optimize** — revenue gaps view (`/dashboard/optimize`)
6. **Act** — tools launcher (`/dashboard/act`)
7. **Neighborhoods** — PLZ intelligence (`/dashboard/neighborhoods`)
8. *(separator)*
9. **Settings** — user prefs (`/dashboard/settings`)

Top bar: page title on left, "Import CSV" (outline teal button) + "+ Add unit" (green pill button) on right.

---

### PAGE 1: PORTFOLIO (`/dashboard`)

**Top stats row (4 cards):**
- "Total units" — count
- "Avg predicted rent" — €X.XX/m² (monospace)
- "Compliance exposure" — €X,XXX/yr (red if > 0)
- "Revenue gap" — +€X,XXX/mo (green)

Data source: `GET /portfolio/summary`

**Alerts banner (dismissible, amber background):**
- Shows pending alerts from `GET /monitor/alerts`
- Example: "3 units drifted above legal maximum since last week — review compliance risk"
- Link to Comply page

**Portfolio map (Leaflet):**
- Full-width map showing all portfolio units as circle markers
- Color-coded by compliance status: green = compliant, red = non-compliant, amber = exempt
- Tooltip on hover: address, PLZ, rent gap
- Click marker → navigate to unit detail
- Use CartoDB light tiles: `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png`
- Center on Berlin (52.51, 13.40), zoom 11
- Legend below map: green = Compliant, red = Non-compliant, amber = Exempt

Data source: `GET /portfolio/units` (use lat/lon from address resolution)

**Units table:**
- Sortable columns: Address, PLZ, m², Current rent, Predicted rent, Gap, Compliance status, Last analyzed
- Gap column: green monospace for positive (underpriced), red for negative (overpriced)
- Compliance status: colored dot + badge (green "Compliant", red "Non-compliant", amber "Exempt")
- Click any row → navigate to unit detail page
- Sort by compliance risk by default (non-compliant first)

Data source: `GET /portfolio/units`

**Revenue gap breakdown chart (below units table):**
- Horizontal diverging bar chart showing each unit's rent gap (predicted minus current)
- Green bars extend right for underpriced units (revenue opportunity)
- Red bars extend left for overpriced units (compliance risk)
- Each bar labeled with address (left) and €/m² gap in monospace (on the bar)
- Sorted from most underpriced (top) to most overpriced (bottom)
- Zero line down the center divides "opportunity" from "risk"
- Chart title: "Where the money is — and where the risk is"
- Below chart: aggregate annotation: "Total revenue gap: +€2,180/month across X underpriced units"
- Click any bar → navigate to unit detail

Data source: `GET /portfolio/revenue-gaps`

**Empty state (0 units):**
- Centered message: "Add your first unit to get started"
- Two buttons: "Add unit" (green) + "Import portfolio" (teal outline)
- Below: "Or try with demo data" link → loads 5 demo apartments from `GET /demo/apartments`

---

### PAGE 2: ADD UNITS (`/dashboard/add`)

Two distinct flows displayed side by side on desktop:

**LEFT CARD: Quick Add (for 1-5 units)**

Form with these fields:
- Address (text input with autocomplete) — calls `GET /address/autocomplete?q=` on keystroke, shows dropdown suggestions. On select → calls `POST /address/resolve` → auto-fills PLZ, district, building year
- Living space (m², number)
- Rooms (number)
- Year built (number, pre-filled from address resolve)
- Current rent (€/m², number)
- Condition (dropdown): Well kept, Mint condition, Needs renovation, First time use, By arrangement
- Heating type (dropdown): Central heating, Gas, District heating, Floor heating, etc.
- Checkboxes row: Kitchen, Balcony, Elevator, Cellar, Garden
- "Save and analyze" button (green, full width)

On save: `POST /portfolio/units` → then immediately trigger `POST /portfolio/analyze` for this unit → show loading → redirect to unit detail with results.

**RIGHT CARD: Bulk Import (CSV)**

3-step wizard:
1. **Upload** — drag-and-drop zone + file picker. Accepts .csv, .xlsx, .xls. On upload → `POST /portfolio/import/csv` → returns detected columns
2. **Map columns** — show detected column names on left, our required fields on right with dropdown selectors. Example: "Wohnfläche" → "Living space (m²)". Show preview of first 3 rows below mapping.
3. **Confirm** — summary: "X units detected. Y fields mapped." → `POST /portfolio/import/confirm` → shows progress bar polling `GET /portfolio/import/{job_id}` → on completion: "X units imported. Run batch analysis?" → `POST /portfolio/analyze`

---

### PAGE 3: COMPLY (`/dashboard/comply`)

**Top stats (3 cards):**
- "Total annual exposure" — €X,XXX/yr (red, large)
- "Non-compliant units" — X of Y (red)
- "Avg headroom (compliant)" — €X.XX/m² (green)

Data source: `GET /portfolio/compliance-risk`

**Compliance risk table:**
- Sorted by annual exposure descending (worst first)
- Columns: Address, Current rent, Legal max, Overpayment (€/m²), Annual exposure (€/yr), Status
- Red values for overpayment and exposure
- Click row → unit detail, Comply tab

---

### PAGE 4: OPTIMIZE (`/dashboard/optimize`)

**Top stats (3 cards):**
- "Monthly revenue gap" — +€X,XXX (green)
- "Underpriced units" — X of Y
- "Avg gap (underpriced)" — +€X.XX/m² (green)

Data source: `GET /portfolio/revenue-gaps`

**Revenue gaps table:**
- Sorted by gap descending (most underpriced first)
- Columns: Address, Current rent, Predicted rent, Gap (€/m²), Gap (€/month), Gap (%)
- Green monospace for positive gaps
- Click row → unit detail, Optimize tab

---

### PAGE 5: ACT (`/dashboard/act`)

Three tool cards in a grid (click to enter each tool):

1. **Renovation simulator** — icon: wrench. "See which renovations pay off for any unit. Kitchen vs balcony — backed by 2,288 matched pairs." → Select a unit from portfolio, run `POST /renovate`, show renovation cards with uplift/payback/ROI/cost + comparison chart.

2. **Rent increase letter** — icon: document. "Calculate §558 BGB increase and generate a Mieterhöhungsverlangen — ready to sign." → Select unit, run `POST /rent-increase/calculate`, show result, option to generate PDF via `POST /rent-increase/letter`.

3. **Neighborhood intelligence** — icon: map pin. "Evaluate a PLZ before you invest." → Links to Neighborhoods page.

---

### PAGE 6: NEIGHBORHOODS (`/dashboard/neighborhoods`)

**PLZ selector:**
- Two dropdown selectors for side-by-side comparison
- "Compare" button

**Neighborhood map (Leaflet):**
- Berlin map with PLZ areas shown as colored circles
- Color intensity = average predicted rent (light green = low, dark green = high)
- Selected/compared PLZs outlined with dashed teal border
- Tooltip: PLZ + avg rent
- Use `GET /neighborhood/map` for all PLZ data

Data source: `GET /neighborhood/compare?plz=10961,10435`

**Comparison cards (2x2 grid):**
- Predicted rent range
- Top renovation ROI in this PLZ
- Spatial features vs Berlin average (horizontal bars: transit, restaurants, green space)
- Compliance pressure (% estimated above legal max)

---

### PAGE 7: UNIT DETAIL (`/dashboard/units/:id`)

Accessed by clicking any unit row from any table, or any map pin.

**Header:** Address, PLZ, district, basic specs (m², rooms, year)
**Back button:** "← Back to portfolio"

**4 tabs:**

**Tab 1: Optimize**
- Left panel: unit specs card (all saved fields)
- Right panel: 
  - Big number card: predicted rent, gap analysis if current rent exists
  - Feature contribution breakdown: horizontal bar chart (top 8 features, positive bars in green, negative in red, monospace values)
  - Model info badge

Data: `GET /portfolio/units/{id}` (cached analysis)

**Tab 2: Comply**
- Compliance status banner (green/red, full width)
- 4 stat cards: legal max, your rent, overpayment, annual exposure
- Mietspiegel range bar: horizontal bar showing lower/mid/upper range, red marker at legal max (110%)
- Equipment adjustments list
- §558 Mieterhöhung section: "Can you increase?" + calculation

Data: compliance data from cached unit analysis + `POST /rent-increase/calculate`

**Tab 3: Act**
- 4 renovation cards in 2x2 grid (kitchen, balcony, elevator, garden)
- Each card: left border color (green = positive, red = negative), uplift in monospace, payback/ROI/cost below
- "Already has" badge for features the unit already has (grayed out)

Data: `POST /renovate` with unit specs

**Tab 4: Spatial**
- **Leaflet map** centered on unit address with:
  - Unit pin in center (teal, prominent)
  - 1km radius circle (dashed teal, light fill)
  - Transit stations as blue dots
  - Restaurants as small amber dots
  - NDVI vegetation overlay: grid of semi-transparent green rectangles showing vegetation density
- Legend below map
- Spatial metric cards (2x2): transit count + nearest, restaurant count + percentile, NDVI mean + comparison, NDBI mean

Data: `GET /spatial/{plz}` + unit coordinates

---

### LEAFLET MAP SETUP (all maps)

```
Tile layer: https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png
Attribution: © OpenStreetMap contributors © CARTO
Default zoom controls: top-right
No scroll zoom on portfolio/neighborhood maps (prevent accidental scroll hijack)
```

Install: `npm install leaflet react-leaflet @types/leaflet`

---

### API CONNECTION

Same as existing setup — all API calls to `VITE_API_URL` (default `http://localhost:8000`).

**New endpoints to connect:**

| Method | Endpoint | Page |
|--------|----------|------|
| GET | `/portfolio/units` | Portfolio, all tables |
| GET | `/portfolio/units/{id}` | Unit detail |
| POST | `/portfolio/units` | Add unit (Quick add) |
| PUT | `/portfolio/units/{id}` | Edit unit |
| DELETE | `/portfolio/units/{id}` | Delete unit |
| GET | `/portfolio/summary` | Portfolio stats |
| GET | `/portfolio/compliance-risk` | Comply page |
| GET | `/portfolio/revenue-gaps` | Optimize page |
| POST | `/portfolio/import/csv` | CSV upload |
| POST | `/portfolio/import/confirm` | CSV confirm |
| GET | `/portfolio/import/{job_id}` | Import progress |
| POST | `/portfolio/analyze` | Batch analysis |
| GET | `/portfolio/analyze/{job_id}` | Analysis progress |
| GET | `/address/autocomplete?q=` | Address search |
| POST | `/address/resolve` | Address → PLZ/district |
| POST | `/rent-increase/calculate` | §558 calculation |
| POST | `/rent-increase/letter` | Generate PDF letter |
| GET | `/monitor/alerts` | Portfolio alerts |
| POST | `/monitor/alerts/{id}/dismiss` | Dismiss alert |
| GET | `/neighborhood/map` | All PLZs for map |
| GET | `/neighborhood/compare?plz=` | PLZ comparison |

**Existing endpoints (keep connected):**
| POST | `/predict` | Unit prediction |
| POST | `/compliance` | Compliance check |
| POST | `/renovate` | Renovation simulation |
| GET | `/spatial/{plz}` | Spatial features |

---

### SUPABASE TABLES (add to existing)

Add these tables for portfolio persistence:

```sql
-- Units in user's portfolio
CREATE TABLE portfolio_units (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  name TEXT, -- friendly name (optional)
  address TEXT NOT NULL,
  plz TEXT,
  district TEXT,
  lat FLOAT,
  lon FLOAT,
  living_space FLOAT,
  rooms INT,
  year_built INT,
  floor INT,
  building_floors INT,
  condition TEXT,
  interior_quality TEXT,
  heating_type TEXT,
  energy_kwh FLOAT,
  flat_type TEXT,
  building_era TEXT,
  has_kitchen BOOLEAN DEFAULT FALSE,
  has_balcony BOOLEAN DEFAULT FALSE,
  has_elevator BOOLEAN DEFAULT FALSE,
  has_cellar BOOLEAN DEFAULT FALSE,
  has_garden BOOLEAN DEFAULT FALSE,
  is_new_construction BOOLEAN DEFAULT FALSE,
  current_rent FLOAT, -- €/m² nettokalt
  -- Cached analysis results
  predicted_rent FLOAT,
  compliance_status TEXT, -- compliant, non_compliant, exempt
  legal_max_rent FLOAT,
  rent_gap FLOAT,
  annual_exposure FLOAT,
  last_analyzed_at TIMESTAMPTZ,
  analysis_json JSONB, -- full API response cached
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE portfolio_units ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own units" ON portfolio_units FOR ALL USING (auth.uid() = user_id);

-- Import jobs
CREATE TABLE import_jobs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, mapping, processing, completed, failed
  file_name TEXT,
  detected_columns JSONB,
  column_mapping JSONB,
  total_rows INT,
  processed_rows INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE import_jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own jobs" ON import_jobs FOR ALL USING (auth.uid() = user_id);
```

---

### IMPORTANT NOTES

- Portfolio map pins should update live as units are added/analyzed
- The "Add unit" button in the top bar should be accessible from ANY page (it's the most common action)
- When a unit has no analysis yet, show gray compliance dot and "—" for predicted rent/gap
- Address autocomplete should debounce at 300ms
- CSV column mapper should auto-detect common German column names: Wohnfläche, Zimmer, Baujahr, Kaltmiete, PLZ, Bezirk, Heizung, Zustand
- All map markers should be interactive (hover tooltip, click to navigate)
- Spatial map NDVI overlay: use a grid of semi-transparent green rectangles (opacity proportional to vegetation index) — this simulates the satellite data visualization
- The unit detail page should be bookmarkable at `/dashboard/units/:id`
