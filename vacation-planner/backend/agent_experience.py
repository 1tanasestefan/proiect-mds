import asyncio
from time import monotonic

from ddgs import DDGS
from fastapi import HTTPException
from loguru import logger

from local_llm import generate_local_json, local_model_name
from models import Activity, AgentOneOutput, DailyItinerary, UserInput

STATIC_FALLBACK = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1000&q=80"

search_lock = asyncio.Lock()
_last_image_search = 0.0
_IMAGE_SEARCH_COOLDOWN = 0.3
_image_search_available = True


EXPERIENCE_SYSTEM_PROMPT = """
You are VibeTrips' local Experience Guide agent. You run fully locally and do not call paid or hosted AI APIs.
Create authentic, practical, destination-aware vacation itineraries from the user's constraints.

Return exactly one valid JSON object with this schema:
{
  "trip_title": "string",
  "vibe_summary": "string",
  "itinerary": [
    {
      "day_number": 1,
      "activities": [
        {
          "title": "string",
          "description": "string",
          "time": "string",
          "cost": "string",
          "location": "string",
          "image_url": "",
          "type": "experience"
        }
      ]
    }
  ]
}

Rules:
- Output raw JSON only. No markdown, commentary, XML, or function calls.
- Generate exactly 3 activities per day.
- Keep activity types within: experience, dining, tour, cruise, cookingclass, festival, adventure, culture,
  relaxation, shopping, nightlife, transport, arrival, departure, flight, hotel, sightseeing, museum,
  landmark, park, beach.
- Keep image_url as an empty string. The backend web image scraper fills it later.
- Avoid generic filler like "explore the city"; name concrete neighborhoods, landmarks, markets, museums,
  restaurants, waterfronts, parks, or local experiences.
"""


def _is_valid_image(url: str) -> bool:
    if not url:
        return False
    low = url.lower()
    blocked = ("wikipedia", "wikimedia", "foursquare", "tripadvisor", "svg", "icon", "logo")
    if any(item in low for item in blocked):
        return False
    return any(ext in low for ext in (".jpg", ".jpeg", ".png", ".webp"))


def _search_image_sync(query: str) -> str | None:
    with DDGS() as ddgs:
        results = ddgs.images(query, max_results=8, safesearch="moderate")
        for item in results:
            candidate = item.get("image") or item.get("thumbnail")
            if _is_valid_image(candidate):
                return candidate
    return None


def _search_destination_context_sync(query: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5, safesearch="moderate")
    snippets = []
    for item in results[:5]:
        title = item.get("title") or "Result"
        body = item.get("body") or item.get("snippet") or ""
        href = item.get("href") or item.get("url") or ""
        snippets.append(f"- {title}: {body} ({href})")
    return "\n".join(snippets)


async def fetch_destination_web_context(destination: str, vibe: str) -> str:
    """Collect a compact keyless web-search context for the local model."""
    query = f"{destination} best things to do neighborhoods food culture {vibe} travel"
    try:
        return await asyncio.to_thread(_search_destination_context_sync, query)
    except Exception as exc:
        logger.warning(f"[search] Destination context search failed for '{query}': {exc}")
        return "No live web context available; rely on local travel knowledge."


async def fetch_image_for_activity(activity_name: str, destination: str) -> str:
    """
    Fetch an activity image through DuckDuckGo image search.

    This keeps image enrichment keyless. If search fails or returns blocked links,
    the UI still gets a stable fallback image.
    """
    global _image_search_available, _last_image_search
    if not _image_search_available:
        return STATIC_FALLBACK

    query = f"{activity_name} {destination} travel photo"

    async with search_lock:
        elapsed = monotonic() - _last_image_search
        if elapsed < _IMAGE_SEARCH_COOLDOWN:
            await asyncio.sleep(_IMAGE_SEARCH_COOLDOWN - elapsed)
        _last_image_search = monotonic()

        try:
            image_url = await asyncio.to_thread(_search_image_sync, query)
            if image_url:
                logger.info(f"[img] Found keyless DDGS image for '{query}'")
                return image_url
        except Exception as exc:
            logger.warning(f"[img] DDGS image search failed for '{query}': {exc}")
            _image_search_available = False

    return STATIC_FALLBACK


