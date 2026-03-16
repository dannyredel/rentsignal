---
name: paper-reviewer
description: Reads academic papers in docs/papers/, produces per-paper summaries in docs/papers/summaries/, then updates the compressed docs/PAPER-COMPILATION.md with actionable takeaways for MietOptimal
---

# Paper Reviewer Skill

## Purpose
Review academic/industry papers related to rental price prediction, hedonic pricing, ML-based valuation, hybrid models, and spatial analytics. Produce two layers of output:
1. **Per-paper summaries** (detailed, standalone) → `docs/papers/summaries/`
2. **Compilation doc** (compressed, action-oriented) → `docs/PAPER-COMPILATION.md`

## Workflow

### Step 1: Inventory
- Scan `docs/papers/` for all PDF files
- List each paper with title, authors, year
- Check `docs/papers/summaries/` for already-summarized papers — skip those unless asked to re-review

### Step 2: Per-Paper Summary → `docs/papers/summaries/{filename}_summary.md`

For each new paper, create a standalone summary file:

```markdown
# Summary: [Paper Title]

## Citation
Authors, title, year, journal/venue

## Research Question
What problem does this paper address?

## Data
- Dataset(s) used (city, country, size, time period)
- Key variables / features

## Methodology
- Modeling approach (hedonic, ML, hybrid, deep learning, spatial, ensemble, etc.)
- Specific algorithms and configurations
- Evaluation metrics used
- Train/test split strategy

## Key Results
- Performance comparison table (if multiple methods tested)
- Which method wins, by how much
- Feature importance findings
- Spatial effects (if any)

## Feature Engineering
- Novel features or transformations worth noting
- Spatial variables used
- Interaction terms or nonlinear treatments

## Strengths
- What this paper does well

## Limitations
- What doesn't generalize or apply to our context

## Relevance to MietOptimal: [HIGH / MEDIUM / LOW]
- Why this score
- What specifically we can use
```

### Step 3: Update Compilation → `docs/PAPER-COMPILATION.md`

After writing all summaries, update (or create) the compilation doc. This is **compressed and action-oriented** — a busy developer should get the full picture in 5 minutes.

```markdown
# Paper Compilation — Literature Review for MietOptimal
## Last updated: [date]
## Papers reviewed: [count]

## Executive Summary
[2-3 paragraphs max: what the literature consensus is, what it means for us]

## Method Scorecard
| Paper | Method(s) | Best R² | Best RMSE | Dataset | City | Relevance |
|-------|-----------|---------|-----------|---------|------|-----------|
| ... | ... | ... | ... | ... | ... | HIGH/MED/LOW |

## What We Should Steal
[Prioritized, numbered list of specific techniques/features/design choices to adopt, with paper reference]

1. **[Technique]** — [one-line why] (from: [Paper])
2. ...

## Feature Engineering Consensus
[Table: which features matter across multiple papers, how often they appear, typical importance rank]

## Implications for Our Architecture

### Model Selection
[Does literature validate XGBoost + SHAP? Should we consider hybrid? What benchmark to target?]

### Feature Pipeline Changes
[Concrete additions/modifications to our feature set based on literature]

### Spatial Features
[Literature support for satellite/spatial approach — any precedent?]

### Hybrid Hedonic-ML
[If/how to combine hedonic structure with ML — worth it for us?]

### Caveats & Risks
[What the literature warns about — overfitting, data leakage, spatial autocorrelation, etc.]

## Full Summaries
See `docs/papers/summaries/` for detailed per-paper breakdowns.
```

## Rules
- **Summaries are detailed** — someone should be able to understand the paper without reading it
- **Compilation is compressed** — decisions, not descriptions. "Steal this" not "this paper found that"
- When updating compilation with new papers, integrate them into existing sections — don't just append
- Always note when a paper's context differs from ours (e.g., sale prices vs rental, US vs German market)
- Flag any techniques that contradict our current architecture decisions (logged in `tracking/Decisions.md`)

## Key Context
- MietOptimal uses XGBoost + SHAP for rent prediction (Decision: 2025-03-14)
- German rental market, Berlin-specific
- Dual-method renovation estimation (matching + conjoint)
- Satellite-derived spatial features as differentiator
- Target: hackathon demo with credible methodology
- Daniel's background: econometrics, industrial organization, causal ML, spatial analytics
