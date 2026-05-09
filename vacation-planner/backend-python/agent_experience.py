import warnings
import os
import asyncio
import json
import re
import random
import httpx
from dotenv import load_dotenv
from pydantic_ai import Agent
from models import UserInput, AgentOneOutput
from loguru import logger
from fastapi import HTTPException

# Global lock to serialize searches
search_lock = asyncio.Lock()

load_dotenv()

# The ONE AND ONLY fallback image
STATIC_FALLBACK = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1000&q=80"

# Cooldown between DDGS image requests (seconds)
_last_ddgs_time = 0.0
_DDGS_COOLDOWN = 3.0


# ---------- AGENT DEFINITION ----------
experience_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=str,  # str avoids pydantic-ai injecting a second `final_result` tool which Groq rejects
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', a premier Travel Concierge. "
        "Your mission is to provide an authentic, high-end itinerary for the specified destination. "
        "The number of days will be specified in the user prompt. "

        "CRITICAL OUTPUT RULES: "
        "1. Your ENTIRE response must be a single valid JSON object — no markdown fences, no prose, no commentary. "
        "2. The root JSON object MUST have exactly these three top-level keys: "
        "   'trip_title' (string), 'vibe_summary' (string), 'itinerary' (array of day objects). "
        "   Do NOT wrap them inside a 'trip', 'data', 'result', or any other key. "
        "3. Each day object: { 'day_number': int, 'activities': [ ... ] }. "
        "4. Each activity: { 'title', 'description', 'time', 'cost', 'location', 'image_url': '', 'type': 'experience' }. "
        "   Allowed types: 'experience', 'dining', 'tour', 'cruise', 'cookingclass', 'festival', 'adventure', 'culture', 'relaxation', 'shopping', 'nightlife', 'transport', 'arrival', 'departure', 'flight', 'hotel', 'sightseeing', 'museum', 'landmark', 'park', 'beach'. "
        "   If unsure, use 'experience'. "
        "5. UNIQUENESS IS MANDATORY: Every activity title across ALL days must be completely unique. "
        "   NEVER repeat the same activity, place, restaurant, or attraction on different days. "
        "   Before writing each new activity, mentally verify it has not appeared on any previous day. "
        "6. You have NO tools available. Do NOT output function calls, XML tags, or <function=...> syntax. "
        "7. Use your own extensive knowledge of the destination. Begin your response with '{' immediately."
    ),
)


# ---------- IMAGE FETCHER — "SNIPER" ARCHITECTURE ----------

def _is_valid_image(url: str) -> bool:
    """
    Returns True only if the URL points to an actual hotlink-safe image file.
    Rejects sites known to block hotlinking and non-image extensions.
    """
    if not url:
        return False
    low = url.lower()

    # Blocklist: sites that do not allow hotlinking or won't resolve to a raw image
    BLOCKED_DOMAINS = ("wikipedia", "wikimedia", "foursquare", "tripadvisor")
    BLOCKED_PATTERNS = ("svg", "icon", "logo")
    for blocked in BLOCKED_DOMAINS + BLOCKED_PATTERNS:
        if blocked in low:
            return False

    # Allowlist: must contain a valid image extension
    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
    return any(ext in low for ext in VALID_EXTENSIONS)


def _pick_photo(photos: list) -> str:
    """Pick from top 3 results for relevance, with slight variety."""
    pool = photos[:3] if len(photos) >= 3 else photos
    return random.choice(pool)["src"]["large"]


async def fetch_image_for_activity(activity_name: str, destination: str, activity_type: str = "") -> str:
    """
    3-tier query strategy for accurate, activity-specific images:
      1. "{activity_name} {destination}"  — most specific
      2. "{activity_name}"                — activity without location
      3. "{activity_type} {destination}"  — type-based fallback
    Picks from top 3 results to balance relevance and variety.
    """
    pexels_key = os.getenv("PEXELS_API_KEY")
    if not pexels_key:
        logger.warning("[img] PEXELS_API_KEY not found in .env, returning fallback.")
        return STATIC_FALLBACK

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": pexels_key}

    # Map activity types to better search terms
    TYPE_SEARCH_MAP = {
        "dining": "restaurant food dining",
        "nightlife": "nightlife bar cocktails",
        "tour": "city tour sightseeing",
        "cruise": "boat cruise sea",
        "cookingclass": "cooking class food",
        "festival": "festival celebration crowd",
        "adventure": "adventure outdoor sport",
        "culture": "culture museum art",
        "relaxation": "spa relaxation wellness",
        "shopping": "shopping market street",
        "beach": "beach sea waves",
        "museum": "museum art gallery",
        "landmark": "landmark monument famous",
        "park": "nature park garden",
        "sightseeing": "sightseeing tourist attraction",
    }
    type_term = TYPE_SEARCH_MAP.get(activity_type.lower(), activity_type)

    queries = [
        f"{activity_name} {destination}",
        activity_name,
        f"{type_term} {destination}" if type_term else None,
    ]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for query in queries:
                if not query:
                    continue
                params = {"query": query, "per_page": 5, "orientation": "landscape"}
                response = await client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    photos = response.json().get("photos", [])
                    if photos:
                        img_url = _pick_photo(photos)
                        logger.info(f"[img] ✅ Pexels '{query}' -> {img_url[:60]}")
                        return img_url
                logger.debug(f"[img] No results for query: '{query}'")

    except Exception as e:
        logger.error(f"[img] Pexels API request failed: {e}")

    logger.warning(f"[img] All Pexels attempts failed for '{activity_name}'. Returning fallback.")
    return STATIC_FALLBACK




