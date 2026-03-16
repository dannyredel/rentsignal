# RentSignal — Supabase Schema

## How to apply migrations

Go to your Supabase project dashboard → SQL Editor → paste each file in order:

1. `001_profiles.sql` — User profiles + auto-create trigger (from AUTH-SETUP-GUIDE.md)
2. `002_units.sql` — Portfolio units (the core entity)
3. `003_analyses.sql` — Cached analysis results (predict/comply/renovate)
4. `004_import_jobs.sql` — CSV import job tracking
5. `005_alerts.sql` — Monitoring alerts (P2, but schema ready now)
6. `006_batch_jobs.sql` — Batch analysis job tracking
7. `007_views.sql` — Portfolio dashboard views (summary, latest analysis per unit)
8. `008_functions.sql` — Helper functions (prediction limits, tier checks)

## Schema overview

```
auth.users (Supabase managed)
    │
    ├── profiles (1:1, auto-created on signup)
    │   └── plan_tier, predictions_used, display_name
    │
    ├── units (1:many, the portfolio)
    │   ├── address, plz, district, structural features
    │   ├── compliance fields (bathroom, kitchen, balcony...)
    │   ├── energy fields (class, consumption, fuel)
    │   ├── rent increase tracking (last increase date, 6yr history)
    │   └── is_monitored flag
    │
    ├── analyses (1:many per unit, immutable log)
    │   ├── type: predict | comply | renovate | full
    │   ├── result: full API response as JSONB
    │   └── denormalized: predicted_rent, is_compliant, overpayment...
    │
    ├── import_jobs (CSV upload tracking)
    │   └── status, column_mapping, errors
    │
    ├── batch_jobs (portfolio-wide analysis tracking)
    │   └── status, unit_ids, progress
    │
    └── alerts (monitoring notifications)
        └── type, message, severity, is_dismissed
```

## Key views

- `units_with_latest_analysis` — joins units with their most recent predict + comply results
- `portfolio_summary` — aggregated metrics per user (total units, avg gap, compliance exposure)

## RLS

All tables have Row Level Security enabled. Users can only access their own data via `auth.uid() = user_id`.

## Auth flow

1. User signs in with Google OAuth → Supabase creates `auth.users` row
2. Trigger `on_auth_user_created` auto-creates `profiles` row with `plan_tier = 'free'`
3. Frontend gets JWT → sends as `Authorization: Bearer <token>` to FastAPI
4. FastAPI validates JWT → extracts `user_id` → queries Supabase with service role
