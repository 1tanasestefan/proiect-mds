# VibeTrips FastAPI Backend

FastAPI backend for local AI travel planning. The experience, logistics, and regeneration agents use a local Ollama-compatible model instead of hosted AI API keys.

## Tech Stack

- FastAPI and Uvicorn
- Pydantic v2 response contracts
- Local Ollama chat endpoint for AI agents
- DuckDuckGo image search through `ddgs`
- OpenStreetMap Nominatim and OSRM for keyless map/routing data
- Supabase for auth, saved trips, likes, forks, and profiles

## Setup

1. Install and start Ollama.

2. Pull a local model:

   ```powershell
   ollama pull llama3.1:8b
   ```

3. Install Python dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create `.env` from `.env.template` and configure:

   ```env
   LOCAL_LLM_BASE_URL=http://localhost:11434
   LOCAL_LLM_MODEL=llama3.1:8b
   SUPABASE_URL=...
   SUPABASE_KEY=...
   SUPABASE_JWT_SECRET=...
   ```

5. Run the backend:

   ```powershell
   python main.py
   ```

The server runs at `http://localhost:8000`.

## Notes

- No Groq, Gemini, or Pexels key is required for agent generation or image enrichment.
- If Ollama is not running, the backend uses deterministic fallback planners so the frontend still receives valid JSON.
- Supabase credentials are still needed for authenticated persistence and community features.

## Agent Evaluation

Run the offline evaluator before demos or pull requests:

```powershell
python agent_eval.py --mode offline --threshold 0.75
```

The offline mode scores the deterministic experience and logistics paths used when the local LLM is unavailable. It checks itinerary shape, activity quality, destination relevance, logistics options, concrete booking links, budget consistency, assumptions, and route signal.

To evaluate the full orchestrator with live local generation and network enrichment:

```powershell
python agent_eval.py --mode live --threshold 0.75 --output eval-results/latest.md
```

CI runs the offline evaluator so regressions in the critical agent contracts fail automatically.
