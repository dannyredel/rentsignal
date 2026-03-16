"""Tier checking utilities for endpoint access control."""

from fastapi import HTTPException

from backend.auth import User
from backend.supabase_client import get_supabase

TIER_HIERARCHY = {"free": 0, "pro": 1, "business": 2, "enterprise": 3}
UNIT_LIMITS = {"free": 3, "pro": 15, "business": float("inf"), "enterprise": float("inf")}
PREDICTION_LIMIT_FREE = 3


async def get_user_profile(user: User) -> dict:
    """Fetch user profile from Supabase."""
    sb = get_supabase()
    result = sb.table("profiles").select("*").eq("user_id", user.user_id).single().execute()
    return result.data


async def check_tier(user: User, required_tier: str):
    """Raise 403 if user's tier is below required_tier."""
    profile = await get_user_profile(user)
    current = profile.get("plan_tier", "free")
    if TIER_HIERARCHY.get(current, 0) < TIER_HIERARCHY.get(required_tier, 0):
        raise HTTPException(
            403,
            detail={
                "error": "tier_required",
                "required": required_tier,
                "current": current,
                "message": f"This feature requires {required_tier} tier",
            },
        )
    return profile


async def check_can_add_unit(user: User):
    """Check if user can add another unit within their tier limit."""
    profile = await get_user_profile(user)
    tier = profile.get("plan_tier", "free")
    limit = UNIT_LIMITS.get(tier, 3)

    sb = get_supabase()
    count_result = sb.table("units").select("id", count="exact").eq("user_id", user.user_id).execute()
    current_count = count_result.count or 0

    if current_count >= limit:
        raise HTTPException(
            403,
            detail={
                "error": "unit_limit_reached",
                "current_count": current_count,
                "limit": int(limit) if limit != float("inf") else None,
                "tier": tier,
                "message": f"{tier.title()} tier allows up to {int(limit)} units. Upgrade to add more.",
            },
        )
    return profile, current_count


async def check_can_predict(user: User):
    """Check if user can run a prediction (Free: 3/month, Pro+: unlimited)."""
    profile = await get_user_profile(user)
    tier = profile.get("plan_tier", "free")
    if tier != "free":
        return profile

    used = profile.get("predictions_used_this_month", 0)
    if used >= PREDICTION_LIMIT_FREE:
        raise HTTPException(
            403,
            detail={
                "error": "prediction_limit_reached",
                "used": used,
                "limit": PREDICTION_LIMIT_FREE,
                "tier": "free",
                "message": f"Free tier allows {PREDICTION_LIMIT_FREE} predictions per month. Upgrade to Pro for unlimited.",
            },
        )
    return profile
