"""Photo-enhanced prediction endpoint — upload photos for AI-powered rent prediction."""

import sys
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile
from PIL import Image

from backend.services.gemini_service import analyze_photos
from backend.services.ml_service import predict

router = APIRouter(tags=["predict"])

# Same district/condition maps as predict.py
DISTRICT_TO_BEZIRK = {
    "Charlottenburg-Wilmersdorf": "Charlottenburg",
    "Friedrichshain-Kreuzberg": "Kreuzberg",
    "Marzahn-Hellersdorf": "Marzahn",
    "Steglitz-Zehlendorf": "Steglitz",
    "Tempelhof-Schöneberg": "Tempelhof",
    "Treptow-Köpenick": "Treptow",
    "Mitte": "Mitte", "Neukölln": "Neukölln", "Pankow": "Pankow",
    "Lichtenberg": "Lichtenberg", "Reinickendorf": "Reinickendorf",
    "Spandau": "Spandau",
    "Wilmersdorf": "Wilmersdorf", "Charlottenburg": "Charlottenburg",
    "Kreuzberg": "Kreuzberg", "Friedrichshain": "Friedrichshain",
    "Schöneberg": "Schöneberg", "Tempelhof": "Tempelhof",
    "Steglitz": "Steglitz", "Zehlendorf": "Zehlendorf",
    "Neukölln": "Neukölln", "Treptow": "Treptow",
}

CONDITION_MAP = {
    "good": "well_kept", "normal": "well_kept", "simple": "need_of_renovation",
    "luxury": "mint_condition",
    "first_time_use": "first_time_use",
    "first_time_use_after_refurbishment": "first_time_use_after_refurbishment",
    "fully_renovated": "fully_renovated",
    "modernized": "modernized",
    "mint_condition": "mint_condition",
    "well_kept": "well_kept",
    "need_of_renovation": "need_of_renovation",
    "refurbished": "refurbished",
}


def _year_to_era(year: int) -> str:
    if year < 1918: return "pre_1918"
    if year < 1949: return "1919_1949"
    if year < 1965: return "1950_1964"
    if year < 1973: return "1965_1972"
    if year < 1991: return "1973_1990"
    if year < 2003: return "1991_2002"
    if year < 2015: return "2003_2014"
    return "2015_plus"


@router.post("/predict/with-photos")
async def predict_with_photos(
    photos: list[UploadFile] = File(..., description="Apartment photos (1-10 images)"),
    plz: int = Form(...),
    district: str = Form(...),
    living_space_sqm: float = Form(...),
    rooms: int = Form(...),
    year_built: int = Form(...),
    floor: int = Form(0),
    building_floors: int = Form(5),
    condition: str = Form("normal"),
    interior_quality: str = Form("normal"),
    current_rent: Optional[float] = Form(None),
    has_kitchen: bool = Form(False),
    has_balcony: bool = Form(False),
    has_elevator: bool = Form(False),
    has_garden: bool = Form(False),
    has_cellar: bool = Form(False),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
):
    """Predict rent with AI photo analysis.

    Upload 1-10 apartment photos along with structural features.
    Photos are analyzed by Gemini AI to extract visual quality features
    (interior quality, kitchen/bathroom quality, floor type, etc.).
    This typically improves prediction accuracy by 5-15%.
    """
    # 1. Load photos as PIL Images
    images = []
    for photo in photos[:10]:
        try:
            content = await photo.read()
            img = Image.open(BytesIO(content))
            images.append(img)
        except Exception as e:
            print(f"Failed to load photo {photo.filename}: {e}", file=sys.stderr)

    # 2. Analyze with Gemini
    gemini_features = {}
    n_photos = len(images)
    if images:
        print(f"Analyzing {n_photos} photos with Gemini...", file=sys.stderr)
        gemini_features = analyze_photos(images)
        print(f"Gemini features: {len(gemini_features)} extracted", file=sys.stderr)

    # 3. Build model input
    bezirk = DISTRICT_TO_BEZIRK.get(district, district)
    mapped_condition = CONDITION_MAP.get(condition, condition)
    building_era = _year_to_era(year_built)

    model_input = {
        "livingSpace": living_space_sqm,
        "noRooms": rooms,
        "yearConstructed": year_built,
        "floor": floor,
        "numberOfFloors": building_floors,
        "thermalChar": 100,
        "balcony": int(has_balcony),
        "hasKitchen": int(has_kitchen),
        "lift": int(has_elevator),
        "cellar": int(has_cellar),
        "garden": int(has_garden),
        "newlyConst": 0,
        "condition": mapped_condition,
        "interiorQual": interior_quality,
        "typeOfFlat": "apartment",
        "heatingType": "central_heating",
        "building_era": building_era,
        "bezirk": bezirk,
    }

    # 4. Run prediction with Gemini features
    result = predict(
        model_input,
        plz=plz,
        lat=lat,
        lon=lon,
        gemini_features=gemini_features if gemini_features else None,
    )

    # 5. Gap analysis
    gap_sqm = None
    gap_pct = None
    status = "FAIR"
    if current_rent is not None and result["predicted_rent_sqm"] > 0:
        gap_sqm = round(result["predicted_rent_sqm"] - current_rent, 2)
        gap_pct = round(gap_sqm / current_rent * 100, 1)
        status = "UNDERPRICED" if gap_sqm > 0 else "OVERPRICED" if gap_sqm < 0 else "FAIR"

    result["current_rent_sqm"] = current_rent
    result["gap_sqm"] = gap_sqm
    result["gap_pct"] = gap_pct
    result["status"] = status
    result["photos_analyzed"] = n_photos
    result["gemini_features_extracted"] = len(gemini_features)

    return result
