# Memory
## MietOptimal — Persistent Context Across Sessions

---

## Current State (last updated: 2025-03-14)

### Components Status
| Component | Status | Notes |
|-----------|--------|-------|
| Project brief | ✅ Complete | v2 with spatial layer, dual-method causal, competitive landscape |
| Prep roadmap | ✅ Complete | 12 tasks across 6 weeks, prioritized with dependencies |
| Data sources guide | ✅ Complete | Listings, demographics, spatial — all URLs and specs documented |
| Project structure | ✅ Complete | Folder layout, API endpoints, .env template, requirements.txt |
| CLAUDE.md | ✅ Complete | Session protocol, skills/agents references, architecture overview |
| Listing data | ❌ Not started | Kaggle ImmoScout24 is primary source. Need to download + filter Berlin |
| XGBoost model | ❌ Not started | Depends on listing data |
| Conjoint calibration | ❌ Not started | BeeSignal engine works, needs rental attribute definitions + Berlin persona calibration |
| Spatial pipeline | ❌ Not started | Need Sentinel-2 tile + Gemini API key + Berlin Umweltatlas layers |
| Compliance engine | ❌ Not started | Rules are documented in brief, need to implement in Python |
| Matching estimator | ❌ Not started | Depends on listing data + model |
| Demo apartments | ❌ Not started | 5 apartments defined in brief, need pre-computed outputs |
| Frontend | ❌ Not started | Will use Lovable at hackathon |
| Backend API | ❌ Not started | FastAPI, endpoints defined in project structure doc |
| Pitch deck | ❌ Not started | Narrative arc defined in brief |

### API Keys Status
| Service | Status |
|---------|--------|
| Gemini API | ❌ Need to set up |
| Google Maps Static API | ❌ Need to set up |
| Gradium API | ❌ Need to set up |
| Lovable account | ❌ Need to set up |
| Supabase project | ❌ Need to set up |
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
- Sentinel-2 NDVI is best in summer months (vegetation signal) — download a summer 2024 or 2025 composite
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
- **Working product name: RentSignal** (connects to BeeSignal brand family)
- The killer pitch line: "Conny tells tenants they're overpaying. Rentana optimizes the US free market. Predium handles ESG. RentSignal combines all three for German property managers."
- Revenue pitch: "Buena alone = €2.16M ARR. TAM Germany = €828M. European TAM = €2B+."
- ESG expansion is nearly free — same satellite pipeline, add energy class + CO2 costs + KfW subsidies
