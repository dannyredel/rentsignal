-- ============================================================
-- 001: Profiles table + auto-create trigger on Google OAuth
-- From: frontend/AUTH-SETUP-GUIDE.md
-- ============================================================

-- Profiles table: one row per user, created on first login
CREATE TABLE IF NOT EXISTS public.profiles (
  user_id     UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  email        TEXT,
  company_name TEXT,
  plan_tier    TEXT NOT NULL DEFAULT 'free'
               CHECK (plan_tier IN ('free', 'pro', 'business', 'enterprise')),

  -- Free tier: 3 predictions/month. Pro+: unlimited.
  predictions_used_this_month INT NOT NULL DEFAULT 0,
  predictions_reset_date      DATE NOT NULL DEFAULT (date_trunc('month', now()) + interval '1 month')::date,

  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS: users can only see/edit their own profile
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = user_id);

-- Auto-create profile on first signup (Google OAuth or email)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (
    user_id,
    display_name,
    email,
    plan_tier,
    predictions_used_this_month,
    predictions_reset_date
  )
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NEW.email,
    'free',
    0,
    (date_trunc('month', now()) + interval '1 month')::date
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
