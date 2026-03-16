"""Spatial features router — serves pre-computed OSM + satellite features per PLZ."""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(tags=["spatial"])

_ROOT = Path(__file__).resolve().parent.parent.parent
_df_osm = pd.read_csv(_ROOT / "data" / "processed" / "spatial_osm_features.csv")
_df_sat = pd.read_csv(_ROOT / "data" / "processed" / "spatial_satellite_features.csv")
_df_spatial = _df_osm.merge(_df_sat, on="plz", how="left")


@router.get("/spatial/{plz}")
def get_spatial_features(plz: int):
    """Get spatial features for a Berlin postal code (PLZ)."""
    row = _df_spatial[_df_spatial["plz"] == plz]
    if len(row) == 0:
        raise HTTPException(status_code=404, detail=f"PLZ {plz} not found (190 Berlin PLZs available)")

    data = row.iloc[0].to_dict()
    # Convert numpy types to native Python
    return {k: (float(v) if hasattr(v, "item") else v) for k, v in data.items()}


@router.get("/spatial")
def list_plz():
    """List all available PLZs with basic stats."""
    return {
        "count": len(_df_spatial),
        "plz_list": sorted(_df_spatial["plz"].tolist()),
    }
