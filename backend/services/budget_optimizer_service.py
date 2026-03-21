"""Portfolio renovation budget optimizer with substitution-aware CATE adjustment.

Two modes:
- Greedy: rank all renovations by ROI, fill budget top-down (independent)
- Substitution-aware: discount CATE for renovations that make similar units MORE similar

The comparison between both modes is the key insight: "differentiate, don't duplicate."
"""

import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent

# Load matching results for CATE
try:
    v2_path = _ROOT / "data" / "processed" / "matching_results_v2.json"
    v1_path = _ROOT / "data" / "processed" / "matching_results.json"

    if v2_path.exists():
        with open(v2_path) as f:
            _CATE_DATA = json.load(f)
        _CATE = _CATE_DATA.get("classic_treatments", {})
    elif v1_path.exists():
        with open(v1_path) as f:
            _CATE = json.load(f).get("results", {})
    else:
        _CATE = {}

    _OPTIMIZER_READY = True
    print(f"Budget optimizer loaded: {len(_CATE)} treatments", file=sys.stderr)
except Exception as e:
    print(f"WARNING: Budget optimizer failed to load: {e}", file=sys.stderr)
    _CATE = {}
    _OPTIMIZER_READY = False

# Renovation costs
COSTS = {
    "hasKitchen": {"cost": 15000, "label": "Modern Kitchen"},
    "balcony": {"cost": 8000, "label": "Small Balcony"},
    "lift": {"cost": 45000, "label": "Elevator"},
    "garden": {"cost": 5000, "label": "Garden Access"},
}

FEATURE_KEYS = ["hasKitchen", "balcony", "lift", "garden"]


# ---------------------------------------------------------------------------
# Similarity & substitution logic
# ---------------------------------------------------------------------------

def unit_similarity(a: dict, b: dict) -> float:
    """Compute 0-1 similarity score between two units based on observable features."""
    score = 0.0
    weights = 0.0

    # Same PLZ (strong geographic signal)
    if str(a.get("plz")) == str(b.get("plz")):
        score += 3.0
    elif a.get("bezirk") == b.get("bezirk"):
        score += 1.5
    weights += 3.0

    # Similar size (within range)
    sqm_a = float(a.get("living_space_sqm", 60))
    sqm_b = float(b.get("living_space_sqm", 60))
    sqm_ratio = min(sqm_a, sqm_b) / max(sqm_a, sqm_b, 1)
    score += sqm_ratio * 2.0
    weights += 2.0

    # Same room count
    if a.get("rooms") == b.get("rooms"):
        score += 2.0
    elif abs(float(a.get("rooms", 2)) - float(b.get("rooms", 2))) <= 1:
        score += 1.0
    weights += 2.0

    # Same building era
    if a.get("building_era") and a.get("building_era") == b.get("building_era"):
        score += 1.5
    weights += 1.5

    # Similar rent level (within 20%)
    rent_a = float(a.get("current_rent_per_sqm", 0) or 0)
    rent_b = float(b.get("current_rent_per_sqm", 0) or 0)
    if rent_a > 0 and rent_b > 0:
        rent_ratio = min(rent_a, rent_b) / max(rent_a, rent_b)
        score += rent_ratio * 1.0
    weights += 1.0

    return score / weights if weights > 0 else 0


def substitution_discount(unit: dict, renovation: str, portfolio: list[dict]) -> tuple[float, str]:
    """Compute substitution discount for a renovation.

    Returns (discount_multiplier, explanation).
    - 1.0 = no discount (no similar unit has this feature)
    - 0.7 = 30% discount (very similar unit already has this feature)
    """
    max_discount = 0.0
    competing_unit = None

    feature_key = {
        "hasKitchen": "has_kitchen",
        "balcony": "has_balcony",
        "lift": "has_elevator",
        "garden": "has_garden",
    }.get(renovation, renovation)

    for other in portfolio:
        if other.get("id") == unit.get("id"):
            continue

        # Does this other unit already have this feature?
        has_feature = bool(other.get(feature_key, False))
        if not has_feature:
            continue

        sim = unit_similarity(unit, other)
        if sim > 0.4:
            discount = (sim - 0.4) * 0.5  # 0-30% discount
            if discount > max_discount:
                max_discount = discount
                competing_unit = other

    multiplier = 1.0 - max_discount

    if competing_unit and max_discount > 0.05:
        explanation = (
            f"Similar unit ({competing_unit.get('address', 'nearby')}) already has "
            f"{COSTS.get(renovation, {}).get('label', renovation).lower()}. "
            f"Adding it here creates competition between your own units. "
            f"CATE discounted by {max_discount:.0%} (similarity: {unit_similarity(unit, competing_unit):.0%})."
        )
    else:
        explanation = "No competing unit with this feature — full CATE applies."

    return multiplier, explanation


