-- ============================================================
-- 008: Helper functions
-- ============================================================

-- Reset prediction counter monthly (called by cron or on-demand)
CREATE OR REPLACE FUNCTION public.reset_prediction_counters()
RETURNS void AS $$
BEGIN
  UPDATE public.profiles
  SET
    predictions_used_this_month = 0,
    predictions_reset_date = (date_trunc('month', now()) + interval '1 month')::date
  WHERE predictions_reset_date <= CURRENT_DATE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user can make a prediction (Free tier: 3/month, Pro+: unlimited)
CREATE OR REPLACE FUNCTION public.can_predict(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_tier TEXT;
  v_used INT;
BEGIN
  SELECT plan_tier, predictions_used_this_month
  INTO v_tier, v_used
  FROM public.profiles
  WHERE user_id = p_user_id;

  IF v_tier IN ('pro', 'business', 'enterprise') THEN
    RETURN true;
  END IF;

  -- Free tier: 3 predictions/month
  RETURN v_used < 3;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Increment prediction counter
CREATE OR REPLACE FUNCTION public.increment_prediction_count(p_user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE public.profiles
  SET predictions_used_this_month = predictions_used_this_month + 1
  WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get unit count for tier limit checks
-- Free: 3, Pro: 15, Business+: unlimited
CREATE OR REPLACE FUNCTION public.get_unit_count(p_user_id UUID)
RETURNS INT AS $$
BEGIN
  RETURN (SELECT COUNT(*) FROM public.units WHERE user_id = p_user_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user can add another unit (enforces tier limits)
CREATE OR REPLACE FUNCTION public.can_add_unit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_tier TEXT;
  v_count INT;
BEGIN
  SELECT plan_tier INTO v_tier FROM public.profiles WHERE user_id = p_user_id;
  SELECT COUNT(*) INTO v_count FROM public.units WHERE user_id = p_user_id;

  IF v_tier IN ('business', 'enterprise') THEN
    RETURN true;
  ELSIF v_tier = 'pro' THEN
    RETURN v_count < 15;
  ELSE
    -- Free tier
    RETURN v_count < 3;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
