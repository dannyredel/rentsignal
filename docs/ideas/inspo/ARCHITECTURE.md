# BeeSignal Minimal - Architecture

System design for the minimal rebuild. Focused on clarity and understandability over feature completeness.

---

## 1. Design Principles

1. **Readable over clever.** Every module should be understandable by reading it top-to-bottom. No 2000-line files.
2. **Small modules, clear contracts.** Each file does one thing. Input types and output types are obvious.
3. **Separate data generation from analysis.** LLM calls (expensive, slow) are never mixed with estimation (cheap, fast, iterative).
4. **Save everything intermediate.** After each pipeline stage, save results to disk. Re-run analysis without re-calling APIs.
5. **Config-driven.** Study parameters live in a config file/object, not scattered across code.

---

## 2. What Changed From the Old Codebase

The old codebase works but has readability problems:

| Issue | Old Codebase | Minimal Version |
|-------|-------------|-----------------|
| God files | `run_client_study.py` is 2050 lines, `conjoint_survey.py` is 1467 lines | Max ~300-400 lines per module |
| Mixed concerns | Survey + parsing + data prep all in `conjoint_survey.py` | Split into focused modules |
| Estimation library | `xlogit` (optional) with scipy BFGS fallback; `pylogit` mentioned in docs but not used | Conditional logit via scipy L-BFGS-B (analytical gradient + Hessian) |
| Implicit dependencies | Lazy imports scattered throughout | Explicit imports, clear dependency graph |
| Config complexity | `study_config.py` is 577 lines of conversion logic | Simpler Pydantic models |
| Report generation | 3200-line HTML generator with inline matplotlib | Composable section system (`reports/`). Pricing Discovery report done; 4 remaining. |

---

## 3. Tech Stack

### Core (P0)

| Library | Purpose | Why This One |
|---------|---------|-------------|
| **Python 3.11+** | Runtime | Current stable, good typing support |
| **pydantic** | Config validation, data models | Clean schemas, validation, serialization |
| **openai** | LLM API (GPT-5-mini primary, GPT-4o-mini fallback) | Sync + async clients (`OpenAI` + `AsyncOpenAI`). Reasoning model auto-detection for API param differences. |
| **numpy** | Numerics | Standard |
| **pandas** | Data manipulation | Standard for tabular data |
| **statsmodels** | OLS + HC3 for AMCE/ATE inference | Used for robust SEs in AMCE (cluster-robust), ATE (HC3), and HTE fallback. NOT used for MNL (see scipy). |
| **scipy** | Conditional logit MLE (L-BFGS-B), D-optimal design, delta method, demand curves | Core estimation engine. Analytical gradient + Hessian for MNL. Also optimization for design + pricing. |
| **scikit-learn** | Clustering (KMeans), silhouette scoring | Standard ML toolkit |

### Visualization (P0-lite)

| Library | Purpose |
|---------|---------|
| **matplotlib** | Core charts (demand curves, forest plots, bar charts) |
| **seaborn** | Statistical plots (heatmaps, violin plots) |

### Future (P1+)

| Library | Purpose | When |
|---------|---------|------|
| **pymc** | HB-MNL (Bayesian estimation) | P1: individual-level part-worths |
| **econml** | Causal forests, DML (HTE estimation) | P1: experimental studies |
| **anthropic** | Claude API (Sonnet 4.6 for model bake-off) | Near-term: multi-model validation |
| **streamlit** | Interactive UI | P1: research wizard |

### Libraries We're NOT Using

| Library | Why Not |
|---------|---------|
| **pylogit** | Unmaintained since 2020, sparse documentation |
| **xlogit** | Niche, GPU-focused, overkill for our sample sizes |
| **pyblp** | Market-level estimation -- we have individual choice data. Future P2 direction. |
| **choicemodels** | Thin wrapper, less diagnostic output than statsmodels |

---

## 4. Module Architecture

