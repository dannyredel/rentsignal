-- ============================================================
-- 004: Import jobs — tracks CSV import status
-- ============================================================

CREATE TYPE import_status AS ENUM ('pending', 'mapping', 'processing', 'completed', 'failed');

CREATE TABLE IF NOT EXISTS public.import_jobs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  status          import_status NOT NULL DEFAULT 'pending',

  -- Upload metadata
  original_filename TEXT,
  total_rows        INT,

  -- Column mapping (set after user confirms mapping)
  -- e.g. {"Wohnfläche": "living_space_sqm", "PLZ": "plz", ...}
  column_mapping    JSONB,

  -- Detected columns from uploaded file (for mapping UI)
  -- e.g. ["Wohnfläche", "PLZ", "Baujahr", "Bezirk", ...]
  detected_columns  JSONB,

  -- Sample rows for preview (first 5 rows)
  sample_rows       JSONB,

  -- Processing results
  rows_imported     INT DEFAULT 0,
  rows_skipped      INT DEFAULT 0,
  errors            JSONB,            -- array of {row: N, error: "..."}

  -- Timestamps
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at  TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

CREATE INDEX idx_import_jobs_user ON public.import_jobs(user_id, created_at DESC);

-- RLS
ALTER TABLE public.import_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own import jobs"
  ON public.import_jobs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own import jobs"
  ON public.import_jobs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own import jobs"
  ON public.import_jobs FOR UPDATE
  USING (auth.uid() = user_id);
