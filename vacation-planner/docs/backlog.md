# VibeTrips Backlog

This backlog summarizes the main product stories, technical tasks, and bug-fix work completed for the VibeTrips AI travel planner.

## Project Scope

VibeTrips is an AI-assisted travel planning application. Users can generate personalized vacation itineraries, receive logistics and budget recommendations, save trips, publish itineraries, discover community trips, and collaborate through reactions, voting, and regeneration flows.

## User Stories

### Story 1 - AI itinerary generation

**As a** traveler, **I want** to enter my travel preferences and generate a complete itinerary, **so that** I can quickly plan a vacation without manually searching across many websites.

**Acceptance criteria:**

- The user can enter budget, lifestyle, vacation type, origin, destination, dates, and number of travelers.
- The frontend sends the request to the backend itinerary endpoint.
- The backend returns a structured trip plan.
- The UI displays the generated plan with daily activities and trip details.

**Status:** Done

### Story 2 - Experience Agent for daily activities

**As a** traveler, **I want** the application to generate daily activities adapted to my trip style, **so that** the itinerary feels personal and useful.

**Acceptance criteria:**

- The Experience Agent generates a day-by-day activity plan.
- Each activity includes title, time, location, description, type, and estimated cost.
- The generated activities are shown in the frontend itinerary view.
- The output is sanitized to avoid missing or malformed fields.

**Status:** Done

### Story 3 - Logistics Agent for transport, accommodation, and budget

**As a** traveler, **I want** the app to recommend flights, accommodation, transport, and budget estimates, **so that** I can understand the practical cost of the trip.

**Acceptance criteria:**

- The Logistics Agent receives the trip context and generated activity anchors.
- The final plan includes flight options, accommodation options, transport information, assumptions, and budget breakdown.
- Booking links and positive price estimates are included where applicable.
- Backend tests verify logistics contract quality.

**Status:** Done

### Story 4 - Local AI model integration and deterministic fallback

**As a** demo team, **I want** local AI generation with a stable fallback, **so that** the product can still work if the local model or hardware is unreliable.

**Acceptance criteria:**

- The backend can call an Ollama-compatible local model using `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`.
- If the local model fails, deterministic fallback generation still returns valid JSON.
- Offline agent evaluations can run without requiring a live model.
- The README documents local model setup.

**Status:** Done

### Story 5 - Flexible destination recommendations

**As a** user who is undecided, **I want** to mark the destination as flexible, **so that** the app can recommend a suitable destination based on my preferences.

**Acceptance criteria:**

- The frontend supports a flexible destination option.
- The backend can recommend destinations from user preferences and travel signals.
- The selected recommendation is used in itinerary generation when no destination is provided.

**Status:** Done

### Story 6 - Flexible date recommendations

**As a** user with flexible travel dates, **I want** the app to recommend a travel window, **so that** I can receive a plan without manually choosing exact dates.

**Acceptance criteria:**

- The frontend supports flexible date selection.
- The backend selects a date window based on destination and budget.
- The final generated plan includes the selected start and end dates.

**Status:** Done

### Story 7 - User authentication

**As a** user, **I want** to register, log in, and keep a session, **so that** I can save and manage my trips.

**Acceptance criteria:**

- The app supports register, login, logout, forgot password, and reset password pages.
- The frontend stores the Supabase session.
- Protected API operations send the access token to the backend.
- Backend security tests validate JWT-related behavior.

**Status:** Done

### Story 8 - Save generated itineraries

**As a** logged-in user, **I want** to save a generated itinerary, **so that** I can return to it later.

**Acceptance criteria:**

- The user can save a generated plan from the itinerary output.
- The backend stores the itinerary in Supabase with owner metadata.
- Saved trips are associated with the authenticated user.
- Private user data is protected by authorization checks.

**Status:** Done

### Story 9 - Personal dashboard

**As a** logged-in user, **I want** to see my saved trips in a dashboard, **so that** I can manage previous plans.

**Acceptance criteria:**

- The dashboard fetches the current user's itineraries.
- Saved trips are displayed with destination, dates, visibility, and trip metadata.
- The user can navigate from the dashboard to a trip details page.

**Status:** Done

### Story 10 - Trip details page

**As a** user, **I want** to open a saved itinerary, **so that** I can inspect the complete trip after generation.

**Acceptance criteria:**

- The frontend supports dynamic trip pages.
- The backend can return one itinerary by id.
- The page displays saved AI data and trip metadata.
- Access rules distinguish owned/private trips from public trips.

**Status:** Done

### Story 11 - Community Discover feed

**As a** traveler, **I want** to browse public itineraries, **so that** I can get inspiration from other users' trips.

**Acceptance criteria:**

- Users can mark trips as public.
- Public trips appear in the Discover feed.
- The feed supports community trip cards with relevant metadata.
- The backend returns only public community items.