```
app/
├── inputs/                    # Study inputs (Pydantic models)
│   ├── config.py              # StudyConfig, Attribute, AttributeLevel, StudyParameters
│   └── market.py              # MarketDefinition, PersonaProfile (B2B + B2C)
│
├── core/                      # Shared survey infrastructure (D1 + D2)
│   ├── personas.py            # Demographic sampling + profile rendering
│   ├── prompts.py             # LLM prompt construction (expert framing, unblinding)
│   ├── llm.py                 # LLM API client (sync + async OpenAI, reasoning model detection, retry logic)
│   ├── ssr.py                 # SSR scoring (sync + async, embedding + cosine sim + softmax PMF)
│   └── parser.py              # Response parsing (choice extraction, confidence)
│
├── conjoint/                  # CBC pipeline (P0)
│   ├── design.py              # D-optimal experimental design generator
│   └── survey.py              # CBC orchestrator (asyncio + semaphore concurrency, design + personas + LLM + SSR + parser)
│
├── experimental/              # RCT/Vignette pipeline (P0.5)
│   ├── vignette.py            # Vignette engine (treatment arms, between-subjects randomization)
│   ├── ate.py                 # Average Treatment Effect estimator
│   └── hte.py                 # Heterogeneous Treatment Effects (causal forests via econml)
│
├── estimation/                # Estimation engine (D3) -- shared by CBC + RCT
│   ├── results.py             # EstimationResults, AMCEResults, WTPResults, ATEResults (typed containers)
│   ├── data_prep.py           # Survey responses -> estimation-ready data (CBC long-format or RCT treatment-assignment)
│   ├── mnl.py                 # Conditional logit via scipy L-BFGS-B (CBC)
│   ├── amce.py                # Non-parametric AMCE (CBC)
│   ├── wtp.py                 # WTP from MNL + delta method CIs (CBC)
│   └── demand.py              # Demand curves + elasticities (CBC)
│
├── analysis/                  # Analysis suite (D4)
│   ├── simulator.py           # MarketSimulator (MNL utility -> shares -> revenue) (CBC)
│   ├── pricing.py             # Optimal price, demand curves, price sensitivity (CBC)
│   ├── segments.py            # Cluster analysis (KMeans, segment profiles) (shared)
│   ├── tiers.py               # Tier design (feature gating, value audit) (RCT)
│   ├── price_change.py        # Price change impact (break-even, waterfall) (dual-mode)
│   ├── competitive.py         # Market shares, diversion ratios, switching (dual-mode)
│   ├── launch.py              # New product launch simulation (dual-mode)
│   └── segment_analysis.py    # Per-segment MNL + WTP + pricing (persona-based segmentation)
│
├── diagnostics/               # Per-stage validation checks (D6)
│   ├── personas.py            # Sampling distribution, trait softening, attitude spread
│   ├── design.py              # D-efficiency, level balance, confounding check
│   ├── survey.py              # Position bias, none-option rate, response distribution
│   ├── estimation.py          # Coefficient sign checks, pseudo-R² thresholds, convergence
│   ├── experiment.py          # RCT checks: covariate balance, sample size, SSR degeneracy
│   └── analysis.py            # Share reasonableness, WTP ranges, demand curve shape
│
├── pipeline/                  # Orchestration (D5)
│   ├── runner.py              # End-to-end pipeline: config -> survey -> estimate -> analyze
│   ├── io.py                  # Save/load intermediate results (CSV, JSON)
│   └── logging.py             # Structured logging for pipeline runs
│
├── viz/                       # Visualizations (subset of D4)
│   ├── charts.py              # Core chart functions (AMCE plot, WTP bars, demand curve, ATE forest)
│   └── style.py               # Shared styling constants
│
├── reports/                   # Client-facing report generation
│   ├── sections.py            # Composable Section dataclass + ReportData + common builders
│   ├── renderer.py            # HTML renderer (three-layer: executive/manager/technical)
│   └── pricing.py             # Pricing Discovery report (SCQA exec summary, auto-recommendations)
│
├── templates/                 # SaaS templates (convenience)
│   └── saas.py                # Pre-built attribute sets + market definitions
│
└── tests/                     # Test fixtures + simulated outputs
    └── fixtures/              # Fake stage outputs for pipeline testing
        ├── sample_config.json # Sample StudyConfig (B2B + B2C examples)
        ├── sample_tasks.json  # Pre-generated choice tasks (CBC)
        ├── sample_vignettes.json  # Pre-generated treatment arms (RCT)
        ├── sample_responses.csv   # Simulated survey responses
        └── sample_mnl.json    # Simulated MNL params
```

**Key structural change from old codebase:** The old `core/conjoint_survey.py` mixed CBC-specific logic (D-optimal design, choice tasks) with shared infrastructure (personas, prompts, LLM, SSR). We split these:
- `core/` holds shared infrastructure used by both CBC and RCT
- `conjoint/` holds CBC-specific logic (D-optimal design, CBC survey orchestration)
- `experimental/` holds RCT-specific logic (vignette engine, ATE, HTE)

