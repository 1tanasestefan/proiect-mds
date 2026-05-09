from __future__ import annotations
import httpx
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/geocoding")

@router.get("/search")
async def geocoding_search(q: str = Query(..., min_length=2)):
    # Photon is an open geocoder based on OpenStreetMap, no API key required
    url = "https://photon.komoot.io/api/"
    params = {"q": q, "limit": 5, "lang": "en"}
    headers = {"User-Agent": "VibeTrips/1.0"}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Normalize to same format the frontend expects: [{place_id, display_name}]
            results = []
            for i, feature in enumerate(data.get("features", [])):
                props = feature.get("properties", {})
                city = props.get("city") or props.get("name", "")
                country = props.get("country", "")
                state = props.get("state", "")
                if city and country:
                    display = f"{city}, {country}"
                elif props.get("name") and country:
                    display = f"{props['name']}, {country}"
                else:
                    display = props.get("name", q)
                results.append({"place_id": i, "display_name": display})
            # Deduplicate
            seen = set()
            unique = []
            for r in results:
                if r["display_name"] not in seen:
                    seen.add(r["display_name"])
                    unique.append(r)
            return JSONResponse(content=unique)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {e}")
