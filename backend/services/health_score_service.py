"""Portfolio Health Score — per-unit and aggregate scoring.

Combines 4 dimensions into a 0-100 score:
1. Pricing position (is the rent optimal vs market?)
2. Compliance risk (how far from legal max?)
3. Renovation opportunity (untapped CATE potential)
4. Market positioning (how does it compare to comparables?)

Each dimension is 0-25 points. Higher = healthier.
"""

import sys
from typing import Any


def _clamp(val: float, lo: float = 0, hi: float = 25) -> float:
    return max(lo, min(hi, val))


def score_pricing(predicted_sqm: float, current_sqm: float) -> dict:
    """Score pricing position (0-25).

    Perfect: current rent is within ±5% of predicted → 25
    Good: within ±15% → 20
    Moderate: within ±25% → 15
    Poor: >25% gap → 5-10 (overpriced or heavily underpriced)
    """
    if not predicted_sqm or not current_sqm:
        return {"score": 12.5, "label": "Unknown", "detail": "No prediction available"}

    gap_pct = abs(current_sqm - predicted_sqm) / predicted_sqm * 100
    direction = "overpriced" if current_sqm > predicted_sqm else "underpriced"

    if gap_pct <= 5:
        score = 25
        label = "Optimal"
        detail = f"Rent is within 5% of market prediction (€{predicted_sqm:.2f}/m²)"
    elif gap_pct <= 15:
        score = 20
        label = "Good"
        detail = f"Rent is {gap_pct:.0f}% {direction} vs market (€{predicted_sqm:.2f}/m²)"
    elif gap_pct <= 25:
        score = 15
        label = "Moderate"
        detail = f"Rent is {gap_pct:.0f}% {direction} — consider adjustment"
    elif gap_pct <= 40:
        score = 10
        label = "Poor"
        detail = f"Rent is {gap_pct:.0f}% {direction} — significant gap"
    else:
        score = 5
        label = "Critical"
        detail = f"Rent is {gap_pct:.0f}% {direction} — major repricing needed"

    return {"score": score, "label": label, "detail": detail, "gap_pct": round(gap_pct, 1)}


def score_compliance(is_compliant: bool, overpayment_sqm: float = 0, headroom_sqm: float = 0) -> dict:
    """Score compliance risk (0-25).

    Compliant with headroom → 25
    Compliant near ceiling → 20
    Non-compliant small overpayment → 10
    Non-compliant large overpayment → 5
    """
    if is_compliant is None:
        return {"score": 12.5, "label": "Unknown", "detail": "No compliance check available"}

    if is_compliant:
        if headroom_sqm and headroom_sqm > 1.0:
            score = 25
            label = "Safe"
            detail = f"Compliant with €{headroom_sqm:.2f}/m² headroom below legal max"
        elif headroom_sqm and headroom_sqm > 0:
            score = 20
            label = "Tight"
            detail = f"Compliant but only €{headroom_sqm:.2f}/m² below legal max"
        else:
            score = 22
            label = "Compliant"
            detail = "Within legal limits"
    else:
        overpay = abs(overpayment_sqm)
        if overpay <= 2:
            score = 12
            label = "At Risk"
            detail = f"Exceeds legal max by €{overpay:.2f}/m² — moderate exposure"
        elif overpay <= 5:
            score = 8
            label = "Non-Compliant"
            detail = f"Exceeds legal max by €{overpay:.2f}/m² — tenants can reclaim"
        else:
            score = 3
            label = "Critical"
            detail = f"Exceeds legal max by €{overpay:.2f}/m² — high legal exposure"

    return {"score": score, "label": label, "detail": detail}


def score_renovation(renovation_options: list) -> dict:
    """Score renovation opportunity (0-25).

    All features present → 25 (no opportunities = fully optimized)
    Some high-ROI opportunities → 15-20 (untapped potential)
    Many missing features with high CATE → 10 (lots of upside left)

    Note: HIGH score = good (either fully optimized or limited opportunity).
    We want to flag units with untapped potential as LOWER score to prompt action.
    """
    if not renovation_options:
        return {"score": 20, "label": "Unknown", "detail": "No renovation data"}

    already_has = sum(1 for r in renovation_options if r.get("already_has"))
    total = len(renovation_options)
    available = [r for r in renovation_options if not r.get("already_has") and r.get("combined_sqm", 0) > 0]

    if not available:
        return {"score": 25, "label": "Optimized", "detail": "All key features installed — fully optimized"}

    # Score based on how much untapped uplift exists
    max_uplift = max(r.get("combined_sqm", 0) for r in available) if available else 0
    total_uplift = sum(r.get("combined_sqm", 0) for r in available)
    best_roi = max(r.get("roi_annual_pct", 0) for r in available) if available else 0
    best_option = max(available, key=lambda r: r.get("roi_annual_pct", 0))

    if total_uplift > 5:
        score = 10
        label = "High Potential"
        detail = f"{len(available)} renovation(s) available — best: {best_option.get('label', '?')} (+€{max_uplift:.2f}/m², {best_roi:.0f}% ROI)"
    elif total_uplift > 2:
        score = 15
        label = "Some Potential"
        detail = f"{len(available)} option(s) — best: {best_option.get('label', '?')} ({best_roi:.0f}% ROI)"
    else:
        score = 20
        label = "Limited"
        detail = f"Minor improvements available (+€{total_uplift:.2f}/m² total)"

    return {"score": score, "label": label, "detail": detail}