### Testing Strategy

Each pipeline stage can be tested independently using simulated outputs from the previous stage. The `tests/fixtures/` directory holds sample data for every stage, so we can develop and test estimation, analysis, and viz without running expensive LLM calls.

### RCT vs CBC: Impact on Architecture

Three study types are **dual-mode** (price_change, competitive, launch) -- they run as CBC if a Discovery study exists, or as RCT standalone. Two studies are always RCT (pricing_model, tier_design). This means the experimental/vignette pipeline is essential for the full product offering.

**Build order:** CBC pipeline first (P0: Phases 0A-0E), then RCT pipeline (P0.5: Phases 0.5A-0.5C). The two pipelines share `core/` (personas, prompts, LLM, SSR, parser) and `estimation/results.py`. Dual-mode analysis modules (`price_change`, `competitive`, `launch`) start as CBC-only in P0 and gain RCT mode in P0.5.

See [PRODUCT.md](PRODUCT.md) Section 2 for the full method selection framework.

### What's NOT in P0 or P0.5

These exist in the old codebase but are deferred:

| Old Module | Why Deferred |
|-----------|-------------|
| `research_wizard/` (conversational study config) | P1 -- manual JSON config is fine for now |
| `deliverables/` (remaining report templates) | Pricing Discovery done in `reports/`. 4 remaining report types are P1. |
| `tier_optimizer.py` (cross-study synthesis) | P1 -- requires multiple completed studies |
| `portfolio_analysis.py` | P1 -- requires multi-product setup |
| `results_json_builder.py` (Lovable dashboard JSON) | P2 -- no frontend yet |

---

## 5. Data Flow

### Pipeline Stages

```
Stage 1: CONFIG
  study_config.json -> Pydantic StudyConfig
  Output: validated config object

Stage 2: DESIGN
  StudyConfig -> D-optimal choice tasks
  Output: tasks.json (list of choice task specifications)

Stage 3: SURVEY
  tasks + personas -> async LLM calls (asyncio + Semaphore) -> SSR scoring -> choices
  Concurrency: bounded by Semaphore (default 40), parallelized at task level
  Output: survey_responses.csv (one row per consumer per task)
  *** SAVE HERE -- most expensive stage ***

Stage 4: PREPARE
  survey_responses.csv -> long-format estimation data
  Output: estimation_data.csv (one row per alternative per task)

Stage 5: ESTIMATE
  estimation_data.csv -> MNL + AMCE + WTP
  Output: amce_results.csv, wtp_results.csv, mnl_params.json

Stage 6: ANALYZE
  estimation results + config -> study-specific analysis
  Output: pricing_analysis.json, segments.json, etc.

Stage 7: VISUALIZE
  analysis results -> charts
  Output: PNG files
```

### File Layout Per Study

```
studies/
└── acme_analytics_2026-03-07/
    ├── study_config.json          # Input
    ├── tasks.json                 # Stage 2 output
    ├── survey_responses.csv       # Stage 3 output (expensive!)
    ├── estimation_data.csv        # Stage 4 output
    ├── amce_results.csv           # Stage 5 output
    ├── wtp_results.csv            # Stage 5 output
    ├── mnl_params.json            # Stage 5 output
    ├── importance_results.csv     # Stage 5 output
    ├── segments.json              # Stage 6 output
    ├── pricing_analysis.json      # Stage 6 output
    └── charts/                    # Stage 7 output
        ├── amce_plot.png
        ├── wtp_bars.png
        ├── demand_curve.png
        └── importance.png
```

---

## 6. Key Design Decisions

### Async Survey Execution

Stage 3 (SURVEY) uses `asyncio` + `asyncio.Semaphore` for bounded concurrent API calls, replacing the earlier `ThreadPoolExecutor` approach. Key design points:

- **Task-level parallelism:** Each `(consumer, task)` pair is an independent coroutine. Variants within a task also run concurrently.
- **Bounded concurrency:** `Semaphore(max_workers)` caps in-flight API calls (default 40). GPT-5-mini: 30-40 safe; GPT-4o-mini: 20-30 safe.
- **Jupyter compatibility:** Detects running event loops and applies `nest_asyncio` automatically.
- **Reasoning model detection:** `LLMClient._build_chat_params()` auto-detects GPT-5/o-series models and adapts: `max_completion_tokens` (not `max_tokens`), 8x token budget for hidden reasoning, temperature locked at 1.
- **Speedup:** ~7-10x faster than sequential (1.6s/task concurrent vs ~11s/task sequential for GPT-5-mini).

