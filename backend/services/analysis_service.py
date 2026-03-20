"""Auto-analysis service — runs predict + comply + renovate on a unit and stores results."""

import traceback
from typing import Any

from backend.models.apartment import ApartmentInput, PredictionResult, SHAPFeature
from backend.models.compliance import ComplianceInput, ComplianceResult
from backend.routers.predict import CONDITION_MAP, DISTRICT_TO_BEZIRK, _year_to_era
from backend.services.compliance_service import check_compliance
from backend.services.ml_service import predict as ml_predict
from backend.services.renovation_service import simulate_renovations
from backend.supabase_client import get_supabase


def _unit_to_predict_input(unit: dict) -> tuple[dict, int | None]:
    """Convert a unit DB row to the format ml_service.predict() expects."""
    district = unit.get("district", "")
    bezirk = DISTRICT_TO_BEZIRK.get(district, district)
    condition = CONDITION_MAP.get(unit.get("condition", "well_kept"), "well_kept")
    year_built = unit.get("year_built", 1960)

    building_era = unit.get("building_era") or _year_to_era(year_built)

    model_input = {
        "livingSpace": unit.get("living_space_sqm", 60),
        "noRooms": unit.get("rooms", 2),
        "yearConstructed": year_built,
        "floor": unit.get("floor", 0),
        "numberOfFloors": unit.get("building_floors", 1),
        "thermalChar": unit.get("thermal_char", 100),
        "balcony": int(unit.get("has_balcony", False)),
        "hasKitchen": int(unit.get("has_kitchen", False)),
        "lift": int(unit.get("has_elevator", False)),
        "cellar": int(unit.get("has_cellar", False)),
        "garden": int(unit.get("has_garden", False)),
        "newlyConst": int(unit.get("is_new_construction", False)),
        "condition": condition,
        "interiorQual": unit.get("interior_quality", "normal"),
        "typeOfFlat": unit.get("flat_type", "apartment"),
        "heatingType": unit.get("heating_type", "central_heating"),
        "building_era": building_era,
        "bezirk": bezirk,
    }
    return model_input, unit.get("plz")


def _run_predict(unit: dict) -> dict[str, Any]:
    """Run prediction and return result dict + denormalized metrics."""
    model_input, plz = _unit_to_predict_input(unit)
    result = ml_predict(model_input, plz=plz)

    current_rent = unit.get("current_rent_per_sqm")
    gap_sqm = None
    gap_pct = None
    status = None
    if current_rent is not None:
        gap_sqm = round(result["predicted_rent_sqm"] - current_rent, 2)
        gap_pct = round((gap_sqm / current_rent) * 100, 1) if current_rent > 0 else None
        if gap_sqm > 0.5:
            status = "UNDERPRICED"
        elif gap_sqm < -0.5:
            status = "OVERPRICED"
        else:
            status = "FAIRLY_PRICED"

    full_result = {
        "predicted_rent_sqm": result["predicted_rent_sqm"],
        "current_rent_sqm": current_rent,
        "gap_sqm": gap_sqm,
        "gap_pct": gap_pct,
        "status": status,
        "base_value": result["base_value"],
        "shap_top_features": result["shap_top_features"],
        "prediction_interval_80": result.get("prediction_interval_80"),
        "prediction_interval_50": result.get("prediction_interval_50"),
        "model_r2": result["model_r2"],
        "model_version": result["model_version"],
        "enrichment_level": result.get("enrichment_level", "basic"),
    }
    return {
        "result": full_result,
        "predicted_rent_sqm": result["predicted_rent_sqm"],
        "rent_gap_pct": gap_pct,
    }


