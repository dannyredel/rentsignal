# Memory
## MietOptimal — Persistent Context Across Sessions

---

## Current State (last updated: 2026-03-16)

### Components Status
| Component | Status | Notes |
|-----------|--------|-------|
| Project brief | ✅ Complete | v2 with spatial layer, dual-method causal, competitive landscape |
| Prep roadmap | ✅ Complete | 12 tasks across 6 weeks, prioritized with dependencies |
| Data sources guide | ✅ Complete | Listings, demographics, spatial — all URLs and specs documented |
| Project structure | ✅ Complete | Folder layout created, matches spec. Git initialized. |
| CLAUDE.md | ✅ Complete | Session protocol, skills/agents references, architecture overview |
| Competitive teardown | ✅ Complete | Rentana, Predium, Conny — in `docs/COMPETITIVE-TEARDOWN.md` |
| Listing data | ✅ Complete | 10,275 clean Berlin listings in `data/processed/listings_clean.parquet` |
| XGBoost model | ✅ Complete | **v3: R²=0.749, RMSE=2.59 €/m²** (37 features: 19 original + 9 OSM + 9 satellite). count_food_1000m is #1 SHAP (1.71). ndwi_median is top satellite feature (#9, SHAP=0.24). |
| Conjoint calibration | ✅ Complete | CBC with 75 LLM respondents, 6 Berlin persona segments. Kitchen WTP +€4.13/m² converges with CATE +€4.01/m² (3% diff). Balcony stated/revealed gap. Results in `data/processed/conjoint_results.json`. |
| Spatial pipeline | ✅ Phases 1 & 2 done | OSM (9 features) + Sentinel-2 (9 features) complete for 190 PLZs. Phase 3 (Gemini) hackathon day. Microsoft Planetary Computer = free Sentinel-2. |
| Compliance engine | ✅ Complete | §556d + §559 + §559e BGB. Berlin Mietspiegel 2024 lookup, equipment adjustments, 3 exemptions, modernization caps (standard + GEG heating). Bilingual DE/EN. Full docs in `docs/COMPLIANCE-ENGINE.md`. |
| Matching estimator | ✅ Complete | PSM 1:1 NN matching. Kitchen +2.91, Lift +1.09, Garden +0.93, Balcony -0.72 €/m². All 14/14 confounders balanced. Results in `data/processed/matching_results.json`. |
| Blog article | ✅ Draft complete | `docs/blog-synthetic-users-validation.md` — "We Ran the Same Experiment Two Ways" for BeeSignal blog |
| Demo apartments | ✅ Complete | 5 apartments with all 4 layers computed. Charts + JSON in `data/demo/`. Speaker notes auto-generated. |
| Product strategy | ✅ Complete | `docs/PRODUCT.md` — 18 sections: **Comply · Optimize · Act** three-pillar framework, data ingestion, Mieterhöhung wizard, energy compliance (CO2KostAufG, EU EPBD), full API endpoint spec (P0-P4), retention-driven pricing, ICP usage patterns. §17 is source of truth for brand voice & vocabulary. |
| Marketing strategy | ✅ Complete | `docs/MARKETING.md` — SEO keywords, channels, Conny positioning, launch sequence. |
| Brand identity | 🔄 In progress | Name locked: **RentSignal**. Domain: rentsignal.de (€5.93/yr, available, not yet purchased). Colors TBD (iterating with Nano Banana — liked architectural grid + dashboard layout from round 1, not the green palette). Architectural blueprint grid is the brand texture. |
| Positioning evolution | ✅ Complete | `docs/POSITIONING-EVOLUTION.md` — 3 phases with **Comply · Optimize · Act** pillars scaling across each. Hero: "Know what every unit is worth. Stay compliant. Make the right move." Copy reference section for landing page, investor, demo contexts. |
| Railway deployment files | ✅ Ready | `requirements-api.txt`, `Procfile`, `railway.toml`, `nixpacks.toml` created. Need to push to GitHub + connect Railway. Consider computing SHAP explainer on-the-fly to avoid committing 26MB file. |
| Backend API | ✅ Complete | FastAPI with 8 endpoints (health, demo×2, predict, comply, renovate, spatial×2). Tested on localhost:8000. |
| Backend deployment | ✅ Live | Railway: `https://web-production-f2b2f.up.railway.app` · Python 3.11.15 · Auto-deploys from GitHub `dannyredel/rentsignal` main branch · Supabase env vars set |
| Lovable prompt | ✅ Complete | `docs/LOVABLE-PROMPT.md` — landing page + 5 dashboard pages + Supabase auth. Ready to paste. |
| Frontend | ✅ Live | Lovable-generated React dashboard at `rentsignal.de`. Portfolio + Unit detail (4 tabs) + Comply + Optimize + Act + Neighborhoods all working with live API. Google OAuth working. Add units form works (predict + comply) but doesn't save to DB yet. |
| Pitch deck | ❌ Not started | Narrative arc defined in brief |

