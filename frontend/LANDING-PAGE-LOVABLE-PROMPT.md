# RentSignal Landing Page — Lovable Update Prompt

Paste this into Lovable to update the existing landing page. The HTML prototype file is attached as visual reference.

---

## PROMPT

Update the RentSignal landing page to match the attached HTML design. Keep the existing design system (colors, fonts, components). Here are the specific changes:

---

### COLORS (update CSS variables if needed)

- Primary headings: `#004746` (deep teal)
- Accent/CTA: `#00BC72` (bright green)  
- Section labels: `#E8913A` (amber)
- CTA buttons: green with shadow (`box-shadow: 0 4px 14px rgba(0,188,114,0.35)`)
- Secondary buttons: teal outline (`border: 2px solid #004746`, hover fills solid teal)
- Headings font: General Sans, weight 600 (semibold)
- Body: Inter
- Data/monospace: JetBrains Mono

---

### SECTION ORDER (new)

```
1. Hero (updated copy)
2. Three Pillars — Comply · Optimize · Act (NEW — replaces old Predict/Comply/Renovate)
3. Built Different (renamed from "Why RentSignal", same card content)
4. Demo Moment — "Don't build the balcony" (updated copy + CTA)
5. Social Proof (unchanged, rename label to "THE NUMBERS")
6. Pricing (unchanged)
7. Bottom CTA — "Check your rent before your tenant does" (keep)
8. Footer (unchanged)
```

---

### SECTION 1: HERO — updated copy

**Tagline (pill badge above headline with green dot):**
> "Rent intelligence for the German rental market"

**Headline:**
> Know what every unit is worth.
> **Stay compliant.** *(in green)*
> Make the right move.

**Subheadline:**
> "Comply with the law, optimize every unit's rent, and act on the right data — from a single apartment to an entire portfolio."

**CTAs (unchanged):**
- "Try Free Compliance Check →" (green pill button with shadow)
- "Request Demo" (teal outline button)

**Trust badge (monospace, bordered box):**
> "Based on 10,275 Berlin apartments · 37 features · Sentinel-2 satellite data"

*(Note: changed from "37 ML features" to "37 features" and "Satellite spatial data" to "Sentinel-2 satellite data" — more concrete)*

---

### SECTION 2: THREE PILLARS — NEW (replaces features section)

**Section label (amber, monospace, uppercase):** "WHAT YOU GET"
**Section headline:** "Three things every landlord needs to know."

**Three cards — larger titles (1.5rem) with headline + body + detail footer:**

**Card 1: Comply**
- Icon: shield with checkmark
- Title: "Comply" (1.5rem, teal)
- Headline: "Know your legal position — always." (bold, 0.95rem)
- Body: "Check Mietpreisbremse compliance instantly. Calculate how much you can legally raise rent on existing tenants. See your energy cost exposure under the CO2 cost-sharing law. All before Conny does."
- Detail footer (monospace, light gray, separated by border-top): "§556d BGB · §558 BGB · §559 BGB · CO2KostAufG"

**Card 2: Optimize**
- Icon: signal/pulse waveform
- Title: "Optimize"
- Headline: "Know what every unit is worth — and what you're leaving on the table."
- Body: "Rent prediction with 37 features including satellite vegetation indices and transit proximity. See exactly why with a feature contribution breakdown — which factors push your rent up or down, and by how much."
- Detail footer: "R²=0.749 · 37 features · 190 Berlin postal codes"

**Card 3: Act**
- Icon: lightning bolt
- Title: "Act"
- Headline: "Make the right move — renovation, rent increase, or new acquisition."
- Body: "Dual-method renovation ROI: kitchen adds €4.01/m², balcony loses money. Generate a legally compliant rent increase letter in one click. Evaluate a neighborhood before you invest — rent range, spatial features, which renovations pay off there."
- Detail footer: "Renovation simulator · Mieterhöhung wizard · Neighborhood intelligence"

---

### SECTION 3: BUILT DIFFERENT — renamed, same content

**Section label:** "BUILT DIFFERENT" *(was "WHY RENTSIGNAL")*
**Section headline:** "Not another calculator. **Real intelligence.**" *(green on "Real intelligence.")*
**Subheadline:** "Conny tells tenants they're overpaying. We tell property managers where the money is — and where the risk is."

**Three cards — KEEP EXACTLY AS-IS:**
1. Satellite spatial features
2. Dual-method validation  
3. Explainable, not black-box (full width)

---

### SECTION 4: DEMO MOMENT — updated copy

**Section label (amber):** "THE INSIGHT"

**Headline (two lines):**
> "Most landlords assume balconies increase rent."
> "**The data disagrees.**" *(green)*

**Body:**
> "We matched 2,288 apartment pairs to isolate the effect of each renovation on rent — controlling for size, location, condition, and everything else. Kitchen renovation: +€4.01/m², 54-month payback, 26% annual ROI. Balcony: a negative market impact despite a positive legal passthrough."
>
> "Before you spend €25,000 on a balcony, see the data."

**Chart — simplified to 2 bars (was 4):**
- Kitchen: +€4.01/m² (green, full width)
- Balcony: −€0.72/m² (red, short)
- Chart title (monospace small): "Causal rent impact by renovation type · 2,288 matched pairs"
- Animated bars that fill on scroll into view

**CTA below chart:**
> "Run the renovation simulator →" (green pill button)

**Footer text under chart:**
> "Validated against independent demand-side estimation. Kitchen: +€4.01 vs +€4.13 (3% convergence between two methods)."

---

### SECTION 5: SOCIAL PROOF — label change only

Change section label from "TRUSTED METHODOLOGY" to "THE NUMBERS"
Everything else unchanged.

---

### SECTIONS 6-8: UNCHANGED

Pricing, Bottom CTA, Footer — no changes needed.

---

### COPY RULES

- Never use "AI-powered" in any headline
- Never use "CATE", "WTP", "propensity score matching", "synthetic conjoint"
- Say "feature contribution breakdown" not "SHAP values" 
- Say "demand-side estimation" not "willingness to pay"
- Say "real apartment matching" not "observational causal matching"
- The Conny line stays exactly as written — do not paraphrase
- All €/m² values in JetBrains Mono
