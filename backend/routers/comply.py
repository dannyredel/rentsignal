"""Compliance router — Mietpreisbremse check."""

from fastapi import APIRouter

from backend.models.compliance import ComplianceInput, ComplianceResult
from backend.services.compliance_service import check_compliance

router = APIRouter(tags=["compliance"])


@router.post("/compliance", response_model=ComplianceResult)
def check_rent_compliance(inp: ComplianceInput):
    """Check if current rent complies with Mietpreisbremse (§556d BGB)."""
    return check_compliance(inp)
