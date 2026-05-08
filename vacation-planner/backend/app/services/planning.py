import asyncio
from typing import Optional

from fastapi import HTTPException
from loguru import logger

from agent_experience import generate_experience_itinerary
from agent_logistics import generate_logistics
from app.services.recommendations import recommend_dates_for, recommend_destination
from models import FinalTripPlan, UserInput


async def generate_trip_plan(user_input: UserInput, user_id: Optional[str]) -> FinalTripPlan:
    try:
        if user_input.flexible_destination and not (user_input.destination or "").strip():
            recommended_destination = await recommend_destination(user_input, user_id)
            user_input = user_input.model_copy(update={"destination": recommended_destination})
        if user_input.flexible_dates:
            date_recommendation = recommend_dates_for(user_input.destination, user_input.budget)
            user_input = user_input.model_copy(
                update={
                    "start_date": date_recommendation["start_date"],
                    "end_date": date_recommendation["end_date"],
                }
            )

        logger.info(f"[Orchestrator] Running experience and logistics in parallel for {user_input.destination}")
        logistics_context = (
            f"Origin: {user_input.origin}, Destination: {user_input.destination}, "
            f"Check-in: {user_input.start_date}, Check-out: {user_input.end_date}, "
            f"Price range per person: {user_input.price_range_per_person or user_input.budget}. "
            "Provide flight and hotel estimates."
        )
        experience_result, logistics_result = await asyncio.gather(
            generate_experience_itinerary(user_input),
            generate_logistics(user_input, logistics_context),
        )

        final_plan = FinalTripPlan(
            experience=experience_result,
            logistics=logistics_result,
        )

        logger.info(f"[Orchestrator] Complete plan generated for {user_input.destination}")
        return final_plan

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Orchestrator] Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
