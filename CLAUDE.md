# CLAUDE.md
## RentSignal — Claude Code Project Guide

---

## Project Overview

**RentSignal** is a Regulated Rent Intelligence platform for the German rental market, built around three pillars: **Comply · Optimize · Act**.

It combines Mietpreisbremse compliance checking, ML-powered rent prediction (XGBoost + SHAP), satellite-derived spatial features (Sentinel-2 NDVI + Gemini multimodal), and dual-method renovation impact estimation (observational matching + synthetic conjoint via BeeSignal engine).

**Solo build by Daniel.** Background: econometrics, industrial organization, causal ML, spatial analytics / remote sensing.

---

## Key Reference Documents

Read these before starting any work session:

| Document | Location | Purpose |
|----------|----------|---------|
| Product Strategy | `docs/PRODUCT.md` | **Source of truth** — three pillars, tiers, pricing, roadmap, API spec, brand voice |
| Positioning | `docs/POSITIONING-EVOLUTION.md` | Phase 1→2→3 positioning, hero copy, taglines |
| Project Brief | `docs/PROJECT-BRIEF.md` | Founding brief — problem statement, Q&A prep, pitch narrative |
| Project Structure | `docs/PROJECT-STRUCTURE.md` | Folder layout, dependency flows, quick start |
| Backlog | `tracking/Backlog.md` | P0→P4 task queue with dependencies |
| Technical: Compliance | `docs/technical/COMPLIANCE-ENGINE.md` | §556d/§559 BGB rules engine spec |
| Technical: Spatial | `docs/technical/SPATIAL-TECHNICAL-NOTES.md` | Sentinel-2 + OSM pipeline |
| Technical: Data | `docs/technical/DATA-SOURCES.md` | All datasets, URLs, APIs |

---

## Session Management Protocol

**Every Claude Code session MUST follow this protocol:**

### At Session Start
1. Read `tracking/Backlog.md` — understand what tasks are pending and their priority
2. Read `tracking/Memory.md` — recall context, decisions, and state from previous sessions
3. Read `tracking/Changelog.md` — understand what was done recently and current momentum
4. Read `tracking/Decisions.md` — review key decisions made to avoid revisiting them
5. Identify the highest-priority task from the Backlog that is unblocked

### During Session
- Work on the identified task(s)
- When making non-trivial decisions, record them immediately in `tracking/Decisions.md`
- If new tasks emerge, add them to `tracking/Backlog.md` with appropriate priority

### At Session End (MANDATORY — never skip this)
1. **Update `tracking/Changelog.md`** — Record what was accomplished this session with date and detail
2. **Update `tracking/Backlog.md`** — Mark completed tasks, reprioritize if needed, add new tasks discovered
3. **Update `tracking/Memory.md`** — Record any context, gotchas, or state that the next session needs to know
4. **Update `tracking/Decisions.md`** — Record any decisions made and their rationale

---

## Tracking Documents

### `tracking/Backlog.md`
The task queue. Organized by priority tier (P0/P1/P2/P3). Each task has:
- Priority level
- Description
- Status: `[ ]` todo, `[~]` in progress, `[x]` done
- Dependencies (which tasks must complete first)
- Estimated time

### `tracking/Decisions.md`
Architectural and strategic decisions with rationale. Format:
```
### [Date] Decision: [Title]
**Context:** Why this decision came up
**Decision:** What was decided
**Rationale:** Why this option over alternatives
**Implications:** What this means for downstream work
```

### `tracking/Memory.md`
Persistent context across sessions. Includes:
- Current state of each component (what works, what's broken, what's untested)
- API keys status (which are set up, which need renewal)
- Known issues and workarounds
- Environment-specific notes (Python version, dependency conflicts, etc.)
- "Don't forget" items that aren't tasks but are important context

### `tracking/Changelog.md`
Chronological log of what happened. Format:
```
### [Date] Session N
**Duration:** ~Xh
**Tasks completed:**
- [description of what was done]
**Artifacts produced:**
- [files created or modified]
**State at end of session:**
- [what's working, what's next]
```

---

## Skills & Agents (.claude/)

The `.claude/` folder contains reusable skills and agent configurations that assist with specific workflows in this project.

### `.claude/skills/`

| Skill | File | When to Use |
|-------|------|-------------|
| **spatial-analysis** | `.claude/skills/spatial-analysis.md` | When working on NDVI computation, OSM feature extraction, Gemini spatial prompts, or any geospatial data processing. Contains best practices for rasterio, geopandas, and Sentinel-2 workflows. |
| **ml-pipeline** | `.claude/skills/ml-pipeline.md` | When training the XGBoost model, computing SHAP values, building the matching estimator, or evaluating model performance. Contains feature engineering patterns and evaluation standards. |
| **conjoint-engine** | `.claude/skills/conjoint-engine.md` | When adapting the BeeSignal CBC/RCT engine for rental context. Contains the persona calibration approach, attribute definitions, and WTP extraction methods. |
| **fastapi-backend** | `.claude/skills/fastapi-backend.md` | When building API endpoints. Contains router patterns, Pydantic schema conventions, and deployment configuration for Railway. |
| **compliance-rules** | `.claude/skills/compliance-rules.md` | When implementing the Mietpreisbremse engine. Contains §556d BGB rules, §559 BGB modernization rules, Mietspiegel lookup logic, and exception handling. |
| **gemini-integration** | `.claude/skills/gemini-integration.md` | When calling Gemini API for spatial extraction, apartment photo analysis, or NL→structured feature parsing. Contains tested prompts and structured output schemas. |
| **demo-prep** | `.claude/skills/demo-prep.md` | When preparing demo apartments, pre-computing outputs, or assembling demo data JSONs. Contains the 5 demo apartment specs and expected outputs. |