**Status:** Done

### Story 12 - Like and unlike public itineraries

**As a** user, **I want** to like or unlike public trips, **so that** useful itineraries can be ranked and discovered more easily.

**Acceptance criteria:**

- The Discover feed displays like state and like count.
- The user can toggle a like.
- The backend persists likes and updates counts.
- Duplicate likes by the same user are handled correctly.

**Status:** Done

### Story 13 - Fork public itineraries

**As a** user, **I want** to fork a public itinerary into my own account, **so that** I can reuse and adapt a trip created by another user.

**Acceptance criteria:**

- Public itineraries expose a fork action.
- The backend clones the public itinerary into the current user's saved trips.
- Fork counts are tracked.
- Forked trips remain associated with the new owner.

**Status:** Done

### Story 14 - Group voting and activity regeneration

**As a** group of travelers, **we want** to vote against an activity and regenerate it, **so that** the final plan better matches the group's preferences.

**Acceptance criteria:**

- Users can react or vote on activities.
- The backend stores votes per itinerary/day/activity/user.
- When the regeneration condition is met, the backend invokes the Regeneration Agent.
- The replacement activity preserves the day context and trip preferences.

**Status:** Done

### Story 15 - Image enrichment for itineraries

**As a** user, **I want** activities and trips to have relevant images, **so that** the generated itinerary is easier to inspect visually.

**Acceptance criteria:**

- Activities can receive image URLs from keyless image search or fallback sources.
- Broken or irrelevant image behavior is reduced through query and fallback improvements.
- Images appear in generated itinerary and Discover views.

**Status:** Done

### Story 16 - Map and transport visualization

**As a** traveler, **I want** to see route and transport information, **so that** I can understand how the itinerary works geographically.

**Acceptance criteria:**

- Transport/map components are available in the frontend.
- The app uses map/routing data where available.
- Route and marker colors match the visual theme.
- Leaflet dependency issues are fixed for build stability.

**Status:** Done

### Story 17 - Frontend visual redesign and navigation consistency

**As a** user, **I want** the app to look cohesive and have predictable navigation, **so that** I can use the product comfortably during planning.

**Acceptance criteria:**

- The homepage, planning page, dashboard, Discover, and trip views share a consistent visual style.
- Main buttons route correctly to planning and product flows.
- Loading and animation states do not break the layout.
- Frontend build passes after design changes.

**Status:** Done

### Story 18 - Automated tests and CI pipeline

**As a** development team, **we want** automated tests and CI checks, **so that** pull requests can be validated before merging.

**Acceptance criteria:**

- CI runs automatically on push and pull request to `main`.
- The frontend production build is validated.
- Backend tests run with `pytest`.
- Offline agent evaluation runs with a minimum quality threshold.
- Java legacy build remains checked while still present in the repository.

**Status:** Done

## Bug / Fix Backlog Items

### Bug 1 - Duplicate activities across multiple days

**Problem:** The itinerary generator could return duplicate activities on different days.

**Fix:** Prompt constraints and post-processing were strengthened to deduplicate activities.

**Status:** Done

### Bug 2 - Generated images not loading correctly

**Problem:** Some itinerary or Discover images did not load or were too generic.

**Fix:** Image lookup was improved with more specific query strategies and fallback behavior.

**Status:** Done

### Bug 3 - Start Planning button navigation

**Problem:** Some homepage or CTA buttons did not navigate reliably to the planning flow.

**Fix:** Buttons were updated to route to `/plan`.

**Status:** Done

### Bug 4 - City autocomplete/geocoding issues

**Problem:** City autocomplete and geocoding were unreliable in some cases.

**Fix:** Geocoding implementation was adjusted and corrected in the active backend.

**Status:** Done

### Bug 5 - Logistics planning errors

**Problem:** Logistics generation could fail or produce weak planning output.

**Fix:** Logistics planning logic and tests were updated.

**Status:** Done

### Bug 6 - CI/frontend build issues

**Problem:** Type mismatches and missing fields could break frontend CI.

**Fix:** Missing types and build-related issues were fixed.

**Status:** Done

## Technical Tasks

### Task 1 - Refactor backend architecture

**Description:** Reorganize the backend around FastAPI routes, services, core configuration, database access, and AI agents.

**Status:** Done

### Task 2 - Move active backend to Python

**Description:** Make the Python/FastAPI backend the active backend for the product.

**Status:** Done

### Task 3 - Add Docker setup

**Description:** Add container configuration for running backend and frontend services together.

**Status:** Done

### Task 4 - Add route and unit tests

**Description:** Add automated tests for backend routes, models, recommendations, security, planning, logistics, and agent evaluation.

**Status:** Done

### Task 5 - Add offline agent evaluation

**Description:** Add deterministic scenarios to evaluate AI agent output quality in CI without requiring a live local model.

**Status:** Done
