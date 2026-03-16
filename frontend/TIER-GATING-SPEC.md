# RentSignal — Tier Gating & Dashboard Adaptation Spec

*Last updated: 2026-03-16*

---

## Design Philosophy

**Show value before gating.** The user should always see *what* they're missing before hitting a wall. Show the locked feature with blurred/dimmed results or a preview, then gate the full output. Never hide a feature entirely — hidden features can't sell themselves.

**Gate outputs, not inputs.** Let any user fill out any form. Gate the *result*, not the *form*. A Free user who fills out a renovation form and clicks "Simulate" should see a teaser of the result with an upgrade prompt — not a locked button. They've already invested effort; reward that with a glimpse, then convert.

**Upgrade prompts are contextual, not generic.** "Upgrade to Pro" is weak. "This unit is underpriced by €1.67/m² — unlock the full breakdown for €29/month" is strong. Every upgrade prompt should reference the specific value the user is about to unlock, ideally with their own data.

---

## Tier Matrix: What Each Tier Sees

### Sidebar Navigation by Tier

| Sidebar Item | Free | Pro | Business |
|-------------|------|-----|----------|
| Portfolio | ✅ (max 3 units) | ✅ (max 15 units) | ✅ (unlimited) |
| Add units | ✅ (manual form only) | ✅ (form + CSV template, max 15) | ✅ (form + intelligent CSV mapper) |
| Comply | ✅ (Mietpreisbremse only) | ✅ (+ Mieterhöhung + CO2) | ✅ (+ portfolio risk dashboard) |
| Optimize | ✅ (3 predictions/mo) | ✅ (unlimited + full breakdown) | ✅ (+ batch + revenue gap ranking) |
| Act | 🔒 Visible but locked | ✅ | ✅ (+ acquisition comparison) |
| Neighborhoods | 🔒 Visible but locked | ✅ | ✅ (+ PDF export) |
| Settings | ✅ | ✅ | ✅ |

**Key principle:** All sidebar items are always visible. Locked items show a small lock icon and a "Pro" or "Business" badge. Clicking a locked item opens the page with an upgrade prompt — not a dead end.

---

## Page-by-Page Gating

### 1. PORTFOLIO

| Element | Free | Pro | Business |
|---------|------|-----|----------|
| Stats row | ✅ (shows for their units) | ✅ | ✅ |
| Portfolio map | ✅ (up to 3 pins) | ✅ (up to 15 pins) | ✅ (unlimited) |
| Units table | ✅ (max 3 rows) | ✅ (max 15 rows) | ✅ (unlimited) |
| Revenue gap breakdown chart | ✅ (3 bars) | ✅ (up to 15 bars) | ✅ (unlimited, scrollable) |
| Alerts banner | ❌ hidden | ✅ | ✅ |
| "Add unit" button | ✅ | ✅ | ✅ |
| "Import CSV" button | 🔒 shows "Pro" badge | ✅ (template CSV) | ✅ (any format) |
| Batch "Analyze all" | ❌ hidden | ✅ | ✅ |

**Unit limit enforcement:**
- Free: when user tries to add 4th unit → upgrade prompt: "Free accounts include up to 3 units. Upgrade to Pro (€29/month) to manage up to 15."
- Pro: when user tries to add 16th unit → upgrade prompt: "Pro accounts include up to 15 units. Upgrade to Business (€99/month) for unlimited units."
- Enforce in both frontend (disable Add button, show counter "3/3 units") and backend (reject POST /portfolio/units if over limit).

**Portfolio stats for Free users:**
Show the stats but with a subtle nudge. If they have 3 units and there's a revenue gap: "You're leaving +€340/month on the table across 3 units. Imagine what you'd find across your full portfolio."

**Revenue gap breakdown chart (below units table):**
A horizontal bar chart showing each unit's rent gap (predicted − current) sorted from most underpriced to most overpriced. Green bars extend right for underpriced units (revenue opportunity), red bars extend left for overpriced units (compliance risk). Each bar is labeled with the address and the €/m² gap in monospace. The chart visually connects the aggregate stat cards ("Revenue gap: +€2,180/mo") to the individual units that make up that number.