### Conditional Logit via scipy

We use conditional logit (McFadden 1974), NOT multinomial logit. Key difference: conditional logit has shared β coefficients across alternatives with alternative-specific attributes (the CBC case). statsmodels `MNLogit` is multinomial logit (wrong model for CBC choice data).

Implementation in `estimation/mnl.py`:
- scipy L-BFGS-B optimizer with analytical gradient
- Hessian-based standard errors
- Long-format data reshaped to 3D (obs × alts × features) for vectorized computation
- Effects coding for categorical attributes (base level = -1, None option = 0)

```python
# Long format (what we generate):
# obs_id | alt_id | choice | price | feature_engagement | feature_standard
#   0    |   A    |   0    | 8.00  |       -1           |    1
#   0    |   B    |   1    | 15.00 |        1           |   -1
#   0    |  none  |   0    | 0     |        0           |    0
```

statsmodels is used elsewhere: OLS + HC3 for AMCE inference, ATE estimation, and HTE fallback.

### Pydantic for Config

Replace the 577-line `study_config.py` with Pydantic models in `inputs/`:

```python
class AttributeLevel(BaseModel):
    name: str
    value: float | str
    display_text: str | None = None

class Attribute(BaseModel):
    name: str
    levels: list[AttributeLevel]
    is_price: bool = False
    display_name: str | None = None

class StudyConfig(BaseModel):
    client_name: str
    study_type: Literal["pricing", "tier_design", "price_change", "competitive", "launch"]
    attributes: list[Attribute]
    market: MarketDefinition
    # ... etc
```

Benefits: validation on load, serialization for free, clear schema, IDE autocomplete.

### B2B vs B2C Flexibility

`inputs/market.py` and `inputs/config.py` must support both B2B and B2C scenarios. The key differences:

| Dimension | B2C | B2B |
|-----------|-----|-----|
| Persona mode | **Distribution** -- sample from demographic distributions (age, income, location) | **Segment** -- define named buyer segments with traits (role, company size, budget authority) |
| Persona traits | Demographics (age, gender, income, education, location) | Firmographics (role, company size, industry, budget, tech maturity) |
| Price framing | Per-unit, monthly, one-time | Per-seat/mo, usage-based, annual contract |
| Market context | Consumer category (e.g., "organic wine market in Germany") | Business category (e.g., "analytics platform for marketing teams") |

The `PersonaProfile` model uses a flexible `traits: dict[str, str]` field that works for both modes. The `MarketDefinition` model includes a `market_type: Literal["b2b", "b2c"]` field that downstream modules (personas, prompts) use to adjust behavior.

### MarketSimulator as the Hub

Same pattern as the old codebase -- `MarketSimulator` converts product feature dicts to MNL utilities, shares, revenue, and elasticities. All analysis modules receive a simulator instance rather than raw betas.

```python
class MarketSimulator:
    def __init__(self, betas: dict[str, float], market_size: int): ...
    def utility(self, product: dict) -> float: ...
    def shares(self, products: list[dict]) -> np.ndarray: ...
    def revenue(self, products: list[dict], price_key: str) -> pd.DataFrame: ...
    def elasticity(self, products: list[dict], price_param: str) -> pd.DataFrame: ...
```

---

## 7. Dependency Graph

