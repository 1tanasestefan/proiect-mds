import warnings
import os
import asyncio
import json
import re
import random
import time
from urllib.parse import quote_plus, urlparse
from dotenv import load_dotenv

# Silence the DDGS rename warning
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*renamed to ddgs.*")

from pydantic_ai import Agent, RunContext
from duckduckgo_search import DDGS
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
    output_type=str,
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', a premier Travel Concierge. "
        "Your mission is to provide an authentic, high-end 3-day itinerary for the specified destination. "

        "CRITICAL RULES: "
        "1. You MUST use `search_web` to find REAL place names. "
        "2. Set `image_url` to an empty string for every activity. Images are handled by the backend. "
        "3. Output ONLY a single valid JSON block. NO text before or after. "
        "4. Every activity `type` MUST be exactly `experience`. "
        "5. Structure: "
        "{"
        "  \"trip_title\": \"...\", "
        "  \"vibe_summary\": \"...\", "
        "  \"itinerary\": ["
        "    {"
        "      \"day_number\": 1, "
        "      \"activities\": ["
        "        {\"title\": \"REAL Venue Name\", \"description\": \"...\", \"time\": \"...\", \"cost\": \"...\", \"location\": \"...\", \"image_url\": \"\", \"type\": \"experience\"}"
        "      ]"
        "    }"
        "  ]"
        "}"
    ),
)


# ---------- WEB SEARCH TOOL ----------
@experience_agent.tool
async def search_web(ctx: RunContext[UserInput], query: str) -> str:
    """Search the web for real venues and places."""
    async with search_lock:
        try:
            logger.info(f"[search_web] {query}")
            def run_sync():
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=5))
            results = await asyncio.wait_for(asyncio.to_thread(run_sync), timeout=15)
            if not results:
                return "No results found."
            return "\n\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
        except Exception as e:
            logger.error(f"[search_web] error: {e}")
            return "Search tool unavailable."


# ---------- IMAGE FETCHER (DDGS ONLY — NO WIKIPEDIA) ----------
async def fetch_image_for_activity(activity_name: str, destination: str, activity_type: str) -> str:
    """
    Fetch an image URL using DDGS().images() ONLY.
    - Single attempt, no retries, no secondary strategies.
    - Filters out wikipedia/wikimedia/svg results.
    - Returns static Unsplash fallback on ANY failure.
    """
    global _last_ddgs_time

    query = f"{activity_name} {destination} {activity_type} interior venue high quality"
    logger.debug(f"[img] DDGS query: '{query}'")

    async with search_lock:
        # Enforce cooldown
        now = time.monotonic()
        elapsed = now - _last_ddgs_time
        if elapsed < _DDGS_COOLDOWN:
            await asyncio.sleep(_DDGS_COOLDOWN - elapsed)

        try:
            def _run():
                with DDGS() as ddgs:
                    return list(ddgs.images(keywords=query, max_results=5, safesearch="moderate"))

            results = await asyncio.wait_for(asyncio.to_thread(_run), timeout=15)
            _last_ddgs_time = time.monotonic()

            if results:
                for r in results:
                    img_url = r.get("image", "")
                    if not img_url:
                        continue
                    low = img_url.lower()
                    # Quality gate: reject junk
                    if "wikipedia" in low or "wikimedia" in low or low.endswith(".svg"):
                        logger.debug(f"[img] Rejected (blocked domain/svg): {img_url[:60]}")
                        continue
                    # Valid image found
                    logger.info(f"[img] ✅ '{activity_name}' -> {img_url[:80]}")
                    return img_url

            # No valid results after filtering
            logger.warning(f"[img] No valid DDGS results for '{activity_name}', using static fallback.")
            return STATIC_FALLBACK

        except Exception as e:
            _last_ddgs_time = time.monotonic()
            logger.warning(f"[img] DDGS failed for '{activity_name}': {e}")
            return STATIC_FALLBACK


# ---------- JSON PARSER ----------
def _parse_itinerary_json(raw: str) -> AgentOneOutput:
    """Extract and validate the JSON block from agent output."""
    logger.debug(f"Parsing raw agent output (length: {len(raw)})")

    cleaned = re.sub(r"<function.*?>.*?</function>", '"RECOVERED_URL"', raw)
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

    decoder = json.JSONDecoder()
    pos = 0

    while True:
        match_pos = cleaned.find('{', pos)
        if match_pos == -1:
            break
        try:
            data, index = decoder.raw_decode(cleaned[match_pos:])
            if isinstance(data, dict) and "trip_title" in data and "itinerary" in data:
                logger.info("Valid itinerary JSON found.")
                return AgentOneOutput(**data)
            pos = match_pos + index
        except (json.JSONDecodeError, ValueError):
            pos = match_pos + 1

    logger.error(f"No valid itinerary JSON. Raw: {raw[:500]}")
    raise ValueError("No valid itinerary JSON block found in agent output.")


# ---------- MAIN ENTRY POINT ----------
async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """Generate itinerary then enrich every activity with a real image."""
    try:
        logger.info(f"Starting itinerary generation for: {user_input.destination}")

        result = await asyncio.wait_for(
            experience_agent.run(
                f"Create a 3-day itinerary for {user_input.destination}. "
                f"Lifestyle: {user_input.lifestyle}, Budget: {user_input.budget}, "
                f"Vibe: {user_input.vacationType}. Output ONLY raw JSON.",
                deps=user_input
            ),
            timeout=120
        )

        logger.debug(f"RAW AGENT OUTPUT:\n{result.output}")
        parsed = _parse_itinerary_json(result.output)

        # --- IMAGE ENRICHMENT (DDGS ONLY) ---
        logger.info("Starting image enrichment (DDGS only)...")
        normalized_days = []
        for day in parsed.itinerary:
            normalized_acts = []
            for act in day.activities:
                img_url = await fetch_image_for_activity(
                    activity_name=act.title,
                    destination=user_input.destination,
                    activity_type=act.type or "experience"
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