def _run_comply(unit: dict) -> dict[str, Any]:
    """Run compliance check and return result dict + denormalized metrics."""
    inp = ComplianceInput(
        district=unit.get("district", ""),
        living_space_sqm=unit.get("living_space_sqm", 60),
        building_year=unit.get("year_built", 1960),
        current_rent_per_sqm=unit.get("current_rent_per_sqm"),
        previous_rent_per_sqm=unit.get("previous_rent_per_sqm"),
        has_modern_bathroom=unit.get("has_modern_bathroom"),
        has_fitted_kitchen=unit.get("has_fitted_kitchen"),
        has_balcony=unit.get("has_balcony"),
        has_elevator=unit.get("has_elevator"),
        has_parquet_flooring=unit.get("has_parquet_flooring"),
        has_modern_heating=unit.get("has_modern_heating"),
        has_good_insulation=unit.get("has_good_insulation"),
        has_basement_storage=unit.get("has_basement_storage"),
        location_quality=unit.get("location_quality"),
        is_first_rental_after_comprehensive_modernization=unit.get(
            "is_first_rental_after_comprehensive_modernization", False
        ),
    )
    result: ComplianceResult = check_compliance(inp)
    result_dict = result.model_dump()

    return {
        "result": result_dict,
        "is_compliant": result.is_compliant,
        "overpayment_annual": result.overpayment_annual,
        "legal_max_rent_sqm": result.mietpreisbremse.legal_max_rent_per_sqm,
        "headroom_sqm": result.headroom_per_sqm,
    }


def _run_renovate(unit: dict) -> dict[str, Any]:
    """Run renovation simulation and return result dict."""
    apt = {
        "hasKitchen": int(unit.get("has_kitchen", False)),
        "balcony": int(unit.get("has_balcony", False)),
        "lift": int(unit.get("has_elevator", False)),
        "garden": int(unit.get("has_garden", False)),
    }
    living_space = unit.get("living_space_sqm", 60)
    options = simulate_renovations(apt, living_space)
    return {
        "result": {
            "living_space_sqm": living_space,
            "options": options,
        }
    }


def run_full_analysis(unit: dict, user_id: str) -> dict[str, Any]:
    """Run predict + comply + renovate on a unit and store in analyses table.

    Args:
        unit: dict with unit fields (from Supabase row or UnitCreate)
        user_id: the owning user's ID

    Returns:
        dict with analysis results and any errors
    """
    unit_id = unit["id"]
    sb = get_supabase()
    errors = []

    # --- Predict ---
    predict_data = None
    try:
        predict_data = _run_predict(unit)
        sb.table("analyses").insert({
            "unit_id": unit_id,
            "user_id": user_id,
            "type": "predict",
            "result": predict_data["result"],
            "predicted_rent_sqm": predict_data["predicted_rent_sqm"],
            "rent_gap_pct": predict_data["rent_gap_pct"],
            "model_version": predict_data["result"].get("model_version", "v4.2.0"),
        }).execute()
    except Exception as e:
        errors.append({"type": "predict", "error": str(e), "traceback": traceback.format_exc()})

    # --- Comply ---
    comply_data = None
    try:
        comply_data = _run_comply(unit)
        sb.table("analyses").insert({
            "unit_id": unit_id,
            "user_id": user_id,
            "type": "comply",
            "result": comply_data["result"],
            "is_compliant": comply_data["is_compliant"],
            "overpayment_annual": comply_data["overpayment_annual"],
            "legal_max_rent_sqm": comply_data["legal_max_rent_sqm"],
            "headroom_sqm": comply_data["headroom_sqm"],
        }).execute()
    except Exception as e:
        errors.append({"type": "comply", "error": str(e), "traceback": traceback.format_exc()})

    # --- Renovate ---
    renovate_data = None
    try:
        renovate_data = _run_renovate(unit)
        sb.table("analyses").insert({
            "unit_id": unit_id,
            "user_id": user_id,
            "type": "renovate",
            "result": renovate_data["result"],
        }).execute()
    except Exception as e:
        errors.append({"type": "renovate", "error": str(e), "traceback": traceback.format_exc()})

    return {
        "predict": predict_data["result"] if predict_data else None,
        "comply": comply_data["result"] if comply_data else None,
        "renovate": renovate_data["result"] if renovate_data else None,
        "errors": errors if errors else None,
    }