```
inputs/config.py ─────────────────────────────────────────┐
inputs/market.py ─────────────────────────────────────────┤
                                                          │
--- Shared infrastructure (core/) ---                     │
core/personas.py ◄── inputs/market                        │
core/prompts.py ◄── inputs/market, core/personas          │
core/llm.py (standalone)                                  │
core/ssr.py ◄── core/llm                                  │
core/parser.py (standalone)                               │
                                                          │
--- CBC pipeline (conjoint/) ---                          │
conjoint/design.py ◄── inputs/config                      │
conjoint/survey.py ◄── conjoint/design, core/*            │
                                                          │
--- RCT pipeline (experimental/) ---                      │
experimental/vignette.py ◄── inputs/config, core/*        │
experimental/ate.py ◄── estimation/results                │
experimental/hte.py ◄── estimation/results (econml)       │
                                                          │
--- Estimation (shared) ---                               │
estimation/results.py (standalone, typed containers)      │
estimation/data_prep.py ◄── inputs/config                 │
estimation/amce.py ◄── estimation/results         (CBC)   │
estimation/mnl.py ◄── estimation/results          (CBC)   │
estimation/wtp.py ◄── estimation/mnl              (CBC)   │
estimation/demand.py ◄── estimation/mnl           (CBC)   │
                                                          │
--- Analysis ---                                          │
analysis/simulator.py ◄── estimation/mnl          (CBC)   │
analysis/pricing.py ◄── analysis/simulator        (CBC)   │
analysis/segments.py (standalone, uses sklearn)  (shared) │
analysis/tiers.py ◄── analysis/simulator          (RCT)   │
analysis/price_change.py ◄── analysis/simulator   (dual)  │
analysis/competitive.py ◄── analysis/simulator    (dual)  │
analysis/launch.py ◄── analysis/simulator         (dual)  │
                                                          │
--- Diagnostics (cross-cutting) ---                       │
diagnostics/personas.py ◄── core/personas          (D6)   │
diagnostics/design.py ◄── conjoint/design          (D6)   │
diagnostics/survey.py ◄── conjoint/survey          (D6)   │
diagnostics/estimation.py ◄── estimation/results   (D6)   │
diagnostics/analysis.py ◄── analysis/simulator     (D6)   │
                                                          │
pipeline/runner.py ◄── everything above                   │
pipeline/io.py (standalone)                               │
```

**Diagnostics pattern:** Each diagnostics module reads the output of its corresponding pipeline stage and produces warnings/pass/fail checks. `pipeline/runner.py` calls diagnostics after each stage and logs results. Diagnostics never block the pipeline — they report.

**Note on dual-mode analysis modules:** `price_change.py`, `competitive.py`, and `launch.py` can work in two modes:
- **CBC mode:** receives `MarketSimulator` (from MNL betas) for continuous simulation
- **RCT mode:** receives `ATEResults` for point-estimate scenario comparison

The modules accept either input and produce the appropriate deliverables.

**Key property:** No circular dependencies. Data flows top-to-bottom. Each module can be tested and understood independently.

---

## 8. Porting Strategy

For each old module, we decide: **port** (adapt existing code), **rewrite** (new implementation), or **defer**.

| Old File | Lines | Decision | New Location | Notes |
|----------|-------|----------|-------------|-------|
| `core/market_definitions.py` | 78 | **Rewrite** as Pydantic | `inputs/market.py` | Simple, cleaner with Pydantic. B2B + B2C persona modes. |
| `core/config.py` | 55 | **Rewrite** | `inputs/config.py` + `.env` | Merge with study config |
| `core/study_config.py` | 577 | **Rewrite** as Pydantic | `inputs/config.py` | 577 lines -> ~150 with Pydantic |
| `core/conjoint_survey.py` | 1467 | **Split + port** | `core/personas.py`, `core/prompts.py`, `core/ssr.py`, `core/parser.py`, `conjoint/design.py`, `conjoint/survey.py` | 1467 lines -> 6 files of ~150-250 each |
| `core/generate_synthetic_consumers.py` | 367 | **Port** | `core/personas.py` | Keep DemographicSampler + render_profile |
| `core/demand_estimation.py` | 1236 | **Rewrite** | `estimation/mnl.py`, `estimation/amce.py`, `estimation/wtp.py`, `estimation/demand.py` | Conditional logit via scipy L-BFGS-B. AMCE/WTP via statsmodels OLS. |
| `analysis/market_simulator.py` | 244 | **Port** (mostly as-is) | `analysis/simulator.py` | Clean, well-designed already |
| `analysis/pricing_analysis.py` | 565 | **Port** | `analysis/pricing.py` | Trim to core functions |
| `analysis/tier_design.py` | 470 | **Port** | `analysis/tiers.py` | Trim to core functions |
| `analysis/price_change_impact.py` | 316 | **Port** | `analysis/price_change.py` | Clean, port mostly as-is |
| `analysis/market_simulator.py` (competitive parts) | -- | **Port** | `analysis/competitive.py` | From `core/competitive_analysis.py` |
| `analysis/product_launch_simulator.py` | 285 | **Port** | `analysis/launch.py` | Clean, port mostly as-is |
| `core/saas_templates.py` | 533 | **Port** | `templates/saas.py` | Convenience, low priority |
| `client_intake/run_client_study.py` | 2050 | **Rewrite** | `pipeline/runner.py` | 2050 -> ~200-300 orchestration |
| `experimental/vignette_engine.py` | 589 | **Port** | `experimental/vignette.py` | P0.5: vignette engine for RCT studies |
| `experimental/ssr_scorer.py` | 437 | **Port** (merge) | `core/ssr.py` | SSR logic shared with CBC, merge into core |
| `experimental/ate_estimator.py` | 408 | **Port** | `experimental/ate.py` | P0.5: ATE estimation |
| `experimental/hte_estimator.py` | 407 | **Port** | `experimental/hte.py` | P0.5: HTE via econml causal forests |
| `experimental/experiment_config.py` | 227 | **Merge** | `inputs/config.py` | P0.5: RCT config fields added to StudyConfig |
| `analysis/tier_optimizer.py` | 772 | **Defer** | -- | P1: cross-study synthesis |
| `analysis/portfolio_analysis.py` | 364 | **Defer** | -- | P1: multi-product analysis |
| `experimental/*` | ~2500 | **Done** | `experimental/vignette.py`, `ate.py`, `hte.py` | P0.5: complete. Vignette engine, ATE (statsmodels HC3), HTE (econml CausalForestDML). |
| `deliverables/*` | ~3000+ | **Partial** | `reports/sections.py`, `renderer.py`, `pricing.py` | Pricing Discovery report done. 4 study-type reports remaining. |
| `research_wizard/*` | ~1000 | **Defer** | -- | P1: guided study config |