### `.claude/agents/`

| Agent | File | When to Use |
|-------|------|-------------|
| **scope-guardian** | `.claude/agents/scope-guardian.md` | Invoke at scope-check moments (every 4 hours during hackathon, or when tempted to add features). Evaluates whether a task is demo-critical or should be cut. |
| **code-reviewer** | `.claude/agents/code-reviewer.md` | Run before committing. Checks for: hardcoded secrets, missing error handling, unused imports, type consistency with Pydantic schemas. |
| **pitch-coach** | `.claude/agents/pitch-coach.md` | When drafting or refining pitch content. Evaluates clarity, timing, wow-moment placement, and judge Q&A readiness. |

---

## Architecture Quick Reference

```
User Input (form / voice / NL)
       │
       ▼
┌─────────────────────────────────────────────┐
│  Layer 0: INPUT PROCESSING                  │
│  Gradium STT (voice) → Gemini (NL→struct)   │
│  → Structured apartment features             │
└──────────────────┬──────────────────────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
┌────────────┐ ┌────────┐ ┌──────────────┐
│ Layer 1    │ │Layer 0b│ │ Layer 1b     │
│ PREDICT    │ │COMPLY  │ │ SPATIAL      │
│ XGBoost    │ │Rules   │ │ Sentinel-2   │
│ rent/m²    │ │engine  │ │ + Gemini     │
│ + interval │ │legal   │ │ features     │
└─────┬──────┘ │max     │ └──────┬───────┘
      │        └───┬────┘        │
      ▼            │             │
┌────────────┐     │             │
│ Layer 2    │     │             │
│ EXPLAIN    │◄────┘─────────────┘
│ SHAP       │  (all feed into dashboard)
│ waterfall  │
└─────┬──────┘
      │
      ▼
┌─────────────────────────────────────────────┐
│ Layer 3: SIMULATE (renovation toggle)       │
│                                             │
│  Approach A          Approach B             │
│  Observational       Synthetic Conjoint     │
│  Matching CATE       BeeSignal WTP          │
│       │                    │                │
│       └──────┬─────────────┘                │
│              ▼                              │
│     Convergence check + ROI + payback       │
└─────────────────────────────────────────────┘
```

---

## Tech Stack Summary

| Layer | Tech | Notes |
|-------|------|-------|
| Backend | FastAPI (Python 3.11+) | Deployed on Railway |
| Frontend | React + Tailwind (Lovable-generated) | Deployed on Vercel |
| ML | XGBoost, SHAP, scikit-learn | Model artifacts in `models/` |
| Causal | Matching (scikit-learn) + BeeSignal conjoint | Conjoint in `conjoint/` module |
| Spatial | rasterio, geopandas, Sentinel-2, OSM | Pipeline in `spatial/` |
| AI — Vision | Gemini API (multimodal) | Satellite + apartment photos |
| AI — NLP | Gemini API (text) | NL description → features |
| Voice | Gradium API (German STT) | WebSocket streaming |
| Database | Supabase | Demo data only |
| Dev tracking | Entire CLI | Session capture |
| Pitch | Gamma.app | Slide generation |

---

## Infrastructure Partner API Quick Reference

### Gemini (Google AI)
```python
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")  # or gemini-3.1-pro
# Multimodal: pass image + text prompt
response = model.generate_content([image_part, "Extract spatial features..."])
```

### Gradium (Voice STT)
```python
# WebSocket-based streaming STT
# Endpoint: wss://eu.api.gradium.ai/api/speech/asr
# API key in header, 24kHz mono PCM audio input
# Returns: text transcription + VAD events
```

### Supabase
```python
from supabase import create_client
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
data = supabase.table("demo_apartments").select("*").execute()
```

---

## Critical Reminders

- **Hackathon date:** April 25-26, 2026 (Saturday-Sunday, Berlin)
- **Submission deadline:** Sunday 15:00
- **Build window:** ~29 hours (Saturday 10:00 → Sunday 15:00)
- **Track:** Buena — "Prosperity through Property"
- **Secondary prize target:** Google DeepMind infrastructure prize
- **Solo build** — Lovable handles frontend, you handle everything else
- **Feature freeze at hour 16** — after that, only bug fixes and pitch prep
- **The wow moment:** "Don't build the balcony" — renovation toggle showing kitchen ROI vs balcony anti-ROI
- **The differentiator:** Satellite spatial features that nobody else has
- **The causal credibility:** Dual-method convergence (matching + conjoint)
