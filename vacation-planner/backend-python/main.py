from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import UserInput, AgentOneOutput
from agent_experience import generate_experience_itinerary
from loguru import logger
import sys

# Configure logger to show DEBUG messages
logger.remove()
logger.add(sys.stderr, level="DEBUG")

app = FastAPI(title="AI Travel Planner Backend (Free Stack)")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific frontend origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Travel Planner - Zero-Cost API Backend is running"}

@app.post("/api/generate-itinerary", response_model=AgentOneOutput)
async def generate_itinerary(user_input: UserInput):
    """
    Endpoint to trigger Agent 1 (The Experience Guide) using Google Gemini and DuckDuckGo.
    """
    try:
        logger.info(f"Received request for itinerary: {user_input}")
        itinerary = await generate_experience_itinerary(user_input)
        return itinerary
    except HTTPException as e:
        # Re-raise HTTPExceptions so FastAPI can handle them (e.g., 504 timeouts)
        raise e
    except Exception as e:
        logger.error(f"Failed to generate itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
