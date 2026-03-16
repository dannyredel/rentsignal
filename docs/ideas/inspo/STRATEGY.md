# BeeSignal Strategy & Roadmap

Vision, build sequence, content strategy, and growth plan.

*Updated March 2026 — reflects category naming ("Continuous Pricing Intelligence"), vocabulary decisions, framing framework (A/B), and updated content cluster language from the March 2026 positioning session.*

---

## 1. The Vision

A $5M ARR SaaS company in 2028 opens BeeSignal and sees:

- **Live demand feed:** "Your estimated willingness to pay in the SMB segment has drifted 22% above your current price over the past 6 months. Probability that you are underpricing this segment: 84%."
- **Pricing event log:** Every price change auto-triggers a causal event study. The effect on churn and expansion is calculated and stored. Over three years, a documented causal history of every pricing decision.
- **Model simulator:** "If you move from per-seat to usage-based, here is the expected ARR impact, modeled with 95% posterior credible intervals."
- **Tier optimizer:** "Based on current feature usage and last quarter's demand distribution, here is the optimal tier architecture for your current ICP mix."

None of this requires owning billing. All of it requires owning the methodology and the data relationships. That is where the moat lives.

### What We Are NOT Building

- Not billing infrastructure (Stripe's territory)
- Not a price management / CPQ platform (PriceFx's territory)
- Not "Paddle on steroids" — that puts us in competition with $1B+ companies
- We are the **intelligence layer above any billing stack**

---

## 2. Build Sequence

The sequence is dictated by data dependencies, not ambition:

1. **Capability A — Simulate the Market** (demand experiments + demand curves) — standalone, produces immediate value, requires no customer behavioral data → **MVP anchor**
2. **Capability B — Track Causal Impact** (causal event studies) — requires the customer to have a price change in their history + enough Stripe panel data → **month 4–6 feature**
3. **Capability C — Recalibrate** (continuous demand monitoring) — requires a calibrated demand model already running → **month 6+ feature, built on A**

### Phased Revenue Model

| Phase | Timeline | Mode | Revenue Per Customer |
|-------|----------|------|---------------------|
| 1. Service-Led | Month 1–4 | Manual studies, you are the product | $3,500/study |
| 2. Product-Led Service | Month 4–8 | Partially automated, 5–7 day delivery | $3,500/study + $300–500/mo signal feed |
| 3. Platform | Month 9–18 | Self-serve + automated pipeline + monitoring | Per-study + $1K–5K/mo platform |

### Year 1 Revenue Milestones

| Month | Studies | Signal Feed Subs | MRR |
|-------|---------|-----------------|-----|
| 3 | 2–3 | 0 | $7K–10K |
| 6 | 5–6 | 2–4 | $18K–22K |
| 9 | 8–10 | 8–12 | $35K–47K |
| 12 | 12–15 | 20–30 | $55K–75K |

**Year 2 target:** $700K–$900K ARR (15–20 studies/month + 50+ signal feed subscriptions).

---

## 3. The 90-Day Action Plan

### Days 1–14: Foundation

**Content:**
- Publish "Why Your Pricing A/B Test Is Lying to You" (Medium/Substack) — aim for Hacker News front page
- Optimize LinkedIn profile (headline, about, featured section)
- Post daily: clusters 1 (pricing mistakes) + 4 (causal inference)

**Product:**
- Define exact onboarding form (10–12 fields)
- Run one internal demand study on BeeSignal's own pricing → first social proof content
- Set up Typeform intake, Stripe payment link, Notion study tracker

### Days 15–30: First Customers

**Content:**
- Launch "SaaS Pricing Diagnostic" scorecard (Typeform/Tally, 3 hours to build)
- Post internal BeeSignal study as case study
- Begin daily commenting on ICP posts (30 comments/day)

**Product:**
- Reach out to 5 SaaS founders — offer free/discounted study for feedback + testimonial
- Run first 1–2 studies manually. Document every friction point.

### Days 31–60: Validate

**Content:**
- Publish anonymized findings from design partner studies
- Launch lead magnet: "Why A/B Testing Your Price Is Broken" PDF
- Start Thursday "setup call" posts with CTA

**Product:**
- Iterate workflow based on design partner feedback
- Build Python pipeline into repeatable script (not a platform — a script with config)
- Price: $3,500 for first paying customers

### Days 61–90: Systematize

**Content:**
- Publish "SaaS Pricing Undercharge Report" benchmark piece (anonymized data from early studies)
- Cross-post to Hacker News, SaaStr, Lenny's Slack

**Product:**
- Study intake → output pipeline in lightweight app (4 hours active work per study, down from 8–10)
- Begin planning Stripe integration for DiD event study (month 4)

---

## 4. Content Strategy

### The Parallel Approach

Run education and product tracks simultaneously. Content builds the vocabulary and demand. Product proves the mechanism. They converge at month 4–5 when content has an audience and the MVP can convert it.

The category name to establish first: **Continuous Pricing Intelligence**. The credibility layer to seed in parallel: causal methods, choice experiments, demand recalibration. Both tracks build toward the same ownership claim.

### Five Content Clusters

| Cluster | Theme | Example Posts |
|---------|-------|-------------|
| 1. Pricing Mistakes | "Set & forget" is broken | "The hidden cost of frozen pricing," "3 signals your pricing has drifted," "Your pricing has a shelf life" |
| 2. Demand Education | Choice experiments, demystified | "We tested simulated demand against 90 days of real Stripe data," "Why demand research isn't a one-time exercise" |
| 3. AI + Econometrics | The technical moat | "Why LLMs alone can't optimize pricing (but LLMs + econometrics can)," "What a Pricing Health Score actually measures" |
| 4. Experiments & Causality | Why standard methods fail | "A/B testing your pricing? You're doing it wrong," "The counterfactual approach to pricing" |
| 5. Pricing Breakdowns | Real-world case studies | "We monitored a SaaS company's pricing for 6 months," "Anatomy of a pricing drift" |

### Lead Magnets (Priority Stack)

1. **"SaaS Pricing Diagnostic"** (month 1) — interactive scorecard, gates behind email
2. **"Why A/B Testing Your Price Is Broken"** PDF (month 2) — repurposed from anchor piece
3. **"Willingness to Pay Without Surveys: 3 Methods"** (month 3) — introduces choice experiments on simulated demand
4. **"Pricing Model Migration Playbook"** (month 4) — flat-rate to usage-based playbook
5. **"The Demand Study Template"** (month 5) — naturally leads to "or we can run this for you"

### Recurring Series: "Pricing Vital Signs"

Monthly anonymized insights from the platform:
- Aggregate trends in plan mix, conversion, packaging alignment across customers
- Positions BeeSignal as the authority with proprietary demand data no one else has

### Content Cadence

- Mix: 60% educational / 20% case studies / 10% methodology / 10% engagement
- Cluster 4 (causal inference) rotated in aggressively in months 1–2 to establish methodological positioning before competitors can imitate
- Default to Framing B (outcome language) in all content; unlock Framing A only when post topic is explicitly methodological

---

## 5. Key Messaging by Audience

| Audience | Message |
|----------|---------|
| Founders / CEOs | "You wouldn't run your product without error monitoring. Why run your pricing without it?" |
| Heads of Product | "Your product ships updates every sprint. Your pricing hasn't changed in a year. BeeSignal keeps them in sync." |
| VPs of Revenue / CFOs | "Every month your pricing drifts from optimal, you're leaving revenue on the table. We quantify the gap and tell you how to close it." |
| Data / Analytics Teams | "Choice experiments on simulated demand, continuous causal price tracking, and a calibration loop that improves every cycle." |

---

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Studies take too long, limiting throughput | High | Medium | Ruthlessly scope MVP output; 30-min readout replaces long narrative initially |
| Content doesn't generate inbound | Medium | High | Target 3 HN/Reddit posts in first 60 days; go direct to SaaStr/Lenny communities |
| Simulated demand quality questioned | Medium | High | Publish methodology transparently; include diagnostics in every report; lean into limitations as credibility |
| Paddle launches self-serve product | Low–Medium | High | Speed to content ownership > feature completeness; establish vocabulary now |
| Time constraint (building alongside full-time job) | High | High | MVP is a workflow, not a platform; 6 hours/week is enough for 2 studies/month manually |
| Stripe/Chargebee builds pricing intelligence | Low | Very High | First-mover on category naming; calibration data moat; complementary positioning (integrate, don't compete) |

---

## 7. Strategic Principles

1. **Methodology story first, platform story second.** Month 1–3: you're an econometrician who runs pricing research. Month 4–8: you're a SaaS company with a product. Month 9+: you're building toward category ownership.

2. **Every customer is a likelihood update.** Every study is evidence that sharpens your prior about what the product should become. Build the prior carefully, run the studies, let the posterior guide the roadmap.

3. **Don't compete with billing.** Integrate with Stripe, Paddle, Chargebee as data sources. Be complementary, not competitive. This opens partnership channels and acquisition optionality.

4. **The calibration loop is the moat.** Simulated demand prediction vs. real outcome data. Each cycle makes the next prediction more accurate. No competitor can replicate this without the same installed base.

5. **Name the category before someone else does.** "Continuous Pricing Intelligence" doesn't exist as a search query yet. First-mover advantage is real for category creation. Own the vocabulary, own the category.

---

*Last updated: March 2026*
*Supersedes previous STRATEGY.md. Updated to reflect "Continuous Pricing Intelligence" as the primary category name, vocabulary decisions (no "WTP", no "dashboard", no "synthetic customers"), Framing B as default content stance, and updated cluster language from the March 2026 positioning session.*
