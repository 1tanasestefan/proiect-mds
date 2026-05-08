import json
import os
from urllib.parse import quote_plus

from fastapi import HTTPException
from loguru import logger

from local_llm import generate_local_json, local_model_name
from maps_service import get_multimodal_options
from models import AccommodationOption, FlightOption, TripLogistics, UserInput


LOGISTICS_SYSTEM_PROMPT = """
You are VibeTrips' local Logistics Agent. You run locally and must not call hosted AI APIs.
Create realistic flight, stay, budget, and transfer recommendations from the user's travel constraints.

Return exactly one valid JSON object with this schema:
{
  "flights": [
    {
      "airline_type": "Low Cost / Standard / Premium",
      "estimated_price_usd": 250,
      "description": "string",
      "booking_link": "SKYSCANNER_LINK"
    }
  ],
  "accommodations": [
    {
      "name": "string",
      "type": "string",
      "neighborhood": "string",
      "estimated_price_per_night_usd": 120,
      "booking_link": "BOOKING_LINK"
    }
  ],
  "total_estimated_budget_usd": 900,
  "transit_options": {
    "budget": {
      "total_price": 0,
      "currency": "USD",
      "legs": [],
      "map_center": {"lat": 0, "lng": 0}
    }
  }
}

Rules:
- Output raw JSON only. No markdown, commentary, XML, or function calls.
- Produce 2-3 flight options and 2-3 accommodation options.
- Use realistic price estimates in USD. If exact live prices are unavailable, say "estimated" in descriptions.
- For flight booking_link, use exactly "SKYSCANNER_LINK".
- For accommodation booking_link, use either "BOOKING_LINK" or "AIRBNB_LINK".
- If route data is provided, include transit_options and keep the same top-level option keys.
- If no route data is provided, omit transit_options.
"""


def build_skyscanner_link(origin: str, destination: str, start_date: str, end_date: str) -> str:
    origin_slug = quote_plus(origin.split(",")[0].strip().lower())
    dest_slug = quote_plus(destination.split(",")[0].strip().lower())
    start_short = start_date[2:].replace("-", "")
    end_short = end_date[2:].replace("-", "")
    return f"https://www.skyscanner.net/transport/flights/{origin_slug}/{dest_slug}/{start_short}/{end_short}/"


def build_booking_link(destination: str, start_date: str, end_date: str) -> str:
    return (
        "https://www.booking.com/searchresults.html"
        f"?ss={quote_plus(destination)}"
        f"&checkin={start_date}"
        f"&checkout={end_date}"
    )


def build_airbnb_link(destination: str, start_date: str, end_date: str) -> str:
    return (
        f"https://www.airbnb.com/s/{quote_plus(destination)}/homes"
        f"?checkin={start_date}"
        f"&checkout={end_date}"
    )


def _inject_booking_links(logistics: TripLogistics, user_input: UserInput) -> TripLogistics:
    updated_flights = []
    for flight in logistics.flights:
        link = flight.booking_link
        if "SKYSCANNER" in link.upper():
            link = build_skyscanner_link(
                user_input.origin,
                user_input.destination,
                user_input.start_date,
                user_input.end_date,
            )
        updated_flights.append(flight.model_copy(update={"booking_link": link}))

    updated_accommodations = []
    for accommodation in logistics.accommodations:
        link = accommodation.booking_link or "BOOKING_LINK"
        if "AIRBNB" in link.upper():
            link = build_airbnb_link(user_input.destination, user_input.start_date, user_input.end_date)
        else:
            link = build_booking_link(user_input.destination, user_input.start_date, user_input.end_date)
        updated_accommodations.append(accommodation.model_copy(update={"booking_link": link}))

    return logistics.model_copy(update={"flights": updated_flights, "accommodations": updated_accommodations})


def _estimate_base_flight(user_input: UserInput) -> float:
    budget = (user_input.budget or "medium").lower()
    if budget in {"low", "economy", "budget"}:
        return 180.0
    if budget in {"luxury", "premium", "unlimited"}:
        return 650.0
    return 320.0


