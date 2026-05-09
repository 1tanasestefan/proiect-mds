# AI Travel Planner - Python Backend (Zero-Cost Stack)

This backend uses a completely free tech stack for agentic travel planning.

## Tech Stack

- **Framework:** FastAPI
- **Agent Model:** Google Gemini (via `pydantic-ai`)
- **Search Tool:** DuckDuckGo Search (`duckduckgo-search`)
- **Data Contracts:** Pydantic v2

## Setup Instructions

1. **Activate Virtual Environment:**
   ```powershell
   cd backend-python
   .\venv\Scripts\activate
   ```

2. **Install Requirements:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **API Keys:**
   - Create a `.env` file from `.env.template`.
   - Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

4. **Run the Backend:**
   ```powershell
   python main.py
   ```
   Server runs at `http://localhost:8000`.

## Features

- **Agent 1 (Experience Guide):** Uses Gemini + DDG to find real activities matching user vibes.
- **Robustness:** DDG search is wrapped in error handling to prevent pipeline failures.
- **Typed Output:** Strictly validated JSON responses using PydanticAI.
