"""Comparable listings service — find K nearest similar apartments from our dataset."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Load dataset at module level
# ---------------------------------------------------------------------------

try:
    _units = pd.read_parquet(_ROOT / "data" / "processed" / "units.parquet")
    _listings = pd.read_parquet(_ROOT / "data" / "processed" / "listings.parquet")
    _comps = _units.merge(_listings[["unit_id", "rent_sqm", "baseRent", "observed_date"]], on="unit_id")

    # Pre-compute features for matching
    _comps["lat_f"] = _comps["lat"].fillna(0).astype(float)
    _comps["lon_f"] = _comps["lon"].fillna(0).astype(float)
    _comps["sqm_f"] = _comps["livingSpace"].astype(float)
    _comps["rooms_f"] = _comps["noRooms"].astype(float)

    # Filter out Tauschwohnungen (swap listings with below-market rents)
    # Tausch median is ~10.37 €/m² — use 12.0 as threshold to exclude
    _n_before = len(_comps)
    _comps = _comps[_comps["rent_sqm"] >= 12.0].reset_index(drop=True)
    _n_tausch = _n_before - len(_comps)

    _COMPS_READY = True
    _SCRAPE_DATE = _comps["observed_date"].max() if "observed_date" in _comps.columns else "2026-03"
    print(f"Comparables service loaded: {len(_comps):,} market listings "
          f"({_n_tausch:,} Tauschwohnungen excluded, scraped {_SCRAPE_DATE})", file=sys.stderr)

except Exception as e:
    print(f"WARNING: Comparables service failed to load: {e}", file=sys.stderr)
    _comps = None
    _COMPS_READY = False
    _SCRAPE_DATE = None


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def find_comparables(
    plz: int,
    living_space: float,
    n_rooms: float,
    building_era: str = "unknown",
    condition: str = "unknown",
    bezirk: str = None,
    lat: float = None,
    lon: float = None,
    k: int = 5,
    max_results: int = 10,
) -> dict:
    """Find K most similar apartments from our dataset.

    Matching is done via weighted distance across multiple dimensions:
    - Geographic proximity (lat/lon or PLZ match)
    - Living space similarity
    - Room count similarity
    - Building era match (bonus)
    - Condition match (bonus)

    Returns dict with comparables list + summary stats.
    """
    if not _COMPS_READY or _comps is None:
        return {"comparables": [], "summary": {}, "data_date": None}

    df = _comps.copy()

    # --- Stage 1: Pre-filter to reasonable candidates ---
    # Expand search if needed to guarantee enough candidates
    sqm_range = 0.25  # ±25% of living space
    room_range = 1

    candidates = df[
        (df["sqm_f"].between(living_space * (1 - sqm_range), living_space * (1 + sqm_range)))
        & (df["rooms_f"].between(n_rooms - room_range, n_rooms + room_range))
    ]

    # If too few candidates, expand
    if len(candidates) < k * 3:
        sqm_range = 0.4
        room_range = 2
        candidates = df[
            (df["sqm_f"].between(living_space * (1 - sqm_range), living_space * (1 + sqm_range)))
            & (df["rooms_f"].between(n_rooms - room_range, n_rooms + room_range))
        ]

    if len(candidates) == 0:
        return {"comparables": [], "summary": {}, "data_date": str(_SCRAPE_DATE)}

    # --- Stage 2: Compute similarity score ---
    scores = np.zeros(len(candidates))

    # Living space similarity (weight: 3)
    sqm_diff = np.abs(candidates["sqm_f"].values - living_space) / max(living_space, 1)
    scores += sqm_diff * 3.0

    # Room count similarity (weight: 2)
    room_diff = np.abs(candidates["rooms_f"].values - n_rooms)
    scores += room_diff * 2.0

    # Geographic proximity
    if lat is not None and lon is not None and lat != 0 and lon != 0:
        # Use actual distance (weight: 2)
        lat_diff = np.abs(candidates["lat_f"].values - lat) * 111_320
        lon_diff = np.abs(candidates["lon_f"].values - lon) * 67_700
        geo_dist_km = np.sqrt(lat_diff ** 2 + lon_diff ** 2) / 1000
        scores += np.minimum(geo_dist_km, 10) * 0.5  # cap at 10km
    else:
        # PLZ match (weight: 1 bonus for same PLZ, 0.5 for same bezirk)
        same_plz = (candidates["plz"].astype(str) == str(plz)).astype(float)
        scores += (1 - same_plz) * 2.0

        if bezirk:
            same_bezirk = (candidates["bezirk"] == bezirk).astype(float)
            scores += (1 - same_bezirk) * 1.0

    # Building era match (weight: 1 bonus)
    if building_era and building_era != "unknown":
        same_era = (candidates["building_era"] == building_era).astype(float)
        scores += (1 - same_era) * 1.0

    # Condition match (weight: 0.5 bonus)
    if condition and condition != "unknown":
        same_condition = (candidates["condition"] == condition).astype(float)
        scores += (1 - same_condition) * 0.5

    # --- Stage 3: Select top K ---
    candidates = candidates.copy()
    candidates["similarity_score"] = scores
    top_k = candidates.nsmallest(min(k, len(candidates)), "similarity_score")

    # --- Stage 4: Build response ---
    comparables = []
    for _, row in top_k.iterrows():
        # Compute distance if coords available
        dist_m = None
        if lat is not None and lon is not None and row["lat_f"] != 0:
            dlat = (row["lat_f"] - lat) * 111_320
            dlon = (row["lon_f"] - lon) * 67_700
            dist_m = int(np.sqrt(dlat ** 2 + dlon ** 2))

        # Build address display
        street = row.get("street", "")
        house = row.get("house_number", "")
        if pd.notna(street) and street and street != "nan":
            address = f"{street} {house}".strip() if pd.notna(house) else street
        else:
            address = f"PLZ {row['plz']}"

        comparables.append({
            "address": address,
            "plz": str(row["plz"]),
            "bezirk": row.get("bezirk", ""),
            "living_space": float(row["sqm_f"]),
            "rooms": float(row["rooms_f"]),
            "building_era": row.get("building_era", "unknown"),
            "condition": row.get("condition", "unknown"),
            "asking_rent_sqm": round(float(row["rent_sqm"]), 2),
            "asking_rent_total": round(float(row.get("baseRent", row["rent_sqm"] * row["sqm_f"])), 0),
            "lat": float(row["lat_f"]) if row["lat_f"] != 0 else None,
            "lon": float(row["lon_f"]) if row["lon_f"] != 0 else None,
            "distance_m": dist_m,
            "similarity_score": round(float(row["similarity_score"]), 2),
        })

    # Summary statistics
    asking_rents = [c["asking_rent_sqm"] for c in comparables]
    summary = {
        "n_comparables": len(comparables),
        "avg_asking_rent": round(np.mean(asking_rents), 2) if asking_rents else None,
        "median_asking_rent": round(np.median(asking_rents), 2) if asking_rents else None,
        "min_asking_rent": round(min(asking_rents), 2) if asking_rents else None,
        "max_asking_rent": round(max(asking_rents), 2) if asking_rents else None,
        "total_listings_searched": len(candidates),
    }

    return {
        "comparables": comparables,
        "summary": summary,
        "data_date": str(_SCRAPE_DATE),
    }
