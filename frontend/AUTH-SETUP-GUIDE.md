# RentSignal — Auth Setup Guide
## Google OAuth via Supabase (copy-paste ready)

*Time: ~30 minutes. Do this once, never think about auth again.*

---

## Why Supabase + Google OAuth (not Lovable built-in)

1. Your FastAPI backend needs to validate users (tier checks, rate limits, portfolio ownership)
2. Supabase JWTs work natively with FastAPI — one middleware, done
3. You'll need background jobs (nightly monitoring, digest emails) that query user data
4. Migration from Lovable auth → Supabase auth later is painful — do it now

## Why Google OAuth (not email/password)

1. One click to sign up — no password to create, no email to verify
2. Every property manager has a Google account
3. Reduces signup friction by ~60% vs email/password
4. You can always add email/password later as a secondary option

---

## Step 1: Google Cloud Console (10 min)

### 1a. Create OAuth credentials

1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new project (or use existing): "RentSignal"
3. Click "Create Credentials" → "OAuth client ID"
4. Application type: "Web application"
5. Name: "RentSignal Web"
6. Authorized JavaScript origins:
   ```
   http://localhost:3000
   http://localhost:5173
   https://your-app.lovable.app
   https://rentsignal.de
   ```
7. Authorized redirect URIs:
   ```
   https://<YOUR_SUPABASE_PROJECT>.supabase.co/auth/v1/callback
   ```
   (Get your project URL from Supabase dashboard → Settings → API)
8. Click "Create"
9. Copy the **Client ID** and **Client Secret** — you'll need them next

### 1b. Configure OAuth consent screen

1. Go to "OAuth consent screen" in the left sidebar
2. User type: "External"
3. App name: "RentSignal"
4. User support email: your email
5. Authorized domains: add `supabase.co` and `rentsignal.de`
6. Developer contact: your email
7. Scopes: just `email` and `profile` (default)
8. Test users: add your own email for now
9. Save

**Note:** While in "Testing" mode, only emails you add as test users can sign in. When ready to launch, submit for verification (takes 1-3 days) or switch to "Production" (immediate, but shows "unverified app" warning until verified).

---

## Step 2: Supabase Configuration (5 min)

1. Go to your Supabase project dashboard
2. Navigate to: Authentication → Providers → Google
3. Toggle Google to **Enabled**
4. Paste your **Client ID** from Step 1
5. Paste your **Client Secret** from Step 1
6. Authorized Client IDs: leave empty (or add your Client ID)
7. Click Save

That's it for Supabase.

---

## Step 3: Frontend — Lovable/React (10 min)

### 3a. The login page

Replace your current login page with this. It shows Google as the primary option with email/password as secondary.

```tsx
// LoginPage.tsx
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

const LoginPage = () => {
  const navigate = useNavigate();

  // Check if already logged in
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) navigate("/dashboard");
    });
  }, []);

  const handleGoogleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/dashboard`,
      },
    });
    if (error) console.error("Login error:", error.message);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-sm p-8 border border-border bg-card">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" 
            stroke="#00BC72" strokeWidth="2.5" strokeLinecap="round" 
            strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          <span className="text-xl font-heading font-semibold">RentSignal</span>
        </div>

        <h2 className="text-lg font-heading font-semibold text-center mb-2">
          Sign in to your account
        </h2>
        <p className="text-sm text-muted-foreground text-center mb-8">
          Rent intelligence for your portfolio
        </p>

        {/* Google OAuth — primary, most prominent */}
        <Button
          onClick={handleGoogleLogin}
          variant="outline"
          className="w-full mb-4 h-11 text-sm font-medium"
        >
          <svg className="mr-2" width="18" height="18" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Continue with Google
        </Button>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border"></div>
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="px-2 bg-card text-muted-foreground">or</span>
          </div>
        </div>

        {/* Email/password — secondary, smaller */}
        <p className="text-xs text-center text-muted-foreground">
          Prefer email?{" "}
          <a href="/login/email" className="text-primary underline">
            Sign in with email and password
          </a>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
