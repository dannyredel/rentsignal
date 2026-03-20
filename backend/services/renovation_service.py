"""Renovation simulator service — combines CATE + WTP for dual-method ROI.

v2: Uses matching_results_v2.json (2026 data, no inflation adjustment needed).
Falls back to v1 (matching_results.json + inflation) if v2 not available.
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent

# Try v2 first (2026 data, no inflation needed), fall back to v1
_CATE_VERSION = None
_INFLATION = 1.0

try:
    v2_path = _ROOT / "data" / "processed" / "matching_results_v2.json"
    v1_path = _ROOT / "data" / "processed" / "matching_results.json"

    if v2_path.exists():
        with open(v2_path) as f:
            _CATE_DATA = json.load(f)
        # v2 has classic_treatments and extended_treatments
        _CATE_RESULTS = _CATE_DATA.get("classic_treatments", _CATE_DATA.get("results", {}))
        _CATE_EXTENDED = _CATE_DATA.get("extended_treatments", {})
        _INFLATION = 1.0  # v2 is on 2026 data, no inflation
        _CATE_VERSION = "v2"
    elif v1_path.exists():
        with open(v1_path) as f:
            _CATE_DATA = json.load(f)
        _CATE_RESULTS = _CATE_DATA.get("results", {})
        _CATE_EXTENDED = {}
        _INFLATION = 1.378  # v1 is 2019 data, needs inflation to 2025
        _CATE_VERSION = "v1"
    else:
        _CATE_DATA = {}
        _CATE_RESULTS = {}
        _CATE_EXTENDED = {}

    # Load conjoint WTP
    conjoint_path = _ROOT / "data" / "processed" / "conjoint_results.json"
    if conjoint_path.exists():
        with open(conjoint_path) as f:
            _WTP_DATA = json.load(f)
    else:
        _WTP_DATA = {}

    _RENOVATION_READY = True
    print(f"Renovation service loaded: CATE {_CATE_VERSION}, "
          f"{len(_CATE_RESULTS)} classic + {len(_CATE_EXTENDED)} extended treatments, "
          f"inflation={_INFLATION}", file=sys.stderr)

except Exception as e:
    print(f"WARNING: Renovation service failed to load: {e}", file=sys.stderr)
    _CATE_DATA = _WTP_DATA = {}
    _CATE_RESULTS = _CATE_EXTENDED = {}
    _INFLATION = 1.0
    _RENOVATION_READY = False

# Renovation costs and labels
_RENOVATION_COSTS = {
    "hasKitchen": {"cost_eur": 15000, "label": "Modern Kitchen"},
    "balcony": {"cost_eur": 8000, "label": "Small Balcony"},
    "lift": {"cost_eur": 45000, "label": "Elevator"},
    "garden": {"cost_eur": 5000, "label": "Garden Access"},
}

# Map treatment keys to conjoint WTP keys
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

        # CATE from matching
        cate_entry = _CATE_RESULTS.get(treatment, {})
        cate_raw = cate_entry.get("att", 0)
        cate_adj = cate_raw * _INFLATION
        cate_ci = [
            cate_entry.get("ci_low", 0) * _INFLATION,
            cate_entry.get("ci_high", 0) * _INFLATION,
        ]

        # Conjoint WTP
        wtp_sqm = 0
        wtp_key = _WTP_MAP.get(treatment)
        if wtp_key and _WTP_DATA:
            wtp_results = _WTP_DATA.get("wtp_results", {})
            wtp_entry = list(wtp_results.get(wtp_key, {}).values())
            wtp_sqm = wtp_entry[0]["wtp_eur_sqm"] if wtp_entry else 0

        # Combined (average of both methods, or just CATE if no WTP)
        if wtp_sqm != 0:
            combined = (cate_adj + wtp_sqm) / 2
        else:
            combined = cate_adj

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
            "cate_version": _CATE_VERSION,
        })
        results.append(option)

    return results