def differentiation_bonus(unit: dict, renovation: str, portfolio: list[dict]) -> tuple[float, str]:
    """Bonus for renovations that differentiate a unit from similar ones.

    If a similar unit does NOT have this feature, adding it creates
    differentiation — making the units less substitutable.
    """
    max_bonus = 0.0
    differentiated_from = None

    feature_key = {
        "hasKitchen": "has_kitchen",
        "balcony": "has_balcony",
        "lift": "has_elevator",
        "garden": "has_garden",
    }.get(renovation, renovation)

    for other in portfolio:
        if other.get("id") == unit.get("id"):
            continue

        has_feature = bool(other.get(feature_key, False))
        if has_feature:
            continue  # They already have it — no differentiation value

        sim = unit_similarity(unit, other)
        if sim > 0.5:
            # High similarity + different feature = differentiation opportunity
            bonus = (sim - 0.5) * 0.3  # up to 15% bonus
            if bonus > max_bonus:
                max_bonus = bonus
                differentiated_from = other

    multiplier = 1.0 + max_bonus

    if differentiated_from and max_bonus > 0.02:
        explanation = (
            f"This differentiates your unit from {differentiated_from.get('address', 'a similar unit')} "
            f"which doesn't have {COSTS.get(renovation, {}).get('label', renovation).lower()}. "
            f"Different features attract different tenants — less self-competition."
        )
    else:
        explanation = ""

    return multiplier, explanation


# ---------------------------------------------------------------------------
# Optimizer
# ---------------------------------------------------------------------------