- Free: shows 3 bars (their 3 units). If the gap suggests more value: "These are just 3 units. Imagine the full picture."
- Pro: shows up to 15 bars. Full unit breakdown.
- Business: shows all units with scrollable chart. Aggregate annotation: "Total gap: +€8,940/mo across 147 units."

Data source: `GET /portfolio/revenue-gaps` (same endpoint as Optimize page, reused here in chart form)

---

### 2. ADD UNITS

| Element | Free | Pro | Business |
|---------|------|-----|----------|
| Quick add form | ✅ | ✅ | ✅ |
| Address autocomplete | ✅ | ✅ | ✅ |
| CSV upload (left panel) | 🔒 Dimmed with "Pro" overlay | ✅ (our template, max 15) | ✅ (any format, unlimited) |
| Intelligent CSV mapper | ❌ | ❌ | ✅ |
| Unit counter | "1/3 units" | "5/15 units" | "147 units" (no limit shown) |

**CSV upload gating (Free → Pro):**
The CSV card is visible but overlaid with a frosted glass effect and centered text: "Import your portfolio from CSV. Available on Pro." + "Upgrade to Pro — €29/month" button. The form fields behind the overlay are slightly visible (blurred) to show what they're missing.

**CSV mapper gating (Pro → Business):**
Pro users see the upload step but get a simplified flow: "Upload our CSV template" with a download link for the template. They don't get the intelligent column mapper. A small note: "Using a different format? Business tier includes automatic column detection for any spreadsheet."

---

### 3. COMPLY

| Element | Free | Pro | Business |
|---------|------|-----|----------|
| Mietpreisbremse check | ✅ (unlimited) | ✅ | ✅ |
| Compliance result (full) | ✅ | ✅ | ✅ |
| Mietspiegel breakdown | ✅ | ✅ | ✅ |
| §558 Mieterhöhung calc | 🔒 Teaser | ✅ | ✅ |
| CO2KostAufG energy exposure | 🔒 Teaser | ✅ | ✅ |
| Portfolio compliance risk table | ❌ | 🔒 Shows top 3 + blur | ✅ (full table, sortable) |
| "Total annual exposure" stat | ❌ | ✅ (for their units) | ✅ |

**Mieterhöhung teaser (Free → Pro):**
Free users see the §558 section but with the result blurred. Above the blur: "Can you raise rent on this tenant? Pro users get the full §558 calculation + a ready-to-send letter." Button: "Unlock for €29/month".

**Portfolio compliance risk (Pro → Business):**
Pro users see the compliance risk table but only the top 3 rows (their highest-exposure units). Below: a blurred section with "You have X more units. Business tier shows your full compliance risk — ranked by annual exposure, €X,XXX total." Button: "Upgrade to Business".

---

### 4. OPTIMIZE

| Element | Free | Pro | Business |
|---------|------|-----|----------|
| Prediction (result) | ✅ (3/month) | ✅ (unlimited) | ✅ |
| Predicted rent big number | ✅ | ✅ | ✅ |
| Rent gap | ✅ (if current rent provided) | ✅ | ✅ |
| Feature contribution (top 3) | ✅ | — | — |
| Feature contribution (full) | 🔒 Blurred below top 3 | ✅ (all features) | ✅ |
| Revenue gap table | ❌ | 🔒 Top 3 + blur | ✅ (full, sortable) |
| Portfolio monitoring alerts | ❌ | ✅ (up to 15 units) | ✅ |
| Weekly digest email | ❌ | ✅ | ✅ |
| Comparable benchmarking | ❌ | ❌ | ✅ |

**Prediction counter (Free):**
Show "2 of 3 predictions remaining this month" below the predict button. When exhausted: "You've used all 3 predictions this month. Resets on [date]. Or upgrade to Pro for unlimited."

**Feature contribution teaser (Free → Pro):**
Show the top 3 features clearly, then the remaining features as blurred rows with a gradient overlay. Text over the blur: "See all 37 features contributing to this prediction." Button: "Unlock full breakdown — €29/month".

This is the sharpest upgrade trigger: they can see that more features are there, they just can't read them.

---

### 5. ACT