def _fallback_logistics(user_input: UserInput, transit_options: dict | None) -> TripLogistics:
    destination = user_input.destination or "Destination"
    city = destination.split(",")[0].strip()
    nights = max(user_input.trip_days, 1)
    base_flight = _estimate_base_flight(user_input)

    if (user_input.budget or "").lower() in {"low", "economy", "budget"}:
        hotel_prices = [55.0, 85.0]
    elif (user_input.budget or "").lower() in {"luxury", "premium", "unlimited"}:
        hotel_prices = [220.0, 360.0, 520.0]
    else:
        hotel_prices = [95.0, 145.0, 210.0]

    flights = [
        FlightOption(
            airline_type="Low Cost",
            estimated_price_usd=round(base_flight * 0.75, 2),
            description=f"Estimated basic fare from {user_input.origin} to {destination}; luggage and seat selection may cost extra.",
            booking_link="SKYSCANNER_LINK",
        ),
        FlightOption(
            airline_type="Standard",
            estimated_price_usd=round(base_flight, 2),
            description="Estimated standard carrier fare with more comfortable timing and fewer tradeoffs.",
            booking_link="SKYSCANNER_LINK",
        ),
        FlightOption(
            airline_type="Premium",
            estimated_price_usd=round(base_flight * 1.8, 2),
            description="Estimated premium itinerary with better schedule flexibility and comfort.",
            booking_link="SKYSCANNER_LINK",
        ),
    ]

    accommodations = [
        AccommodationOption(
            name=f"{city} Central Stay",
            type="Hotel",
            neighborhood=f"Central {city}",
            estimated_price_per_night_usd=hotel_prices[0],
            booking_link="BOOKING_LINK",
        ),
        AccommodationOption(
            name=f"{city} Local Apartment",
            type="Apartment",
            neighborhood=f"{city} residential district",
            estimated_price_per_night_usd=hotel_prices[min(1, len(hotel_prices) - 1)],
            booking_link="AIRBNB_LINK",
        ),
    ]

    if len(hotel_prices) > 2:
        accommodations.append(
            AccommodationOption(
                name=f"{city} Boutique Hotel",
                type="Boutique Hotel",
                neighborhood=f"{city} historic center",
                estimated_price_per_night_usd=hotel_prices[2],
                booking_link="BOOKING_LINK",
            )
        )

    mid_hotel = accommodations[min(1, len(accommodations) - 1)].estimated_price_per_night_usd
    total = round(base_flight + (mid_hotel * nights) + (45.0 * user_input.trip_days), 2)
    return TripLogistics(
        flights=flights,
        accommodations=accommodations,
        total_estimated_budget_usd=total,
        transit_options=transit_options,
    )


async def _build_transit_context(user_input: UserInput) -> tuple[dict, str]:
    try:
        raw_transit_data = await get_multimodal_options(
            user_input.origin,
            user_input.destination,
            _estimate_base_flight(user_input),
        )
        pruned_transit_data = {}
        for key, value in raw_transit_data.items():
            value_copy = value.model_dump()
            for leg in value_copy.get("legs", []):
                leg["polyline"] = None
            pruned_transit_data[key] = value_copy
        return raw_transit_data, json.dumps(pruned_transit_data, indent=2)
    except Exception as exc:
        logger.warning(f"Could not fetch keyless map data: {exc}")
        return {}, "No route data available. Generate standard flight and accommodation options only."


async def generate_logistics(user_input: UserInput, logistics_context: str) -> TripLogistics:
    """Generate logistics locally and enrich with keyless map data and booking deep links."""
    try:
        logger.info(
            f"Starting local logistics generation: {user_input.origin} -> "
            f"{user_input.destination} ({user_input.start_date} to {user_input.end_date})"
        )
        raw_transit_data, transit_context = await _build_transit_context(user_input)
        has_transit_data = bool(raw_transit_data)
        use_local_logistics_agent = os.getenv("LOCAL_LLM_LOGISTICS", "false").lower() in {"1", "true", "yes"}

        prompt = (
            f"User constraints and context:\n{logistics_context}\n\n"
            f"Route data from keyless OpenStreetMap/OSRM services:\n{transit_context}\n\n"
            "Generate logistics JSON. Keep booking links as placeholders for backend injection."
        )

        if use_local_logistics_agent:
            try:
                data = await generate_local_json(
                    LOGISTICS_SYSTEM_PROMPT,
                    prompt,
                    timeout=75,
                    temperature=0.25,
                    num_predict=900,
                )
                if not has_transit_data:
                    data.pop("transit_options", None)
                parsed = TripLogistics(**data)
                logger.info(f"Local logistics agent completed with model {local_model_name()}.")
            except Exception as exc:
                logger.warning(f"Local logistics agent unavailable or invalid; using deterministic fallback. {exc}")
                parsed = _fallback_logistics(user_input, raw_transit_data or None)
        else:
            logger.info("Using fast deterministic logistics estimator with keyless map routing.")
            parsed = _fallback_logistics(user_input, raw_transit_data or None)

        hotel_name = parsed.accommodations[0].name if parsed.accommodations else None
        precise_data = raw_transit_data
        if hotel_name and parsed.transit_options:
            try:
                first_leg_price = list(parsed.transit_options.values())[0].legs[0].price
                precise_data = await get_multimodal_options(
                    user_input.origin,
                    user_input.destination,
                    first_leg_price,
                    hotel_name=hotel_name,
                )
            except Exception as exc:
                logger.warning(f"Failed to fetch precise hotel routing for {hotel_name}: {exc}")

        if parsed.transit_options and precise_data:
            for key, stored_value in precise_data.items():
                if key in parsed.transit_options:
                    parsed.transit_options[key].map_center = stored_value.map_center
                    for index, leg in enumerate(parsed.transit_options[key].legs):
                        if index < len(stored_value.legs):
                            precise_leg = stored_value.legs[index]
                            leg.origin_coords = precise_leg.origin_coords
                            leg.destination_coords = precise_leg.destination_coords
                            leg.polyline = precise_leg.polyline

        return _inject_booking_links(parsed, user_input)

    except Exception as exc:
        logger.error(f"Logistics generation failed: {exc}")
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=f"Logistics agent error: {str(exc)}")