def optimize_budget(portfolio: list[dict], budget: float) -> dict:
    """Run both greedy and substitution-aware optimization.

    Args:
        portfolio: list of unit dicts from Supabase
        budget: total renovation budget in EUR

    Returns:
        dict with greedy_plan, smart_plan, comparison, and insights
    """
    if not _OPTIMIZER_READY:
        return {"error": "Optimizer not ready — CATE data not loaded"}

    # Build candidate renovations for all units
    candidates = []
    for unit in portfolio:
        sqm = float(unit.get("living_space_sqm", 60))
        unit_address = unit.get("address", f"Unit {unit.get('id', '?')[:8]}")

        for treatment in FEATURE_KEYS:
            feature_key = {
                "hasKitchen": "has_kitchen",
                "balcony": "has_balcony",
                "lift": "has_elevator",
                "garden": "has_garden",
            }.get(treatment)

            # Skip if already has this feature
            if bool(unit.get(feature_key, False)):
                continue

            cate_entry = _CATE.get(treatment, {})
            cate_sqm = cate_entry.get("att", 0)
            cost = COSTS[treatment]["cost"]
            label = COSTS[treatment]["label"]

            if cate_sqm <= 0:
                continue

            monthly_uplift = cate_sqm * sqm
            annual_uplift = monthly_uplift * 12
            roi_pct = (annual_uplift / cost) * 100 if cost > 0 else 0
            payback = cost / monthly_uplift if monthly_uplift > 0 else None

            # Substitution adjustment
            sub_mult, sub_explanation = substitution_discount(unit, treatment, portfolio)
            diff_mult, diff_explanation = differentiation_bonus(unit, treatment, portfolio)
            adjusted_mult = sub_mult * diff_mult
            adjusted_cate = cate_sqm * adjusted_mult
            adjusted_monthly = adjusted_cate * sqm
            adjusted_annual = adjusted_monthly * 12
            adjusted_roi = (adjusted_annual / cost) * 100 if cost > 0 else 0

            candidates.append({
                "unit_id": unit.get("id", ""),
                "unit_address": unit_address,
                "plz": str(unit.get("plz", "")),
                "treatment": treatment,
                "label": label,
                "cost": cost,
                "sqm": sqm,
                # Greedy (unadjusted)
                "cate_sqm": round(cate_sqm, 2),
                "monthly_uplift": round(monthly_uplift, 0),
                "annual_uplift": round(annual_uplift, 0),
                "roi_pct": round(roi_pct, 1),
                "payback_months": round(payback, 0) if payback else None,
                # Substitution-aware (adjusted)
                "sub_multiplier": round(sub_mult, 2),
                "diff_multiplier": round(diff_mult, 2),
                "adjusted_multiplier": round(adjusted_mult, 2),
                "adjusted_cate_sqm": round(adjusted_cate, 2),
                "adjusted_monthly": round(adjusted_monthly, 0),
                "adjusted_annual": round(adjusted_annual, 0),
                "adjusted_roi_pct": round(adjusted_roi, 1),
                "sub_explanation": sub_explanation,
                "diff_explanation": diff_explanation,
            })

    if not candidates:
        return {
            "greedy_plan": [],
            "smart_plan": [],
            "comparison": {"message": "No renovation opportunities — all units already have all features."},
            "budget": budget,
        }

    # --- Greedy plan: sort by ROI, fill budget ---
    greedy_sorted = sorted(candidates, key=lambda c: -c["roi_pct"])
    greedy_plan = []
    greedy_spent = 0
    for c in greedy_sorted:
        if greedy_spent + c["cost"] <= budget:
            greedy_plan.append(c)
            greedy_spent += c["cost"]

    greedy_total_monthly = sum(c["monthly_uplift"] for c in greedy_plan)
    greedy_total_annual = sum(c["annual_uplift"] for c in greedy_plan)

    # --- Smart plan: sort by adjusted ROI, fill budget ---
    smart_sorted = sorted(candidates, key=lambda c: -c["adjusted_roi_pct"])
    smart_plan = []
    smart_spent = 0
    for c in smart_sorted:
        if smart_spent + c["cost"] <= budget:
            smart_plan.append(c)
            smart_spent += c["cost"]

    smart_total_monthly = sum(c["adjusted_monthly"] for c in smart_plan)
    smart_total_annual = sum(c["adjusted_annual"] for c in smart_plan)

    # --- Comparison & insights ---
    greedy_treatments = [(c["unit_address"], c["label"]) for c in greedy_plan]
    smart_treatments = [(c["unit_address"], c["label"]) for c in smart_plan]

    plans_differ = greedy_treatments != smart_treatments

    if plans_differ:
        # Find what changed
        greedy_set = set((c["unit_id"], c["treatment"]) for c in greedy_plan)
        smart_set = set((c["unit_id"], c["treatment"]) for c in smart_plan)
        only_greedy = greedy_set - smart_set
        only_smart = smart_set - greedy_set

        dropped = [c for c in greedy_plan if (c["unit_id"], c["treatment"]) in only_greedy]
        added = [c for c in smart_plan if (c["unit_id"], c["treatment"]) in only_smart]

        insight_parts = []
        for d in dropped:
            insight_parts.append(
                f"Dropped {d['label']} at {d['unit_address']} "
                f"(a similar unit already has it → {d['sub_explanation']})"
            )
        for a in added:
            explanation = a['diff_explanation'] or a['sub_explanation']
            insight_parts.append(
                f"Added {a['label']} at {a['unit_address']} instead "
                f"({explanation})"
            )

        comparison = {
            "plans_differ": True,
            "message": (
                "The portfolio-aware plan differs from the greedy plan. "
                "Instead of duplicating features across similar units, "
                "it prioritizes differentiation — making your units compete less with each other."
            ),
            "greedy_monthly_uplift": round(greedy_total_monthly, 0),
            "smart_monthly_uplift": round(smart_total_monthly, 0),
            "greedy_annual_uplift": round(greedy_total_annual, 0),
            "smart_annual_uplift": round(smart_total_annual, 0),
            "greedy_spent": greedy_spent,
            "smart_spent": smart_spent,
            "changes": insight_parts,
        }
    else:
        comparison = {
            "plans_differ": False,
            "message": (
                "Both plans agree — no substitution effects detected. "
                "Your units are sufficiently different that renovations don't create self-competition."
            ),
            "greedy_monthly_uplift": round(greedy_total_monthly, 0),
            "smart_monthly_uplift": round(smart_total_monthly, 0),
            "greedy_annual_uplift": round(greedy_total_annual, 0),
            "smart_annual_uplift": round(smart_total_annual, 0),
            "greedy_spent": greedy_spent,
            "smart_spent": smart_spent,
            "changes": [],
        }

    return {
        "budget": budget,
        "greedy_plan": greedy_plan,
        "smart_plan": smart_plan,
        "comparison": comparison,
        "portfolio_size": len(portfolio),
        "total_candidates": len(candidates),
    }