**Total old code:** ~12,000+ lines
**Minimal P0 estimate:** ~2,500-3,500 lines across ~20 files

---

## 9. Study Config Schema

### B2B Example

```json
{
  "client_name": "Acme Analytics",
  "study_type": "pricing",
  "research_questions": [
    "What is the optimal price for the Pro tier?",
    "Which features drive willingness-to-pay?"
  ],
  "market": {
    "name": "US B2B SaaS",
    "market_type": "b2b",
    "category": "Analytics platform for marketing teams",
    "currency": "USD",
    "currency_symbol": "$",
    "location": { "country": "United States" },
    "context": "Marketing analytics SaaS market"
  },
  "personas": [
    {
      "name": "Startup Founder",
      "weight": 0.30,
      "traits": {
        "role": "Founder / CEO",
        "company_size": "1-10 employees",
        "budget_authority": "Full",
        "price_sensitivity": "High",
        "tech_savviness": "High"
      }
    },
    {
      "name": "Enterprise Buyer",
      "weight": 0.40,
      "traits": {
        "role": "VP Marketing",
        "company_size": "500-2000 employees",
        "budget_authority": "Departmental",
        "price_sensitivity": "Low",
        "tech_savviness": "Medium"
      }
    }
  ],
  "attributes": [
    {
      "name": "price",
      "display_name": "Monthly Price (per seat)",
      "is_price": true,
      "levels": [
        { "name": "49", "value": 49, "display_text": "$49/seat/mo" },
        { "name": "99", "value": 99, "display_text": "$99/seat/mo" },
        { "name": "149", "value": 149, "display_text": "$149/seat/mo" },
        { "name": "199", "value": 199, "display_text": "$199/seat/mo" },
        { "name": "299", "value": 299, "display_text": "$299/seat/mo" }
      ]
    }
  ],
  "parameters": {
    "n_respondents": 50,
    "n_tasks": 6,
    "llm_model": "gpt-5-mini",
    "temperature": 1.0,
    "framing": "expert",
    "counterbalance": true,
    "include_none_option": true
  }
}
```

### B2C Example

```json
{
  "client_name": "Mangalitza Pork",
  "study_type": "pricing",
  "market": {
    "name": "Hungarian Premium Pork",
    "market_type": "b2c",
    "category": "Premium pork products",
    "currency": "HUF",
    "currency_symbol": "Ft",
    "location": { "country": "Hungary" },
    "context": "Mangalitza heritage breed pork market"
  },
  "personas": [
    {
      "name": "Health-Conscious Urban",
      "weight": 0.35,
      "traits": {
        "age_range": "30-45",
        "income": "Above average",
        "location": "Budapest",
        "diet_consciousness": "High",
        "shopping_habit": "Specialty stores + online"
      }
    }
  ]
}
```

The same `StudyConfig` schema handles both -- the `market_type` field tells downstream modules (persona generation, prompt framing) how to adapt.

---

*Last updated: March 2026*
