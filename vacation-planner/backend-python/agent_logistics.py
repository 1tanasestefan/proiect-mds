import warnings
import asyncio
import json
import re
from urllib.parse import quote_plus
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*renamed to ddgs.*")

from pydantic_ai import Agent
from models import UserInput, AgentOneOutput, TripLogistics
from loguru import logger
from fastapi import HTTPException

load_dotenv()


# ── Deep-Link URL Builders (Date-Aware) ──────────────────────────

def build_skyscanner_link(origin: str, destination: str, start_date: str, end_date: str) -> str:
    """Construct a date-aware Skyscanner flight search deep-link."""
    origin_slug = quote_plus(origin.split(",")[0].strip().lower())
    dest_slug = quote_plus(destination.split(",")[0].strip().lower())
    # Skyscanner date format: YYMMDD
    start_short = start_date[2:].replace("-", "")  # 2026-03-25 → 260325
    end_short = end_date[2:].replace("-", "")
    return f"https://www.skyscanner.net/transport/flights/{origin_slug}/{dest_slug}/{start_short}/{end_short}/"


def build_booking_link(destination: str, start_date: str, end_date: str) -> str:
    """Construct a date-aware Booking.com search deep-link."""
    return (
        f"https://www.booking.com/searchresults.html"
        f"?ss={quote_plus(destination)}"
        f"&checkin={start_date}"
        f"&checkout={end_date}"
    )


def build_airbnb_link(destination: str, start_date: str, end_date: str) -> str:
    """Construct a date-aware Airbnb search deep-link."""
    return (
        f"https://www.airbnb.com/s/{quote_plus(destination)}/homes"
        f"?checkin={start_date}"
        f"&checkout={end_date}"
    )


# ── Agent 2: The Logistics & Booking Agent ───────────────────────
logistics_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=TripLogistics, # Use Pydantic model for native structured output
    retries=3,
    system_prompt=(
        "You are the 'Logistics Agent', an elite Travel Booking Advisor. "
        "You receive a user's travel constraints and a proposed itinerary. "
        "Your job is to provide REALISTIC cost estimates and booking recommendations.\n\n"

        "CRITICAL RULES:\n"
        "1. Analyze the user's budget level, origin city, travel dates, and the itinerary vibe to calibrate prices.\n"
        "2. Generate 2-3 flight options at different price tiers (Low Cost, Standard, Premium).\n"
        "3. Generate 2-3 accommodation options matched to neighborhoods from the itinerary.\n"
        "4. All prices must be in USD and REALISTIC for the route and destination.\n"
        "5. Do NOT invent fictional airlines. Use real airline categories (e.g., 'Wizz Air / Ryanair tier', 'Lufthansa / KLM tier').\n"
        "6. The total_estimated_budget_usd should include: mid-tier flight + mid-tier hotel for ALL nights + sum of activity costs.\n"
        "7. For booking_link fields, use EXACTLY the placeholder strings: "
        "\"SKYSCANNER_LINK\" for flights and \"BOOKING_LINK\" or \"AIRBNB_LINK\" for accommodations. "
        "The backend will replace these with real date-aware URLs.\n"
        "8. Return a perfectly structured logistics plan matching the required schema."
    ),
)


# ── JSON Parser ──────────────────────────────────────────────────



# ── Deep-Link Injection (Date-Aware) ─────────────────────────────

def _inject_booking_links(
    logistics: TripLogistics,
    user_input: UserInput,
) -> TripLogistics:
    """Replace placeholder strings with real date-aware deep-link URLs."""

    # 1. Inject flight links
    updated_flights = []
    for f in logistics.flights:
        link = f.booking_link
        if "SKYSCANNER" in link.upper():
            link = build_skyscanner_link(
                user_input.origin,
                user_input.destination,
                user_input.start_date,
                user_input.end_date,
            )
        updated_flights.append(f.model_copy(update={"booking_link": link}))

    # 2. Inject accommodation links
    updated_accom = []
    for a in logistics.accommodations:
        link = a.booking_link
        if not link:
            link = "BOOKING_LINK" # Fallback to default
            
        if "BOOKING" in link.upper():
            link = build_booking_link(
                user_input.destination,
                user_input.start_date,
                user_input.end_date,
            )
        elif "AIRBNB" in link.upper():
            link = build_airbnb_link(
                user_input.destination,
                user_input.start_date,
                user_input.end_date,
                )
        else:
            link = build_booking_link(
                user_input.destination,
                user_input.start_date,
                user_input.end_date,
            )
        updated_accom.append(a.model_copy(update={"booking_link": link}))

    return logistics.model_copy(update={
        "flights": updated_flights,
        "accommodations": updated_accom,
    })


# ── Main Entry Point ─────────────────────────────────────────────

async def generate_logistics(
    user_input: UserInput,
    itinerary: AgentOneOutput,
) -> TripLogistics:
    """
    Run Agent 2 to generate logistics & booking recommendations.
    Takes Agent 1's output as additional context.
    """
    try:
        itinerary_summary = json.dumps(itinerary.model_dump(), indent=2, default=str)

        prompt = (
            f"User constraints:\n"
            f"  Origin City: {user_input.origin}\n"
            f"  Destination: {user_input.destination}\n"
            f"  Travel Dates: {user_input.start_date} to {user_input.end_date} ({user_input.trip_days} nights)\n"
            f"  Budget: {user_input.budget}\n"
            f"  Lifestyle: {user_input.lifestyle}\n"
            f"  Vacation Type: {user_input.vacationType}\n"
            f"  Travelers: {user_input.travelers}\n\n"
            f"Proposed Itinerary (from Experience Agent):\n{itinerary_summary}\n\n"
            f"Based on the above, generate logistics JSON with flights (from {user_input.origin} to {user_input.destination}), "
            f"accommodations (for {user_input.trip_days} nights), "
            f"and total budget estimation. Output ONLY raw JSON."
        )

        logger.info(f"Starting logistics generation: {user_input.origin} → {user_input.destination} ({user_input.start_date} to {user_input.end_date})")

        result = await asyncio.wait_for(
            logistics_agent.run(prompt),
            timeout=120 # Increased timeout
        )

        # 1. Access the output. It might be a model (if pydantic-ai worked) or a string (older versions)
        output_obj = getattr(result, 'output', result)
        
        if isinstance(output_obj, TripLogistics):
            logger.info("Logistics agent provided structured data directly as TripLogistics.")
            parsed = output_obj
        else:
            raw_text = str(output_obj)
            logger.debug(f"Raw Logistics Output (length {len(raw_text)}): {raw_text[:200]}...")

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
                logger.error(f"Failed to extract JSON from logistics: {raw_text}")
                raise ValueError("No valid JSON found in logistics agent output.")
                
            parsed = TripLogistics(**data)
        

        # Inject real date-aware booking URLs
        enriched = _inject_booking_links(parsed, user_input)

        logger.info("Logistics generation complete.")
        return enriched

    except Exception as e:
        logger.error(f"Logistics generation failed: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Logistics agent error: {str(e)}")
