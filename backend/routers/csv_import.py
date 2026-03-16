"""CSV import endpoints for bulk portfolio onboarding."""

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from backend.auth import User, get_current_user
from backend.models.portfolio import CSVMappingConfirm, CSVUploadResponse, ImportJobResponse
from backend.supabase_client import get_supabase
from backend.tier import check_tier

router = APIRouter(prefix="/portfolio/import", tags=["import"])

# Known column aliases → our field names
COLUMN_ALIASES = {
    # German
    "wohnfläche": "living_space_sqm",
    "wohnflaeche": "living_space_sqm",
    "fläche": "living_space_sqm",
    "qm": "living_space_sqm",
    "m²": "living_space_sqm",
    "m2": "living_space_sqm",
    "zimmer": "rooms",
    "räume": "rooms",
    "baujahr": "year_built",
    "bezirk": "district",
    "stadtteil": "district",
    "plz": "plz",
    "postleitzahl": "plz",
    "adresse": "address",
    "straße": "address",
    "strasse": "address",
    "etage": "floor",
    "stockwerk": "floor",
    "miete": "current_rent_per_sqm",
    "kaltmiete": "current_rent_per_sqm",
    "nettokaltmiete": "current_rent_per_sqm",
    "küche": "has_kitchen",
    "kueche": "has_kitchen",
    "balkon": "has_balcony",
    "aufzug": "has_elevator",
    "fahrstuhl": "has_elevator",
    "garten": "has_garden",
    "keller": "has_cellar",
    "bezeichnung": "label",
    "name": "label",
    "notizen": "notes",
    # English
    "living_space": "living_space_sqm",
    "area": "living_space_sqm",
    "size": "living_space_sqm",
    "year": "year_built",
    "built": "year_built",
    "postal_code": "plz",
    "zip": "plz",
    "rent": "current_rent_per_sqm",
    "kitchen": "has_kitchen",
    "balcony": "has_balcony",
    "elevator": "has_elevator",
    "lift": "has_elevator",
    "garden": "has_garden",
    "cellar": "has_cellar",
}


@router.post("/csv", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Upload a CSV file. Returns detected columns and sample rows for mapping UI."""
    await check_tier(user, "pro")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(400, detail="Could not detect CSV columns")

    rows = []
    for i, row in enumerate(reader):
        rows.append(row)
        if i >= 100:  # cap at 100 rows for processing
            break

    sample = rows[:5]
    detected = list(reader.fieldnames)

    # Auto-suggest mappings
    suggestions = {}
    for col in detected:
        normalized = col.strip().lower().replace(" ", "_")
        if normalized in COLUMN_ALIASES:
            suggestions[col] = COLUMN_ALIASES[normalized]

    sb = get_supabase()
    job = {
        "user_id": user.user_id,
        "status": "mapping",
        "original_filename": file.filename,
        "total_rows": len(rows),
        "detected_columns": detected,
        "sample_rows": sample,
    }
    result = sb.table("import_jobs").insert(job).execute()
    job_data = result.data[0]

    return {
        "job_id": job_data["id"],
        "detected_columns": detected,
        "sample_rows": sample,
        "total_rows": len(rows),
    }


@router.post("/confirm", response_model=ImportJobResponse)
async def confirm_mapping(
    data: CSVMappingConfirm,
    user: User = Depends(get_current_user),
):
    """Submit column mapping and start import. Creates units from the CSV rows."""
    await check_tier(user, "pro")

    sb = get_supabase()

    # Get the import job
    job_result = (
        sb.table("import_jobs")
        .select("*")
        .eq("id", str(data.job_id))
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not job_result.data:
        raise HTTPException(404, detail="Import job not found")

    job = job_result.data
    if job["status"] != "mapping":
        raise HTTPException(400, detail=f"Job is in '{job['status']}' state, expected 'mapping'")

    sample_rows = job.get("sample_rows", [])

    # Update job status
    sb.table("import_jobs").update({
        "status": "processing",
        "column_mapping": data.column_mapping,
    }).eq("id", str(data.job_id)).execute()

    # Process rows (synchronous for now — async for large files later)
    imported = 0
    skipped = 0
    errors = []

    for i, raw_row in enumerate(sample_rows):  # TODO: use full stored rows, not just sample
        try:
            unit = _map_row(raw_row, data.column_mapping, user.user_id)
            if unit:
                sb.table("units").insert(unit).execute()
                imported += 1
            else:
                skipped += 1
        except Exception as e:
            skipped += 1
            errors.append({"row": i + 1, "error": str(e)})

    # Update job completion
    result = (
        sb.table("import_jobs")
        .update({
            "status": "completed",
            "rows_imported": imported,
            "rows_skipped": skipped,
            "errors": errors if errors else None,
        })
        .eq("id", str(data.job_id))
        .execute()
    )

    return result.data[0]


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_status(
    job_id: UUID,
    user: User = Depends(get_current_user),
):
    """Poll import job status."""
    sb = get_supabase()
    result = (
        sb.table("import_jobs")
        .select("*")
        .eq("id", str(job_id))
        .eq("user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, detail="Import job not found")
    return result.data


def _map_row(raw_row: dict, mapping: dict[str, str], user_id: str) -> dict | None:
    """Map a raw CSV row to a unit insert dict using the confirmed column mapping."""
    unit = {"user_id": user_id}

    for csv_col, field_name in mapping.items():
        value = raw_row.get(csv_col, "").strip()
        if not value:
            continue

        # Type coercions
        if field_name in ("living_space_sqm", "rooms", "current_rent_per_sqm", "thermal_char"):
            value = float(value.replace(",", "."))
        elif field_name in ("year_built", "plz", "floor", "building_floors"):
            value = int(float(value))
        elif field_name in (
            "has_kitchen", "has_balcony", "has_elevator", "has_cellar",
            "has_garden", "is_new_construction", "is_monitored",
        ):
            value = value.lower() in ("1", "true", "yes", "ja", "x", "✓")

        unit[field_name] = value

    # Require minimum fields
    if "district" not in unit or "living_space_sqm" not in unit or "year_built" not in unit or "rooms" not in unit:
        return None

    return unit
