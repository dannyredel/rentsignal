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
