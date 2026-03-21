"""Portfolio renovation budget optimizer endpoint."""

from fastapi import APIRouter, Depends, Query

from backend.auth import User, get_current_user
from backend.services.budget_optimizer_service import optimize_budget
from backend.supabase_client import get_supabase

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/optimize-budget")
async def optimize_renovation_budget(
    budget: float = Query(..., description="Total renovation budget in EUR", ge=0),
    user: User = Depends(get_current_user),
):
    """Optimize renovation spending across the entire portfolio.

    Returns two plans:
    - greedy: rank by ROI independently (ignores cross-unit effects)
    - smart: substitution-aware (discounts renovations that create self-competition)

    The comparison between plans shows where differentiation beats duplication.
    """
    sb = get_supabase()
    resp = sb.table("units").select("*").eq("user_id", user.user_id).execute()
    portfolio = resp.data or []

    if not portfolio:
        return {
            "budget": budget,
            "greedy_plan": [],
            "smart_plan": [],
            "comparison": {"message": "No units in portfolio."},
            "portfolio_size": 0,
        }

    return optimize_budget(portfolio, budget)
