from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from models import UserInput, FinalTripPlan
from agent_experience import generate_experience_itinerary
from agent_logistics import generate_logistics
from auth_middleware import get_current_user
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
        logistics_result = await generate_logistics(user_input, experience_result)

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
    """Fetch a single itinerary by ID (only if owned by the requesting user)."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured.")

    try:
        result = (
            supabase
            .table("itineraries")
            .select("id, title, destination, start_date, end_date, is_public, created_at, ai_data")
            .eq("id", itinerary_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Itinerary not found.")

        logger.info(f"[DB] Fetched itinerary {itinerary_id} for user {user_id}")
        return result.data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DB] Fetch single failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch itinerary: {str(e)}")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
