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
    output_type=str,  # str avoids pydantic-ai injecting a second `final_result` tool which Groq rejects
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', a premier Travel Concierge. "
        "Your mission is to provide an authentic, high-end itinerary for the specified destination. "
        "The number of days will be specified in the user prompt. "

        "CRITICAL OUTPUT RULES: "
        "1. Your ENTIRE response must be a single valid JSON object — no markdown fences, no prose. "
        "2. The root JSON object MUST have exactly these three top-level keys: "
        "   'trip_title' (string), 'vibe_summary' (string), 'itinerary' (array of day objects). "
        "   Do NOT wrap them inside a 'trip', 'data', 'result', or any other key. "
        "3. Each day object: { 'day_number': int, 'activities': [ ... ] }. "
        "4. Each activity: { 'title', 'description', 'time', 'cost', 'location', 'image_url': '', 'type': 'experience' }. "
        "5. You MAY use `search_web` at most ONCE to look up a venue. Do NOT call it more than once. "
        "6. After any tool use, respond IMMEDIATELY with the full JSON — no further tool calls. "
        "7. Do NOT include any text before or after the JSON object."
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


async def fetch_image_for_activity(activity_name: str, destination: str, activity_type: str) -> str:
    """
    Sniper-architecture image fetcher.
    1. Anti-rate-limit jitter delay at entry.
    2. 3-tier query cascade (Hyper-Specific → Broad → City Aesthetic).
    3. URL quality validator rejects blocklisted/non-image URLs.
    4. Returns the FIRST valid URL found — Unsplash fallback only if all tiers fail.
    """
    global _last_ddgs_time

    # --- Anti-Rate-Limit: randomised entry delay ---
    jitter = random.uniform(1.0, 2.5)
    logger.debug(f"[img] Jitter delay {jitter:.2f}s before fetching '{activity_name}'")
    await asyncio.sleep(jitter)

    # --- 3-Tier query cascade ---
    tiers = [
        ("Tier-1 (Hyper-Specific)", f"{activity_name} {destination} photo high quality"),
        ("Tier-2 (Broad/Contextual)", f"{activity_name} {destination}"),
        ("Tier-3 (City Aesthetic)",   f"{destination} beautiful travel photography"),
    ]

    async with search_lock:
        # Honour the global cooldown on top of jitter
        now = time.monotonic()
        elapsed = now - _last_ddgs_time
        if elapsed < _DDGS_COOLDOWN:
            wait = _DDGS_COOLDOWN - elapsed
            logger.debug(f"[img] Cooldown: waiting an additional {wait:.2f}s")
            await asyncio.sleep(wait)

        for tier_name, query in tiers:
            logger.debug(f"[img] {tier_name} — query: '{query}'")
            try:
                def _run(q=query):
                    with DDGS() as ddgs:
                        return list(ddgs.images(keywords=q, max_results=3, safesearch="moderate"))

                results = await asyncio.wait_for(asyncio.to_thread(_run), timeout=15)
                _last_ddgs_time = time.monotonic()

                if not results:
                    logger.debug(f"[img] {tier_name} returned 0 results — trying next tier.")
                    continue

                for r in results:
                    img_url = r.get("image", "")
                    if _is_valid_image(img_url):
                        logger.info(f"[img] ✅ '{activity_name}' [{tier_name}] -> {img_url[:80]}")
                        return img_url
                    else:
                        logger.debug(f"[img] Rejected by validator: {img_url[:60]}")

                logger.debug(f"[img] {tier_name} — no URLs passed the validator, trying next tier.")

            except Exception as e:
                _last_ddgs_time = time.monotonic()
                logger.warning(f"[img] {tier_name} threw exception: {e} — trying next tier.")

    # --- Ultimate Failsafe ---
    logger.warning(f"[img] All 3 tiers failed for '{activity_name}'. Returning Unsplash fallback.")
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

            # Unwrap any single-key envelope (e.g. {"trip": {...}}, {"result": {...}})
            if data and "trip_title" not in data and len(data) == 1:
                inner = next(iter(data.values()))
                if isinstance(inner, dict) and "trip_title" in inner:
                    logger.info(f"Unwrapping envelope key: '{next(iter(data.keys()))}'")
                    data = inner

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
