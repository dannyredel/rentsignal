"""Scenario simulator — what-if analysis for rent, renovations, and Mietspiegel changes.

Three scenarios:
A. Rent adjustment: slide rent up/down → see compliance + market position change
B. Renovation toggle: add/remove features → see predicted rent + ROI change
C. Mietspiegel update: simulate future Mietspiegel changes → see compliance impact
"""

import json
import sys
from pathlib import Path
from typing import Optional

from backend.models.compliance import ComplianceInput
from backend.services.compliance_service import lookup_mietspiegel

_ROOT = Path(__file__).resolve().parent.parent.parent

# Load matching CATE for renovation scenarios
try:
    v2_path = _ROOT / "data" / "processed" / "matching_results_v2.json"
    if v2_path.exists():
        with open(v2_path) as f:
            _CATE_DATA = json.load(f)
        _CATE = _CATE_DATA.get("classic_treatments", {})
    else:
        _CATE = {}
except Exception:
    _CATE = {}

_RENOVATION_COSTS = {
    "hasKitchen": {"cost": 15000, "label": "Modern Kitchen", "cate_key": "hasKitchen"},
    "balcony": {"cost": 8000, "label": "Small Balcony", "cate_key": "balcony"},
    "lift": {"cost": 45000, "label": "Elevator", "cate_key": "lift"},
    "garden": {"cost": 5000, "label": "Garden Access", "cate_key": "garden"},
}


def simulate_rent_adjustment(unit: dict, rent_points: list[float] = None) -> dict:
    """Scenario A: What happens at different rent levels?

    For each rent level, compute compliance status and market position.
    """
    sqm = float(unit.get("living_space_sqm", 60))
    year = int(unit.get("year_built", 1960) or 1960)
    district = unit.get("district", "")
    current_sqm = float(unit.get("current_rent_per_sqm", 0) or 0)
    predicted_sqm = float(unit.get("predicted_rent_sqm", 0) or 0)

    # Mietspiegel lookup
    try:
        compliance_input = ComplianceInput(
            district=district, living_space_sqm=sqm, building_year=year,
            current_rent_per_sqm=current_sqm,
            has_fitted_kitchen=unit.get("has_kitchen"),
            has_balcony=unit.get("has_balcony"),
            has_elevator=unit.get("has_elevator"),
        )
        ms = lookup_mietspiegel(compliance_input)
        legal_max = ms.adjusted_mid * 1.1  # Mietpreisbremse: mid + 10%
        mietspiegel_mid = ms.adjusted_mid
    except Exception:
        legal_max = 0
        mietspiegel_mid = 0

    # Default rent points if not provided
    if not rent_points:
        if current_sqm > 0:
            low = max(5, current_sqm * 0.6)
            high = current_sqm * 1.4
            rent_points = [round(low + (high - low) * i / 6, 2) for i in range(7)]
        else:
            rent_points = [8, 10, 12, 14, 16, 18, 20]

    results = []
    for rent in rent_points:
        is_compliant = rent <= legal_max if legal_max > 0 else None
        overpayment = max(0, rent - legal_max) if legal_max > 0 else 0
        monthly_total = round(rent * sqm, 0)

        # Market position (percentile estimate based on prediction)
        if predicted_sqm > 0:
            position_pct = min(99, max(1, int(50 + (rent - predicted_sqm) / predicted_sqm * 100)))
        else:
            position_pct = 50

        # Vacancy risk heuristic
        if position_pct <= 30:
            vacancy_risk = "Very Low"
        elif position_pct <= 50:
            vacancy_risk = "Low"
        elif position_pct <= 70:
            vacancy_risk = "Medium"
        elif position_pct <= 85:
            vacancy_risk = "High"
        else:
            vacancy_risk = "Very High"

        results.append({
            "rent_sqm": rent,
            "monthly_total": monthly_total,
            "annual_total": monthly_total * 12,
            "is_compliant": is_compliant,
            "overpayment_sqm": round(overpayment, 2),
            "overpayment_monthly": round(overpayment * sqm, 0),
            "market_position_pct": position_pct,
            "vacancy_risk": vacancy_risk,
            "vs_current": round(rent - current_sqm, 2) if current_sqm > 0 else None,
            "vs_predicted": round(rent - predicted_sqm, 2) if predicted_sqm > 0 else None,
        })

    return {
        "scenario": "rent_adjustment",
        "current_rent_sqm": current_sqm,
        "predicted_rent_sqm": predicted_sqm,
        "legal_max_sqm": round(legal_max, 2),
        "mietspiegel_mid": round(mietspiegel_mid, 2),
        "results": results,
    }


