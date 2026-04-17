from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from models import UserInput, FinalTripPlan, ItineraryUpdate, VoteRequest, CommunityItinerary
from agent_experience import generate_experience_itinerary
from agent_regenerate import regenerate_single_activity
import math
import json
from fastapi import BackgroundTasks
from agent_logistics import generate_logistics
from auth_middleware import get_current_user, get_optional_user
from database import supabase
from loguru import logger
import sys

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


# ── PUBLIC: Generate Itinerary (No auth required) ────────────────

@app.post("/api/generate-itinerary", response_model=FinalTripPlan)
async def generate_itinerary(user_input: UserInput):
    """
    Master Orchestrator: chains Agent 1 (Experience) → Agent 2 (Logistics).
    Returns the combined FinalTripPlan to the frontend.
    """
    try:
        logger.info(f"[Orchestrator] Step 1: Experience Agent for {user_input.destination}")
        experience_result = await generate_experience_itinerary(user_input)

        logger.info(f"[Orchestrator] Step 2: Logistics Agent for {user_input.destination}")
        logistics_context = f"Origin: {user_input.origin}, Destination: {user_input.destination}, Check-in: {user_input.start_date}, Check-out: {user_input.end_date}. Provide flight and hotel estimates."
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
