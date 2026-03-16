"""Portfolio CRUD endpoints — the core portfolio entity management."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from backend.auth import User, get_current_user
from backend.models.portfolio import (
    BatchJobCreate,
    BatchJobResponse,
    PortfolioSummary,
    UnitCreate,
    UnitResponse,
    UnitUpdate,
)
from backend.supabase_client import get_supabase
from backend.tier import check_can_add_unit, check_tier

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# ── Unit CRUD ──


@router.post("/units", response_model=UnitResponse, status_code=201)
async def create_unit(data: UnitCreate, user: User = Depends(get_current_user)):
    """Create a new unit in the user's portfolio."""
    await check_can_add_unit(user)

    sb = get_supabase()
    row = data.model_dump(exclude_none=True)
    row["user_id"] = user.user_id

    # Derive building_era if not provided
    if not row.get("building_era"):
        row["building_era"] = _year_to_era(row["year_built"])

    result = sb.table("units").insert(row).execute()
    return result.data[0]


@router.get("/units", response_model=list[UnitResponse])
async def list_units(user: User = Depends(get_current_user)):
    """List all units in the user's portfolio with latest analysis summary."""
    sb = get_supabase()
    result = (
        sb.table("units_with_latest_analysis")
        .select("*")
        .eq("user_id", user.user_id)
        .order("unit_created_at", desc=True)
        .execute()
    )
    return [_map_view_to_response(row) for row in result.data]


@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: UUID, user: User = Depends(get_current_user)):
    """Get a single unit with its latest analysis."""
    sb = get_supabase()
    result = (
        sb.table("units_with_latest_analysis")
        .select("*")
        .eq("unit_id", str(unit_id))
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, detail="Unit not found")
    return _map_view_to_response(result.data)


@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: UUID, data: UnitUpdate, user: User = Depends(get_current_user)
):
    """Update a unit's data. Only provided fields are changed."""
    sb = get_supabase()

    # Verify ownership
    existing = (
        sb.table("units")
        .select("id")
        .eq("id", str(unit_id))
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(404, detail="Unit not found")

    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, detail="No fields to update")

    # Re-derive building_era if year_built changed
    if "year_built" in updates and "building_era" not in updates:
        updates["building_era"] = _year_to_era(updates["year_built"])

    result = (
        sb.table("units")
        .update(updates)
        .eq("id", str(unit_id))
        .eq("user_id", user.user_id)
        .execute()
    )
    return result.data[0]


@router.delete("/units/{unit_id}", status_code=204)
async def delete_unit(unit_id: UUID, user: User = Depends(get_current_user)):
    """Remove a unit from the portfolio."""
    sb = get_supabase()
    result = (
        sb.table("units")
        .delete()
        .eq("id", str(unit_id))
        .eq("user_id", user.user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, detail="Unit not found")


# ── Portfolio Summary ──


@router.get("/summary", response_model=PortfolioSummary)
async def portfolio_summary(user: User = Depends(get_current_user)):
    """Aggregate portfolio metrics: total units, avg gap, compliance exposure."""
    sb = get_supabase()
    result = (
        sb.table("portfolio_summary")
        .select("*")
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return PortfolioSummary()
    return result.data


# ── Compliance Risk & Revenue Gaps ──


@router.get("/compliance-risk")
async def compliance_risk(user: User = Depends(get_current_user)):
    """All units with compliance status, sorted by annual exposure (highest first)."""
    await check_tier(user, "pro")

    sb = get_supabase()
    result = (
        sb.table("units_with_latest_analysis")
        .select("*")
        .eq("user_id", user.user_id)
        .not_.is_("overpayment_annual", "null")
        .order("overpayment_annual", desc=True)
        .execute()
    )
    return [_map_view_to_response(row) for row in result.data]


@router.get("/revenue-gaps")
async def revenue_gaps(user: User = Depends(get_current_user)):
    """Units sorted by rent gap (most underpriced first)."""
    await check_tier(user, "pro")

    sb = get_supabase()
    result = (
        sb.table("units_with_latest_analysis")
        .select("*")
        .eq("user_id", user.user_id)
        .not_.is_("rent_gap_pct", "null")
        .order("rent_gap_pct", desc=True)
        .execute()
    )
    return [_map_view_to_response(row) for row in result.data]


# ── Batch Analysis ──


@router.post("/analyze", response_model=BatchJobResponse, status_code=202)
async def trigger_batch_analysis(
    data: BatchJobCreate, user: User = Depends(get_current_user)
):
    """Trigger predict+comply on all (or selected) units. Returns job ID to poll."""
    await check_tier(user, "pro")

    sb = get_supabase()

    # Count units to process
    if data.unit_ids:
        unit_ids = [str(uid) for uid in data.unit_ids]
        count_result = (
            sb.table("units")
            .select("id", count="exact")
            .eq("user_id", user.user_id)
            .in_("id", unit_ids)
            .execute()
        )
    else:
        count_result = (
            sb.table("units")
            .select("id", count="exact")
            .eq("user_id", user.user_id)
            .execute()
        )

    total = count_result.count or 0
    if total == 0:
        raise HTTPException(400, detail="No units to analyze")

    # Create batch job
    job = {
        "user_id": user.user_id,
        "status": "queued",
        "job_type": "analyze",
        "unit_ids": [str(uid) for uid in data.unit_ids] if data.unit_ids else None,
        "total_units": total,
    }
    result = sb.table("batch_jobs").insert(job).execute()

    # TODO: trigger async processing (background task or worker queue)
    # For now, return the job for polling

    return result.data[0]


@router.get("/analyze/{job_id}", response_model=BatchJobResponse)
async def get_batch_status(job_id: UUID, user: User = Depends(get_current_user)):
    """Poll status of a batch analysis job."""
    sb = get_supabase()
    result = (
        sb.table("batch_jobs")
        .select("*")
        .eq("id", str(job_id))
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, detail="Job not found")
    return result.data


# ── Helpers ──


def _year_to_era(year: int) -> str:
    """Convert building year to era category matching OrdinalEncoder categories."""
    if year < 1918:
        return "pre_1918"
    elif year < 1950:
        return "1919_1949"
    elif year < 1965:
        return "1950_1964"
    elif year < 1973:
        return "1965_1972"
    elif year < 1991:
        return "1973_1990"
    elif year < 2003:
        return "1991_2002"
    elif year < 2015:
        return "2003_2014"
    else:
        return "2015_plus"


def _map_view_to_response(row: dict) -> dict:
    """Map the units_with_latest_analysis view columns to UnitResponse fields."""
    return {
        "id": row.get("unit_id"),
        "user_id": row.get("user_id"),
        "address": row.get("address"),
        "plz": row.get("plz"),
        "district": row.get("district"),
        "label": row.get("label"),
        "living_space_sqm": row.get("living_space_sqm"),
        "rooms": row.get("rooms", 0),
        "year_built": row.get("year_built"),
        "current_rent_per_sqm": row.get("current_rent_per_sqm"),
        "is_monitored": row.get("is_monitored", False),
        "predicted_rent_sqm": row.get("predicted_rent_sqm"),
        "rent_gap_pct": row.get("rent_gap_pct"),
        "is_compliant": row.get("is_compliant"),
        "overpayment_annual": row.get("overpayment_annual"),
        "legal_max_rent_sqm": row.get("legal_max_rent_sqm"),
        "created_at": row.get("unit_created_at"),
        "updated_at": row.get("unit_created_at"),  # view doesn't expose updated_at
    }