| Element | Free | Pro | Business |
|---------|------|-----|----------|
| Act page access | 🔒 Locked page | ✅ | ✅ |
| Renovation simulator | ❌ | ✅ | ✅ |
| Mieterhöhung wizard | ❌ | ✅ | ✅ |
| Mieterhöhung letter PDF | ❌ | ✅ | ✅ |
| Neighborhood intelligence | ❌ | ✅ (view only) | ✅ (+ PDF export) |
| Acquisition comparison | ❌ | ❌ | ✅ (up to 5 candidates) |

**Act page locked state (Free):**
Show the three tool cards but with a full-page overlay: "Renovation simulator, rent increase letters, and neighborhood intelligence are available on Pro." Show a preview: the "don't build the balcony" chart from the landing page, embedded. This reminds them of the demo moment and creates desire. Button: "Start Pro trial — €29/month".

**Acquisition comparison (Pro → Business):**
Pro users see the Neighborhood intelligence page but without the comparison feature. A card at the bottom: "Compare up to 5 candidate properties side by side. Available on Business." Button: "Upgrade to Business".

---

### 6. NEIGHBORHOODS

| Element | Free | Pro | Business |
|---------|------|-----|----------|
| Page access | 🔒 Locked page | ✅ | ✅ |
| PLZ selector | — | ✅ | ✅ |
| Neighborhood map | — | ✅ | ✅ |
| Spatial comparison cards | — | ✅ | ✅ |
| Side-by-side PLZ compare | — | ✅ | ✅ |
| PDF export | — | 🔒 "Business" badge | ✅ |
| Acquisition analysis | — | ❌ | ✅ |

---

### 7. UNIT DETAIL (tabs)

| Tab | Free | Pro | Business |
|-----|------|-----|----------|
| Optimize tab | ✅ (top 3 features) | ✅ (full) | ✅ |
| Comply tab | ✅ (Mietpreisbremse) | ✅ (+ §558 + CO2) | ✅ |
| Act tab | 🔒 Locked with preview | ✅ | ✅ |
| Spatial tab | 🔒 Locked with preview | ✅ | ✅ |

**Locked tab behavior:**
Tab is visible and clickable. Content area shows a blurred preview of what the output looks like (use demo data or a static screenshot) with a centered upgrade card. The tab label has a small lock icon.

---

## Upgrade Prompt Patterns

### Pattern 1: Blurred preview (for partial results)
Used when the user has *some* result but we're withholding depth.
```
┌─────────────────────────────────────────┐
│  Top 3 features (visible, clear)        │
│  Living space          +€1.82/m²        │
│  Location              +€1.54/m²        │
│  Restaurants           +€1.12/m²        │
│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← gradient blur
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░░ See all 37 features ░░░░░░░░░░░░░░ │
│  ░░ [Unlock — €29/month] ░░░░░░░░░░░░░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────┘
```

### Pattern 2: Locked page with value preview
Used when the entire feature is locked.
```
┌─────────────────────────────────────────┐
│                                         │
│    🔒  Renovation simulator             │
│                                         │
│    Kitchen: +€4.01/m²                   │
│    Balcony: -€0.72/m²                   │
│    [mini bar chart preview]             │
│                                         │
│    See which renovations pay off —      │
│    before you spend.                    │
│                                         │
│    [ Start Pro trial — €29/month ]      │
│                                         │
└─────────────────────────────────────────┘
```

### Pattern 3: Limit counter with nudge
Used for metered features (predictions, units).
```
┌─────────────────────────────────────────┐
│  ⚡ 1 of 3 predictions remaining       │
│     Resets March 1 · or upgrade for     │
│     unlimited predictions               │
└─────────────────────────────────────────┘
```

### Pattern 4: Contextual value-based upgrade
Used when we can calculate the specific € value for this user.
```
┌─────────────────────────────────────────┐
│  Your 3 units have a combined revenue   │
│  gap of +€340/month.                    │
│                                         │
│  Pro users can monitor up to 15 units   │
│  and get alerts when gaps change.       │
│                                         │
│  [ Upgrade to Pro — €29/month ]         │
│                                         │
│  One prevented Conny complaint pays     │
│  for 10 years of Pro.                   │
└─────────────────────────────────────────┘
```

---

## Conversion Triggers (When to Show Upgrade Prompts)

