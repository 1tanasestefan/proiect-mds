from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from models import UserInput, FinalTripPlan, ItineraryUpdate, VoteRequest, CommunityItinerary
from agent_experience import generate_experience_itinerary
from agent_regenerate import regenerate_single_activity
import math
import json
import httpx
from fastapi import BackgroundTasks
from agent_logistics import generate_logistics
from auth_middleware import get_current_user, get_optional_user
from database import supabase
from loguru import logger
import sys
from datetime import date, timedelta

# Configure logger to show DEBUG messages
logger.remove()
logger.add(sys.stderr, level="DEBUG")

app = FastAPI(title="AI Travel Planner Backend (Zero-Cost Stack)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Travel Planner - Zero-Cost API Backend is running"}


@app.get("/api/geocoding/search")
async def geocoding_search(q: str = Query(..., min_length=2)):
    """Proxy to Photon geocoder — returns [{place_id, display_name}]."""
    url = "https://photon.komoot.io/api/"
    params = {"q": q, "limit": 5, "lang": "en"}
    headers = {"User-Agent": "VibeTrips/1.0"}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for i, feature in enumerate(data.get("features", [])):
                props = feature.get("properties", {})
                city = props.get("city") or props.get("name", "")
                country = props.get("country", "")
                if city and country:
                    display = f"{city}, {country}"
                elif props.get("name") and country:
                    display = f"{props['name']}, {country}"
                else:
                    display = props.get("name", q)
                results.append({"place_id": i, "display_name": display})
            seen = set()
            unique = []
            for r in results:
                if r["display_name"] not in seen:
                    seen.add(r["display_name"])
                    unique.append(r)
            return JSONResponse(content=unique)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {e}")


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


def _collect_text_signals(items: List[dict]) -> str:
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


