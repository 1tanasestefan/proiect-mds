from __future__ import annotations
import json
import os
import re
from datetime import datetime
from urllib.parse import quote_plus

from fastapi import HTTPException
from loguru import logger

from local_llm import generate_local_json, local_model_name
from maps_service import get_multimodal_options
from models import AccommodationOption, AgentOneOutput, BudgetBreakdown, FlightOption, TripLogistics, UserInput


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

EUROPE = {
    "romania", "portugal", "spain", "france", "italy", "germany", "netherlands",
    "czech republic", "hungary", "austria", "poland", "greece", "united kingdom",
    "ireland", "belgium", "switzerland", "croatia", "serbia", "bulgaria",
}
MENA = {"morocco", "turkey", "egypt", "united arab emirates"}
ASIA = {"japan", "indonesia", "thailand", "south korea", "singapore", "india"}
NORTH_AMERICA = {"united states", "usa", "canada", "mexico"}

CITY_COST_INDEX = {
    "athens": 0.9,
    "bali": 0.75,
    "barcelona": 1.18,
    "budapest": 0.82,
    "istanbul": 0.88,
    "lisbon": 1.0,
    "marrakesh": 0.78,
    "paris": 1.42,
    "prague": 0.92,
    "rome": 1.2,
    "tokyo": 1.45,
}

HOTEL_PRICE_ANCHORS = {
    "low": [55.0, 82.0],
    "economy": [55.0, 82.0],
    "budget": [55.0, 82.0],
    "medium": [105.0, 155.0, 220.0],
    "mid-range": [105.0, 155.0, 220.0],
    "luxury": [250.0, 390.0, 560.0],
    "premium": [250.0, 390.0, 560.0],
    "unlimited": [340.0, 540.0, 780.0],
}

DAILY_SPEND_ANCHORS = {
    "low": {"food": 30.0, "activities": 24.0, "local_transport": 8.0},
    "economy": {"food": 30.0, "activities": 24.0, "local_transport": 8.0},
    "budget": {"food": 30.0, "activities": 24.0, "local_transport": 8.0},
    "medium": {"food": 55.0, "activities": 42.0, "local_transport": 15.0},
    "mid-range": {"food": 55.0, "activities": 42.0, "local_transport": 15.0},
    "luxury": {"food": 95.0, "activities": 80.0, "local_transport": 28.0},
    "premium": {"food": 95.0, "activities": 80.0, "local_transport": 28.0},
    "unlimited": {"food": 145.0, "activities": 125.0, "local_transport": 42.0},
}


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


def _city_name(place: str | None) -> str:
    return (place or "").split(",")[0].strip() or "Destination"


def _country_name(place: str | None) -> str:
    parts = [part.strip() for part in (place or "").split(",") if part.strip()]
    return parts[-1].lower() if len(parts) > 1 else ""


def _route_region(country: str) -> str:
    if country in EUROPE:
        return "europe"
    if country in MENA:
        return "mena"
    if country in ASIA:
        return "asia"
    if country in NORTH_AMERICA:
        return "north_america"
    return "global"


def _season_multiplier(date_value: str | None) -> float:
    if not date_value:
        return 1.0
    try:
        month = datetime.strptime(date_value, "%Y-%m-%d").month
    except ValueError:
        return 1.0
    if month in {6, 7, 8, 12}:
        return 1.18
    if month in {1, 2, 11}:
        return 0.92
    return 1.0


def _weekend_multiplier(date_value: str | None) -> float:
    if not date_value:
        return 1.0
    try:
        weekday = datetime.strptime(date_value, "%Y-%m-%d").weekday()
    except ValueError:
        return 1.0
    return 1.08 if weekday in {4, 5, 6} else 1.0


def _route_base_price(origin: str | None, destination: str | None) -> float:
    origin_country = _country_name(origin)
    destination_country = _country_name(destination)
    origin_region = _route_region(origin_country)
    destination_region = _route_region(destination_country)

    if origin_country and origin_country == destination_country:
        return 120.0
    if origin_region == "europe" and destination_region == "europe":
        return 240.0
    if {origin_region, destination_region} == {"europe", "mena"}:
        return 310.0
    if {origin_region, destination_region} == {"europe", "asia"}:
        return 780.0
    if {origin_region, destination_region} == {"europe", "north_america"}:
        return 680.0
    if origin_region == destination_region:
        return 380.0
    return 920.0


