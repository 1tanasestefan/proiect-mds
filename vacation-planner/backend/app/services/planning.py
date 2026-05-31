from __future__ import annotations
from typing import Optional

import httpx
from fastapi import HTTPException
from loguru import logger

from agent_experience import generate_experience_itinerary
from agent_logistics import generate_logistics
from app.services.recommendations import recommend_dates_for, recommend_destination
from models import FinalTripPlan, UserInput


async def search_locations(term: str) -> list[dict]:
    query = term.strip()
    if len(query) < 2:
        return []

    params = {
        "format": "jsonv2",
        "q": query,
        "addressdetails": 1,
        "namedetails": 1,
        "limit": 8,
    }
    headers = {
        "User-Agent": "VibeTripsPlanner/1.0 (contact@vibetrips.test)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
            response.raise_for_status()
            rows = response.json()
    except Exception as exc:
        logger.warning(f"[LocationSearch] Nominatim lookup failed for '{query}': {exc}")
        return []

    seen: set[str] = set()
    results: list[dict] = []
    for row in rows:
        address = row.get("address") or {}
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
            or ""
        )
        country = address.get("country") or ""
        display_name = f"{city}, {country}".strip(", ") if city and country else row.get("display_name", "")
        if not display_name:
            continue
        key = display_name.lower()
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "place_id": row.get("place_id"),
            "display_name": display_name,
        })
        if len(results) >= 5:
            break
    return results


def _experience_logistics_context(experience_result) -> str:
    activities = []
    for day in experience_result.itinerary:
        for activity in day.activities:
            activities.append(
                f"Day {day.day_number}: {activity.title} | {activity.location} | "
                f"{activity.time} | {activity.type} | cost: {activity.cost}"
            )

    if not activities:
        return "No activity locations available yet."

    return (
        "Generated activity anchors for logistics planning:\n"
        + "\n".join(activities[:18])
        + "\nUse these anchors to recommend stay areas, local transport, and budget assumptions."
    )


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

        logger.info(f"[Orchestrator] Step 1: Experience Agent for {user_input.destination}")
        experience_result = await generate_experience_itinerary(user_input)

        logger.info(f"[Orchestrator] Step 2: Logistics Agent for {user_input.destination}")
        logistics_context = (
            f"Origin: {user_input.origin}, Destination: {user_input.destination}, "
            f"Check-in: {user_input.start_date}, Check-out: {user_input.end_date}, "
            f"Price range per person: {user_input.price_range_per_person or user_input.budget}. "
            "Provide flight, stay, local transport, and itemized budget estimates.\n\n"
            f"{_experience_logistics_context(experience_result)}"
        )
        logistics_result = await generate_logistics(
            user_input,
            logistics_context,
            experience_result,
        )

        final_plan = FinalTripPlan(
            experience=experience_result,
            logistics=logistics_result,
            origin=user_input.origin,
            destination=user_input.destination,
            start_date=user_input.start_date,
            end_date=user_input.end_date,
            travelers=user_input.travelers,
            budget=user_input.budget,
            price_range_per_person=user_input.price_range_per_person,
            flexible_dates=user_input.flexible_dates,
            flexible_destination=user_input.flexible_destination,
        )

        logger.info(f"[Orchestrator] Complete plan generated for {user_input.destination}")
        return final_plan

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Orchestrator] Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
