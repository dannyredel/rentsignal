-- ============================================================
-- 002: Units table — the core portfolio entity
-- Each row is one apartment/unit in a user's portfolio.
-- Columns match ApartmentInput + ComplianceInput Pydantic schemas.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.units (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Address / location
  address       TEXT,                  -- full street address (optional)
  plz           INT,                   -- postal code (required for spatial)
  district      TEXT NOT NULL,         -- Berlin Bezirk
  lat           DOUBLE PRECISION,      -- latitude (from address resolve)
  lon           DOUBLE PRECISION,      -- longitude (from address resolve)

  -- Structural features (align with ApartmentInput)
  living_space_sqm    DOUBLE PRECISION NOT NULL CHECK (living_space_sqm > 0),
  rooms               DOUBLE PRECISION NOT NULL CHECK (rooms > 0),
  year_built          INT NOT NULL CHECK (year_built BETWEEN 1800 AND 2030),
  floor               INT DEFAULT 0,
  building_floors     INT DEFAULT 1,
  thermal_char        DOUBLE PRECISION DEFAULT 100,

  -- Binary amenities
  has_kitchen         BOOLEAN DEFAULT false,
  has_balcony         BOOLEAN DEFAULT false,
  has_elevator        BOOLEAN DEFAULT false,
  has_cellar          BOOLEAN DEFAULT false,
  has_garden          BOOLEAN DEFAULT false,
  is_new_construction BOOLEAN DEFAULT false,

  -- Categorical
  condition           TEXT DEFAULT 'well_kept',
  interior_quality    TEXT DEFAULT 'normal',
  flat_type           TEXT DEFAULT 'apartment',
  heating_type        TEXT DEFAULT 'central_heating',
  building_era        TEXT,              -- derived from year_built if not provided

  -- Compliance-specific fields
  current_rent_per_sqm      DOUBLE PRECISION,  -- current nettokalt rent €/m²
  previous_rent_per_sqm     DOUBLE PRECISION,  -- Vormiete (previous tenant) €/m²
  has_modern_bathroom       BOOLEAN,
  has_fitted_kitchen        BOOLEAN,
  has_parquet_flooring      BOOLEAN,
  has_modern_heating        BOOLEAN,
  has_good_insulation       BOOLEAN,
  has_basement_storage      BOOLEAN,
  location_quality          TEXT CHECK (location_quality IN ('einfach', 'mittel', 'gut')),
  is_first_rental_after_comprehensive_modernization BOOLEAN DEFAULT false,

  -- Energy (for CO2KostAufG)
  energy_class              TEXT CHECK (energy_class IN ('A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')),
  energy_consumption_kwh    DOUBLE PRECISION,  -- kWh/m²/year
  heating_fuel_type         TEXT,               -- gas, oil, district, heat_pump, etc.

  -- Rent increase tracking (for Mieterhöhung wizard)
  last_rent_increase_date   DATE,
  prior_increases_6yr_sqm   DOUBLE PRECISION DEFAULT 0,  -- sum of §559 increases in past 6 years

  -- Monitoring
  is_monitored              BOOLEAN DEFAULT false,

  -- User notes
  label                     TEXT,              -- user-assigned label, e.g. "Kreuzberg Altbau"
  notes                     TEXT,

  -- Timestamps
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_units_user_id ON public.units(user_id);
CREATE INDEX idx_units_plz ON public.units(plz);
CREATE INDEX idx_units_monitored ON public.units(user_id, is_monitored) WHERE is_monitored = true;

-- RLS: users can only access their own units
ALTER TABLE public.units ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own units"
  ON public.units FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own units"
  ON public.units FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own units"
  ON public.units FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own units"
  ON public.units FOR DELETE
  USING (auth.uid() = user_id);

-- Auto-update updated_at
CREATE TRIGGER units_updated_at
  BEFORE UPDATE ON public.units
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
