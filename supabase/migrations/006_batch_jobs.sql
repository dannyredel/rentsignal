-- ============================================================
-- 006: Batch analysis jobs — tracks async portfolio-wide analysis
-- ============================================================

CREATE TYPE batch_status AS ENUM ('queued', 'running', 'completed', 'failed');

CREATE TABLE IF NOT EXISTS public.batch_jobs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  status          batch_status NOT NULL DEFAULT 'queued',
  job_type        TEXT NOT NULL DEFAULT 'analyze',  -- 'analyze', 'monitor_nightly'

  -- Scope: which units to process
  unit_ids        UUID[],              -- null = all units for this user
  total_units     INT NOT NULL DEFAULT 0,
  processed_units INT NOT NULL DEFAULT 0,
  failed_units    INT NOT NULL DEFAULT 0,

  -- Error log
  errors          JSONB,               -- array of {unit_id, error}

  -- Timestamps
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at   TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

CREATE INDEX idx_batch_jobs_user ON public.batch_jobs(user_id, created_at DESC);

-- RLS
ALTER TABLE public.batch_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own batch jobs"
  ON public.batch_jobs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own batch jobs"
  ON public.batch_jobs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own batch jobs"
  ON public.batch_jobs FOR UPDATE
  USING (auth.uid() = user_id);
