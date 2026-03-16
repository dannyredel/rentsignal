"""Renovation simulator router — dual-method CATE + WTP + ROI."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.models.apartment import RenovationOption, RenovationResult
from backend.services.renovation_service import simulate_renovations

router = APIRouter(tags=["renovate"])


class RenovationInput(BaseModel):
    living_space_sqm: float = Field(..., gt=0)
    has_kitchen: bool = Field(False)
    has_balcony: bool = Field(False)
    has_elevator: bool = Field(False)
    has_garden: bool = Field(False)
    apartment_id: str | None = None


@router.post("/renovate", response_model=RenovationResult)
def simulate(inp: RenovationInput):
    """Simulate renovation impact using dual-method (observational CATE + synthetic WTP)."""
    apt = {
        "hasKitchen": int(inp.has_kitchen),
        "balcony": int(inp.has_balcony),
        "lift": int(inp.has_elevator),
        "garden": int(inp.has_garden),
    }

    options = simulate_renovations(apt, inp.living_space_sqm)

    return RenovationResult(
        apartment_id=inp.apartment_id,
        living_space_sqm=inp.living_space_sqm,
        options=[RenovationOption(**o) for o in options],
    )
