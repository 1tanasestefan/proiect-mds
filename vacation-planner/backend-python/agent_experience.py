import warnings
import os
import asyncio
import json
import re
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

# output_type=str avoids registering a `final_result` tool which conflicts with
# the `search_web` tool on Groq and triggers tool_use_failed errors.
# We parse and validate the JSON manually after the run.
experience_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=str,
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', a premier Luxury Travel Concierge. "
        "Your mission is to provide an authentic, high-end itinerary for the specified destination. "

        "CRITICAL RULES: "
        "1. NEVER use placeholder text. Find REAL venue names using the `search_web` tool. "
        "2. You MUST use the `search_web` tool for every request to find current restaurants, hotels, and spots. "
        "3. Your ONLY output must be a single valid JSON block. No conversational filler, no markdown fences, no explanations. "
        "4. Every activity 'type' MUST be exactly 'experience'. "
        "5. The output MUST exactly match this structure: "
        "{"
        "  \"trip_title\": \"Catchy Title\", "
        "  \"vibe_summary\": \"Overall summary of the trip matched to user\", "
        "  \"itinerary\": ["
        "    {"
        "      \"day_number\": 1, "
        "      \"activities\": ["
        "        {"
        "          \"title\": \"Venue Name\", "
        "          \"description\": \"Specific description based on REAL venue details\", "
        "          \"time\": \"Morning/Afternoon/Evening\", "
        "          \"cost\": \"Estimated cost in local currency or relative range\", "
        "          \"location\": \"Specific neighborhood or address\", "
        "          \"type\": \"experience\""
        "        }"
        "      ]"
        "    }"
        "  ]"
        "}"
    ),
)


def _parse_itinerary_json(raw: str) -> AgentOneOutput:
    """Extract and validate the JSON block from the agent's raw string output."""
    # Strip markdown code fences if the model wrapped the output anyway
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    # Find the outermost { ... } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in agent output.")
    data = json.loads(match.group())
    return AgentOneOutput(**data)

@experience_agent.tool
async def search_web(ctx: RunContext[UserInput], query: str) -> str:
    """
    Search the web using DDGS in a thread-safe serialized way using asyncio.to_thread.
    """
    async with search_lock:
        try:
            logger.info(f"Initiating search: {query}")
            
            def run_sync_search():
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=5))

            # Individual search timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.to_thread(run_sync_search),
                    timeout=15
                )
            except asyncio.TimeoutError:
                logger.warning(f"Search timed out for query: {query}")
                return "Search was taking too long. Use iconic landmarks iconic to that specific city instead."

            if not results:
                logger.warning(f"No results found for query: {query}")
                return "No search results found. Proceed with iconic local landmark names for this destination."
                
            context_str = ""
            for r in results:
                context_str += f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nURL: {r.get('href')}\n\n"
            
            logger.info(f"Search completed successfully for: {query}")
            return context_str
            
        except Exception as e:
            logger.error(f"Search tool encountered an error: {e}")
            return "Search tool is temporarily unavailable. Use well-known highlights for this destination."

async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """
    Main entry point for itinerary generation with a global time safety boundary.
    """
    try:
        logger.info(f"Starting itinerary generation for: {user_input.destination}")

        # Total generation budget: 90 seconds
        result = await asyncio.wait_for(
            experience_agent.run(
                f"Create a REAL 3-day itinerary for {user_input.destination}. "
                f"Lifestyle: {user_input.lifestyle}, Budget: {user_input.budget}, Vibe: {user_input.vacationType}. "
                f"Group size: {user_input.travelers}. Use `search_web` for REAL venues. "
                "REMINDER: Output ONLY a raw JSON object — no markdown, no explanation.",
                deps=user_input
            ),
            timeout=90
        )

        logger.info(f"Successfully generated itinerary for {user_input.destination}")
        return _parse_itinerary_json(result.output)

    except asyncio.TimeoutError:
        logger.error(f"Generation timed out for {user_input.destination}")
        raise HTTPException(
            status_code=504,
            detail="The concierge is taking longer than usual. Please try again or choose a more major city."
        )
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON parse/validation failed: {e}")
        raise HTTPException(status_code=500, detail="The AI returned an unreadable itinerary. Please try again.")
    except Exception as e:
        logger.error(f"Itinerary generation failed: {e}")
        if isinstance(e, HTTPException):
            raise e
        detail = str(e)
        if "retries" in detail.lower():
            detail = "The AI had trouble formatting your itinerary. Please try one more time."
        raise HTTPException(status_code=500, detail=detail)
