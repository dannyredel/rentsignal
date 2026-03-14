# Changelog
## MietOptimal — Session Log

---

### 2025-03-14 Session 0: Strategic Planning & Project Setup
**Duration:** ~3h (Claude.ai conversation, not Claude Code)
**Type:** Planning / pre-development

**What happened:**
- Analyzed Big Berlin Hack sponsor landscape (Buena, Qontext, Inca + infrastructure partners)
- Evaluated three track partners: scored Buena 4.2/5, Inca 4.0/5, Qontext 3.0/5
- Deep-dived Buena (proptech, €49M raised, 60k units, GV-backed) and Inca (insurance claims AI)
- Generated 3 project ideas per track, scored by feasibility, demo-ability, differentiation
- Built full project brief for ReserveIQ (Inca track) — claims reserve optimizer
- Built full project brief for MietOptimal (Buena track) — rent optimization engine
- Ran head-to-head comparison: MietOptimal won 6-3 on execution safety, sponsor alignment, data availability
- Identified spatial analytics as unique differentiator → satellite-derived neighborhood features
- Mapped all 4 infrastructure partners: Gemini (core AI), Lovable (frontend), Gradium (voice), Entire (dev tracking)
- Refined ML architecture: XGBoost (prediction) + SHAP (explainability) + dual causal method (matching + conjoint)
- Discussed hedonic models vs ML — decided XGBoost for accuracy, SHAP for interpretability, causal matching + conjoint for renovation counterfactuals
- Discussed synthetic conjoint users for identification — decided dual-method approach (observational + simulated) with convergence validation
- Mapped competitive landscape: Official Mietspiegel Rechner, Conny, ImmoScout24, Immowelt, aggregator sites → identified 6 gaps nobody fills
- Researched all data sources: Kaggle listings, IBB reports, Statistik BB demographics, Sentinel-2, Berlin Umweltatlas, OSM

**Artifacts produced:**
- `docs/PROJECT-BRIEF.md` — MietOptimal v2 complete project brief (with spatial layer, dual-method causal, competitive landscape, BeeSignal connection)
- `docs/PREP-ROADMAP.md` — Prioritized 12-task roadmap across 6 weeks
- `docs/DATA-SOURCES.md` — Comprehensive data guide (listings, demographics, spatial imagery)
- `docs/PROJECT-STRUCTURE.md` — Full folder structure, .env, requirements.txt, API endpoints
- `CLAUDE.md` — Session management protocol, skills/agents reference, architecture overview
- `tracking/Backlog.md` — Task queue initialized from roadmap
- `tracking/Decisions.md` — 6 key strategic decisions recorded with rationale
- `tracking/Memory.md` — Current state, API status, context, gotchas
- `tracking/Changelog.md` — This file

**Also produced (not carried forward):**
- ReserveIQ project brief (Inca track) — archived, not pursuing
- MietOptimal v1 project brief — superseded by v2
- RentSignal-Revenue-Model.html — revenue calculations (content merged into project brief)

**State at end of session:**
- All planning documents complete
- Competitive teardown of Rentana, Predium, and Conny complete with stolen features prioritized
- Revenue model with TAM/SAM/SOM and client-level calculations complete
- Feature roadmap prioritized: Hackathon Core → P1 (weeks 1-4 post) → P2 (months 2-3) → P3 (months 4-12)
- ESG expansion path identified (same satellite pipeline, minimal incremental cost)
- Working product name: RentSignal
- Zero code written yet
- Next action: Task 1 (source Berlin listing data) + Task 7 (set up API accounts)
- 6 weeks until hackathon (April 25)
