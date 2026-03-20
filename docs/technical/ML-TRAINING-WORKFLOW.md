# ML Training Workflow
## RentSignal — Data & Model Engineering

*Source of truth for how data flows into models, how models are versioned, and when they are retrained.*

---

## 1. Guiding Principles

Three constraints shape every decision here:

- **Reproducibility**: given a data file and a version tag, anyone can regenerate the exact model artifact.
- **Honest evaluation**: test-set accuracy numbers are never inflated by training-set leakage.
- **Practicality**: no tooling heavier than what notebooks + `model_config.json` already support. This is a solo build.

Five guarantees the workflow must preserve:

1. The sealed test set is never touched during training or hyperparameter search — evaluated exactly once, at the end.
2. Every model artifact is traceable to a specific data file via SHA-256 hash.
3. Retraining produces a new version tag; artifacts are never overwritten in-place.
4. SHAP values in the API always correspond to the currently deployed model.
5. The inflation adjustment is a clearly documented, temporary measure with a defined removal trigger.

---

## 2. Data Pools

Three distinct data pools with different roles:

| Pool | Source | Train? | Evaluate? | Notes |
|---|---|---|---|---|
| **Public listings** | Kaggle / Apify scrape | ✅ | ✅ | Foundation dataset |
| **Sealed test set** | Subset of public listings, frozen | ❌ never | ✅ only | Defined at v1 split, never regenerated |
| **Client units** | User-added via portfolio CRUD | ✅ | ❌ never | GDPR consent required in ToS |

**Why client units go to training only:** Client units are real, verified, current-price rentals — better signal than scraped ask prices. But they are persistent entities (a landlord keeps managing the same unit for years), so they cannot serve as an unbiased evaluation set. Model accuracy is always measured on public-data holdout only.

**GDPR:** ToS must include: *"By adding a unit, you consent to anonymized property data being used to improve our rent prediction models."* The data used is features only (rooms, bezirk, rent/m²) — no PII.

---

## 3. Split Strategy

### Current state (v3.x)
The v3 models use an 80/20 random row split with `random_state=42` on the Kaggle public dataset. The test set is effectively sealed by the fixed seed. This is acceptable for the current data vintage.

### Target state (v4.0.0 — Apify fresh data)
When fresh data arrives, move to **PLZ-blocked 70/15/15** splits using `GroupShuffleSplit`:

```python
from sklearn.model_selection import GroupShuffleSplit

# Assign whole PLZs to splits — prevents spatial leakage
gss_test = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
train_val_idx, test_idx = next(gss_test.split(X, y, groups=df["plz"]))

gss_val = GroupShuffleSplit(n_splits=1, test_size=0.176, random_state=42)
train_idx, val_idx = next(gss_val.split(
    X.iloc[train_val_idx], y.iloc[train_val_idx], groups=df["plz"].iloc[train_val_idx]
))
```

**Why PLZ-blocked:** Spatial features (OSM, satellite) are at PLZ centroid level — all ~54 listings in a PLZ share identical feature values. A random row split puts the same PLZ in both train and test, letting the model learn PLZ fingerprints rather than generalizing. PLZ-blocked split guarantees zero spatial leakage.

**Stratification:** Stratify PLZ assignment by median bezirk × rent quintile to preserve geographic and price-range balance across splits.

**Sealed test PLZ list:** After v4.0.0 split, write `data/splits/test_plzs_v1.txt` (one PLZ per line). This file is permanent — never delete or regenerate. Future retrains on new data assign the same PLZs to the test set for consistent benchmarking.

### Encoder fit order
Fit `OrdinalEncoder` **only on train split rows**, then `transform` val and test. Current v3 notebooks fit on the full dataset before splitting (minor contamination). Fix this in v4.0.0.

---

## 4. Model Versioning

### Semantic versioning: `MAJOR.MINOR.PATCH`

| Increment | Trigger | Example |
|---|---|---|
| **Major** | New data vintage (Apify replaces Kaggle) | v3 → v4.0.0 |
| **Minor** | New features added (noise data, per-listing coords, new city) | v3.0.0 → v3.1.0 |
| **Patch** | Hyperparameter tuning only, same data + features | v3.0.0 → v3.0.1 |

The deployed API always serves **one active version**. Versioning enables rollback and traceability, not multi-version serving (out of scope).

### Artifact naming

```
models/
  xgboost_rent_v3.0.0.joblib       ← versioned (permanent)
  shap_explainer_v3.0.0.joblib     ← versioned (permanent)
  feature_encoder_v3.0.0.joblib    ← versioned (permanent)
  xgboost_rent.joblib              ← symlink → active version
  shap_explainer.joblib            ← symlink → active version
  feature_encoder.joblib           ← symlink → active version
  active_version.txt               ← contains "v3.0.0" (used by ml_service.py)
  model_config.json                ← always reflects active version
```