def _estimate_base_flight(user_input: UserInput) -> float:
    budget = (user_input.budget or "medium").lower()
    base = _route_base_price(user_input.origin, user_input.destination)
    if budget in {"low", "economy", "budget"}:
        budget_multiplier = 0.78
    elif budget in {"luxury", "premium", "unlimited"}:
        budget_multiplier = 1.55
    else:
        budget_multiplier = 1.0

    return round(
        base
        * budget_multiplier
        * _season_multiplier(user_input.start_date)
        * _weekend_multiplier(user_input.start_date),
        2,
    )


def _destination_cost_index(destination: str | None) -> float:
    return CITY_COST_INDEX.get(_city_name(destination).lower(), 1.0)


def _hotel_prices_for(user_input: UserInput) -> list[float]:
    budget = (user_input.budget or "medium").lower()
    anchors = HOTEL_PRICE_ANCHORS.get(budget, HOTEL_PRICE_ANCHORS["medium"])
    multiplier = _destination_cost_index(user_input.destination) * _season_multiplier(user_input.start_date)
    return [round(price * multiplier, 2) for price in anchors]


def _daily_spend_for(user_input: UserInput) -> dict[str, float]:
    budget = (user_input.budget or "medium").lower()
    spend = dict(DAILY_SPEND_ANCHORS.get(budget, DAILY_SPEND_ANCHORS["medium"]))
    intent_text = f"{user_input.vacationType} {user_input.lifestyle}".lower()

    if any(term in intent_text for term in ("culinary", "food", "dining", "wine")):
        spend["food"] *= 1.25
        spend["activities"] *= 0.95
    if any(term in intent_text for term in ("party", "nightlife", "nightowl", "club")):
        spend["food"] *= 1.1
        spend["activities"] *= 1.2
        spend["local_transport"] *= 1.25
    if any(term in intent_text for term in ("relax", "spa", "wellness")):
        spend["activities"] *= 1.15
    if any(term in intent_text for term in ("adventure", "hike", "outdoor")):
        spend["activities"] *= 1.3

    return {key: round(value, 2) for key, value in spend.items()}


def _parse_cost_value(cost: str | None) -> float | None:
    if not cost:
        return None
    if "free" in cost.lower():
        return 0.0
    values = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", cost)]
    if not values:
        return None
    return sum(values) / len(values)


def _activity_cost_total(experience_result: AgentOneOutput | None) -> float:
    if not experience_result:
        return 0.0
    total = 0.0
    for day in experience_result.itinerary:
        for activity in day.activities:
            parsed = _parse_cost_value(activity.cost)
            if parsed is not None:
                total += parsed
    return round(total, 2)


def _activity_anchor(location: str | None, title: str | None) -> str | None:
    candidate = (location or title or "").split(",")[0].strip()
    candidate = re.sub(r"\s+", " ", candidate)
    if len(candidate) < 3:
        return None
    if candidate.lower() in {"city center", "city centre", "downtown", "old town"}:
        return None
    return candidate[:80]


def _activity_anchors(experience_result: AgentOneOutput | None, limit: int = 4) -> list[str]:
    if not experience_result:
        return []
    anchors: list[str] = []
    seen: set[str] = set()
    for day in experience_result.itinerary:
        for activity in day.activities:
            anchor = _activity_anchor(activity.location, activity.title)
            if not anchor:
                continue
            key = anchor.lower()
            if key in seen:
                continue
            anchors.append(anchor)
            seen.add(key)
            if len(anchors) >= limit:
                return anchors
    return anchors


def _stay_areas(user_input: UserInput, experience_result: AgentOneOutput | None) -> list[tuple[str, str]]:
    city = _city_name(user_input.destination)
    anchors = _activity_anchors(experience_result)
    if not anchors:
        return [
            (f"Central {city}", "Keeps arrival simple and close to major sights."),
            (f"{city} residential district", "Usually gives better apartment value for groups."),
            (f"{city} historic center", "Prioritizes walkability for short trips."),
        ]

    areas = [
        (f"Near {anchors[0]}", f"Closest to the first itinerary anchor: {anchors[0]}."),
        (f"Central {city}", "Balanced fallback for walkability across the full itinerary."),
    ]
    if len(anchors) > 1:
        areas.append((f"Near {anchors[1]}", f"Good alternative because the plan also spends time around {anchors[1]}."))
    return areas


