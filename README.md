# VibeTrips - AI Travel Planner

VibeTrips is an AI-assisted travel planning application built for generating, saving, sharing, and improving vacation itineraries. A user can enter travel preferences, generate a personalized day-by-day plan, review logistics and budget recommendations, save the trip, publish it to a community feed, and collaborate through reactions, voting, and activity regeneration.

The active product is split into:

- `vacation-planner/frontend` - Next.js frontend application
- `vacation-planner/backend` - FastAPI backend with local AI agents, Supabase persistence, tests, and agent evaluations

The repository also contains older prototype code, but the active backend used by the current application is `vacation-planner/backend`.

## Features

- AI-generated vacation itineraries based on destination, origin, budget, dates, lifestyle, vacation type, and number of travelers
- Flexible destination and flexible date recommendations
- Experience Agent for daily activities, local places, trip vibe, activity descriptions, locations, costs, and image enrichment
- Logistics Agent for flights, accommodation, local transport, assumptions, and budget breakdowns
- Activity Regeneration Agent for replacing activities based on user feedback and voting
- Supabase authentication with login, register, forgot password, reset password, and protected routes
- Saved itineraries and personal dashboard
- Public Discover feed for shared trips
- Like/unlike and fork flows for public itineraries
- Shared trip viewing, activity reactions, and collaboration-oriented trip state
- Transport/map UI with Leaflet-based components
- Docker setup for running frontend and backend together
- CI pipeline with frontend build, backend tests, agent evals, and Java legacy build check

## Architecture

The frontend collects user preferences and displays the generated trip. The FastAPI backend orchestrates recommendation logic, AI agents, persistence, and community/collaboration APIs.

```text
User
  |
  v
Next.js Frontend
  |
  v
FastAPI Backend
  |
  +--> Experience Agent
  +--> Logistics Agent
  +--> Regeneration Agent
  +--> Supabase Auth + Database
  +--> Image, geocoding, map, and routing helpers
```

Main backend flow:

1. The frontend sends trip preferences to `POST /api/generate-itinerary`.
2. The backend optionally resolves flexible destination/date preferences.
3. The Experience Agent generates the day-by-day itinerary.
4. The Logistics Agent receives the trip context and activity anchors, then adds transport, accommodation, and budget information.
5. The backend validates and returns a structured `FinalTripPlan`.
6. Authenticated users can save, publish, react to, fork, and regenerate parts of the trip.

## Tech Stack

### Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Radix UI components
- lucide-react icons
- motion, GSAP, and Lenis for interaction and animation
- Leaflet and React Leaflet for map/transport UI
- Recharts for dashboard-style visual elements
- Supabase JavaScript client for auth/session handling

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- httpx
- python-dotenv
- loguru
- Supabase Python client
- python-jose for JWT validation
- pytest

### AI and Data Enrichment

- Local Ollama-compatible model through `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`
- Deterministic fallback planners when local generation is unavailable
- Custom Experience, Logistics, and Regeneration agents
- Offline agent evaluation scenarios
- Keyless image enrichment through `ddgs` plus fallback behavior
- OpenStreetMap/Nominatim-style geocoding and routing helpers where available

### DevOps

- GitHub Actions CI
- Docker and Docker Compose
- npm build checks
- pytest backend suite
- offline agent eval threshold checks
- Maven check for the legacy Java module while it remains in the repo

## Project Structure

```text
proiect-mds/
  README.md
  .github/
    workflows/
      ci.yml
  vacation-planner/
    docker-compose.yml
    docs/
      backlog.md
    backend/
      main.py
      agent_experience.py
      agent_logistics.py
      agent_regenerate.py
      agent_eval.py
      local_llm.py
      models.py
      schema.sql
      requirements.txt
      app/
        api/routes/
        core/
        db/
        services/
      tests/
    frontend/
      package.json
      src/app/
      src/components/
      src/context/
      src/hooks/
      src/lib/
```

## Prerequisites

Install:

- Node.js 20 or newer
- npm
- Python 3.12 or newer
- Git

Optional:

- Ollama, if you want live local AI generation instead of deterministic fallback output
- Docker, if you want to run both services with Docker Compose

## Environment Setup

Never commit real API keys or `.env` files.

### Backend

Create `vacation-planner/backend/.env` from the template:

```bash
cd vacation-planner/backend
cp .env.template .env
```

Fill in:

```env
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1:8b
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
PORT=8000
```

Notes:

