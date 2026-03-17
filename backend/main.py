"""RentSignal API — AI-powered rent optimization for the German rental market."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    address, comply, csv_import, demo, energy, neighborhood,
    portfolio, predict, profile, renovate, rent_increase, spatial,
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
app.include_router(profile.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "rentsignal-api", "version": "0.1.0"}