```

### 3b. Auth callback handling

Supabase handles the OAuth callback automatically. After Google auth, the user is redirected to your `redirectTo` URL with a session. You just need to make sure your router handles it:

```tsx
// In your App.tsx or router setup
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

function App() {
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  // ... route based on session
}
```

### 3c. Protected route wrapper

```tsx
// ProtectedRoute.tsx
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

const ProtectedRoute = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });
  }, []);

  if (loading) return null; // or a spinner
  if (!session) return <Navigate to="/login" />;
  return children;
};

export default ProtectedRoute;
```

---

## Step 4: Profile Creation on First Login (5 min)

When a user signs in with Google for the first time, auto-create their profile with Free tier:

```sql
-- Supabase SQL Editor: auto-create profile on signup
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

-- Trigger on auth.users insert
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

Make sure your profiles table exists:

```sql
CREATE TABLE IF NOT EXISTS profiles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  email TEXT,
  company_name TEXT,
  plan_tier TEXT DEFAULT 'free' CHECK (plan_tier IN ('free', 'pro', 'business', 'enterprise')),
  predictions_used_this_month INT DEFAULT 0,
  predictions_reset_date DATE DEFAULT (date_trunc('month', now()) + interval '1 month')::date,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile" ON profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = user_id);
```

---

## Step 5: FastAPI Backend — JWT Validation (5 min)

Your FastAPI backend needs to validate Supabase JWTs to know who's calling:

```python
# backend/auth.py
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
import httpx

SUPABASE_URL = "https://<YOUR_PROJECT>.supabase.co"
SUPABASE_JWT_SECRET = "<your-jwt-secret>"  # Settings → API → JWT Secret

async def get_current_user(authorization: str = Header(...)):
    """Extract and validate user from Supabase JWT."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(401, "Token validation failed")
```

Then use it in your endpoints:

```python
from backend.auth import get_current_user

@app.post("/portfolio/units")
async def create_unit(
    data: UnitInput,
    user = Depends(get_current_user)
):
    # user["user_id"] is the authenticated user
    # Check tier, check unit count, etc.
    ...
```

Frontend sends the token automatically:

```typescript
// apiClient.ts
const getAuthHeaders = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${session?.access_token}`,
  };
};

export const apiCall = async (endpoint: string, options = {}) => {
  const headers = await getAuthHeaders();
  return fetch(`${import.meta.env.VITE_API_URL}${endpoint}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });
};
```

---

## Step 6: Lovable-Specific Notes

If building in Lovable, paste this into your Lovable chat:

> "Set up Supabase authentication with Google OAuth as the primary login method. Use supabase.auth.signInWithOAuth with provider 'google'. The login page should show a prominent 'Continue with Google' button as the main action, with a small 'or sign in with email' link below. After successful login, redirect to /dashboard. Protect all /dashboard/* routes with a session check — redirect to /login if no session. On first Google login, auto-create a profile row with plan_tier='free' using a Supabase database trigger."

---

## Optional: Add Email/Password as Secondary

If you want both (Google primary, email secondary), add these Supabase settings:
- Authentication → Providers → Email: **Enabled**
- Confirm email: **Enabled** (prevents spam signups)
- Minimum password length: 8

Then create a simple `/login/email` page with email + password fields. But honestly, for launch, Google-only is fine. You can add email/password in week 2 if anyone asks for it.

---

## Checklist

- [ ] Google Cloud Console: OAuth credentials created
- [ ] Google Cloud Console: consent screen configured
- [ ] Supabase: Google provider enabled with Client ID + Secret
- [ ] Supabase: profiles table created with RLS
- [ ] Supabase: handle_new_user trigger created
- [ ] Frontend: login page with Google OAuth button
- [ ] Frontend: protected route wrapper on /dashboard/*
- [ ] Backend: JWT validation middleware
- [ ] Test: sign in with Google → redirected to dashboard → profile created
