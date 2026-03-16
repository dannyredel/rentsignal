"""RentSignal API — AI-powered rent optimization for the German rental market."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    address, comply, csv_import, demo, energy, neighborhood,
    portfolio, predict, renovate, rent_increase, spatial,
)

app = FastAPI(
    title="RentSignal API",
    description=(
        "AI-powered rent optimization engine for the German rental market. "
        "Combines XGBoost prediction, SHAP explainability, Mietpreisbremse compliance, "
        "and dual-method renovation simulation (observational CATE + synthetic conjoint WTP)."
    ),
    version="0.1.0",
)

# CORS — allow all origins for now (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(demo.router)
app.include_router(predict.router)
app.include_router(comply.router)
app.include_router(renovate.router)
app.include_router(spatial.router)
app.include_router(address.router)
app.include_router(portfolio.router)
app.include_router(csv_import.router)
app.include_router(rent_increase.router)
app.include_router(energy.router)
app.include_router(neighborhood.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "rentsignal-api", "version": "0.1.0"}


@app.get("/debug/token")
async def debug_token(authorization: str = Header(default="")):
    """Temporary debug endpoint — shows JWT header info. Remove after debugging."""
    import base64, json as _json
    if not authorization.startswith("Bearer "):
        return {"error": "no bearer token", "raw_header": authorization[:50] if authorization else "empty"}
    token = authorization.removeprefix("Bearer ")
    parts = token.split(".")
    if len(parts) != 3:
        return {"error": "not 3 parts", "parts": len(parts)}
    # Decode header
    h = parts[0]
    h += "=" * (4 - len(h) % 4)
    header = _json.loads(base64.urlsafe_b64decode(h))
    # Decode payload (without verification)
    p = parts[1]
    p += "=" * (4 - len(p) % 4)
    payload = _json.loads(base64.urlsafe_b64decode(p))
    return {
        "header": header,
        "payload_sub": payload.get("sub"),
        "payload_aud": payload.get("aud"),
        "payload_role": payload.get("role"),
        "payload_iss": payload.get("iss"),
        "sig_length": len(parts[2]),
        "jwt_secret_configured": bool(os.environ.get("SUPABASE_JWT_SECRET")),
        "jwt_secret_length": len(os.environ.get("SUPABASE_JWT_SECRET", "")),
    }


from fastapi import Header
import os
