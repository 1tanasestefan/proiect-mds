# VibeTrips Project Brief

## Overview

VibeTrips is an AI travel planning application that helps users generate, save, share, and explore vacation itineraries. The main app is split into a Next.js frontend and a FastAPI AI backend.

## Project Structure

- `frontend/`: Next.js app used by travelers.
- `backend/`: FastAPI backend that handles AI itinerary generation, authentication checks, persistence, and community features.

## Technologies Used

- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS.
- UI and UX: Radix UI, lucide-react, motion, GSAP, Lenis, Sonner, Recharts.
- Maps: Leaflet and React Leaflet.
- Backend: Python, FastAPI, Uvicorn, Pydantic.
- AI: local Ollama-compatible model, custom experience/logistics/regeneration agents, deterministic fallbacks.
- Database and auth: Supabase, Supabase Auth, PostgreSQL-style schema, JWT validation.
- External services: keyless DuckDuckGo image search, OpenStreetMap Nominatim, and OSRM routing.

## Main Functionality

- User authentication with login, register, logout, protected routes, and Supabase session handling.
- AI itinerary generation from user preferences such as budget, lifestyle, vacation type, origin, destination, dates, and number of travelers.
- Flexible destination recommendations based on budget, selected travel style, and previous user signals.
- Flexible date recommendations using simple seasonal rules and budget-aware travel windows.
- Multi-agent trip planning: an experience agent creates day-by-day activities, while a logistics agent adds flights, accommodation, budget estimates, transport legs, and map data.
- Trip results view with itinerary details, activities, images, costs, locations, logistics, and reset/regenerate flow.
- Save generated itineraries to the authenticated user's account.
- Personal dashboard for viewing saved trips, travel stats, spotlight destinations, and public/private trip status.
- Individual trip pages for viewing saved plans and shared trip links.
- Edit saved itineraries, including title, destination, dates, visibility, and stored AI data.
- Delete owned itineraries.
- Publish itineraries publicly through the `is_public` flag.
- Community Discover feed with public itineraries sorted by trending likes or newest.
- Like and unlike public itineraries.
- Fork public itineraries into the current user's private saved trips.
- Multiplayer-style trip viewing support through shared itinerary access.
- Group voting to regenerate disliked activities; when a majority votes, the backend regenerates that activity in the background.
- Transport map support for displaying route and transit data.

## Backend API Summary

- `GET /`: health/status endpoint.
- `POST /api/recommend-destinations`: returns destination suggestions.
- `POST /api/generate-itinerary`: generates the final AI trip plan.
- `POST /api/itineraries/save`: saves a generated itinerary.
- `GET /api/itineraries/me`: lists the current user's itineraries.
- `GET /api/itineraries/{id}`: fetches one itinerary.
- `PATCH /api/itineraries/{id}`: updates an owned itinerary.
- `DELETE /api/itineraries/{id}`: deletes an owned itinerary.
- `POST /api/itineraries/{id}/vote-regenerate`: records votes and triggers activity regeneration.
- `GET /api/community/feed`: returns public community itineraries.
- `POST /api/community/like/{id}`: toggles a like.
- `POST /api/community/fork/{id}`: clones a public trip into the user's account.

## Database Summary

Supabase stores user profiles, itineraries, itinerary likes, collections, and collection-itinerary relations. Itineraries keep the generated AI plan in a JSONB `ai_data` field and include metadata such as destination, dates, visibility, likes, forks, and ownership.

## Brief Check Notes

- The active local development path is `backend/` plus `frontend/`.
- The root README already contains setup and run instructions.
- Older local folders such as `backend-python/` are legacy leftovers and should not be used for current development.
- Environment variables are required for Supabase persistence; local AI uses `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`.
