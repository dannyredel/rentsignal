"""Spatial features router — unit-level (from lat/lon) or PLZ-level fallback."""

from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

from backend.services.ml_service import compute_spatial_features, _df_spatial_plz, _kdtrees, _sat_grid

router = APIRouter(tags=["spatial"])


@router.get("/spatial/{plz}")
def get_spatial_features(
    plz: int,
    lat: Optional[float] = Query(None, description="Latitude for unit-level features"),
    lon: Optional[float] = Query(None, description="Longitude for unit-level features"),
):
    """Get spatial features for a location.

    If lat/lon provided: computes unit-level features from actual coordinates (24 features).
    If only PLZ: returns PLZ-level aggregated features (18 features, legacy).
    """
    # Unit-level: compute from coordinates
    if lat is not None and lon is not None and _kdtrees:
        # Validate Berlin bounds
        if not (52.3 < lat < 52.7 and 13.0 < lon < 13.8):
            raise HTTPException(status_code=400, detail="Coordinates outside Berlin bounds")

        features = compute_spatial_features(lat, lon)
        return {
            "plz": plz,
            "level": "unit",
            "coordinates": {"lat": lat, "lon": lon},
            **{k: round(float(v), 4) for k, v in features.items()},
        }

    # PLZ-level fallback
    if _df_spatial_plz is not None:
        row = _df_spatial_plz[_df_spatial_plz["plz"] == plz]
        if len(row) == 0:
            raise HTTPException(status_code=404, detail=f"PLZ {plz} not found")

        data = row.iloc[0].to_dict()
        return {
            "level": "plz",
            **{k: (round(float(v), 4) if isinstance(v, (int, float)) else v) for k, v in data.items()},
        }

    raise HTTPException(status_code=503, detail="Spatial data not loaded")


@router.get("/spatial")
def list_plz():
    """List all available PLZs with basic stats."""
    if _df_spatial_plz is not None:
        return {
            "count": len(_df_spatial_plz),
            "plz_list": sorted(_df_spatial_plz["plz"].tolist()),
            "unit_level_available": bool(_kdtrees),
        }
    return {"count": 0, "plz_list": [], "unit_level_available": False}
