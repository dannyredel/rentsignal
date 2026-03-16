-- ============================================================
-- 003: Analyses table — cached results from predict/comply/renovate
-- One row per analysis run per unit. Latest row = current state.
-- ============================================================

CREATE TYPE analysis_type AS ENUM ('predict', 'comply', 'renovate', 'full');

CREATE TABLE IF NOT EXISTS public.analyses (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  unit_id      UUID NOT NULL REFERENCES public.units(id) ON DELETE CASCADE,
  user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  type         analysis_type NOT NULL,

  -- Store the full API response as JSONB
  -- For 'predict': PredictionResult schema
  -- For 'comply': ComplianceResult schema
  -- For 'renovate': RenovationResult schema
  -- For 'full': { predict: {...}, comply: {...}, renovate: {...} }
  result       JSONB NOT NULL,

  -- Denormalized key metrics for portfolio queries (avoid parsing JSONB)
  predicted_rent_sqm       DOUBLE PRECISION,  -- from predict
  rent_gap_pct             DOUBLE PRECISION,  -- from predict (current vs predicted)
  is_compliant             BOOLEAN,           -- from comply
  overpayment_annual       DOUBLE PRECISION,  -- from comply (€/year exposure)
  legal_max_rent_sqm       DOUBLE PRECISION,  -- from comply
  headroom_sqm             DOUBLE PRECISION,  -- from comply (room to increase)

  -- Metadata
  model_version            TEXT,
  analyzed_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for portfolio dashboard queries
CREATE INDEX idx_analyses_unit ON public.analyses(unit_id, analyzed_at DESC);
CREATE INDEX idx_analyses_user ON public.analyses(user_id, type, analyzed_at DESC);
CREATE INDEX idx_analyses_compliance ON public.analyses(user_id, is_compliant)
  WHERE type IN ('comply', 'full');
CREATE INDEX idx_analyses_rent_gap ON public.analyses(user_id, rent_gap_pct DESC NULLS LAST)
  WHERE type IN ('predict', 'full');

-- RLS
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own analyses"
  ON public.analyses FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
  ON public.analyses FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users should not update or delete analyses (immutable audit log)
-- Backend can delete old ones via service role if needed
