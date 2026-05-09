from __future__ import annotations
import json

from fastapi import HTTPException
from loguru import logger

from agent_experience import fetch_image_for_activity
from local_llm import generate_local_json, local_model_name
from models import Activity


REGENERATE_SYSTEM_PROMPT = """
You are VibeTrips' local Activity Regeneration Agent. You run locally and must not call hosted AI APIs.
Replace exactly one rejected itinerary activity with a fresh alternative that fits the same day and vibe.

Return exactly one valid JSON object:
{
  "title": "string",
  "description": "string",
  "time": "string",
  "cost": "string",
  "location": "string",
  "image_url": "",
  "type": "experience"
}

Rules:
- Output raw JSON only. No markdown, commentary, XML, or function calls.
- Do not duplicate the rejected activity or the existing activities in the same day.
- Keep type within: experience, dining, tour, cruise, cookingclass, festival, adventure, culture,
  relaxation, shopping, nightlife, transport, sightseeing, museum, landmark, park, beach.
- Keep image_url empty; the backend scraper fills it later.
"""


def _fallback_activity(vibe_summary: str, day_context: str, destination: str, old_activity_json: str) -> Activity:
    city = (destination or "the destination").split(",")[0].strip()
    try:
        old_activity = json.loads(old_activity_json)
        old_time = old_activity.get("time", "Afternoon")
    except Exception:
        old_time = "Afternoon"

    return Activity(
        title=f"Alternative local highlight in {city}",
        description=(
            f"Swap in a different local experience that keeps the {vibe_summary or 'trip'} vibe, "
            f"avoids the already planned activities ({day_context}), and gives the group a fresh option."
        ),
        time=old_time,
        cost="Moderate",
        location=f"{city} local district",
        image_url="",
        type="experience",
    )


async def regenerate_single_activity(
    vibe_summary: str,
    day_context: str,
    destination: str,
    old_activity_json: str,
) -> Activity:
    """Generate one replacement activity locally and enrich it with a keyless scraped image."""
    try:
        logger.info(f"Regenerating activity locally for: {destination}")
        prompt = (
            f"Destination: {destination}\n"
            f"Overall vibe: {vibe_summary}\n"
            f"Existing activities in this day, do not duplicate: {day_context}\n"
            f"Rejected activity to replace:\n{old_activity_json}\n\n"
            "Provide a fresh, different replacement activity as raw JSON."
        )

        try:
            data = await generate_local_json(REGENERATE_SYSTEM_PROMPT, prompt, timeout=90, temperature=0.55)
            parsed = Activity(**data)
            logger.info(f"Local regeneration agent completed with model {local_model_name()}.")
        except Exception as exc:
            logger.warning(f"Local regeneration agent unavailable or invalid; using fallback. {exc}")
            parsed = _fallback_activity(vibe_summary, day_context, destination, old_activity_json)

        image_url = await fetch_image_for_activity(parsed.title, destination)
        return parsed.model_copy(update={"image_url": image_url})

    except Exception as exc:
        logger.error(f"Activity regeneration failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Regeneration error: {str(exc)}")
