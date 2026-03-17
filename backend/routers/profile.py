"""Profile endpoint — returns user's plan tier and limits."""

from fastapi import APIRouter, Depends

from backend.auth import User, get_current_user
from backend.supabase_client import get_supabase

router = APIRouter(tags=["profile"])

TIER_LIMITS = {
    "free": {"max_units": 3, "max_predictions_month": 3},
    "pro": {"max_units": 15, "max_predictions_month": -1},
    "business": {"max_units": -1, "max_predictions_month": -1},
    "enterprise": {"max_units": -1, "max_predictions_month": -1},
}


@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    """Get the current user's profile with plan tier and limits."""
    sb = get_supabase()
    result = (
        sb.table("profiles")
        .select("*")
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return {
            "user_id": user.user_id,
            "email": user.email,
            "plan_tier": "free",
            "limits": TIER_LIMITS["free"],
        }

    profile = result.data
    tier = profile.get("plan_tier", "free")
    return {
        "user_id": profile["user_id"],
        "display_name": profile.get("display_name"),
        "email": profile.get("email"),
        "company_name": profile.get("company_name"),
        "plan_tier": tier,
        "limits": TIER_LIMITS.get(tier, TIER_LIMITS["free"]),
        "predictions_used_this_month": profile.get("predictions_used_this_month", 0),
    }
