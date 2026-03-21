"""Scenario simulator endpoint — what-if analysis for portfolio units."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.auth import User, get_current_user
from backend.services.simulator_service import (
    simulate_rent_adjustment,
    simulate_renovation,
    simulate_mietspiegel_change,
)
from backend.supabase_client import get_supabase

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


def _get_unit_with_analysis(unit_id: str, user_id: str) -> dict:
    """Get unit data merged with latest analysis results."""
    sb = get_supabase()
    resp = sb.from_("units_with_latest_analysis") \
        .select("*") \
        .eq("unit_id", unit_id) \
        .eq("user_id", user_id) \
        .execute()

    if not resp.data:
        return None

    unit = resp.data[0]
    # Parse predict_result for predicted_rent_sqm
    predict_result = unit.get("predict_result")
    if isinstance(predict_result, str):
        try:
            predict_result = json.loads(predict_result)
        except (json.JSONDecodeError, TypeError):
            predict_result = {}

    unit["predicted_rent_sqm"] = (
        predict_result.get("predicted_rent_sqm")
        or unit.get("predicted_rent_sqm")
        or 0
    )
    return unit


@router.get("/simulate/{unit_id}")
async def simulate_scenarios(
    unit_id: str,
    scenario: str = Query("all", description="Scenario: rent, renovation, mietspiegel, or all"),
    user: User = Depends(get_current_user),
):
    """Run what-if scenarios for a specific unit.

    Scenarios:
    - rent: slide rent up/down → compliance + market position
    - renovation: toggle features → predicted rent + ROI
    - mietspiegel: simulate future Mietspiegel changes → compliance shift
    - all: run all three
    """
    unit = _get_unit_with_analysis(unit_id, user.user_id)
    if not unit:
        return {"error": "Unit not found"}

    result = {"unit_id": unit_id, "address": unit.get("address", "Unknown")}

    if scenario in ("rent", "all"):
        result["rent_adjustment"] = simulate_rent_adjustment(unit)

    if scenario in ("renovation", "all"):
        result["renovation"] = simulate_renovation(unit)

    if scenario in ("mietspiegel", "all"):
        result["mietspiegel_change"] = simulate_mietspiegel_change(unit)

    return result
