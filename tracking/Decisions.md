# Decisions
## MietOptimal — Decision Log

---

### 2025-03-14 Decision: Target Buena track over Inca track
**Context:** Big Berlin Hack has three track partners: Buena (proptech), Qontext (AI context layer), Inca (insurance AI). Needed to choose which to build for.
**Decision:** Buena track with MietOptimal (rent optimization engine).
**Rationale:** Higher demo-ability (everyone understands rent), stronger data availability (public listings + Mietspiegel), better domain credibility (Daniel lives in Berlin), spatial analytics background maps directly to neighborhood features. Scored 6 wins vs 3 for ReserveIQ (Inca) in head-to-head comparison. Inca had stronger causal story but weaker execution safety for solo build.
**Implications:** All development focuses on German rental market domain. Demo data uses Berlin-specific neighborhoods and regulations.

### 2025-03-14 Decision: XGBoost over linear hedonic model for Layer 1
**Context:** Traditional rental pricing uses hedonic regression (Rosen 1974). Needed to decide between linear hedonic vs ML for prediction.
**Decision:** XGBoost for prediction accuracy, SHAP for interpretability. Linear hedonic model NOT used.
**Rationale:** XGBoost captures nonlinearities (floor premiums don't scale linearly) and interactions (balcony value varies by neighborhood) that linear models miss. SHAP recovers interpretability post-hoc. Best of both worlds: ML accuracy + hedonic-style decomposition.
**Implications:** Need SHAP waterfall visualization in frontend. Can't directly interpret coefficients — must use SHAP values for feature contribution explanations.

### 2025-03-14 Decision: Dual-method renovation estimation (matching + conjoint)
**Context:** Renovation impact estimation requires causal identification. Single method has weaknesses.
**Decision:** Use BOTH observational matching (Approach A) and synthetic conjoint simulation via BeeSignal engine (Approach B). Show convergence.
**Rationale:** Matching handles selection-on-observables but assumes no unobserved confounders. Conjoint sidesteps selection bias via experimental design but relies on calibration quality. When both agree, credibility is high. Divergence itself is informative. Also directly connects to BeeSignal product vision.
**Implications:** Need to adapt BeeSignal conjoint engine for rental context (attribute definitions, tenant personas calibrated to Berlin demographics). Need matching estimator built on listing data.

### 2025-03-14 Decision: Satellite spatial layer as core differentiator
**Context:** Needed a unique angle that no other hackathon team can replicate. Daniel has spatial analytics / remote sensing background.
**Decision:** Extract neighborhood quality features from satellite imagery (Sentinel-2 NDVI) + aerial imagery (Gemini multimodal). Use as covariates in XGBoost model.
**Rationale:** Nobody at the hackathon will have this. Stacks three of Daniel's skills (spatial + econometrics + ML). Maximizes Google DeepMind infrastructure prize scoring (multimodal = 5/5 points). Validated against Umweltatlas ground truth data.
**Implications:** Need Sentinel-2 data, Google Maps Static tiles, Gemini API access, and Berlin Umweltatlas validation data pre-downloaded.

### 2025-03-14 Decision: Four infrastructure partner integration (Gemini + Lovable + Gradium + Entire)
**Context:** Hackathon has four infrastructure partners. Using more = better impression.
**Decision:** Integrate all four: Gemini (spatial + NLP, core), Lovable (frontend), Gradium (voice input), Entire (build process tracking).
**Rationale:** Maximizes partner impression score. Each integration serves a genuine purpose (not forced). Voice input via Gradium is demo bonus, not critical path.
**Implications:** Need API keys for all four before hackathon. Voice input is a "nice to have" — form input is the reliable fallback.

### 2025-03-14 Decision: Solo build strategy
**Context:** Going to hackathon without a team.
**Decision:** Solo build. Use Lovable for frontend, Supabase for database, pre-train all models before the event. Hackathon time is integration + polish only.
**Rationale:** Per hackathon playbook: build something small that works perfectly over something ambitious that's half-broken. Heavy pre-hackathon prep compensates for no team.
**Implications:** ~28 hours of pre-hackathon prep across 6 weeks. Strict MVP scope. Feature freeze at hour 16 of hackathon.

### 2025-03-14 Decision: Product name — RentSignal (working title)
**Context:** Originally called MietOptimal. Discussed naming during session.
**Decision:** Working title is RentSignal. Connects to BeeSignal brand family. Not finalized.
**Rationale:** "RentSignal" communicates both the rent domain and the intelligence/signal angle. Echoes BeeSignal brand. "MietOptimal" sounded like a utility calculator.
**Implications:** Use RentSignal in pitch and materials. Can still change before hackathon.

### 2025-03-14 Decision: Steal from Rentana, Predium, and Conny — prioritized
**Context:** Competitive teardown revealed specific features worth adapting and weaknesses to exploit.
**Decision:** Steal Rentana's Copilot explanation pattern and amenity-level pricing. Steal Predium's satellite approach and ESG renovation ROI with subsidies. Steal Conny's viral free calculator mechanic. Fix Conny's broken Mietspiegel calculations and tenant self-classification UX.
**Rationale:** Each competitor does one thing well but none combine all four pillars. Stealing the best from each creates a product that's "Rentana + Predium + Conny" in one platform.
**Implications:** Hackathon core: SHAP explanations, conjoint amenity WTP, accurate compliance, photo classification, satellite features, dual-method renovation. Post-hackathon P1: energy class, CO2 costs, KfW subsidies, market comps, English language. P2: portfolio dashboard, ESG scoring, Nebenkostencheck.

### 2025-03-14 Decision: ESG as expansion path, not hackathon core
**Context:** Predium raised €13M for ESG in real estate using same satellite pipeline we're building.
**Decision:** Don't build ESG for hackathon. Mention as expansion path in pitch. Build in post-hackathon P1 (energy class, CO2 costs, KfW subsidies).
**Rationale:** ESG adds minimal incremental cost because our satellite pipeline already exists. But it's scope creep for a 24-hour solo build. Better to nail rent optimization and tease ESG than to half-build both.
**Implications:** Add energy class to XGBoost model post-hackathon. Add KfW subsidy lookup to renovation simulator. Mention Predium's €13M raise in pitch as validation of the satellite approach.

### 2025-03-14 Decision: Revenue model — freemium + per-unit enterprise
**Context:** Needed a business model for pitch Q&A.
**Decision:** Free tier (single apartment compliance + market estimate), Pro €19-29/month (landlords 1-10 units), Enterprise €2-3/unit/month (property managers 50+ units).
**Rationale:** Free tier = growth engine (Conny's model, but for landlords). Enterprise per-unit = scales with portfolio size. At €3/unit for Buena's 60k units = €2.16M ARR from one client.
**Implications:** TAM Germany = €828M/year. SOM Year 2 = €6.7M ARR. European expansion TAM = €2B+.

### 2026-03-15 Decision: Brand name — RentSignal (not MietOptimal)
**Context:** Needed to choose between German-first (MietOptimal, MietIQ) vs international (RentSignal) brand name. MietOptimal scored highest (40pts) for Germany-only SEO, RentSignal scored 38pts.
**Decision:** Go with RentSignal.
**Rationale:** (1) EU expansion is part of the pitch narrative — Austria, Netherlands, France, Sweden all have rent regulation. (2) Hackathon judges are international, English-speaking. (3) BeeSignal brand family adds credibility ("we built BeeSignal for consumer research, now RentSignal for rent"). (4) Conny precedent — they went FROM German (Wenigermiete) TO international. (5) German SEO comes from content language, not brand name.
**Implications:** Domain: rentsignal.de (€5.93/yr, available). Buy .de for launch, negotiate .com later or use .app. All German SEO content works fine under an English brand name.

### 2026-03-16 Decision: Positioning scope — "Rent intelligence" not "portfolio" or "apartment"
**Context:** Debated whether to position as "apartment intelligence" (what we built), "portfolio intelligence" (the vision), or "rent intelligence" (neutral).
**Decision:** Phase 1 = "Rent intelligence platform." Phase 2 = "Portfolio rent intelligence." Phase 3 = "Intelligence layer for regulated rental markets." Documented in `docs/POSITIONING-EVOLUTION.md`.
**Rationale:** "Apartment" sounds too small, doesn't justify B2B pricing. "Portfolio" overpromises features we haven't built. "Rent" is the core object at any scale. Also: rental vs purchase are fundamentally different products — don't try to do both at launch.
**Implications:** Landing page hero says "rent intelligence" not "portfolio." Expand language when portfolio features ship.

### 2026-03-16 Decision: Three-pillar framework — Comply · Optimize · Act
**Context:** Old product structure was Predict/Comply/Explain/Simulate — too feature-centric, no clear narrative for sales.
**Decision:** Reorganize entire product around three pillars: **Comply** (legal position), **Optimize** (what's the unit worth), **Act** (what to do next). Each pillar scales from unit-level to portfolio to enterprise.
**Rationale:** Pillars describe the customer's journey, not our tech stack. "Comply" leads because it's the freemium hook (compliance anxiety). "Optimize" is the subscription value (monitoring). "Act" is the premium differentiator (renovation ROI, Mieterhöhung wizard, neighborhood intelligence).
**Implications:** All docs, landing page, API naming, and pricing tiers restructured around three pillars. Hero updated to "Know what every unit is worth. Stay compliant. Make the right move." PRODUCT.md expanded from 14 to 18 sections with new features: data ingestion (§5), neighborhood intelligence (§7), Mieterhöhung wizard (§8), energy compliance (§9), full API spec (§13).

### 2026-03-16 Decision: Vocabulary source of truth — PRODUCT.md §13
**Context:** Brand voice and vocabulary rules were split between PRODUCT.md §13 and MARKETING.md §8.
**Decision:** PRODUCT.md §13 is the single source of truth for voice, vocabulary, and messaging rules. MARKETING.md §8 covers visual identity and tone as it applies to content.
**Rationale:** Avoids conflicts between two documents. PRODUCT.md is higher in the source of truth hierarchy.
**Implications:** Any vocabulary rule changes go to PRODUCT.md §13 first.

### 2026-03-15 Decision: Channel strategy — LinkedIn-first, avoid TikTok/Instagram
**Context:** Conny has heavy paid presence on YouTube, TikTok, Instagram, Google Search targeting tenants. We need a channel strategy that doesn't compete on their budget.
**Decision:** LinkedIn as primary channel. Don't enter TikTok/Instagram for MVP.
**Rationale:** Conny targets tenants (B2C) on social video. We target property managers (B2B) who live on LinkedIn. Different audience = different channel. Conny's ad spend actually creates our demand (compliance anxiety → landlords Google solutions → find us). Authority > volume.
**Implications:** Content cadence: LinkedIn 3×/week, blog 2×/month, YouTube 2×/month. No TikTok/Instagram budget. Revisit social video in Month 6.