The non-versioned names (`xgboost_rent.joblib`) are what Railway's `ml_service.py` loads — no code change needed when deploying a new version. Update the symlinks (Linux/Railway) or `active_version.txt` to switch.

### `model_config.json` schema (extended)

```json
{
  "model_version": "v3.0.0",
  "trained_at": "2026-03-15T15:48:00",
  "data_source": "kaggle_immoscout24_berlin_2018_2019",
  "data_file": "data/processed/listings_with_spatial.parquet",
  "data_file_sha256": "573345c6e56d1095f45e79729ff6e1badf011124c0b2b43d8bfc64688dd331ad",
  "split_strategy": "random_80_20_seed42",
  "split_file": null,
  "n_train_rows": 8179,
  "n_val_rows": null,
  "n_test_rows": 2045,
  "inflation_factor": 1.378,
  "inflation_factor_active": true,
  "inflation_note": "IBB rent index 2019→2024 +37.8%. Remove when retraining on fresh data.",
  "sklearn_version": "1.6.x",
  "xgboost_version": "3.x",
  "metrics": { "r2": 0.7491, "rmse": 2.5923, "mae": 1.7033 },
  "...": "...existing fields..."
}
```

---

## 5. Data Lineage

Every served prediction traces back through this chain:

```
Raw data
  data/raw/immo_scout_berlin_2019.csv          [immutable — never modify]
       │
       ▼ notebook 01_data_exploration
  data/processed/listings_clean.parquet        [SHA-256: 825685a1...]
       │
       ▼ notebooks 03a (OSM) + 03b (Sentinel-2)
  data/processed/listings_with_spatial.parquet [SHA-256: 573345c6...]
       │
       ▼ notebook 04_spatial_model_integration  (train split only)
  models/xgboost_rent_v3.0.0.joblib
  models/shap_explainer_v3.0.0.joblib
  models/feature_encoder_v3.0.0.joblib
       │
       ▼ backend/services/ml_service.py
  predicted_rent_sqm = raw_prediction × inflation_factor (if active)
  shap_values = raw_shap × inflation_factor (if active)
```

The SHA-256 hash in `model_config.json` is the lineage anchor: it proves which exact parquet produced which model artifact. Compute it at training time:

```python
import hashlib
sha = hashlib.sha256(open("data/processed/listings_with_spatial.parquet", "rb").read()).hexdigest()
```

**For client units:** When client units are incorporated into training (v4.x+), add a `client_units_count` field to `model_config.json` indicating how many client-contributed rows supplemented the public dataset. No individual unit is identifiable from this count.

---

## 6. Retraining Cadence

### Philosophy: event-triggered, not calendar-based

Calendar retraining (e.g., "every quarter no matter what") is operationally heavy for a solo build and wastes compute when nothing has meaningfully changed. The right trigger is a *reason* to retrain.

### Primary trigger — new data arrives

The main reason to retrain is fresh market data. When an Apify scrape produces a new Berlin listings dataset, retrain. This is the most common trigger and produces a major version bump (v3 → v4.0.0).

Scraping cadence: **quarterly** (~10k Berlin listings per run, ~$5-10 Apify cost). Berlin rents drift ~7% annually (~0.7-1.0 €/m² added to prediction error per year of staleness). Quarterly keeps the model within one seasonal cycle of market conditions.

### Secondary trigger — drift detection

Track model MAE on a rolling window of "verifiable" predictions: cases where a client entered the actual current rent and the model predicted market rent. Compare against the training baseline MAE (1.70 €/m²).

**Rule:** if rolling-30-day MAE on client units exceeds 3.0 €/m² (≈ 15% above baseline, or 1 standard deviation), flag for investigation. Either the market has shifted significantly or there is a data quality issue.

This check is manual for now: once a month, run a quick query against the `analyses` table comparing `predicted_rent_sqm` to the actual rent entered by the client. If drift is confirmed, trigger an early scrape + retrain.

### Tertiary trigger — new features available

If new data sources become available (Umweltatlas noise data, per-listing GPS coordinates, Hamburg Mietspiegel), retrain with the new features. This is a minor version bump (v3.0.0 → v3.1.0).

### What does NOT trigger retraining

- Seasonal price fluctuations (covered by data vintage)
- Small metric fluctuations within noise
- New users or new units added
- Routine bug fixes or API changes

### Time budget per retrain

| Step | Estimated time |
|---|---|
| Apify scrape (~10k listings) | 30-60 min |
| Data cleaning (notebook 01) | 15 min |
| OSM feature extraction (notebook 03a) | 2-3 h (bottleneck) |
| Sentinel-2 download + processing (notebook 03b) | 1-2 h |
| Model training + GridSearchCV (notebook 04) | 30-45 min |
| SHAP regeneration | 10 min |
| Evaluation + report | 15 min |
| **Total** | **~5-7 h** |