def _fallback_experience(user_input: UserInput) -> AgentOneOutput:
    destination = user_input.destination or "the destination"
    city = destination.split(",")[0].strip()
    vibe = user_input.vacationType or user_input.lifestyle or "balanced"
    budget = user_input.budget or "medium"
    days: list[DailyItinerary] = []

    for day_number in range(1, user_input.trip_days + 1):
        activities = [
            Activity(
                title=f"{city} orientation walk",
                description=f"Start with a walk through the most central area of {city}, using it to understand the rhythm, transport links, and nearby food options.",
                time="Morning",
                cost="Free to low cost",
                location=f"Central {city}",
                image_url="",
                type="sightseeing",
            ),
            Activity(
                title=f"Local food stop in {city}",
                description=f"Choose a well-reviewed local market, bistro, or casual restaurant that fits a {budget} budget and gives the group a strong first taste of the destination.",
                time="Lunch",
                cost="Moderate",
                location=f"{city} food district",
                image_url="",
                type="dining",
            ),
            Activity(
                title=f"{vibe.title()} highlight experience",
                description=f"Spend the afternoon on an experience matched to the trip vibe: culture, waterfront time, nightlife scouting, museums, shopping streets, or a scenic viewpoint.",
                time="Afternoon",
                cost="Varies",
                location=f"{city} highlights",
                image_url="",
                type="experience",
            ),
            Activity(
                title=f"Evening in {city}",
                description="End the day with a relaxed dinner or evening walk in an active but safe area close to the accommodation.",
                time="Evening",
                cost="Moderate",
                location=f"{city} evening district",
                image_url="",
                type="nightlife",
            ),
        ]
        days.append(DailyItinerary(day_number=day_number, activities=activities))

    return AgentOneOutput(
        trip_title=f"{city} {vibe.title()} Escape",
        vibe_summary=f"A {user_input.trip_days}-day {vibe} itinerary for {destination}, tuned for a {budget} budget and {user_input.travelers} traveler(s).",
        itinerary=days,
    )


async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """Generate itinerary locally, then enrich every activity with a keyless scraped image."""
    try:
        logger.info(f"Starting local itinerary generation for: {user_input.destination}")
        web_context = await fetch_destination_web_context(
            user_input.destination or "",
            user_input.vacationType or user_input.lifestyle or "",
        )
        compact_web_context = web_context[:1200]
        user_prompt = (
            f"Create a {user_input.trip_days}-day itinerary.\n"
            f"Destination: {user_input.destination}\n"
            f"Travel dates: {user_input.start_date} to {user_input.end_date}\n"
            f"Origin: {user_input.origin}\n"
            f"Travelers: {user_input.travelers}\n"
            f"Lifestyle: {user_input.lifestyle}\n"
            f"Vacation type / vibe: {user_input.vacationType}\n"
            f"Budget tier: {user_input.budget}\n"
            f"Price range per person: {user_input.price_range_per_person or 'not specified'}\n"
            f"Keyless web-search context:\n{compact_web_context}\n"
            "Remember: raw JSON only."
        )

        try:
            data = await generate_local_json(
                EXPERIENCE_SYSTEM_PROMPT,
                user_prompt,
                timeout=90,
                temperature=0.35,
                num_predict=1300,
            )
            parsed = AgentOneOutput(**data)
            logger.info(f"Local experience agent completed with model {local_model_name()}.")
        except Exception as exc:
            logger.warning(f"Local experience agent unavailable or invalid; using deterministic fallback. {exc}")
            parsed = _fallback_experience(user_input)

        normalized_days = []
        for day in parsed.itinerary:
            image_tasks = [
                fetch_image_for_activity(act.title, user_input.destination or "")
                for act in day.activities
            ]
            image_urls = await asyncio.gather(*image_tasks)
            normalized_acts = [
                act.model_copy(update={"image_url": image_url})
                for act, image_url in zip(day.activities, image_urls)
            ]
            normalized_days.append(day.model_copy(update={"activities": normalized_acts}))

        return parsed.model_copy(update={"itinerary": normalized_days})

    except Exception as exc:
        logger.error(f"Itinerary generation failed: {exc}")
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=str(exc))
