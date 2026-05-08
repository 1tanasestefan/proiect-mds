from datetime import date
from typing import Optional

from loguru import logger

from app.db.supabase import get_supabase
from models import UserInput

DESTINATION_CATALOG = [
    {"destination": "Lisbon, Portugal", "budget": ["low", "medium"], "tags": ["relaxed", "culinary", "sightseeing", "nightlife"], "related": ["Barcelona", "Porto", "Athens", "Seville"], "reason": "sunny, social, food-heavy, and usually friendly for tighter budgets"},
    {"destination": "Prague, Czech Republic", "budget": ["low", "medium"], "tags": ["sightseeing", "nightowl", "party", "culture"], "related": ["Vienna", "Budapest", "Berlin", "Krakow"], "reason": "historic by day, lively at night, and strong value for groups"},
    {"destination": "Budapest, Hungary", "budget": ["low", "medium"], "tags": ["nightowl", "party", "relaxed", "sightseeing"], "related": ["Prague", "Vienna", "Krakow"], "reason": "thermal baths, ruin bars, and good prices for a group trip"},
    {"destination": "Barcelona, Spain", "budget": ["medium", "luxury"], "tags": ["party", "culinary", "sightseeing", "energetic"], "related": ["Lisbon", "Madrid", "Valencia"], "reason": "beaches, food, architecture, and nightlife in one easy city break"},
    {"destination": "Athens, Greece", "budget": ["low", "medium"], "tags": ["sightseeing", "culinary", "culture", "relaxed"], "related": ["Rome", "Istanbul", "Lisbon"], "reason": "ancient sights, relaxed evenings, and excellent food without luxury pricing"},
    {"destination": "Istanbul, Turkey", "budget": ["low", "medium"], "tags": ["culinary", "sightseeing", "energetic", "culture"], "related": ["Athens", "Marrakesh", "Cairo"], "reason": "big-city energy, deep culture, and memorable food experiences"},
    {"destination": "Amsterdam, Netherlands", "budget": ["medium", "luxury"], "tags": ["nightowl", "sightseeing", "party", "relaxed"], "related": ["Berlin", "Paris", "Bruges"], "reason": "walkable, scenic, and good for nightlife with a comfort budget"},
    {"destination": "Rome, Italy", "budget": ["medium", "luxury"], "tags": ["culinary", "sightseeing", "culture", "relaxed"], "related": ["Florence", "Athens", "Paris"], "reason": "classic culture and food with plenty of polished hotel options"},
    {"destination": "Bali, Indonesia", "budget": ["medium", "luxury"], "tags": ["relaxed", "culinary", "beach", "adventure"], "related": ["Thailand", "Phuket", "Ubud"], "reason": "relaxed, scenic, and best when the budget allows a longer flight"},
    {"destination": "Tokyo, Japan", "budget": ["medium", "luxury"], "tags": ["culinary", "sightseeing", "energetic", "nightowl"], "related": ["Seoul", "Osaka", "Singapore"], "reason": "dense, exciting, food-focused, and ideal for high-energy explorers"},
    {"destination": "Paris, France", "budget": ["medium", "luxury"], "tags": ["culinary", "sightseeing", "culture", "relaxed"], "related": ["Rome", "Amsterdam", "Barcelona"], "reason": "romantic, cultural, and strongest with a comfort or luxury budget"},
    {"destination": "Marrakesh, Morocco", "budget": ["low", "medium"], "tags": ["culinary", "sightseeing", "culture", "energetic"], "related": ["Istanbul", "Lisbon", "Cairo"], "reason": "colorful markets, food, and culture at a strong value"},
]

SEASONAL_DATE_WINDOWS = {
    "tokyo": {
        "low": ("2026-02-03", "2026-02-06", "Tokyo is calmer and better priced before cherry blossom demand peaks."),
        "medium": ("2026-11-10", "2026-11-13", "Autumn gives strong weather and scenery without spring's biggest price spike."),
        "luxury": ("2026-03-31", "2026-04-03", "Cherry blossom season is expensive, but it is the iconic Tokyo moment."),
        "unlimited": ("2026-03-31", "2026-04-03", "Cherry blossom season is the best-of-everything Tokyo choice when budget is open."),
    },
    "paris": {
        "low": ("2026-02-10", "2026-02-13", "Late winter keeps Paris costs lower while museums and restaurants stay excellent."),
        "medium": ("2026-05-12", "2026-05-15", "May balances pleasant weather with less pressure than peak summer."),
        "luxury": ("2026-06-09", "2026-06-12", "Early summer brings long evenings and premium outdoor dining."),
        "unlimited": ("2026-06-09", "2026-06-12", "Early summer is the polished Paris experience when price is not a constraint."),
    },
    "barcelona": {
        "low": ("2026-03-10", "2026-03-13", "March keeps prices easier before beach-season demand rises."),
        "medium": ("2026-05-05", "2026-05-08", "May gives warm days without the full summer surge."),
        "luxury": ("2026-06-16", "2026-06-19", "June is lively, warm, and ideal for premium hotels and restaurants."),
        "unlimited": ("2026-06-16", "2026-06-19", "June is the best Barcelona energy if you are not optimizing for price."),
    },
}

