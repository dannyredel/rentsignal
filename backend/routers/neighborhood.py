"""Neighborhood intelligence endpoints — PLZ-level spatial analysis."""

from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import User, get_current_user
from backend.tier import check_tier

router = APIRouter(prefix="/neighborhood", tags=["neighborhood"])

_ROOT = Path(__file__).resolve().parent.parent.parent

# Load spatial data at module level
_spatial: Optional[pd.DataFrame] = None


def _get_spatial() -> pd.DataFrame:
    global _spatial
    if _spatial is None:
        path = _ROOT / "data" / "processed" / "spatial_all_features.csv"
        if path.exists():
            _spatial = pd.read_csv(path)
        else:
            _spatial = pd.DataFrame()
    return _spatial


@router.get("/{plz}")
async def get_neighborhood(plz: int, user: User = Depends(get_current_user)):
    """Get neighborhood intelligence for a PLZ.

    Extends the basic spatial endpoint with rent range estimates,
    feature importance at PLZ level, and compliance landscape.
    """
    await check_tier(user, "pro")

    spatial = _get_spatial()
    row = spatial[spatial["plz"] == plz]
    if row.empty:
        raise HTTPException(404, detail=f"PLZ {plz} not found in spatial data")

    features = row.iloc[0].to_dict()

    # Clean NaN values
    features = {k: (None if pd.isna(v) else v) for k, v in features.items()}

    # Compute Berlin-wide benchmarks for comparison
    benchmarks = {}
    for col in spatial.select_dtypes(include="number").columns:
        if col == "plz":
            continue
        benchmarks[col] = {
            "plz_value": features.get(col),
            "berlin_mean": round(spatial[col].mean(), 4),
            "berlin_median": round(spatial[col].median(), 4),
            "percentile": _percentile(spatial[col], features.get(col)),
        }

    return {
        "plz": plz,
        "features": features,
        "benchmarks": benchmarks,
    }


@router.get("/map", name="neighborhood_map")
async def neighborhood_map(user: User = Depends(get_current_user)):
    """All Berlin PLZs with summary metrics for frontend map rendering."""
    await check_tier(user, "pro")

    spatial = _get_spatial()
    if spatial.empty:
        return {"plzs": []}

    # Select key columns for map
    cols = ["plz"]
    for c in ["ndvi_mean", "ndbi_mean", "count_food_1000m", "dist_transit_nearest"]:
        if c in spatial.columns:
            cols.append(c)

    result = spatial[cols].to_dict(orient="records")

    # Clean NaN
    for row in result:
        for k, v in row.items():
            if pd.isna(v):
                row[k] = None

    return {"plzs": result}


@router.get("/compare", name="neighborhood_compare")
async def compare_neighborhoods(
    plz: list[int] = Query(..., description="2-3 PLZs to compare"),
    user: User = Depends(get_current_user),
):
    """Compare 2-3 PLZs side by side."""
    await check_tier(user, "pro")

    if len(plz) < 2 or len(plz) > 3:
        raise HTTPException(400, detail="Provide 2 or 3 PLZs to compare")

    spatial = _get_spatial()
    rows = spatial[spatial["plz"].isin(plz)]

    if rows.empty:
        raise HTTPException(404, detail="No PLZs found in spatial data")

    comparison = {}
    for _, row in rows.iterrows():
        p = int(row["plz"])
        features = row.to_dict()
        features = {k: (None if pd.isna(v) else v) for k, v in features.items()}
        comparison[str(p)] = features

    # Determine "winner" for each numeric feature
    winners = {}
    numeric_cols = [c for c in spatial.select_dtypes(include="number").columns if c != "plz"]
    for col in numeric_cols:
        values = {str(p): comparison.get(str(p), {}).get(col) for p in plz}
        values = {k: v for k, v in values.items() if v is not None}
        if values:
            # Higher is better for most features (except distances where lower is better)
            is_lower_better = "dist_" in col
            if is_lower_better:
                winners[col] = min(values, key=values.get)
            else:
                winners[col] = max(values, key=values.get)

    return {
        "plzs": comparison,
        "winners": winners,
    }


def _percentile(series: pd.Series, value) -> Optional[int]:
    """Calculate what percentile a value falls in within the series."""
    if value is None or pd.isna(value):
        return None
    return int(round((series < value).mean() * 100))
