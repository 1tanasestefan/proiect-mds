import warnings
import os
import asyncio
import json
import re
from urllib.parse import quote_plus, urlparse
from dotenv import load_dotenv

# Absolute first thing: silence the DDGS rename warning
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*renamed to ddgs.*")

from pydantic_ai import Agent, RunContext
from duckduckgo_search import DDGS
from models import UserInput, AgentOneOutput
from loguru import logger
from fastapi import HTTPException

# Global lock to strictly serialize searches and prevent rate limiting/hangs
search_lock = asyncio.Lock()

load_dotenv()

def _unsplash_source_url(query: str) -> str:
    # Reliable, hotlink-friendly image source that works well in the browser.
    return f"https://source.unsplash.com/1600x900/?{quote_plus(query)}"

def _normalize_image_url(url: str | None, *, query: str) -> str:
    """Return a browser-loadable https image URL (falls back to Unsplash source)."""
    if not url or not isinstance(url, str):
        return _unsplash_source_url(query)

    cleaned = url.strip().strip('"').strip("'")
    if not cleaned or cleaned == "RECOVERED_URL" or "example.com" in cleaned:
        return _unsplash_source_url(query)

    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return _unsplash_source_url(query)

    # Try to upgrade http to https where possible.
    if parsed.scheme == "http":
        cleaned = "https://" + cleaned[len("http://") :]

    return cleaned

# We use output_type=str for compatibility and handle parsing manually to recover from hallucinations.
experience_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=str,
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', a premier Travel Concierge. "
        "Your mission is to provide an authentic, high-end 3-day itinerary for the specified destination. "

        "CRITICAL RULES: "
        "1. MISSION: Discover REAL venues and REAL images. "
        "2. FLOW: You MUST use `search_web` for venues and `search_images` for EVERY venue. "
        "3. OUTPUT: Output ONLY a single valid JSON block. NO conversational filler, NO meta-tags like <function>. "
        "4. NO HALLUCINATIONS: Do NOT write things like '<function=search_images>...' in the output. Perform the search and put the REAL URL in the `image_url` field. "
        "5. Structure: "
        "{"
        "  \"trip_title\": \"...\", "
        "  \"vibe_summary\": \"...\", "
        "  \"itinerary\": ["
        "    {"
        "      \"day_number\": 1, "
        "      \"activities\": ["
        "        {\"title\": \"...\", \"description\": \"...\", \"time\": \"...\", \"cost\": \"...\", \"location\": \"...\", \"image_url\": \"...\", \"type\": \"experience\"}"
        "      ]"
        "    }"
        "  ]"
        "}"
    ),
)

def _parse_itinerary_json(raw: str) -> AgentOneOutput:
    """Extract and validate the JSON block, recovering from tool hallucinations."""
    logger.debug(f"Parsing raw agent output (length: {len(raw)})")
    
    # Hallucination Recovery: Strip any <function>... fragments the AI might have shard into the output
    # Example: "image_url": <function=search_images>{"query": "..."}</function> -> "image_url": "PLACEHOLDER"
    # We first try to clean up these to make it valid JSON
    cleaned = re.sub(r"<function.*?>.*?</function>", '"RECOVERED_URL"', raw)
    # Also strip markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()
    
    decoder = json.JSONDecoder()
    pos = 0
    found_any = False
    
    while True:
        match_pos = cleaned.find('{', pos)
        if match_pos == -1:
            break
        
        try:
            data, index = decoder.raw_decode(cleaned[match_pos:])
            found_any = True
            
            # Specifically check for our expected root keys
            if isinstance(data, dict) and "trip_title" in data and "itinerary" in data:
                logger.info("VALID ITINERARY JSON FOUND AFTER RECOVERY.")
                return AgentOneOutput(**data)
            
            pos = match_pos + index
        except (json.JSONDecodeError, ValueError):
            pos = match_pos + 1
            
    if not found_any:
        logger.error(f"NO JSON OBJECTS FOUND. Raw: {raw[:500]}...")
    else:
        logger.error(f"Found JSON blocks but none were valid itineraries. Raw sample: {cleaned[:500]}...")
        
    raise ValueError("No valid itinerary JSON block found in agent output.")

@experience_agent.tool
async def search_web(ctx: RunContext[UserInput], query: str) -> str:
    """Search the web using DDGS in a thread-safe serialized way."""
    async with search_lock:
        try:
            logger.info(f"Initiating search: {query}")
            def run_sync_search():
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=5))
            results = await asyncio.wait_for(asyncio.to_thread(run_sync_search), timeout=15)
            if not results: return "No results found."
            return "\n\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
        except Exception as e:
            logger.error(f"Search tool error: {e}")
            return "Search tool unavailable."

@experience_agent.tool
async def search_images(ctx: RunContext[UserInput], query: str) -> str:
    """Return a reliable image URL for the browser (Unsplash source)."""
    # Many arbitrary image hosts block hotlinking; this keeps the UI reliable.
    return _unsplash_source_url(query)

async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """Entry point for itinerary generation."""
    try:
        logger.info(f"Starting itinerary generation for: {user_input.destination}")
        result = await asyncio.wait_for(
            experience_agent.run(
                f"Create a 3-day itinerary for {user_input.destination}. "
                f"Lifestyle: {user_input.lifestyle}, Budget: {user_input.budget}, Vibe: {user_input.vacationType}. "
                "Output ONLY raw JSON.",
                deps=user_input
            ),
            timeout=120
        )
        logger.debug(f"RAW AGENT OUTPUT:\n{result.output}")
        parsed = _parse_itinerary_json(result.output)

        # Ensure every activity has a loadable image URL to prevent broken UI cards.
        normalized_days = []
        for day in parsed.itinerary:
            normalized_acts = []
            for act in day.activities:
                q = f"{user_input.destination} {act.title}"
                normalized_acts.append(
                    act.model_copy(update={"image_url": _normalize_image_url(act.image_url, query=q)})
                )
            normalized_days.append(day.model_copy(update={"activities": normalized_acts}))

        return parsed.model_copy(update={"itinerary": normalized_days})
    except Exception as e:
        logger.error(f"Itinerary generation failed: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
