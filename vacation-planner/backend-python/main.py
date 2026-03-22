from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import UserInput, FinalTripPlan
from agent_experience import generate_experience_itinerary
from agent_logistics import generate_logistics
from loguru import logger
import sys

# Configure logger to show DEBUG messages
logger.remove()
logger.add(sys.stderr, level="DEBUG")

app = FastAPI(title="AI Travel Planner Backend (Zero-Cost Stack)")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Travel Planner - Zero-Cost API Backend is running"}

@app.post("/api/generate-itinerary", response_model=FinalTripPlan)
async def generate_itinerary(user_input: UserInput):
    """
    Master Orchestrator: chains Agent 1 (Experience) → Agent 2 (Logistics).
    Returns the combined FinalTripPlan to the frontend.
    """
    try:
        # ── Step 1: Run Agent 1 (Experience Guide) ──
        logger.info(f"[Orchestrator] Step 1: Experience Agent for {user_input.destination}")
        experience_result = await generate_experience_itinerary(user_input)

        # ── Step 2: Run Agent 2 (Logistics & Booking) ──
        logger.info(f"[Orchestrator] Step 2: Logistics Agent for {user_input.destination}")
        logistics_result = await generate_logistics(user_input, experience_result)

        # ── Step 3: Combine into FinalTripPlan ──
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