| Trigger | From → To | Where | Message |
|---------|-----------|-------|---------|
| Prediction limit hit | Free → Pro | Optimize page | "You've used all 3 predictions. Upgrade for unlimited." |
| Unit limit hit | Free → Pro | Add unit form | "Free includes up to 3 units. Pro gives you 15." |
| Feature breakdown scrolled | Free → Pro | Unit detail, Optimize tab | Blurred features below top 3 |
| Clicks "Act" tab or page | Free → Pro | Act page / Unit detail Act tab | Locked page with renovation chart preview |
| Clicks "Spatial" tab | Free → Pro | Unit detail Spatial tab | Locked with map preview |
| Clicks "Neighborhoods" | Free → Pro | Neighborhoods page | Locked page |
| Tries CSV upload | Free → Pro | Add units page | Frosted overlay on CSV card |
| Clicks Mieterhöhung section | Free → Pro | Unit detail, Comply tab | Blurred result |
| Unit limit hit (21st) | Pro → Business | Add unit form | "Pro includes up to 15. Business is unlimited." |
| Wants full compliance table | Pro → Business | Comply page | Top 3 visible, rest blurred |
| Wants full revenue gap table | Pro → Business | Optimize page | Top 3 visible, rest blurred |
| Clicks "Export PDF" on neighborhood | Pro → Business | Neighborhoods page | "PDF exports on Business" badge |
| Clicks acquisition comparison | Pro → Business | Act page | "Compare properties on Business" |
| Wants monthly portfolio report | Pro → Business | Portfolio page | "Monthly client-ready PDF on Business" |

---

## Backend Enforcement

Frontend gating is a UX decision. Backend enforcement is a security decision. Both are needed.

### Middleware: Tier Check

Every protected endpoint checks the user's tier from their profile before executing:

```python
# Pseudocode for FastAPI middleware
async def check_tier(user_id: str, required_tier: str):
    profile = await get_user_profile(user_id)
    tier_hierarchy = {"free": 0, "pro": 1, "business": 2, "enterprise": 3}
    if tier_hierarchy[profile.plan_tier] < tier_hierarchy[required_tier]:
        raise HTTPException(403, detail={
            "error": "tier_required",
            "required": required_tier,
            "current": profile.plan_tier,
            "message": f"This feature requires {required_tier} tier"
        })
```

### Endpoint Tier Requirements

