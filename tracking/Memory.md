# Memory
## MietOptimal — Persistent Context Across Sessions

---

## Current State (last updated: 2026-03-20)

### Components Status
| Component | Status | Notes |
|-----------|--------|-------|
| Project brief | ✅ Complete | v2 with spatial layer, dual-method causal, competitive landscape |
| Data architecture | ✅ Complete | Relational schema: units + listings + spatial_unit + gemini_image_features. See `docs/technical/DATA-ARCHITECTURE.md` |
| Listing data | ✅ v2 Complete | **Apify 2026: 8,256 clean units** in `data/processed/units.parquet` + `listings.parquet`. Kaggle 2019 data archived (used for cross-match geocoding only). |
| XGBoost model | ✅ v4.2 | **R²=0.761, RMSE=3.81 €/m²**, 75 features (structural + NLP + spatial + Gemini image). No inflation hack. Top SHAP: is_tauschwohnung (1.43), condition (1.26), renovation_level (1.06). |
| Spatial pipeline | ✅ Unit-level | 24 unit-level features (15 OSM + 9 satellite) computed from actual coordinates. POIs cached in `data/processed/osm_pois/`. Noise map (10m GeoTIFF) extracted for 5,844 units. |
| Gemini image pipeline | ✅ Complete | 6,997 listings processed (96%), 21 features per listing (interior/kitchen/bathroom quality, style, floor type, building exterior). ~$29 cost. 54,866 photos downloaded locally (9.4 GB). |
| Geocoding | ✅ 99.9% | 5,081 from listings + 770 geocoded (title mining + Kaggle cross-match) + 2,399 centroid fallback. |
| Conjoint calibration | ✅ Complete | CBC with 75 LLM respondents. Kitchen WTP +€4.13/m² converges with CATE +€4.01/m². Needs re-running on 2026 data. |
| Compliance engine | ✅ Complete | §556d + §559 BGB. Needs no model changes. |
| Backend API | ✅ Live (v3) | Railway deployed. **Needs update to serve v4.2 model.** |
| Frontend | ✅ Live | Lovable React dashboard. Needs SHAP label updates for new features. |
| Blog | ✅ Live | 3 articles published on blog.rentsignal.de |
| Portfolio optimization | 📋 Planned | Strategy doc ready (`docs/strategy/portfolio-optimization-pitch.md`). Cross-unit pricing, substitution matrix, "competing with yourself" framing. |
| Compliance engine | ✅ Complete | §556d + §559 + §559e BGB. Berlin Mietspiegel 2024 lookup, equipment adjustments, 3 exemptions, modernization caps (standard + GEG heating). Bilingual DE/EN. Full docs in `docs/COMPLIANCE-ENGINE.md`. |
| Matching estimator | ✅ Complete | PSM 1:1 NN matching. Kitchen +2.91, Lift +1.09, Garden +0.93, Balcony -0.72 €/m². All 14/14 confounders balanced. Results in `data/processed/matching_results.json`. |
| Blog article | ✅ Draft complete | `docs/blog-synthetic-users-validation.md` — "We Ran the Same Experiment Two Ways" for BeeSignal blog |
| Demo apartments | ✅ Complete | 5 apartments with all 4 layers computed. Charts + JSON in `data/demo/`. Speaker notes auto-generated. |
| Product strategy | ✅ Complete | `docs/PRODUCT.md` — 18 sections: **Comply · Optimize · Act** three-pillar framework, data ingestion, Mieterhöhung wizard, energy compliance (CO2KostAufG, EU EPBD), full API endpoint spec (P0-P4), retention-driven pricing, ICP usage patterns. §17 is source of truth for brand voice & vocabulary. |
| Marketing strategy | ✅ Complete | `docs/MARKETING.md` — SEO keywords, channels, Conny positioning, launch sequence. |
| Brand identity | 🔄 In progress | Name locked: **RentSignal**. Domain: rentsignal.de (€5.93/yr, available, not yet purchased). Colors TBD (iterating with Nano Banana — liked architectural grid + dashboard layout from round 1, not the green palette). Architectural blueprint grid is the brand texture. |
| Positioning evolution | ✅ Complete | `docs/POSITIONING-EVOLUTION.md` — 3 phases with **Comply · Optimize · Act** pillars scaling across each. Hero: "Know what every unit is worth. Stay compliant. Make the right move." Copy reference section for landing page, investor, demo contexts. |
| Railway deployment files | ✅ Ready | `requirements-api.txt`, `Procfile`, `railway.toml`, `nixpacks.toml` created. Need to push to GitHub + connect Railway. Consider computing SHAP explainer on-the-fly to avoid committing 26MB file. |
| Backend API | ✅ Complete | FastAPI with 28 endpoints. All working on Railway. |
| Backend deployment | ✅ Live | Railway: `https://web-production-f2b2f.up.railway.app` · Python 3.11.15 · Auto-deploys from GitHub `dannyredel/rentsignal` main branch · Supabase env vars set |
| Lovable prompt | ✅ Complete | `docs/LOVABLE-PROMPT.md` — landing page + 5 dashboard pages + Supabase auth. |
| Frontend | ✅ Live | Lovable-generated React dashboard at `rentsignal.de`. Full CRUD with auto-analysis. All 4 unit detail tabs (Optimize/Comply/Act/Spatial) working. Google OAuth + logout. Tier enforcement (unit counter + limits). Empty states. Demo mode link. |
| Pitch deck | ✅ Content ready | `pitch/PITCH-DECK.md` — Gamma-ready pitch deck content |
| Blog | ✅ Live | `blog.rentsignal.de` — Quarto blog, auto-deploys via GitHub Actions. First article "Küche oder Balkon?" published. |
| SEO strategy | ✅ Complete | `docs/strategy/rentsignal-seo-strategy.md` + tracking setup doc. GA4 (G-85X4K34WMV) + GSC live. 3 articles published. blog-content skill created. |
| Maps (Leaflet) | 🔄 Partial | Tile rendering + zoom controls work. Choropleth fill not showing (data loads, polygons don't color). PLZ type mismatch fixed server-side, may be frontend caching or rendering issue. |

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
- **Apify small scrape (Mar 17, 568 records) is TEST DATA ONLY** — first-page overlap with big scrape. Do NOT use for training.
- **v4.2 model trained on 2026 Apify data only** — no Kaggle mixing. No inflation hack.
- **Implied rent inflation 2019→2026: 1.145×** (not 1.378× as IBB index). The IBB tracks Bestandsmieten, not Angebotsmieten.
- **41% of listings are Tauschwohnungen** (apartment swaps) — median €10.37/m² vs €19.00/m² for regular listings. `is_tauschwohnung` is SHAP #1 (1.43).
- **Backend still serves v3 model** — needs deployment update to serve v4.2 with 75-feature set.
- **Gemini 2.5 Flash requires `thinking_budget=0`** — the thinking model uses output tokens for reasoning, truncating the JSON response.
- Mietpreisbremse doesn't apply to post-2014 new builds — compliance engine must handle this exception
- Sentinel-2 ✅ done — summer 2024 scene (Aug 20, 0.6% cloud). Microsoft Planetary Computer is free, no account needed
- Gemini spatial extraction needs prompt iteration — budget 1 hour for prompt engineering
- Gradium German STT accuracy unknown — have form input as reliable fallback, voice as demo bonus
- **JWT auth uses decode-without-verification** — Supabase issues ES256 tokens; server decodes without signature check (acceptable since Supabase service role handles DB auth). If security tightens, fetch Supabase JWKS for proper ES256 verification.
- **Debug/token endpoint removed** ✅ 2026-03-17
- **SHAP is pre-computed** — live SHAP computation was too slow on Railway. Pre-computed SHAP values are loaded from file. If model is retrained, must regenerate pre-computed SHAP.
- **Gemini 2.5 Flash truncation fix:** Must set `thinking_config=types.ThinkingConfig(thinking_budget=0)` — the "thinking" model uses output tokens for internal reasoning, leaving none for the response. This is NOT a billing issue.
- **Model v4.1 is current best:** R²=0.736, 55 features, trained on 2026 Apify data. Key new features: is_tauschwohnung (SHAP #2), picturecount (SHAP #6).
- **Gemini image pipeline ready:** notebook 19 (batch) + 19a (test). Multi-photo (6 per listing) with building exterior fields. 21 JSON fields per listing. ~$22 estimated cost for full 7,344 batch.
- **scikit-learn and xgboost versions pinned** — model was trained with scikit-learn 1.6.x and xgboost 3.x. Changing versions will break model deserialization.
- **Inflation adjustment ×1.378** applied to predictions (2019→2024). Demo apartments still show raw 2019 prices (fix pending).

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
