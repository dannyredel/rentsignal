"""Demo apartments router — serves pre-computed outputs."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/demo", tags=["demo"])

_ROOT = Path(__file__).resolve().parent.parent.parent
_DEMO_PATH = _ROOT / "data" / "demo" / "demo_apartments.json"

with open(_DEMO_PATH) as f:
    _DEMO_DATA = json.load(f)

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