| Endpoint | Free | Pro | Business |
|----------|------|-----|----------|
| POST /portfolio/units | ✅ (max 3) | ✅ (max 15) | ✅ |
| POST /predict | ✅ (3/month) | ✅ | ✅ |
| POST /compliance | ✅ | ✅ | ✅ |
| POST /renovate | ❌ | ✅ | ✅ |
| POST /rent-increase/calculate | ❌ | ✅ | ✅ |
| POST /rent-increase/letter | ❌ | ✅ | ✅ |
| POST /compliance/energy | ❌ | ✅ | ✅ |
| GET /portfolio/compliance-risk | ❌ | ✅ (own units) | ✅ |
| GET /portfolio/revenue-gaps | ❌ | ✅ (own units) | ✅ |
| POST /portfolio/import/csv | ❌ | ✅ (max 15) | ✅ |
| GET /neighborhood/* | ❌ | ✅ | ✅ |
| GET /neighborhood/*/report | ❌ | ❌ | ✅ |
| POST /acquisition/* | ❌ | ❌ | ✅ |
| GET /portfolio/report/monthly | ❌ | ❌ | ✅ |
| POST /monitor/subscribe | ❌ | ✅ | ✅ |

### Rate Limits

| Tier | Predictions/month | Units | CSV rows/import | API calls/day |
|------|-------------------|-------|-----------------|---------------|
| Free | 3 | 3 | 0 | 50 |
| Pro | Unlimited | 15 | 15 | 1,000 |
| Business | Unlimited | Unlimited | Unlimited | 10,000 |
| Enterprise | Unlimited | Unlimited | Unlimited | Custom |

### Supabase Profile Table Update

```sql
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS
  predictions_used_this_month INT DEFAULT 0,
  predictions_reset_date DATE DEFAULT (date_trunc('month', now()) + interval '1 month')::date;
```

Reset logic: a nightly job checks if `predictions_reset_date <= today()` and resets the counter.

---

## Dashboard Adaptation by Tier

### What the Dashboard Looks Like Per Tier

**Free user (1-3 units):**
- Sidebar: all items visible, Act + Neighborhoods show lock icon + "Pro" badge
- Portfolio: stat cards + map + table (up to 3 units), no alerts banner
- Add units: Quick add form only, CSV card frosted/locked
- Comply: Mietpreisbremse works fully, §558 and CO2 sections blurred
- Optimize: predictions work (counter shown), feature breakdown shows top 3 + blur
- Act: locked page with renovation chart preview
- Neighborhoods: locked page
- Unit detail: Optimize + Comply tabs work (with partial gates), Act + Spatial tabs locked with previews

**Pro user (5-15 units):**
- Sidebar: all items accessible, no lock icons
- Portfolio: full stats + map + table + alerts banner
- Add units: Quick add + CSV template upload (max 15)
- Comply: full Mietpreisbremse + §558 + CO2, compliance risk table (own units)
- Optimize: unlimited predictions, full feature breakdown, revenue gaps (own units)
- Act: all three tools fully functional
- Neighborhoods: full access, no PDF export
- Unit detail: all 4 tabs fully functional

**Business user (15+ units):**
- Everything in Pro, plus:
- Unlimited units + intelligent CSV mapper
- Full compliance risk table (sortable, filterable, exportable)
- Full revenue gap ranking
- Monthly portfolio health PDF
- Neighborhood PDF export
- Acquisition comparison (up to 5 candidates)

---

## Trial & Conversion Mechanics

### Pro Trial (14 days)
- Triggered when Free user clicks any upgrade prompt
- Full Pro access for 14 days, no credit card required
- Day 1: welcome email with "here's what you can do now"
- Day 10: reminder email with "your trial ends in 4 days"
- Day 14: trial ends, reverts to Free, email: "your portfolio is no longer being watched"
- At any point during trial: "Subscribe to Pro — €29/month" in a persistent but non-intrusive banner

### Upgrade Moments (ranked by conversion likelihood)
1. **Prediction limit hit** — highest intent, user just tried to use the product
2. **Feature breakdown blur** — they can see value exists, want to read it
3. **Act tab click** — they have a renovation question, we have the answer
4. **Unit limit hit** — they have more properties, natural expansion
5. **CSV import attempt** — they have a portfolio, want to onboard it all

### Downgrade Handling
When a user downgrades from Pro to Free:
- Units beyond the 3-unit limit become "archived" — visible but not analyzable
- "You have 12 archived units. Upgrade to reactivate them."
- No data is deleted — just gated
- Monitoring stops, alerts stop, digest emails stop
- A "your portfolio is no longer being watched" email is sent

---

## Frontend Implementation Notes

### Tier Context Provider
```typescript
// React context that wraps the app
interface TierContext {
  tier: 'free' | 'pro' | 'business' | 'enterprise';
  limits: {
    maxUnits: number;       // 3, 15, Infinity
    predictionsLeft: number; // 3, Infinity
    canAccessAct: boolean;
    canAccessNeighborhoods: boolean;
    canImportCSV: boolean;
    canExportPDF: boolean;
    canCompareAcquisitions: boolean;
    fullFeatureBreakdown: boolean;
    portfolioComplianceTable: boolean;
    portfolioRevenueTable: boolean;
    monitoringAlerts: boolean;
  };
  unitCount: number;
  showUpgrade: (feature: string, context?: object) => void;
}
```

### Locked Feature Component
```typescript
// Reusable component for any locked feature
<LockedFeature
  requiredTier="pro"
  feature="renovation_simulator"
  preview={<RenovationChartPreview />}  // optional preview content
  message="See which renovations pay off — before you spend."
  ctaText="Start Pro trial — €29/month"
/>
```

### Blur Overlay Component
```typescript
// For partial results (feature breakdown, tables)
<BlurGate
  requiredTier="pro"
  message="See all 37 features contributing to this prediction."
>
  {/* Full feature list renders here, CSS blur applied */}
</BlurGate>
```

### Usage Counter Component
```typescript
// For metered features
<UsageCounter
  used={2}
  limit={3}
  feature="predictions"
  resetDate="2026-04-01"
/>
// Renders: "⚡ 1 of 3 predictions remaining · Resets Apr 1"
```