### API Keys Status
| Service | Status |
|---------|--------|
| Gemini API | ❌ Deferred to hackathon day |
| Google Maps Static API | ❌ Need to set up |
| Gradium API | ❌ Deferred to hackathon day |
| Lovable account | ✅ User already has |
| Supabase project | ✅ User already has |
| Entire CLI | ❌ Need to install |

## BeeSignal Connection
- The conjoint engine (CBC + RCT on synthetic users) already works in BeeSignal
- For MietOptimal, need to: define apartment attributes/levels, calibrate Berlin tenant personas, validate WTP against market data
- This is adaptation, not building from scratch — estimated 3-4 hours

## Key Context for Future Sessions
- **Hackathon date:** April 25-26, 2026 (6 weeks from project start)
- **Hackathon venue:** The Delta Campus, Donaustraße 44, 12043 Berlin
- **Track:** Buena (proptech, "Prosperity through Property")
- **Format:** Saturday 10:00 → Sunday 15:00 submission, finalist pitches at 16:15
- **Prize pool:** €25k+ total, main prize €5,000 cash
- **Daniel is going solo** — no teammate
- **The "don't build the balcony" moment** is the demo punchline — always build toward this

## Known Issues / Gotchas
- Kaggle ImmoScout24 data is from 2018-2019, not current. Need to address in Q&A: "trained on historical data, architecture is the product, would retrain on current data in production"
- Mietpreisbremse doesn't apply to post-2014 new builds — compliance engine must handle this exception
- Sentinel-2 ✅ done — summer 2024 scene (Aug 20, 0.6% cloud). Microsoft Planetary Computer is free, no account needed
- Gemini spatial extraction needs prompt iteration — budget 1 hour for prompt engineering
- Gradium German STT accuracy unknown — have form input as reliable fallback, voice as demo bonus

## Don't Forget
- The competitive landscape shows 6 gaps that NO existing tool fills — use this in pitch ("we fill all six")
- IBB Wohnungsmarktbericht has English summary available — use for tenant persona calibration
- Berlin Umweltatlas noise data is a sleeper feature — powerful rent predictor nobody uses
- Mention Entire in the pitch even though it's a build-process tool, not product-facing
- §559 BGB caps modernization rent increase at €2/m² over 6 years for rents up to €7/m², and €3/m² otherwise
- **Conny's calculations are documented as structurally incorrect** — position RentSignal as more accurate
- **Conny charges 5-6× monthly savings** — our freemium model is more accessible
- **Rentana raised $5M and users love their "why" explanations** — SHAP waterfall is our version
- **Predium raised €13M for ESG with same satellite pipeline** — mention in pitch as validation
- **Product name LOCKED: RentSignal** (connects to BeeSignal brand family, EU expansion ready)
- The killer pitch line: "Conny tells tenants they're overpaying. Rentana optimizes the US free market. Predium handles ESG. RentSignal combines all three for German property managers."
- Revenue pitch: "Buena alone = €2.16M ARR. TAM Germany = €828M. European TAM = €2B+."
- ESG expansion is nearly free — same satellite pipeline, add energy class + CO2 costs + KfW subsidies
