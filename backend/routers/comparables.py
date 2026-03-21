"""Comparable listings endpoint — find similar apartments from our dataset."""

from fastapi import APIRouter, Query
from backend.services.comparables_service import find_comparables

router = APIRouter(tags=["comparables"])


@router.get("/comparables/{plz}")
def get_comparables(
    plz: int,
    living_space: float = Query(..., description="Living space in m²"),
    rooms: float = Query(..., description="Number of rooms"),
    building_era: str = Query("unknown", description="Building era category"),
    condition: str = Query("unknown", description="Apartment condition"),
    bezirk: str = Query(None, description="District name"),
    lat: float = Query(None, description="Latitude for distance-based matching"),
    lon: float = Query(None, description="Longitude for distance-based matching"),
    k: int = Query(5, description="Number of comparables to return", ge=1, le=20),
):
    """Return K most similar apartments from our listing dataset.

    Uses weighted nearest-neighbor matching across size, rooms, location,
    building era, and condition. When lat/lon are provided, uses actual
    geographic distance; otherwise falls back to PLZ/bezirk matching.
    """
    return find_comparables(
        plz=plz,
        living_space=living_space,
        n_rooms=rooms,
        building_era=building_era,
        condition=condition,
        bezirk=bezirk,
        lat=lat,
        lon=lon,
        k=k,
    )
