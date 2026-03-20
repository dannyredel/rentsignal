"""Address autocomplete and resolution via OSM Photon API."""

from typing import Optional

import httpx
from fastapi import APIRouter, Query

router = APIRouter(tags=["address"])

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Berlin bounding box for biasing results
BERLIN_LAT = 52.52
BERLIN_LON = 13.405
BERLIN_VIEWBOX = "13.08,52.34,13.76,52.68"


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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                NOMINATIM_URL,
                params={
                    "q": f"{q}, Berlin",
                    "format": "jsonv2",
                    "addressdetails": 1,
                    "limit": limit,
                    "viewbox": BERLIN_VIEWBOX,
                    "bounded": 1,
                    "countrycodes": "de",
                },
                headers={"User-Agent": "RentSignal/1.0 (contact@rentsignal.de)"},
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        import sys
        print(f"Address autocomplete HTTP error for '{q}': {e}", file=sys.stderr)
        return {"query": q, "results": []}
    except httpx.RequestError as e:
        import sys
        print(f"Address autocomplete request error for '{q}': {e}", file=sys.stderr)
        return {"query": q, "results": []}

    items = resp.json()
    if not isinstance(items, list):
        return {"query": q, "results": []}

    results = []
    for item in items:
        addr = item.get("address", {})
        postcode = addr.get("postcode")
        if not postcode:
            continue

        street = addr.get("road") or addr.get("pedestrian") or addr.get("neighbourhood")
        house_number = addr.get("house_number")
        district = addr.get("suburb") or addr.get("city_district") or addr.get("city")

        display = item.get("display_name", "")
        # Shorten display: take first 2-3 parts
        parts = display.split(", ")
        short_display = ", ".join(parts[:3]) if len(parts) > 3 else display

        results.append({
            "display": short_display,
            "street": street,
            "house_number": house_number,
            "plz": postcode,
            "district": district,
            "lat": float(item["lat"]) if item.get("lat") else None,
            "lon": float(item["lon"]) if item.get("lon") else None,
        })

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

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 1,
                "viewbox": BERLIN_VIEWBOX,
                "bounded": 1,
                "countrycodes": "de",
            },
            headers={"User-Agent": "RentSignal/1.0 (contact@rentsignal.de)"},
        )
        resp.raise_for_status()

    items = resp.json()
    if not items:
        return {"resolved": False, "error": "Address not found"}

    item = items[0]
    addr = item.get("address", {})

    return {
        "resolved": True,
        "street": addr.get("road") or addr.get("pedestrian"),
        "house_number": addr.get("house_number"),
        "plz": addr.get("postcode"),
        "district": addr.get("suburb") or addr.get("city_district") or addr.get("city"),
        "lat": float(item["lat"]) if item.get("lat") else None,
        "lon": float(item["lon"]) if item.get("lon") else None,
        "building_year_inferred": None,
    }


def _format_display(props: dict) -> str:
    """Format address properties into a display string."""
    parts = []
    street = props.get("road") or props.get("street")
    if street:
        hn = props.get("house_number", "")
        parts.append(f"{street} {hn}".strip())
    postcode = props.get("postcode")
    city = props.get("city") or props.get("suburb")
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif city:
        parts.append(city)
    return ", ".join(parts) if parts else "Unknown"
