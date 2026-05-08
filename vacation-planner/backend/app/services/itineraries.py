import json
import math

from fastapi import BackgroundTasks, HTTPException
from loguru import logger

from agent_regenerate import regenerate_single_activity
from app.db.supabase import require_supabase
from models import ItineraryUpdate, VoteRequest


async def save_itinerary(payload, user_id: str) -> dict:
    db = require_supabase()

    try:
        result = db.table("itineraries").insert(
            {
                "user_id": user_id,
                "title": payload.title,
                "destination": payload.destination,
                "start_date": payload.start_date,
                "end_date": payload.end_date,
                "is_public": payload.is_public,
                "ai_data": payload.ai_data,
            }
        ).execute()

        logger.info(f"[DB] Saved itinerary '{payload.title}' for user {user_id}")
        return {"status": "saved", "itinerary_id": result.data[0]["id"]}

    except Exception as e:
        logger.error(f"[DB] Save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save itinerary: {str(e)}")


async def get_my_itineraries(user_id: str) -> dict:
    db = require_supabase()

    try:
        result = (
            db.table("itineraries")
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


async def get_itinerary(itinerary_id: str, user_id: str) -> dict:
    db = require_supabase()

    try:
        result = (
            db.table("itineraries")
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


async def update_itinerary(itinerary_id: str, update_data: ItineraryUpdate, user_id: str) -> dict:
    db = require_supabase()

    try:
        payload = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not payload:
            return {"status": "no_changes"}

        result = (
            db.table("itineraries")
            .update(payload)
            .eq("id", itinerary_id)
            .eq("user_id", user_id)
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


async def delete_itinerary(itinerary_id: str, user_id: str) -> dict:
    db = require_supabase()

    try:
        result = (
            db.table("itineraries")
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


async def _bg_regenerate(itinerary_id: str, vote_req: VoteRequest, current_ai_data: dict, current_trip: dict):
    db = require_supabase()
    vote_key = f"day_{vote_req.day_index}_act_{vote_req.activity_index}"

    try:
        current_ai_data.setdefault("regenerating_keys", {})
        current_ai_data["regenerating_keys"][vote_key] = True

        if "votes" in current_ai_data and vote_key in current_ai_data["votes"]:
            current_ai_data["votes"][vote_key] = []

        db.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()

        day_obj = current_ai_data["experience"]["itinerary"][vote_req.day_index]
        old_act = day_obj["activities"][vote_req.activity_index]
        day_context = json.dumps([a["title"] for i, a in enumerate(day_obj["activities"]) if i != vote_req.activity_index])

        destination = current_trip.get("destination", "Unknown")
        vibe_summary = current_ai_data["experience"].get("vibe_summary", "")

        new_act = await regenerate_single_activity(vibe_summary, day_context, destination, json.dumps(old_act))
        current_ai_data["experience"]["itinerary"][vote_req.day_index]["activities"][vote_req.activity_index] = new_act.model_dump()

        if vote_key in current_ai_data["regenerating_keys"]:
            del current_ai_data["regenerating_keys"][vote_key]

        db.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()
        logger.info(f"Regeneration complete for {vote_key} on iter {itinerary_id}")

    except Exception as e:
        logger.error(f"Background regeneration failed: {e}")
        if vote_key in current_ai_data.get("regenerating_keys", {}):
            del current_ai_data["regenerating_keys"][vote_key]
            db.table("itineraries").update({"ai_data": current_ai_data}).eq("id", itinerary_id).execute()


async def vote_regenerate(
    itinerary_id: str,
    vote_req: VoteRequest,
    bg_tasks: BackgroundTasks,
    user_id: str,
) -> dict:
    db = require_supabase()

    result = db.table("itineraries").select("id, ai_data, destination").eq("id", itinerary_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Itinerary not found.")

    trip = result.data[0]
    ai_data = trip.get("ai_data", {})

    votes_dict = ai_data.setdefault("votes", {})
    vote_key = f"day_{vote_req.day_index}_act_{vote_req.activity_index}"
    vote_arr = votes_dict.setdefault(vote_key, [])

    if ai_data.get("regenerating_keys", {}).get(vote_key) is True:
        return {"status": "already_regenerating"}

    if not any(v.get("id") == vote_req.voter.id for v in vote_arr):
        vote_arr.append(vote_req.voter.model_dump())

    majority_threshold = math.floor(vote_req.total_online / 2.0)

    if len(vote_arr) > majority_threshold:
        bg_tasks.add_task(_bg_regenerate, itinerary_id, vote_req, ai_data, trip)
        return {"status": "regeneration_started"}

    db.table("itineraries").update({"ai_data": ai_data}).eq("id", itinerary_id).execute()
    logger.info(f"[DB] User {user_id} voted to regenerate {vote_key} on itinerary {itinerary_id}")
    return {"status": "vote_recorded"}
