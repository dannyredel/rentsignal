"""Renovation simulator service — combines CATE + WTP for dual-method ROI."""

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent

with open(_ROOT / "data" / "processed" / "matching_results.json") as f:
    _CATE_DATA = json.load(f)

with open(_ROOT / "data" / "processed" / "conjoint_results.json") as f:
    _WTP_DATA = json.load(f)

_RENT_INFLATION = _WTP_DATA["rent_inflation_factor"]  # 1.378

_RENOVATION_COSTS = {
    "hasKitchen": {"cost_eur": 15000, "label": "Modern Kitchen"},
    "balcony": {"cost_eur": 8000, "label": "Small Balcony"},
    "lift": {"cost_eur": 45000, "label": "Elevator"},
    "garden": {"cost_eur": 5000, "label": "Garden Access"},
}

_WTP_MAP = {
    "hasKitchen": "kitchen",
    "balcony": "balcony",
    "lift": "elevator",
    "garden": "garden",
}


def simulate_renovations(apt: dict, living_space_sqm: float) -> list[dict]:
    """Compute renovation simulator outputs for all 4 toggles.

    Args:
        apt: dict with binary feature keys (hasKitchen, balcony, lift, garden)
        living_space_sqm: apartment size for absolute EUR calculations

    Returns:
        list of renovation option dicts
    """
    results = []

    for treatment, info in _RENOVATION_COSTS.items():
        option = {
            "treatment": treatment,
            "label": info["label"],
            "already_has": bool(apt.get(treatment, 0)),
        }

        if option["already_has"]:
            results.append(option)
            continue

        # CATE (inflation-adjusted from 2019 to 2025)
        cate_raw = _CATE_DATA["results"][treatment]["att"]
        cate_adj = cate_raw * _RENT_INFLATION
        cate_ci = [
            _CATE_DATA["results"][treatment]["ci_low"] * _RENT_INFLATION,
            _CATE_DATA["results"][treatment]["ci_high"] * _RENT_INFLATION,
        ]

        # Conjoint WTP
        wtp_key = _WTP_MAP[treatment]
        wtp_entry = list(_WTP_DATA["wtp_results"].get(wtp_key, {}).values())
        wtp_sqm = wtp_entry[0]["wtp_eur_sqm"] if wtp_entry else 0

        # Combined (average of both methods)
        combined = (cate_adj + wtp_sqm) / 2
        monthly_uplift = combined * living_space_sqm
        annual_uplift = monthly_uplift * 12

        # Payback
        payback = info["cost_eur"] / monthly_uplift if monthly_uplift > 0 else None

        # §559 legal passthrough (8% of cost per year)
        legal_monthly = (info["cost_eur"] * 0.08) / 12
        legal_sqm = legal_monthly / living_space_sqm

        option.update({
            "cost_eur": info["cost_eur"],
            "cate_sqm": round(cate_adj, 2),
            "cate_ci": [round(c, 2) for c in cate_ci],
            "wtp_sqm": round(wtp_sqm, 2),
            "combined_sqm": round(combined, 2),
            "monthly_uplift_eur": round(monthly_uplift, 0),
            "annual_uplift_eur": round(annual_uplift, 0),
            "payback_months": round(payback, 0) if payback else None,
            "legal_passthrough_sqm": round(legal_sqm, 2),
            "roi_annual_pct": round((annual_uplift / info["cost_eur"]) * 100, 1) if annual_uplift > 0 else 0,
        })
        results.append(option)

    return results
