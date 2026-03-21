"""Pydantic schemas for portfolio management."""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Unit CRUD ──


class UnitCreate(BaseModel):
    """Input for creating a portfolio unit."""

    # Address
    address: Optional[str] = None
    plz: Optional[int] = None
    district: str
    lat: Optional[float] = None
    lon: Optional[float] = None

    # Structural (same fields as ApartmentInput)
    living_space_sqm: float = Field(..., gt=0)
    rooms: float = Field(..., gt=0)
    year_built: int = Field(..., ge=1800, le=2030)
    floor: int = 0
    building_floors: int = 1
    thermal_char: float = 100

    # Amenities
    has_kitchen: bool = False
    has_balcony: bool = False
    has_elevator: bool = False
    has_cellar: bool = False
    has_garden: bool = False
    is_new_construction: bool = False

    # Categorical
    condition: str = "well_kept"
    interior_quality: str = "normal"
    flat_type: str = "apartment"
    heating_type: str = "central_heating"
    building_era: Optional[str] = None

    # Compliance
    current_rent_per_sqm: Optional[float] = None
    previous_rent_per_sqm: Optional[float] = None
    has_modern_bathroom: Optional[bool] = None
    has_fitted_kitchen: Optional[bool] = None
    has_parquet_flooring: Optional[bool] = None
    has_modern_heating: Optional[bool] = None
    has_good_insulation: Optional[bool] = None
    has_basement_storage: Optional[bool] = None
    location_quality: Optional[str] = None
    is_first_rental_after_comprehensive_modernization: bool = False

    # Energy
    energy_class: Optional[str] = None
    energy_consumption_kwh: Optional[float] = None
    heating_fuel_type: Optional[str] = None

    # Rent increase tracking
    last_rent_increase_date: Optional[date] = None
    prior_increases_6yr_sqm: float = 0

    # Monitoring
    is_monitored: bool = False

    # Optional Gemini image features (from photo upload)
    gemini_features: Optional[dict] = None

    # User notes
    label: Optional[str] = None
    notes: Optional[str] = None


class UnitUpdate(BaseModel):
    """Partial update for a unit. Only provided fields are updated."""

    address: Optional[str] = None
    plz: Optional[int] = None
    district: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    living_space_sqm: Optional[float] = None
    rooms: Optional[float] = None
    year_built: Optional[int] = None
    floor: Optional[int] = None
    building_floors: Optional[int] = None
    thermal_char: Optional[float] = None
    has_kitchen: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_elevator: Optional[bool] = None
    has_cellar: Optional[bool] = None
    has_garden: Optional[bool] = None
    is_new_construction: Optional[bool] = None
    condition: Optional[str] = None
    interior_quality: Optional[str] = None
    flat_type: Optional[str] = None
    heating_type: Optional[str] = None
    building_era: Optional[str] = None
    current_rent_per_sqm: Optional[float] = None
    previous_rent_per_sqm: Optional[float] = None
    has_modern_bathroom: Optional[bool] = None
    has_fitted_kitchen: Optional[bool] = None
    has_parquet_flooring: Optional[bool] = None
    has_modern_heating: Optional[bool] = None
    has_good_insulation: Optional[bool] = None
    has_basement_storage: Optional[bool] = None
    location_quality: Optional[str] = None
    is_first_rental_after_comprehensive_modernization: Optional[bool] = None
    energy_class: Optional[str] = None
    energy_consumption_kwh: Optional[float] = None
    heating_fuel_type: Optional[str] = None
    last_rent_increase_date: Optional[date] = None
    prior_increases_6yr_sqm: Optional[float] = None
    is_monitored: Optional[bool] = None
    label: Optional[str] = None
    notes: Optional[str] = None


class UnitResponse(BaseModel):
    """Unit with latest analysis summary."""

    id: UUID
    user_id: UUID

    # Core fields
    address: Optional[str] = None
    plz: Optional[int] = None
    district: str
    label: Optional[str] = None
    living_space_sqm: float
    rooms: float
    year_built: int
    floor: int = 0
    building_floors: int = 1
    has_kitchen: bool = False
    has_balcony: bool = False
    has_elevator: bool = False
    has_garden: bool = False
    has_cellar: bool = False
    condition: str = "well_kept"
    current_rent_per_sqm: Optional[float] = None
    is_monitored: bool = False

    # Latest analysis (denormalized from analyses table)
    predicted_rent_sqm: Optional[float] = None
    rent_gap_pct: Optional[float] = None
    is_compliant: Optional[bool] = None
    overpayment_annual: Optional[float] = None
    legal_max_rent_sqm: Optional[float] = None

    # Full analysis results (JSONB from view)
    predict_result: Optional[Any] = None
    comply_result: Optional[Any] = None
    renovate_result: Optional[Any] = None

    created_at: datetime
    updated_at: datetime


# ── Portfolio Summary ──


class PortfolioSummary(BaseModel):
    """Aggregated portfolio metrics."""

    total_units: int = 0
    analyzed_units: int = 0
    avg_rent_gap_pct: Optional[float] = None
    total_underpriced_annual: float = 0
    non_compliant_units: int = 0
    total_compliance_exposure_annual: float = 0
    monitored_units: int = 0


# ── Batch Analysis ──


class BatchJobCreate(BaseModel):
    """Input for triggering a batch analysis."""

    unit_ids: Optional[list[UUID]] = None  # None = all units


class BatchJobResponse(BaseModel):
    """Status of a batch analysis job."""

    id: UUID
    status: str
    total_units: int = 0
    processed_units: int = 0
    failed_units: int = 0
    errors: Optional[list[dict]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# ── CSV Import ──


class CSVUploadResponse(BaseModel):
    """Response after uploading a CSV file."""

    job_id: UUID
    detected_columns: list[str]
    sample_rows: list[dict]
    total_rows: int


class CSVMappingConfirm(BaseModel):
    """User-confirmed column mapping for CSV import."""

    job_id: UUID
    column_mapping: dict[str, str]  # {"Wohnfläche": "living_space_sqm", ...}


class ImportJobResponse(BaseModel):
    """Status of a CSV import job."""

    id: UUID
    status: str
    total_rows: int = 0
    rows_imported: int = 0
    rows_skipped: int = 0
    errors: Optional[list[dict]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
