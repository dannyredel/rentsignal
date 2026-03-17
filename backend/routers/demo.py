"""Demo apartments router — serves pre-computed outputs."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/demo", tags=["demo"])

_ROOT = Path(__file__).resolve().parent.parent.parent
_DEMO_PATH = _ROOT / "data" / "demo" / "demo_apartments.json"

# Inflation adjustment: demo data uses 2019 prices, adjust to 2024
INFLATION_FACTOR = 1.378

with open(_DEMO_PATH) as f:
    _DEMO_DATA = json.load(f)

# Apply inflation to all rent-related fields
for apt in _DEMO_DATA["apartments"]:
    p = apt["prediction"]
    p["rent_sqm"] = round(p["rent_sqm"] * INFLATION_FACTOR, 2)
    if p.get("current_rent_sqm"):
        p["current_rent_sqm"] = round(p["current_rent_sqm"] * INFLATION_FACTOR, 2)
    if p.get("gap_sqm"):
        p["gap_sqm"] = round(p["rent_sqm"] - p["current_rent_sqm"], 2)
        p["gap_pct"] = round((p["gap_sqm"] / p["current_rent_sqm"]) * 100, 1) if p["current_rent_sqm"] else None
    # SHAP base value
    if apt.get("shap_base_value"):
        apt["shap_base_value"] = round(apt["shap_base_value"] * INFLATION_FACTOR, 2)
    # SHAP feature values
    for feat in apt.get("shap_top_features", []):
        feat["value"] = round(feat["value"] * INFLATION_FACTOR, 4)

_APARTMENTS = {apt["id"]: apt for apt in _DEMO_DATA["apartments"]}


@router.get("/apartments")
def list_apartments():
    """List all 5 demo apartments with summaries."""
    return {
        "model_version": _DEMO_DATA["model_version"],
        "model_r2": _DEMO_DATA["model_r2"],
        "count": len(_DEMO_DATA["apartments"]),
        "apartments": [
            {
                "id": apt["id"],
                "name": apt["name"],
                "tagline": apt["tagline"],
                "district": apt["district"],
                "plz": apt["plz"],
                "specs": apt["specs"],
                "prediction": apt["prediction"],
            }
            for apt in _DEMO_DATA["apartments"]
        ],
    }


@router.get("/apartments/{apartment_id}")
def get_apartment(apartment_id: str):
    """Get full details for a single demo apartment (all 4 layers)."""
    apt = _APARTMENTS.get(apartment_id)
    if not apt:
        raise HTTPException(status_code=404, detail=f"Apartment '{apartment_id}' not found")
    return apt
