-- ============================================================
-- 009: Add rooms column to units_with_latest_analysis view
-- Must DROP + CREATE because PostgreSQL doesn't allow column
-- reordering via CREATE OR REPLACE VIEW.
-- portfolio_summary depends on this view, so drop it first.
-- ============================================================

DROP VIEW IF EXISTS public.portfolio_summary;
DROP VIEW IF EXISTS public.units_with_latest_analysis;

CREATE VIEW public.units_with_latest_analysis AS
SELECT
  u.id AS unit_id,
  u.user_id,
  u.label,
  u.address,
  u.plz,
  u.district,
  u.living_space_sqm,
  u.rooms,
  u.year_built,
  u.current_rent_per_sqm,
  u.is_monitored,
  u.energy_class,
  u.created_at AS unit_created_at,

  -- Latest predict analysis
  pa.predicted_rent_sqm,
  pa.rent_gap_pct,
  pa.analyzed_at AS predict_analyzed_at,

  -- Latest comply analysis
  ca.is_compliant,
  ca.overpayment_annual,
  ca.legal_max_rent_sqm,
  ca.headroom_sqm,
  ca.analyzed_at AS comply_analyzed_at,

  -- Full result JSONBs (for detail views)
  pa.result AS predict_result,
  ca.result AS comply_result

FROM public.units u
LEFT JOIN LATERAL (
  SELECT predicted_rent_sqm, rent_gap_pct, analyzed_at, result
  FROM public.analyses
  WHERE unit_id = u.id AND type IN ('predict', 'full')
  ORDER BY analyzed_at DESC
  LIMIT 1
) pa ON true
LEFT JOIN LATERAL (
  SELECT is_compliant, overpayment_annual, legal_max_rent_sqm, headroom_sqm, analyzed_at, result
  FROM public.analyses
  WHERE unit_id = u.id AND type IN ('comply', 'full')
  ORDER BY analyzed_at DESC
  LIMIT 1
) ca ON true;

-- Recreate portfolio_summary (depends on units_with_latest_analysis)
CREATE VIEW public.portfolio_summary AS
SELECT
  user_id,
  COUNT(*) AS total_units,
  COUNT(*) FILTER (WHERE predicted_rent_sqm IS NOT NULL) AS analyzed_units,
  AVG(rent_gap_pct) AS avg_rent_gap_pct,
  SUM(CASE WHEN rent_gap_pct < 0 THEN
    ABS(rent_gap_pct / 100.0) * current_rent_per_sqm * living_space_sqm * 12
    ELSE 0 END) AS total_underpriced_annual,
  COUNT(*) FILTER (WHERE is_compliant = false) AS non_compliant_units,
  SUM(COALESCE(overpayment_annual, 0)) AS total_compliance_exposure_annual,
  COUNT(*) FILTER (WHERE is_monitored = true) AS monitored_units
FROM public.units_with_latest_analysis
GROUP BY user_id;
