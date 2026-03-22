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
    output_type=str,
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
        "8. Output ONLY a single valid JSON block matching this structure:\n"
        "{\n"
        '  "flights": [\n'
        '    {"airline_type": "Low Cost (Wizz Air tier)", "estimated_price_usd": 80, '
        '"description": "...", "booking_link": "SKYSCANNER_LINK"}\n'
        "  ],\n"
        '  "accommodations": [\n'
        '    {"type": "Budget Hostel", "neighborhood": "Old Town", '
        '"estimated_price_per_night_usd": 25, "booking_link": "BOOKING_LINK"}\n'
        "  ],\n"
        '  "total_estimated_budget_usd": 450\n'
        "}\n"
        "9. Output ONLY the JSON. NO text before or after."
    ),
)


# ── JSON Parser ──────────────────────────────────────────────────

def _parse_logistics_json(raw: str) -> TripLogistics:
    """Extract and validate logistics JSON from the agent output."""
    logger.debug(f"Parsing logistics output (length: {len(raw)})")

    cleaned = re.sub(r"<function.*?>.*?</function>", '""', raw)
    cleaned = re.sub(r"```(?:json)?", "", cleaned).strip()

    decoder = json.JSONDecoder()
    pos = 0

    while True:
        match_pos = cleaned.find('{', pos)
        if match_pos == -1:
            break
        try:
            data, index = decoder.raw_decode(cleaned[match_pos:])
            if isinstance(data, dict) and "flights" in data and "accommodations" in data:
                logger.info("Valid logistics JSON found.")
                return TripLogistics(**data)
            pos = match_pos + index
        except (json.JSONDecodeError, ValueError):
            pos = match_pos + 1

    logger.error(f"No valid logistics JSON. Raw: {raw[:500]}")
    raise ValueError("No valid logistics JSON found in agent output.")


# ── Deep-Link Injection (Date-Aware) ─────────────────────────────

def _inject_booking_links(
    logistics: TripLogistics,
    user_input: UserInput,
) -> TripLogistics:
    """Replace placeholder strings with real date-aware deep-link URLs."""

    # Inject flight links
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

    # Inject accommodation links
    updated_accom = []
    for a in logistics.accommodations:
        link = a.booking_link
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
            timeout=60
        )

        logger.debug(f"RAW LOGISTICS OUTPUT:\n{result.output}")
        parsed = _parse_logistics_json(result.output)

        # Inject real date-aware booking URLs
        enriched = _inject_booking_links(parsed, user_input)

        logger.info("Logistics generation complete.")
        return enriched

    except Exception as e:
        logger.error(f"Logistics generation failed: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Logistics agent error: {str(e)}")
