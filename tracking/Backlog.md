# Backlog
## MietOptimal — Task Queue

---

## 🔴 P0 — Blocking

- [ ] **Task 1: Source Berlin rental listing data** (~2-3h)
  - Dependencies: none
  - Download Kaggle ImmoScout24 → filter Berlin → clean → save as parquet
  - Fallback: generate synthetic if real data unavailable

- [ ] **Task 2: Train XGBoost rent prediction model** (~3-4h)
  - Dependencies: Task 1
  - Feature engineering → train → evaluate (R², RMSE) → SHAP → save artifacts

## 🟡 P1 — High Priority

- [ ] **Task 3: Calibrate BeeSignal conjoint for rental context** (~3-4h)
  - Dependencies: Task 1 (for calibration validation)
  - Define apartment attributes/levels → synthetic tenant personas → run simulation → validate WTP

- [ ] **Task 4: Spatial feature extraction pipeline** (~3-4h)
  - Dependencies: none (parallel)
  - Sentinel-2 NDVI → Gemini aerial extraction → OSM transit/POI → validate vs Umweltatlas

- [ ] **Task 5: Build Mietpreisbremse compliance engine** (~2h)
  - Dependencies: none (parallel)
  - §556d BGB rules + §559 BGB modernization → Python module

## 🟢 P2 — Important

- [ ] **Task 6: Build matching estimator for observational CATE** (~2h)
  - Dependencies: Task 1, Task 2
  - Nearest-neighbor matching → ATE/CATE → bootstrap CIs → compare with conjoint

- [ ] **Task 7: Set up infrastructure partner accounts** (~1-2h)
  - Dependencies: none
  - Gemini API key, Gradium API key, Lovable account, Entire CLI, Supabase project

- [ ] **Task 8: Prepare demo apartments and narratives** (~2h)
  - Dependencies: Tasks 2, 3, 4, 5
  - 5 apartments with features, pre-computed outputs, speaker notes

- [ ] **Task 9: Draft pitch deck content** (~1.5h)
  - Dependencies: Task 8
  - Gamma-ready slide text + speaker notes

## ⚪ P3 — Nice to Have

- [ ] **Task 10: Test Lovable end-to-end** (~1-2h)
  - Dependencies: knowing final screen designs
  - Full prompt for 3 screens → generate → note issues

- [ ] **Task 11: Record backup demo video** (~30min)
  - Dependencies: everything working
  - Screen recording with narration

- [ ] **Task 12: Prepare "scale with Buena" Q&A slide** (~30min)
  - Dependencies: none