Plan a half-day for a full retrain. If only hyperparameters change (patch bump), skip notebooks 01-03 and run only notebook 04 on the existing spatial parquet.

---

## 7. SHAP Regeneration Protocol

After **every** model retrain, regenerate the SHAP explainer immediately. Do not skip this.

**Why it is not optional:** The `shap_explainer.joblib` stores the model's training distribution as `expected_value` (the base value for waterfall charts). After retraining, `expected_value` changes because the training data distribution changes. Loading the old explainer against a new model produces silent errors: SHAP attributions sum to the wrong base value, making all waterfall charts incorrect.

**Protocol:**

1. Retrain model (notebook 04, training split only)
2. Immediately run the SHAP cell in notebook 04
3. Save `shap_explainer_vX.Y.Z.joblib` with matching version tag
4. Add this sanity check before saving:

```python
assert abs(explainer.expected_value - model.predict(X_train).mean()) < 0.01, \
    "Explainer expected_value does not match model training mean — artifact mismatch"
```

5. Update symlinks / `active_version.txt`
6. Deploy to Railway (git push → auto-deploy)
7. Verify: call `GET /predict` with demo apartment 1, check `base_value` is plausible (≈ mean rent × inflation_factor)

**Note:** The `TreeExplainer` is exact (not approximate) for XGBoost. The 1,000-row sample used for visualization does not affect the explainer object itself. Keep the sampling as-is.

---

## 8. Inflation Factor — Transition Plan

### Current state (v3.x)

`inflation_factor = 1.378` is applied at prediction time in `ml_service.py`. It converts 2018-2019 model outputs to approximate 2024 prices (IBB Wohnungsmarktbericht Berlin rent index, 2019→2024 = +37.8%).

The factor is now **config-driven**, not hardcoded. `ml_service.py` reads `inflation_factor` and `inflation_factor_active` from `model_config.json` at startup.

### Removal trigger

When training data is replaced with fresh 2024-2025 Apify listings, the model learns current prices directly. Setting `"inflation_factor_active": false` in the new `model_config.json` disables the adjustment — **no code change needed**.

### Full transition checklist (v4.0.0 cutover)

- [ ] Retrain on fresh Apify data
- [ ] Set `"inflation_factor_active": false` in new `model_config.json`
- [ ] Re-run notebook 06 (matching estimator) on fresh data — CATE values (kitchen +€4.01/m²) were derived from 2019 prices
- [ ] Update `conjoint_results.json` with fresh-data CATE estimates
- [ ] Re-run notebook 08 (demo apartments) — demo JSONs have hardcoded 2024-adjusted values
- [ ] Remove `apply_inflation()` call in `backend/routers/demo.py`
- [ ] Verify `renovation_service.py` uses updated CATE values

### Rollback

If v4.0.0 performs worse than expected (R² < 0.72), revert `active_version.txt` to `v3.0.0`. The versioned joblib files remain in `models/` — rollback is instantaneous without retraining.

---

## 9. Retraining Checklist

Run this checklist for every retrain. Check each box before proceeding to the next step.

### Pre-training
- [ ] Raw data file saved to `data/raw/` with date in filename (e.g., `apify_berlin_2025-06.parquet`)
- [ ] SHA-256 hash of raw file recorded
- [ ] `listings_clean.parquet` regenerated from scratch (notebook 01)
- [ ] Spatial features recomputed if new PLZs present (notebooks 03a, 03b)
- [ ] `data/splits/test_plzs_v1.txt` preserved — do not regenerate
- [ ] New version tag decided (`vMAJOR.MINOR.PATCH`)

### Training
- [ ] `OrdinalEncoder` fit **only** on train split rows
- [ ] `GridSearchCV` uses train split only (val and test untouched)
- [ ] Val set used only to confirm generalization after hyperparameter selection
- [ ] Test set evaluated **exactly once** at end — record metrics, then close the notebook

### Artifacts
- [ ] `xgboost_rent_vX.Y.Z.joblib` saved
- [ ] `shap_explainer_vX.Y.Z.joblib` saved immediately after model save
- [ ] `feature_encoder_vX.Y.Z.joblib` saved
- [ ] Sanity check passed: `explainer.expected_value ≈ model.predict(X_train).mean()`
- [ ] `model_config.json` updated: version, data hashes, trained_at, metrics, inflation flags
- [ ] `active_version.txt` updated
- [ ] `training_report.md` regenerated

### Post-training
- [ ] Inflation factor status confirmed correct in `model_config.json`
- [ ] Deploy to Railway (`git push` → auto-deploy)
- [ ] Call `GET /predict` with demo apartment 1 — verify `predicted_rent_sqm` is in plausible range (€14-22/m² for Berlin)
- [ ] `tracking/Changelog.md` updated with new model version and metrics
- [ ] `tracking/Memory.md` updated with model version and any new gotchas