def _airport_transfer_cost(transit_options: dict | None) -> float:
    if not transit_options:
        return 0.0
    budget_option = transit_options.get("budget") or next(iter(transit_options.values()), None)
    if not budget_option or len(budget_option.legs) <= 1:
        return 0.0
    return round(sum(leg.price for leg in budget_option.legs[1:]), 2)


def _selected_flight_price(logistics: TripLogistics) -> float:
    if not logistics.flights:
        return 0.0
    standard = next((flight for flight in logistics.flights if "standard" in flight.airline_type.lower()), None)
    selected = standard or logistics.flights[min(1, len(logistics.flights) - 1)]
    return round(selected.estimated_price_usd, 2)


def _selected_hotel_price(logistics: TripLogistics) -> float:
    if not logistics.accommodations:
        return 0.0
    selected = logistics.accommodations[min(1, len(logistics.accommodations) - 1)]
    return round(selected.estimated_price_per_night_usd, 2)


def _price_range_bounds(price_range: str | None) -> tuple[float | None, float | None]:
    if not price_range or "unlimited" in price_range.lower():
        return None, None
    values = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", price_range)]
    if not values:
        return None, None
    if len(values) == 1:
        return None, values[0]
    return min(values), max(values)


def _budget_breakdown(
    logistics: TripLogistics,
    user_input: UserInput,
    experience_result: AgentOneOutput | None,
) -> BudgetBreakdown:
    nights = max(user_input.trip_days, 1)
    travelers = max(user_input.travelers or 1, 1)
    room_share = min(travelers, 2)
    daily_spend = _daily_spend_for(user_input)

    flight = _selected_flight_price(logistics)
    accommodation = round((_selected_hotel_price(logistics) * nights) / room_share, 2)
    food = round(daily_spend["food"] * user_input.trip_days, 2)
    fallback_activities = round(daily_spend["activities"] * user_input.trip_days, 2)
    activities = max(_activity_cost_total(experience_result), fallback_activities)
    local_transport = round(daily_spend["local_transport"] * user_input.trip_days, 2)
    airport_transfer = _airport_transfer_cost(logistics.transit_options)
    subtotal = round(flight + accommodation + food + activities + local_transport + airport_transfer, 2)

    return BudgetBreakdown(
        flight_per_person_usd=flight,
        accommodation_per_person_usd=accommodation,
        food_per_person_usd=food,
        activities_per_person_usd=round(activities, 2),
        local_transport_per_person_usd=local_transport,
        airport_transfer_per_person_usd=airport_transfer,
        subtotal_per_person_usd=subtotal,
        total_group_usd=round(subtotal * travelers, 2),
    )


def _logistics_assumptions(
    user_input: UserInput,
    logistics: TripLogistics,
    breakdown: BudgetBreakdown,
    experience_result: AgentOneOutput | None,
) -> list[str]:
    assumptions = list(logistics.assumptions or [])
    assumptions.extend([
        "Flight and accommodation prices are estimates, not live inventory.",
        "Accommodation cost assumes up to two travelers sharing one room.",
        "Local transport covers simple in-city movement between itinerary areas.",
    ])
    if logistics.transit_options:
        assumptions.append("Airport transfer routes use OpenStreetMap/Nominatim and OSRM public routing data when available.")
    if _activity_anchors(experience_result):
        assumptions.append("Stay areas are chosen from the generated activity anchors.")

    min_price, max_price = _price_range_bounds(user_input.price_range_per_person)
    if max_price is not None and breakdown.subtotal_per_person_usd > max_price:
        assumptions.append(
            f"Estimated per-person cost is above the requested ${max_price:.0f} ceiling; reduce flight/stay tier or trip length."
        )
    elif min_price is not None and breakdown.subtotal_per_person_usd < min_price:
        assumptions.append(
            f"Estimated per-person cost is below the requested ${min_price:.0f} floor; premium options can be added."
        )

    return list(dict.fromkeys(assumptions))