- `SUPABASE_KEY` must be the Supabase `service_role` key and must stay backend-only.
- Do not place the `service_role` key in the frontend.
- For live local AI, install Ollama and run `ollama pull llama3.1:8b`.
- If Ollama is unavailable, the backend can still use deterministic fallbacks for stable demos and tests.

### Frontend

Create `vacation-planner/frontend/.env.local`:

```bash
cd vacation-planner/frontend
touch .env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_ITINERARY_API_URL=http://127.0.0.1:8000/api/generate-itinerary
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_public_key
```

Notes:

- `NEXT_PUBLIC_SUPABASE_ANON_KEY` should be the Supabase anon/public key.
- Frontend environment variables prefixed with `NEXT_PUBLIC_` are visible in the browser.

## Supabase Setup

The backend expects the Supabase schema to exist before authenticated persistence and community features are used.

Run the SQL from:

```text
vacation-planner/backend/schema.sql
```

Then configure:

- backend `.env`: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_JWT_SECRET`
- frontend `.env.local`: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Run Locally

Open two terminals.

### Terminal 1 - Backend

```bash
cd vacation-planner/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

On Windows PowerShell:

```powershell
cd vacation-planner/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend URL:

```text
http://localhost:8000
```

### Terminal 2 - Frontend

```bash
cd vacation-planner/frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

## Run With Docker

Create the same environment files first:

- `vacation-planner/backend/.env`
- `vacation-planner/frontend/.env.local`

Then run:

```bash
cd vacation-planner
docker compose up --build
```

Ports:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

If the backend container must call Ollama running on the host, use:

```env
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434
```

On Linux, replace `host.docker.internal` with the correct host gateway address if needed.

## Tests And Quality Checks

### Backend tests

```bash
cd vacation-planner/backend
source .venv/bin/activate
pytest -q
```

The backend tests cover:

- route behavior
- Pydantic model contracts
- recommendation logic
- planning orchestration
- logistics agent behavior
- experience output sanitization
- security/JWT behavior
- agent eval helpers

### Agent evaluation

Offline mode runs deterministic scenarios and checks the quality of the agent contracts without requiring a live local model:

```bash
cd vacation-planner/backend
source .venv/bin/activate
python agent_eval.py --mode offline --threshold 0.75 --json
```

Live mode can be used when Ollama and enrichment services are available:

```bash
python agent_eval.py --mode live --threshold 0.75 --output eval-results/latest.md
```

### Frontend build

```bash
cd vacation-planner/frontend
npm run build
```

### Java legacy build

The active backend is Python/FastAPI. The Java module is legacy/prototype code, but CI still checks that it builds while it remains in the repo:

```bash
cd vacation-planner/backend
mvn test
```

## CI Pipeline

GitHub Actions is configured in:

```text
.github/workflows/ci.yml
```

The CI workflow runs on pushes and pull requests targeting `main`.

Jobs:

- `Frontend build`: installs frontend dependencies and runs `npm run build`
- `Python backend import check`: installs backend dependencies, verifies imports, runs `pytest`, and runs offline agent evaluation
- `Java backend build`: runs `mvn test` for the legacy Java module

## Useful Commands

```bash
git status --short
```

```bash
cd vacation-planner/backend
python test_db.py
```

```bash
cd vacation-planner/frontend
npm run lint
```

## Common Problems

### Frontend login/register does not work

Check `vacation-planner/frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

Restart the frontend after changing environment variables.

### Trip generation fails

Check:

- backend is running on port `8000`
- frontend uses `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`
- itinerary generation uses `NEXT_PUBLIC_ITINERARY_API_URL=http://127.0.0.1:8000/api/generate-itinerary`
- if using live local AI, Ollama is running at `LOCAL_LLM_BASE_URL`
- `LOCAL_LLM_MODEL` is pulled locally, for example `ollama pull llama3.1:8b`

### Saving trips fails

Check:

- the user is logged in
- Supabase schema was applied
- backend has `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_JWT_SECRET`
- frontend has `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Documentation

Project process documentation lives under:

```text
vacation-planner/docs/
```

Current docs:

- `backlog.md` - user stories, bug backlog, and technical tasks

## Demo Notes

A good demo flow:

1. Open the app and explain the travel planning problem.
2. Generate an itinerary from the `/plan` page.
3. Show the day-by-day experience output.
4. Show logistics, budget, transport, and accommodation recommendations.
5. Save the itinerary.
6. Open the dashboard and trip details page.
7. Show Discover, public trips, likes, forks, and collaboration/regeneration behavior.
8. Show GitHub Actions CI and explain backend tests plus agent evaluations.