DEFAULT_DATE_WINDOWS = {
    "low": ("2026-02-10", "2026-02-13", "This off-peak window is chosen to keep flights and stays more budget-friendly."),
    "medium": ("2026-05-12", "2026-05-15", "This shoulder-season window balances weather, availability, and price."),
    "luxury": ("2026-06-09", "2026-06-12", "This high-comfort window prioritizes better weather and premium options."),
    "unlimited": ("2026-06-09", "2026-06-12", "This window prioritizes the strongest overall experience over price."),
}


def _collect_text_signals(items: list[dict]) -> str:
    chunks = []
    for item in items:
        chunks.append(str(item.get("destination", "")))
        ai_data = item.get("ai_data") or {}
        experience = ai_data.get("experience") or {}
        chunks.append(str(experience.get("trip_title", "")))
        chunks.append(str(experience.get("vibe_summary", "")))
    return " ".join(chunks).lower()


def recommend_dates_for(destination: Optional[str], budget: str) -> dict:
    city = (destination or "").split(",")[0].strip().lower()
    budget_key = (budget or "medium").lower()
    windows = SEASONAL_DATE_WINDOWS.get(city, DEFAULT_DATE_WINDOWS)
    start_date, end_date, reason = windows.get(budget_key, windows.get("medium", DEFAULT_DATE_WINDOWS["medium"]))
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    today = date.today()
    while start <= today:
        start = start.replace(year=start.year + 1)
        end = end.replace(year=end.year + 1)
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "reason": reason,
    }


async def recommend_destinations(user_input: UserInput, user_id: Optional[str], limit: int = 4) -> list[dict]:
    budget = (user_input.budget or "medium").lower()
    selected_tags = {
        (user_input.lifestyle or "").lower(),
        (user_input.vacationType or "").lower(),
    }
    history_items: list[dict] = []
    db = get_supabase()

    if db and user_id:
        try:
            saved = (
                db.table("itineraries")
                .select("destination, title, ai_data")
                .eq("user_id", user_id)
                .limit(20)
                .execute()
            )
            history_items.extend(saved.data or [])

            likes = (
                db.table("itinerary_likes")
                .select("itinerary_id")
                .eq("user_id", user_id)
                .limit(30)
                .execute()
            )
            liked_ids = [item["itinerary_id"] for item in (likes.data or []) if item.get("itinerary_id")]
            if liked_ids:
                liked_trips = (
                    db.table("itineraries")
                    .select("destination, title, ai_data")
                    .in_("id", liked_ids)
                    .execute()
                )
                history_items.extend(liked_trips.data or [])
        except Exception as e:
            logger.warning(f"[Recommender] Could not load user history: {e}")

    signal_text = _collect_text_signals(history_items)
    seen_destinations = {str(item.get("destination", "")).split(",")[0].strip().lower() for item in history_items}

    ranked = []
    for option in DESTINATION_CATALOG:
        score = 0
        if budget in option["budget"]:
            score += 5
        score += len(selected_tags.intersection(option["tags"])) * 3
        score += sum(2 for tag in option["tags"] if tag and tag in signal_text)
        score += sum(4 for related in option["related"] if related.lower() in signal_text)
        city = option["destination"].split(",")[0].strip().lower()
        if city in seen_destinations:
            score -= 2
        ranked.append({**option, "score": score})

    ranked.sort(key=lambda option: option["score"], reverse=True)
    recommendations = [
        {
            "destination": option["destination"],
            "reason": option["reason"],
            "match_score": option["score"],
            "suggested_dates": recommend_dates_for(option["destination"], budget),
        }
        for option in ranked[:limit]
    ]
    logger.info(f"[Recommender] Flexible recommendations: {[item['destination'] for item in recommendations]}")
    return recommendations


async def recommend_destination(user_input: UserInput, user_id: Optional[str]) -> str:
    recommendations = await recommend_destinations(user_input, user_id, limit=1)
    recommendation = recommendations[0]["destination"] if recommendations else "Lisbon, Portugal"
    logger.info(f"[Recommender] Flexible destination resolved to {recommendation}")
    return recommendation
