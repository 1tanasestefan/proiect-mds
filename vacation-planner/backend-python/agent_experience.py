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
    output_type=AgentOneOutput, # Use Pydantic model for native structured output
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', a premier Travel Concierge. "
        "Your mission is to provide an authentic, high-end itinerary for the specified destination. "
        "The number of days will be specified in the user prompt. "

        "CRITICAL RULES: "
        "1. You MUST use any available tools (like `search_web`) to find REAL, existing place names, venues, and neighborhoods. "
        "2. Do NOT hallucinate venue names; if search fails, use well-known landmarks. "
        "3. Every activity `type` MUST be exactly `experience`. "
        "4. Set all `image_url` fields to an empty string (they are enriched by the backend search). "
        "5. Respond with a perfectly structured trip plan matching the required schema."
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
                f"Lifestyle: {user_input.lifestyle}, Budget: {user_input.budget}, "
                f"Vibe: {user_input.vacationType}.",
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
                
            parsed = AgentOneOutput(**data)

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