def _complete_logistics(
    logistics: TripLogistics,
    user_input: UserInput,
    experience_result: AgentOneOutput | None,
) -> TripLogistics:
    breakdown = _budget_breakdown(logistics, user_input, experience_result)
    return logistics.model_copy(
        update={
            "total_estimated_budget_usd": breakdown.subtotal_per_person_usd,
            "budget_breakdown": breakdown,
            "assumptions": _logistics_assumptions(user_input, logistics, breakdown, experience_result),
            "confidence": "route-informed" if logistics.transit_options else logistics.confidence,
        }
    )


def _routing_anchor(accommodation: AccommodationOption) -> str:
    area = accommodation.neighborhood or accommodation.name
    return re.sub(r"^near\s+", "", area, flags=re.IGNORECASE).strip() or accommodation.name


def _fallback_logistics(
    user_input: UserInput,
    transit_options: dict | None,
    experience_result: AgentOneOutput | None = None,
) -> TripLogistics:
    destination = user_input.destination or "Destination"
    city = _city_name(destination)
    base_flight = _estimate_base_flight(user_input)
    hotel_prices = _hotel_prices_for(user_input)
    stay_areas = _stay_areas(user_input, experience_result)
    date_note = f"{user_input.start_date} to {user_input.end_date}" if user_input.start_date and user_input.end_date else "the selected dates"

    flights = [
        FlightOption(
            airline_type="Low Cost",
            estimated_price_usd=round(base_flight * 0.78, 2),
            description=f"Estimated basic fare for {date_note}; assumes limited luggage and less flexible timing.",
            booking_link="SKYSCANNER_LINK",
        ),
        FlightOption(
            airline_type="Standard",
            estimated_price_usd=round(base_flight, 2),
            description=f"Estimated standard round-trip fare from {_city_name(user_input.origin)} to {city}, with more comfortable timing.",
            booking_link="SKYSCANNER_LINK",
        ),
        FlightOption(
            airline_type="Flexible",
            estimated_price_usd=round(base_flight * 1.45, 2),
            description="Estimated fare with better schedule flexibility, improved baggage assumptions, or fewer tradeoffs.",
            booking_link="SKYSCANNER_LINK",
        ),
    ]

    accommodation_templates = [
        ("Search hotels", "Hotel", "BOOKING_LINK"),
        ("Search apartments", "Apartment", "AIRBNB_LINK"),
        ("Search boutique stays", "Boutique Hotel", "BOOKING_LINK"),
    ]
    accommodations = []
    for index, price in enumerate(hotel_prices[:3]):
        area, reason = stay_areas[min(index, len(stay_areas) - 1)]
        prefix, stay_type, link = accommodation_templates[min(index, len(accommodation_templates) - 1)]
        accommodations.append(
            AccommodationOption(
                name=f"{prefix} in {area}",
                type=stay_type,
                neighborhood=area,
                estimated_price_per_night_usd=price,
                booking_link=link,
                reason=reason,
            )
        )

    logistics = TripLogistics(
        flights=flights,
        accommodations=accommodations,
        total_estimated_budget_usd=0,
        transit_options=transit_options,
    )
    return _complete_logistics(logistics, user_input, experience_result)


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


async def generate_logistics(
    user_input: UserInput,
    logistics_context: str,
    experience_result: AgentOneOutput | None = None,
) -> TripLogistics:
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
                parsed = _complete_logistics(TripLogistics(**data), user_input, experience_result)
                logger.info(f"Local logistics agent completed with model {local_model_name()}.")
            except Exception as exc:
                logger.warning(f"Local logistics agent unavailable or invalid; using deterministic fallback. {exc}")
                parsed = _fallback_logistics(user_input, raw_transit_data or None, experience_result)
        else:
            logger.info("Using fast deterministic logistics estimator with keyless map routing.")
            parsed = _fallback_logistics(user_input, raw_transit_data or None, experience_result)

        hotel_name = _routing_anchor(parsed.accommodations[0]) if parsed.accommodations else None
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

        parsed = _complete_logistics(parsed, user_input, experience_result)
        return _inject_booking_links(parsed, user_input)

    except Exception as exc:
        logger.error(f"Logistics generation failed: {exc}")
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=f"Logistics agent error: {str(exc)}")
