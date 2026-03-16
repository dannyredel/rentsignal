"""Address autocomplete and resolution via OSM Photon API."""

from typing import Optional

import httpx
from fastapi import APIRouter, Query

router = APIRouter(tags=["address"])

PHOTON_URL = "https://photon.komoot.io/api/"

# Berlin bounding box for biasing results
BERLIN_LAT = 52.52
BERLIN_LON = 13.405


@router.get("/address/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=2, description="Partial address to search"),
    limit: int = Query(5, ge=1, le=10),
):
    """Search for addresses using OSM Photon (free, no API key needed).

    Returns suggestions with PLZ, district, and coordinates.
    Biased toward Berlin results.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                PHOTON_URL,
                params={
                    "q": q,
                    "lat": BERLIN_LAT,
                    "lon": BERLIN_LON,
                    "limit": limit,
                    "lang": "de",
                },
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError:
        return {"query": q, "results": []}
    except httpx.RequestError:
        return {"query": q, "results": []}

    features = resp.json().get("features", [])
    results = []
    for f in features:
        props = f.get("properties", {})
        coords = f.get("geometry", {}).get("coordinates", [None, None])

        # Only include results with a postcode (filters noise)
        postcode = props.get("postcode")
        if not postcode:
            continue

        results.append(
            {
                "display": _format_display(props),
                "street": props.get("street"),
                "house_number": props.get("housenumber"),
                "plz": postcode,
                "district": props.get("district") or props.get("city"),
                "state": props.get("state"),
                "lat": coords[1] if len(coords) > 1 else None,
                "lon": coords[0] if coords else None,
            }
        )

    return {"query": q, "results": results}


@router.post("/address/resolve")
async def resolve(
    street: str,
    house_number: Optional[str] = None,
    plz: Optional[str] = None,
    city: str = "Berlin",
):
    """Resolve a full address to PLZ, district, lat/lon, and inferred building year.

    Uses OSM Photon for geocoding. Building year inference is approximate
    based on OSM building tags (when available).
    """
    query = f"{street}"
    if house_number:
        query += f" {house_number}"
    if plz:
        query += f", {plz}"
    query += f", {city}"

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(
            PHOTON_URL,
            params={
                "q": query,
                "lat": BERLIN_LAT,
                "lon": BERLIN_LON,
                "limit": 1,
                "lang": "de",
            },
        )
        resp.raise_for_status()

    features = resp.json().get("features", [])
    if not features:
        return {"resolved": False, "error": "Address not found"}

    f = features[0]
    props = f.get("properties", {})
    coords = f.get("geometry", {}).get("coordinates", [None, None])

    return {
        "resolved": True,
        "street": props.get("street"),
        "house_number": props.get("housenumber"),
        "plz": props.get("postcode"),
        "district": props.get("district") or props.get("city"),
        "lat": coords[1] if len(coords) > 1 else None,
        "lon": coords[0] if coords else None,
        "building_year_inferred": None,  # TODO: OSM building:start_date tag lookup
    }


def _format_display(props: dict) -> str:
    """Format a Photon result into a human-readable address string."""
    parts = []
    street = props.get("street")
    if street:
        hn = props.get("housenumber", "")
        parts.append(f"{street} {hn}".strip())
    postcode = props.get("postcode")
    city = props.get("city") or props.get("district")
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif city:
        parts.append(city)
    return ", ".join(parts) if parts else props.get("name", "Unknown")
