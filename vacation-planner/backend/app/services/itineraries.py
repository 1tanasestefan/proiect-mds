from __future__ import annotations
from fastapi import HTTPException
from loguru import logger

from app.services.collaboration import require_edit_access, require_trip_access
from app.db.supabase import require_supabase
from models import ItineraryUpdate


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
        trip, _role = require_trip_access(db, itinerary_id, user_id)
        logger.info(f"[DB] Fetched itinerary {itinerary_id} for user {user_id}")
        return trip

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DB] Fetch single failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch itinerary: {str(e)}")


async def update_itinerary(itinerary_id: str, update_data: ItineraryUpdate, user_id: str) -> dict:
    db = require_supabase()

    try:
        require_edit_access(db, itinerary_id, user_id)
        payload = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not payload:
            return {"status": "no_changes"}

        result = (
            db.table("itineraries")
            .update(payload)
            .eq("id", itinerary_id)
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
