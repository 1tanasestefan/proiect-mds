from __future__ import annotations
from agent_experience import generate_experience_itinerary
from agent_logistics import generate_logistics
from app.db.supabase import supabase
from app.factory import create_app
from app.services.recommendations import (
    DESTINATION_CATALOG,
    DEFAULT_DATE_WINDOWS,
    SEASONAL_DATE_WINDOWS,
    recommend_dates_for,
    recommend_destination,
    recommend_destinations,
)

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