# ---------- MAIN ENTRY POINT ----------
async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """Generate itinerary then enrich every activity with a real image."""
    try:
        logger.info(f"Starting itinerary generation for: {user_input.destination}")

        result = await asyncio.wait_for(
            experience_agent.run(
                f"Create a {user_input.trip_days}-day itinerary for {user_input.destination}. "
                f"Travel dates: {user_input.start_date} to {user_input.end_date}. "
                f"Origin: {user_input.origin}. "
                f"Lifestyle: {user_input.lifestyle}, Budget tier: {user_input.budget}, "
                f"Price range per person: {user_input.price_range_per_person or 'not specified'}, "
                f"Vibe: {user_input.vacationType}. "
                f"IMPORTANT: Each of the {user_input.trip_days} days MUST have completely different activities. "
                f"Do NOT repeat any activity, venue, restaurant, or attraction across different days. "
                f"Every day must explore a different area or theme within {user_input.destination}.",
                deps=user_input
            ),
            timeout=180 # Increased timeout for tool-calling loops
        )

        # 1. Access the output. It might be a model (if pydantic-ai worked) or a string (older versions)
        output_obj = getattr(result, 'output', result)
        
        if isinstance(output_obj, AgentOneOutput):
            logger.info("Agent provided structured data directly as AgentOneOutput.")
            parsed = output_obj
        else:
            raw_text = str(output_obj)
            logger.debug(f"Raw Agent Output (length {len(raw_text)}): {raw_text[:200]}...")

            # 2. Bulletproof JSON Extraction
            def extract_json(text: str):
                match = re.search(r"(\{.*\})", text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        pass
                cleaned = re.sub(r"```(json)?", "", text).strip()
                cleaned = re.sub(r"<function.*?>.*?</function>", "", cleaned, flags=re.DOTALL).strip()
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    return None

            data = extract_json(raw_text)
            if not data:
                logger.error(f"Failed to extract JSON from: {raw_text}")
                raise ValueError("No valid JSON found in agent output.")

            # Unwrap any single-key envelope (e.g. {"trip": {...}}, {"result": {...}})
            if data and "trip_title" not in data and len(data) == 1:
                inner = next(iter(data.values()))
                if isinstance(inner, dict) and "trip_title" in inner:
                    logger.info(f"Unwrapping envelope key: '{next(iter(data.keys()))}'")
                    data = inner

            parsed = AgentOneOutput(**data)

        # --- DEDUPLICATION: remove activities whose title already appeared on a previous day ---
        seen_titles: set[str] = set()
        deduped_days = []
        for day in parsed.itinerary:
            unique_acts = []
            for act in day.activities:
                key = act.title.strip().lower()
                if key not in seen_titles:
                    seen_titles.add(key)
                    unique_acts.append(act)
                else:
                    logger.warning(f"[dedup] Removed duplicate activity '{act.title}' on day {day.day_number}")
            deduped_days.append(day.model_copy(update={"activities": unique_acts}))
        parsed = parsed.model_copy(update={"itinerary": deduped_days})

        # --- IMAGE ENRICHMENT (DDGS ONLY) ---
        logger.info("Starting image enrichment (DDGS only)...")
        normalized_days = []
        for day in parsed.itinerary:
            normalized_acts = []
            for act in day.activities:
                img_url = await fetch_image_for_activity(
                    activity_name=act.title,
                    destination=user_input.destination,
                    activity_type=getattr(act, "type", "")
                )
                normalized_acts.append(
                    act.model_copy(update={"image_url": img_url})
                )
            normalized_days.append(
                day.model_copy(update={"activities": normalized_acts})
            )

        logger.info("Image enrichment complete.")
        return parsed.model_copy(update={"itinerary": normalized_days})

    except Exception as e:
        logger.error(f"Itinerary generation failed: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