async def recommend_destinations(user_input: UserInput, user_id: Optional[str], limit: int = 4) -> List[dict]:
    budget = (user_input.budget or "medium").lower()
    selected_tags = {
        (user_input.lifestyle or "").lower(),
        (user_input.vacationType or "").lower(),
    }
    history_items: List[dict] = []

    if supabase and user_id:
        try:
            saved = (
                supabase.table("itineraries")
                .select("destination, title, ai_data")
                .eq("user_id", user_id)
                .limit(20)
                .execute()
            )
            history_items.extend(saved.data or [])

            likes = (
                supabase.table("itinerary_likes")
                .select("itinerary_id")
                .eq("user_id", user_id)
                .limit(30)
                .execute()
            )
            liked_ids = [item["itinerary_id"] for item in (likes.data or []) if item.get("itinerary_id")]
            if liked_ids:
                liked_trips = (
                    supabase.table("itineraries")
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


@app.post("/api/recommend-destinations")
async def recommend_destination_options(
    user_input: UserInput,
    user_id: Optional[str] = Depends(get_optional_user),
):
    recommendations = await recommend_destinations(user_input, user_id, limit=4)
    return {"recommendations": recommendations}


# ── PUBLIC: Generate Itinerary (No auth required) ────────────────

@app.post("/api/generate-itinerary", response_model=FinalTripPlan)
async def generate_itinerary(
    user_input: UserInput,
    user_id: Optional[str] = Depends(get_optional_user),
):
    """
    Master Orchestrator: chains Agent 1 (Experience) → Agent 2 (Logistics).
    Returns the combined FinalTripPlan to the frontend.
    """
    try:
        if user_input.flexible_destination and not (user_input.destination or "").strip():
            recommended_destination = await recommend_destination(user_input, user_id)
            user_input = user_input.model_copy(update={"destination": recommended_destination})
        if user_input.flexible_dates:
            date_recommendation = recommend_dates_for(user_input.destination, user_input.budget)
            user_input = user_input.model_copy(update={
                "start_date": date_recommendation["start_date"],
                "end_date": date_recommendation["end_date"],
            })

        logger.info(f"[Orchestrator] Step 1: Experience Agent for {user_input.destination}")
        experience_result = await generate_experience_itinerary(user_input)

        logger.info(f"[Orchestrator] Step 2: Logistics Agent for {user_input.destination}")
        logistics_context = f"Origin: {user_input.origin}, Destination: {user_input.destination}, Check-in: {user_input.start_date}, Check-out: {user_input.end_date}, Price range per person: {user_input.price_range_per_person or user_input.budget}. Provide flight and hotel estimates."
        logistics_result = await generate_logistics(user_input, logistics_context)

        final_plan = FinalTripPlan(
            experience=experience_result,
            logistics=logistics_result,
        )

        logger.info(f"[Orchestrator] ✅ Complete plan generated for {user_input.destination}")
        return final_plan

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"[Orchestrator] Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── PROTECTED: Save Itinerary ────────────────────────────────────

class SaveItineraryRequest(BaseModel):
    title: str
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_public: bool = False
    ai_data: dict  # The full FinalTripPlan JSON


@app.post("/api/itineraries/save")
async def save_itinerary(
    payload: SaveItineraryRequest,
    user_id: str = Depends(get_current_user),
):
    """Save a generated itinerary to the user's account."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        result = supabase.table("itineraries").insert({
            "user_id": user_id,
            "title": payload.title,
            "destination": payload.destination,
            "start_date": payload.start_date,
            "end_date": payload.end_date,
            "is_public": payload.is_public,
            "ai_data": payload.ai_data,
        }).execute()

        logger.info(f"[DB] Saved itinerary '{payload.title}' for user {user_id}")
        return {"status": "saved", "itinerary_id": result.data[0]["id"]}

    except Exception as e:
        logger.error(f"[DB] Save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save itinerary: {str(e)}")


# ── PROTECTED: Get My Itineraries ────────────────────────────────

@app.get("/api/itineraries/me")
async def get_my_itineraries(user_id: str = Depends(get_current_user)):
    """Fetch all itineraries belonging to the authenticated user."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        result = (
            supabase
            .table("itineraries")
            .select("id, title, destination, start_date, end_date, is_public, created_at, ai_data")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        logger.info(f"[DB] Fetched {len(result.data)} itineraries for user {user_id}")
        return {"itineraries": result.data}

    except Exception as e:
        logger.error(f"[DB] Fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch itineraries: {str(e)}")


# ── PROTECTED: Get Single Itinerary ──────────────────────────────

@app.get("/api/itineraries/{itinerary_id}")
async def get_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    """Fetch a single itinerary by ID (allows multiplayer viewing if link is shared)."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        # We don't filter by user_id here so friends can view the trip
        result = (
            supabase
            .table("itineraries")
            .select("id, user_id, title, destination, start_date, end_date, is_public, created_at, ai_data")
            .eq("id", itinerary_id)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Itinerary not found.")

        logger.info(f"[DB] Fetched itinerary {itinerary_id} for user {user_id}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DB] Fetch single failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch itinerary: {str(e)}")


# ── PROTECTED: Update Itinerary ──────────────────────────────────

@app.patch("/api/itineraries/{itinerary_id}")
async def update_itinerary(
    itinerary_id: str,
    update_data: ItineraryUpdate,
    user_id: str = Depends(get_current_user),
):
    """Update a specific itinerary (only if owned by the user)."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        # Build payload dynamically based on non-null fields
        payload = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not payload:
            return {"status": "no_changes"}

        result = (
            supabase
            .table("itineraries")
            .update(payload)
            .eq("id", itinerary_id)
            .eq("user_id", user_id)  # Strict! Only host can edit!
            .execute()
        )

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Itinerary not found or you don't have permission.")

        logger.info(f"[DB] Updated itinerary {itinerary_id} for user {user_id}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DB] Update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update itinerary: {str(e)}")

# ── MULTIPLAYER: Vote to Regenerate ──────────────────────────────

async def _bg_regenerate(itinerary_id: str, vote_req: VoteRequest, current_ai_data: dict, current_trip: dict):
    try:
        vote_key = f"day_{vote_req.day_index}_act_{vote_req.activity_index}"
        
        # Mark as REGENERATING globally
        current_ai_data.setdefault("regenerating_keys", {})
        current_ai_data["regenerating_keys"][vote_key] = True
        
        # Clear votes to 0 since we committed to regeneratig
        if "votes" in current_ai_data and vote_key in current_ai_data["votes"]:
             current_ai_data["votes"][vote_key] = []
             
        supabase.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()

        # Isolate context
        day_obj = current_ai_data["experience"]["itinerary"][vote_req.day_index]
        old_act = day_obj["activities"][vote_req.activity_index]
        day_context = json.dumps([a["title"] for i, a in enumerate(day_obj["activities"]) if i != vote_req.activity_index])
        
        destination = current_trip.get("destination", "Unknown")
        vibe_summary = current_ai_data["experience"].get("vibe_summary", "")
        
        # Regenerate!
        new_act = await regenerate_single_activity(vibe_summary, day_context, destination, json.dumps(old_act))
        
        # Splice back in
        current_ai_data["experience"]["itinerary"][vote_req.day_index]["activities"][vote_req.activity_index] = new_act.model_dump()
        
        # Unmark REGENERATING
        if vote_key in current_ai_data["regenerating_keys"]:
            del current_ai_data["regenerating_keys"][vote_key]
            
        supabase.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()
        logger.info(f"Regeneration complete for {vote_key} on iter {itinerary_id}")

    except Exception as e:
        logger.error(f"Background regeneration failed: {e}")
        vote_key = f"day_{vote_req.day_index}_act_{vote_req.activity_index}"
        if vote_key in current_ai_data.get("regenerating_keys", {}):
            del current_ai_data["regenerating_keys"][vote_key]
            supabase.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()


@app.post("/api/itineraries/{itinerary_id}/vote-regenerate")
async def vote_regenerate(
    itinerary_id: str,
    vote_req: VoteRequest,
    bg_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
):
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")
        
    result = supabase.table("itineraries").select("id, ai_data, destination").eq("id", itinerary_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Itinerary not found.")
        
    trip = result.data[0]
    ai_data = trip.get("ai_data", {})
    
    votes_dict = ai_data.setdefault("votes", {})
    vote_key = f"day_{vote_req.day_index}_act_{vote_req.activity_index}"
    vote_arr = votes_dict.setdefault(vote_key, [])
    
    # Check if already regenerating
    if ai_data.get("regenerating_keys", {}).get(vote_key) is True:
        return {"status": "already_regenerating"}
    
    # Add vote if pure new user
    if not any(v.get("id") == vote_req.voter.id for v in vote_arr):
        vote_arr.append(vote_req.voter.model_dump())
        
    # Evaluate > 50% majority strictly
    majority_threshold = math.floor(vote_req.total_online / 2.0)
    
    if len(vote_arr) > majority_threshold:
        # Trigger bg task
        bg_tasks.add_task(_bg_regenerate, itinerary_id, vote_req, ai_data, trip)
        return {"status": "regeneration_started"}
        
    # Just update DB with new vote tally
    supabase.table("itineraries").update({"ai_data": ai_data}).eq("id", itinerary_id).execute()
    return {"status": "vote_recorded"}

# ── PROTECTED: Delete Itinerary ──────────────────────────────────

@app.delete("/api/itineraries/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    """Delete a specific itinerary (only if owned by the user)."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        result = (
            supabase
            .table("itineraries")
            .delete()
            .eq("id", itinerary_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Itinerary not found.")

        logger.info(f"[DB] Deleted itinerary {itinerary_id} for user {user_id}")
        return {"status": "deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DB] Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


# ── COMMUNITY: Discover Feed ────────────────────────────────────

@app.get("/api/community/feed", response_model=List[CommunityItinerary])
async def get_community_feed(
    sort_by: str = "likes",  # "likes" or "newest"
    user_id: Optional[str] = Depends(get_optional_user),
):
    """Fetch public itineraries with author details."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        query = (
            supabase
            .table("itineraries")
            .select("*, profiles!itineraries_user_id_fkey(display_name, avatar_url)")
            .eq("is_public", True)
        )

        if sort_by == "likes":
            query = query.order("likes_count", desc=True)
        else:
            query = query.order("created_at", desc=True)

        result = query.limit(50).execute()
        
        # Format the join result and check likes
        feed_items = []
        
        # Get all likes for the current user in one go if they are logged in
        user_likes = set()
        if user_id:
            likes_res = supabase.table("itinerary_likes").select("itinerary_id").eq("user_id", user_id).execute()
            user_likes = {l["itinerary_id"] for l in likes_res.data}

        for item in result.data:
            profile = item.get("profiles", {})
            feed_items.append(CommunityItinerary(
                id=item["id"],
                user_id=item["user_id"],
                title=item["title"],
                destination=item["destination"],
                start_date=item.get("start_date"),
                end_date=item.get("end_date"),
                likes_count=item.get("likes_count", 0),
                forks_count=item.get("forks_count", 0),
                is_public=item["is_public"],
                created_at=item["created_at"],
                ai_data=item["ai_data"],
                author_name=profile.get("display_name", "Unknown"),
                author_avatar=profile.get("avatar_url"),
                is_liked_by_me=item["id"] in user_likes
            ))

        return feed_items

    except Exception as e:
        logger.error(f"[Community] Feed failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── COMMUNITY: Like/Unlike ──────────────────────────────────────

@app.post("/api/community/like/{itinerary_id}")
async def toggle_like(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    """Toggle a like on an itinerary."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        # Check if already liked
        existing = (
            supabase.table("itinerary_likes")
            .select("*")
            .eq("user_id", user_id)
            .eq("itinerary_id", itinerary_id)
            .execute()
        )

        if existing.data:
            # Unlike: Remove entry and decrement count
            supabase.table("itinerary_likes").delete().eq("user_id", user_id).eq("itinerary_id", itinerary_id).execute()
            
            # Using RPC or manual update (Manual here for simplicity, but RPC is better for atomicity)
            # Fetch current count first
            res = supabase.table("itineraries").select("likes_count").eq("id", itinerary_id).execute()
            new_count = max(0, (res.data[0].get("likes_count") or 0) - 1)
            supabase.table("itineraries").update({"likes_count": new_count}).eq("id", itinerary_id).execute()
            
            return {"status": "unliked", "likes_count": new_count}
        else:
            # Like: Add entry and increment count
            supabase.table("itinerary_likes").insert({
                "user_id": user_id,
                "itinerary_id": itinerary_id
            }).execute()
            
            res = supabase.table("itineraries").select("likes_count").eq("id", itinerary_id).execute()
            new_count = (res.data[0].get("likes_count") or 0) + 1
            supabase.table("itineraries").update({"likes_count": new_count}).eq("id", itinerary_id).execute()
            
            return {"status": "liked", "likes_count": new_count}

    except Exception as e:
        logger.error(f"[Community] Like toggle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── COMMUNITY: Fork (Clone) ─────────────────────────────────────

@app.post("/api/community/fork/{itinerary_id}")
async def fork_itinerary(
    itinerary_id: str,
    user_id: str = Depends(get_current_user),
):
    """Clone a public itinerary for the current user."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        # 1. Fetch source itinerary
        source_res = supabase.table("itineraries").select("*").eq("id", itinerary_id).execute()
        if not source_res.data:
            raise HTTPException(status_code=404, detail="Itinerary not found.")
        
        source = source_res.data[0]
        
        # 2. Create the clone
        new_itinerary = {
            "user_id": user_id,
            "title": f"{source['title']} (Copy)",
            "destination": source["destination"],
            "start_date": source.get("start_date"),
            "end_date": source.get("end_date"),
            "is_public": False,
            "ai_data": source["ai_data"],
            "likes_count": 0,
            "forks_count": 0
        }
        
        clone_res = supabase.table("itineraries").insert(new_itinerary).execute()
        
        # 3. Increment original's fork count
        new_forks_count = (source.get("forks_count") or 0) + 1
        supabase.table("itineraries").update({"forks_count": new_forks_count}).eq("id", itinerary_id).execute()
        
        logger.info(f"[Community] User {user_id} forked itinerary {itinerary_id}")
        return {"status": "forked", "new_id": clone_res.data[0]["id"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Community] Fork failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
