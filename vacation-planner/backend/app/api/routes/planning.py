from typing import Optional

from fastapi import APIRouter, Depends

from app.core.security import get_optional_user
from app.services.planning import generate_trip_plan
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
