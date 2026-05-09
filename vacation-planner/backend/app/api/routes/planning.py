from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.security import get_optional_user
from app.services.planning import generate_trip_plan, search_locations
from app.services.recommendations import recommend_destinations
from models import FinalTripPlan, UserInput

router = APIRouter(prefix="/api", tags=["planning"])


@router.post("/recommend-destinations")
async def recommend_destination_options(
    user_input: UserInput,
    user_id: Optional[str] = Depends(get_optional_user),
):
    recommendations = await recommend_destinations(user_input, user_id, limit=4)
    return {"recommendations": recommendations}


@router.post("/generate-itinerary", response_model=FinalTripPlan)
async def generate_itinerary(
    user_input: UserInput,
    user_id: Optional[str] = Depends(get_optional_user),
):
    return await generate_trip_plan(user_input, user_id)


@router.get("/location-search")
async def location_search(q: str = Query(..., min_length=2, max_length=80)):
    return {"results": await search_locations(q)}
