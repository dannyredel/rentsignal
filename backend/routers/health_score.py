"""Portfolio health score endpoint."""

import json

from fastapi import APIRouter, Depends

from backend.auth import User, get_current_user
from backend.services.health_score_service import compute_unit_health, compute_portfolio_health
from backend.services.comparables_service import find_comparables
from backend.supabase_client import get_supabase

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


def _parse_json_field(val):
    """Parse a JSON string field, or return as-is if already dict/list."""
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return {}
    return val or {}


@router.get("/health")
async def get_portfolio_health(user: User = Depends(get_current_user)):
    """Compute health scores for all units in the portfolio.

    Returns per-unit scores (0-100, grade A-F) across 4 dimensions:
    pricing, compliance, renovation opportunity, market position.
    Plus aggregate portfolio health score.
    """
    sb = get_supabase()

    # Get all units with latest analysis
    resp = sb.from_("units_with_latest_analysis") \
        .select("*") \
        .eq("user_id", user.user_id) \
        .execute()
    units = resp.data or []

    if not units:
        return {
            "portfolio": {"avg_score": 0, "grade": "N/A", "total_units": 0},
            "units": [],
        }

    results = []
    for unit in units:
        # Parse stored analysis results
        predict_result = _parse_json_field(unit.get("predict_result"))
        comply_result = _parse_json_field(unit.get("comply_result"))
        renovate_result = _parse_json_field(unit.get("renovate_result"))

        analysis = {
            "predict": predict_result,
            "comply": {
                "is_compliant": unit.get("is_compliant"),
                "overpayment_per_sqm": comply_result.get("overpayment_per_sqm", 0),
                "headroom_per_sqm": comply_result.get("headroom_per_sqm", unit.get("headroom_sqm", 0)),
            },
            "renovate": renovate_result,
        }

        # Get comparables for market positioning
        plz = unit.get("plz")
        sqm = unit.get("living_space_sqm", 60)
        rooms = unit.get("rooms", 2)
        comparables = None
        if plz:
            try:
                comparables = find_comparables(
                    plz=int(plz), living_space=float(sqm), n_rooms=float(rooms),
                    lat=unit.get("lat"), lon=unit.get("lon"), k=5,
                )
            except Exception:
                pass

        health = compute_unit_health(unit, analysis, comparables)

        results.append({
            "unit_id": unit.get("unit_id"),
            "address": unit.get("address", "Unknown"),
            "plz": str(plz),
            "living_space_sqm": sqm,
            "current_rent_sqm": unit.get("current_rent_per_sqm"),
            "predicted_rent_sqm": unit.get("predicted_rent_sqm"),
            "health": health,
        })

    # Aggregate portfolio score
    portfolio = compute_portfolio_health(results)

    return {
        "portfolio": portfolio,
        "units": results,
    }