def score_market_position(current_sqm: float, comp_avg: float = None, comp_min: float = None, comp_max: float = None) -> dict:
    """Score market positioning vs comparables (0-25).

    Below comparable average → room to increase (good for landlord)
    At comparable average → well positioned
    Above comparable average → at risk of vacancy
    """
    if not comp_avg or not current_sqm:
        return {"score": 12.5, "label": "Unknown", "detail": "No comparable data available"}

    pct_vs_avg = (current_sqm - comp_avg) / comp_avg * 100

    if -10 <= pct_vs_avg <= 10:
        score = 25
        label = "Well Positioned"
        detail = f"Rent is within 10% of comparable avg (€{comp_avg:.2f}/m²)"
    elif -25 <= pct_vs_avg < -10:
        score = 20
        label = "Below Market"
        detail = f"Rent is {abs(pct_vs_avg):.0f}% below comparables — room to increase"
    elif 10 < pct_vs_avg <= 25:
        score = 18
        label = "Above Market"
        detail = f"Rent is {pct_vs_avg:.0f}% above comparables — monitor vacancy risk"
    elif pct_vs_avg < -25:
        score = 15
        label = "Significantly Below"
        detail = f"Rent is {abs(pct_vs_avg):.0f}% below market — significant upside"
    else:
        score = 10
        label = "Overpriced"
        detail = f"Rent is {pct_vs_avg:.0f}% above comparables — high vacancy risk"

    return {"score": score, "label": label, "detail": detail}


def compute_unit_health(unit: dict, analysis: dict = None, comparables: dict = None) -> dict:
    """Compute health score for a single unit.

    Args:
        unit: unit data from Supabase
        analysis: analysis results (predict + comply + renovate)
        comparables: comparable listings summary

    Returns:
        dict with total score (0-100), grade (A-F), and per-dimension breakdown
    """
    predict = analysis.get("predict", {}) if analysis else {}
    comply = analysis.get("comply", {}) if analysis else {}
    renovate = analysis.get("renovate", {}) if analysis else {}

    current_sqm = float(unit.get("current_rent_per_sqm", 0) or 0)
    predicted_sqm = float(predict.get("predicted_rent_sqm", 0) or 0)

    # Compliance
    is_compliant = comply.get("is_compliant")
    overpayment = float(comply.get("overpayment_per_sqm", 0) or 0)
    headroom = float(comply.get("headroom_per_sqm", 0) or 0)

    # Comparables
    comp_summary = comparables.get("summary", {}) if comparables else {}

    # Score each dimension
    pricing = score_pricing(predicted_sqm, current_sqm)
    compliance = score_compliance(is_compliant, overpayment, headroom)
    renovation = score_renovation(renovate.get("options", []) if isinstance(renovate, dict) else [])
    market = score_market_position(
        current_sqm,
        comp_summary.get("avg_asking_rent"),
        comp_summary.get("min_asking_rent"),
        comp_summary.get("max_asking_rent"),
    )

    total = pricing["score"] + compliance["score"] + renovation["score"] + market["score"]

    # Grade
    if total >= 85:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 55:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"

    # Top recommendation
    dimensions = [
        ("pricing", pricing),
        ("compliance", compliance),
        ("renovation", renovation),
        ("market_position", market),
    ]
    weakest = min(dimensions, key=lambda d: d[1]["score"])

    return {
        "total_score": round(total, 1),
        "grade": grade,
        "pricing": pricing,
        "compliance": compliance,
        "renovation": renovation,
        "market_position": market,
        "weakest_area": weakest[0],
        "top_recommendation": weakest[1]["detail"],
    }


def compute_portfolio_health(units_with_scores: list[dict]) -> dict:
    """Aggregate health score across all portfolio units.

    Returns portfolio-level metrics and distribution.
    """
    if not units_with_scores:
        return {"avg_score": 0, "grade": "N/A", "distribution": {}}

    scores = [u["health"]["total_score"] for u in units_with_scores if "health" in u]
    grades = [u["health"]["grade"] for u in units_with_scores if "health" in u]

    if not scores:
        return {"avg_score": 0, "grade": "N/A", "distribution": {}}

    avg = sum(scores) / len(scores)

    if avg >= 85:
        portfolio_grade = "A"
    elif avg >= 70:
        portfolio_grade = "B"
    elif avg >= 55:
        portfolio_grade = "C"
    elif avg >= 40:
        portfolio_grade = "D"
    else:
        portfolio_grade = "F"

    distribution = {}
    for g in ["A", "B", "C", "D", "F"]:
        distribution[g] = grades.count(g)

    # Find units needing attention
    critical = [u for u in units_with_scores if "health" in u and u["health"]["total_score"] < 50]

    return {
        "avg_score": round(avg, 1),
        "grade": portfolio_grade,
        "total_units": len(scores),
        "distribution": distribution,
        "units_needing_attention": len(critical),
        "weakest_unit": min(units_with_scores, key=lambda u: u.get("health", {}).get("total_score", 100)).get("address", "?") if units_with_scores else None,
    }
