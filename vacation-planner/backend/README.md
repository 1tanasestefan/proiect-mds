# AI Travel Planner - FastAPI Backend

This is the only backend for the VibeTrips app. It handles itinerary generation, Supabase-backed saved trips, community actions, and JWT verification for authenticated requests.

## Tech Stack

- **Framework:** FastAPI
- **Agent Model:** Groq-compatible agent services via `pydantic-ai`
- **Search Tool:** DuckDuckGo Search (`duckduckgo-search`)
- **Data Contracts:** Pydantic v2

## Setup Instructions

1. **Activate Virtual Environment:**
   ```powershell
   cd vacation-planner/backend
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. **Install Requirements:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **API Keys:**
   - Create a `.env` file from `.env.template`.
   - Add the backend-only Supabase `service_role` key.
   - Add your AI and image provider keys.

4. **Run the Backend:**
   ```powershell
   python main.py
   ```
   Server runs at `http://localhost:8000`.

## Features

- **Agent 1 (Experience Guide):** Uses the configured AI provider and search tools to find real activities matching user vibes.
- **Agent 2 (Logistics):** Adds flights, stays, budgets, and transport options.
- **Persistence:** Saves itineraries and community interactions through Supabase.
- **Robustness:** DDG search is wrapped in error handling to prevent pipeline failures.
- **Typed Output:** Strictly validated JSON responses using PydanticAI.