def simulate_renovation(unit: dict) -> dict:
    """Scenario B: What if I add/remove features?

    Shows predicted rent change for each renovation toggle.
    """
    sqm = float(unit.get("living_space_sqm", 60))
    current_sqm = float(unit.get("current_rent_per_sqm", 0) or 0)
    predicted_sqm = float(unit.get("predicted_rent_sqm", 0) or 0)

    feature_map = {
        "hasKitchen": "has_kitchen",
        "balcony": "has_balcony",
        "lift": "has_elevator",
        "garden": "has_garden",
    }

    results = []
    for treatment, info in _RENOVATION_COSTS.items():
        db_key = feature_map.get(treatment, treatment)
        has_feature = bool(unit.get(db_key, False))
        cate_entry = _CATE.get(treatment, {})
        cate_sqm = cate_entry.get("att", 0)
        ci = [cate_entry.get("ci_low", 0), cate_entry.get("ci_high", 0)]

        if has_feature:
            results.append({
                "treatment": treatment,
                "label": info["label"],
                "already_has": True,
                "cate_sqm": round(cate_sqm, 2),
            })
            continue

        new_predicted = predicted_sqm + cate_sqm
        monthly_gain = round(cate_sqm * sqm, 0)
        annual_gain = monthly_gain * 12
        cost = info["cost"]
        payback = round(cost / monthly_gain, 0) if monthly_gain > 0 else None
        roi = round(annual_gain / cost * 100, 1) if cost > 0 else 0

        # §559 legal passthrough
        legal_monthly = (cost * 0.08) / 12
        legal_sqm = round(legal_monthly / sqm, 2)

        results.append({
            "treatment": treatment,
            "label": info["label"],
            "already_has": False,
            "cate_sqm": round(cate_sqm, 2),
            "cate_ci": [round(c, 2) for c in ci],
            "predicted_before": round(predicted_sqm, 2),
            "predicted_after": round(new_predicted, 2),
            "monthly_gain": monthly_gain,
            "annual_gain": annual_gain,
            "cost": cost,
            "payback_months": payback,
            "roi_pct": roi,
            "legal_passthrough_sqm": legal_sqm,
        })

    return {
        "scenario": "renovation",
        "current_rent_sqm": current_sqm,
        "predicted_rent_sqm": predicted_sqm,
        "living_space_sqm": sqm,
        "results": results,
    }


def simulate_mietspiegel_change(unit: dict, pct_changes: list[float] = None) -> dict:
    """Scenario C: What if the Mietspiegel changes by X%?

    Shows how compliance status shifts under different Mietspiegel scenarios.
    """
    sqm = float(unit.get("living_space_sqm", 60))
    year = int(unit.get("year_built", 1960) or 1960)
    district = unit.get("district", "")
    current_sqm = float(unit.get("current_rent_per_sqm", 0) or 0)

    if not pct_changes:
        pct_changes = [-5, 0, 5, 10, 15, 20]

    # Get current Mietspiegel
    try:
        compliance_input = ComplianceInput(
            district=district, living_space_sqm=sqm, building_year=year,
            current_rent_per_sqm=current_sqm,
            has_fitted_kitchen=unit.get("has_kitchen"),
            has_balcony=unit.get("has_balcony"),
            has_elevator=unit.get("has_elevator"),
        )
        ms = lookup_mietspiegel(compliance_input)
        base_mid = ms.adjusted_mid
        base_max = base_mid * 1.1
    except Exception:
        return {"scenario": "mietspiegel_change", "error": "Mietspiegel lookup failed"}

    results = []
    for pct in pct_changes:
        new_mid = base_mid * (1 + pct / 100)
        new_max = new_mid * 1.1
        is_compliant = current_sqm <= new_max
        overpayment = max(0, current_sqm - new_max)
        exposure_annual = round(overpayment * sqm * 12, 0)

        # Headroom for rent increase
        headroom = max(0, new_mid - current_sqm)

        results.append({
            "pct_change": pct,
            "label": f"{'+'if pct >= 0 else ''}{pct}%",
            "new_mietspiegel_mid": round(new_mid, 2),
            "new_legal_max": round(new_max, 2),
            "is_compliant": is_compliant,
            "overpayment_sqm": round(overpayment, 2),
            "exposure_annual": exposure_annual,
            "headroom_sqm": round(headroom, 2),
            "rent_increase_potential_monthly": round(headroom * sqm, 0),
        })

    return {
        "scenario": "mietspiegel_change",
        "current_rent_sqm": current_sqm,
        "current_mietspiegel_mid": round(base_mid, 2),
        "current_legal_max": round(base_max, 2),
        "living_space_sqm": sqm,
        "results": results,
    }
