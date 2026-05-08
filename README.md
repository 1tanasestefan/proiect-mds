# VibeTrips - AI Travel Planner

VibeTrips is an AI-powered travel planning app. Users can generate personalized vacation itineraries, save trips to their account, publish public itineraries, discover community trips, and collaborate on saved plans.

The project is built as a multi-part app:

- `vacation-planner/frontend` - Next.js frontend
- `vacation-planner/backend` - FastAPI backend with AI travel agents

For local development, run the FastAPI backend and the Next.js frontend.

## Main Features

- AI-generated day-by-day travel itineraries
- Experience agent for activities, local places, and travel vibe
- Logistics agent for flights, hotels, budgets, and transport options
- Saved itineraries with Supabase authentication
- Dashboard for personal trips
- Public Discover feed
- Like and fork public itineraries
- Multiplayer trip viewing with activity highlights
- Voting flow to regenerate disliked activities

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, PydanticAI
- AI provider: Groq
- Database/auth: Supabase
- Images: Pexels API
- Maps/transport UI: Leaflet-based frontend components

## Prerequisites

Install these before running the project:

- Node.js 20 or newer
- npm
- Python 3.12 or newer
- Git

## Environment Setup

Never commit real API keys or `.env` files.

### Backend env

Create this file:

```powershell
cd "vacation-planner/backend"
copy .env.template .env
```

Fill in:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
PEXELS_API_KEY=your_pexels_api_key
PORT=8000
```

Important:

- `SUPABASE_KEY` must be the Supabase `service_role` key.
- This key is backend-only. Do not put it in the frontend.

### Frontend env

Create this file:

```powershell
cd "../frontend"
notepad .env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_public_key
```

Important:

- `NEXT_PUBLIC_SUPABASE_ANON_KEY` must be the Supabase `anon` / `public` key.
- Do not use the `service_role` key in the frontend.

## How To Run Locally

Open two PowerShell terminals.

### Terminal 1 - Backend

```powershell
cd "vacation-planner/backend"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend should run at:

```text
http://localhost:8000
```

Check it with:

```text
http://localhost:8000
```

Expected response:

```json
{"message":"AI Travel Planner - Zero-Cost API Backend is running"}
```

### Terminal 2 - Frontend

```powershell
cd "vacation-planner/frontend"
npm install
npm run dev
```

The frontend should run at:

```text
http://localhost:3000
```

Open it in your browser.

## Supabase Setup

The backend expects Supabase tables and policies to exist.

Run this SQL in the Supabase SQL Editor:

```text
vacation-planner/backend/schema.sql
```

Then get your keys from:

```text
Supabase Dashboard -> Project Settings -> API
```

Use:

- `service_role` key in `backend/.env`
- `anon` / `public` key in `frontend/.env.local`

## Useful Local Checks

Backend dependency/database diagnostic:

```powershell
cd "vacation-planner/backend"
.\.venv\Scripts\activate
python test_db.py
```

Frontend build check:

```powershell
cd "vacation-planner/frontend"
npm run build
```

Git status:

```powershell
git status --short
```

Make sure `.env` and `.env.local` files are not staged.

## Common Problems

### Frontend login/register does not work

Check `vacation-planner/frontend/.env.local`.

It must contain:

```env
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

Restart the frontend after changing env values.

### Trip generation fails

Check:

- backend is running on port `8000`
- `GROQ_API_KEY` is valid
- `PEXELS_API_KEY` is valid
- frontend uses `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

### Saving trips fails

Check:

- user is logged in
- Supabase schema was applied
- backend has `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_JWT_SECRET`
- frontend has Supabase anon key

### Python install is slow

`pydantic-ai` pulls many optional AI dependencies, so the first install can take a few minutes.

If installation gets stuck after an interrupted run, close lingering Python processes and retry:

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|pip' }
```

## Project Structure

```text
proiect-mds/
  README.md
  vacation-planner/
    backend/
      main.py
      agent_experience.py
      agent_logistics.py
      agent_regenerate.py
      schema.sql
      requirements.txt
    frontend/
      src/app/
      src/components/
      src/context/
      src/hooks/
      package.json
```

## Notes For MDS Evaluation

This project includes multiple AI agents as part of the product:

- Experience Guide agent
- Logistics and Booking agent
- Activity Regeneration agent

Remaining process artifacts should be added under a future `docs/` folder:

- user stories and backlog
- architecture and workflow diagrams
- automated tests and agent evals
- bug report and pull request evidence
- CI/CD workflow
- report about AI tool usage during development
