import asyncio
import re
from time import monotonic

import httpx
from ddgs import DDGS
from fastapi import HTTPException
from loguru import logger

from local_llm import generate_local_json, local_model_name
from models import Activity, AgentOneOutput, DailyItinerary, UserInput

STATIC_FALLBACK = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1000&q=80"

search_lock = asyncio.Lock()
_last_image_search = 0.0
_IMAGE_SEARCH_COOLDOWN = 0.3
_last_place_search = 0.0
_PLACE_SEARCH_COOLDOWN = 1.0
_image_search_available = True


EXPERIENCE_SYSTEM_PROMPT = """
You are VibeTrips' local Experience Guide agent. You run fully locally and do not call paid or hosted AI APIs.
Create authentic, practical, destination-aware vacation itineraries from the user's constraints.

Return exactly one valid JSON object with this schema:
{
  "trip_title": "string",
  "vibe_summary": "string",
  "itinerary": [
    {
      "day_number": 1,
      "activities": [
        {
          "title": "string",
          "description": "string",
          "time": "string",
          "cost": "string",
          "location": "string",
          "image_url": "",
          "type": "experience"
        }
      ]
    }
  ]
}

Rules:
- Output raw JSON only. No markdown, commentary, XML, or function calls.
- Generate exactly 3 activities per day.
- Do not repeat the same activity title or location anywhere in the itinerary.
- Mix categories across the trip. For sightseeing or culture trips, include a balanced spread of landmarks,
  parks/gardens, markets/food stops, viewpoints/squares, museums, and local culture stops. Do not make every
  activity a museum, palace, or walking route.
- Every activity title and location must name a real, visitable place, venue, landmark, market, museum,
  garden, square, restaurant, or neighborhood in the destination.
- Prefer the verified real places supplied in the user prompt. Use their exact names and address-style
  locations whenever possible.
- Do not use broad placeholders such as "city center", "food district", "local district", "highlights",
  "orientation walk", "evening in the city", or "hidden gems".
- Put the precise venue and address/area in location, for example "Jardin Majorelle, Rue Yves Saint Laurent",
  "Djemaa el-Fna, Medina", "Bahia Palace, Rue Riad Zitoun el Jdid", or
  "Musee d'Orsay, Esplanade Valery Giscard d'Estaing".
- Keep activity types within: experience, dining, tour, cruise, cookingclass, festival, adventure, culture,
  relaxation, shopping, nightlife, transport, arrival, departure, flight, hotel, sightseeing, museum,
  landmark, park, beach.
- Keep image_url as an empty string. The backend web image scraper fills it later.
- Avoid generic filler like "explore the city"; name concrete neighborhoods, landmarks, markets, museums,
  restaurants, waterfronts, parks, or local experiences.
"""

REAL_LOCATION_CATALOG: dict[str, list[dict[str, str]]] = {
    "marrakesh": [
        {
            "title": "Jardin Majorelle and Yves Saint Laurent Museum",
            "description": "Visit the cobalt-blue gardens created by Jacques Majorelle, then step into the nearby Yves Saint Laurent Museum for fashion, Berber craft, and design context.",
            "time": "Morning",
            "cost": "$15-25",
            "location": "Jardin Majorelle, Rue Yves Saint Laurent",
            "type": "culture",
        },
        {
            "title": "Bahia Palace Courtyard Walk",
            "description": "Explore the carved cedar ceilings, tiled courtyards, and shaded rooms of one of Marrakesh's most atmospheric 19th-century palaces.",
            "time": "Late morning",
            "cost": "$8-12",
            "location": "Bahia Palace, Rue Riad Zitoun el Jdid",
            "type": "landmark",
        },
        {
            "title": "Djemaa el-Fna Food Stalls and Souk Semmarine",
            "description": "Spend sunset around Djemaa el-Fna, then walk into Souk Semmarine for spices, lanterns, leather goods, and classic Marrakesh street food.",
            "time": "Evening",
            "cost": "$10-25",
            "location": "Djemaa el-Fna and Souk Semmarine",
            "type": "dining",
        },
        {
            "title": "Le Jardin Secret",
            "description": "Step into restored Islamic gardens, tiled courtyards, and rooftop views inside one of the Medina's calmest heritage sites.",
            "time": "Afternoon",
            "cost": "$8-12",
            "location": "Le Jardin Secret, Rue Mouassine",
            "type": "park",
        },
        {
            "title": "Ben Youssef Madrasa",
            "description": "Visit the carved cedar, zellij tilework, and student cells of Marrakesh's historic Quranic school.",
            "time": "Morning",
            "cost": "$5-10",
            "location": "Ben Youssef Madrasa, Kaat Benahid",
            "type": "culture",
        },
        {
            "title": "Saadian Tombs",
            "description": "See the decorated royal necropolis and the Hall of Twelve Columns near the Kasbah Mosque.",
            "time": "Late morning",
            "cost": "$7-12",
            "location": "Saadian Tombs, Rue de La Kasbah",
            "type": "landmark",
        },
        {
            "title": "El Badi Palace",
            "description": "Explore the ruined palace walls, sunken gardens, and rooftop views over the Medina and Atlas foothills.",
            "time": "Afternoon",
            "cost": "$7-12",
            "location": "El Badi Palace, Ksibat Nhass",
            "type": "landmark",
        },
        {
            "title": "Menara Gardens",
            "description": "Take a slower outdoor break around the olive groves, pavilion, and reflecting basin west of the Medina.",
            "time": "Morning",
            "cost": "Free",
            "location": "Menara Gardens, Avenue de la Menara",
            "type": "park",
        },
        {
            "title": "Mellah Spice Market",
            "description": "Browse spice pyramids, olives, preserved lemons, and local ingredients in the old Jewish quarter market area.",
            "time": "Lunch",
            "cost": "$5-20",
            "location": "Mellah Spice Market, Place des Ferblantiers",
            "type": "shopping",
        },
    ],
    "paris": [
        {
            "title": "Musee d'Orsay Impressionist Galleries",
            "description": "See Monet, Renoir, Degas, and Van Gogh inside the former Beaux-Arts railway station on the Left Bank.",
            "time": "Morning",
            "cost": "$15-20",
            "location": "Musee d'Orsay, Esplanade Valery Giscard d'Estaing",
            "type": "museum",
        },
        {
            "title": "Le Marais Food Walk on Rue des Rosiers",
            "description": "Wander the Marais for falafel, bakeries, boutiques, and small galleries around one of Paris's most characterful streets.",
            "time": "Lunch",
            "cost": "$15-35",
            "location": "Rue des Rosiers, Le Marais",
            "type": "dining",
        },
        {
            "title": "Sainte-Chapelle and Ile de la Cite",
            "description": "Visit Sainte-Chapelle's stained glass, then walk the river edges of Ile de la Cite toward Notre-Dame's exterior.",
            "time": "Afternoon",
            "cost": "$15-25",
            "location": "Sainte-Chapelle, 10 Boulevard du Palais",
            "type": "landmark",
        },
        {
            "title": "Jardin du Luxembourg",
            "description": "Take a relaxed park break among fountains, statues, lawns, and the Medici Fountain on the Left Bank.",
            "time": "Afternoon",
            "cost": "Free",
            "location": "Jardin du Luxembourg, Rue de Medicis",
            "type": "park",
        },
        {
            "title": "Marche Bastille",
            "description": "Browse produce, cheese, roast chicken, crepes, and casual lunch stalls at one of Paris's liveliest markets.",
            "time": "Lunch",
            "cost": "$10-25",
            "location": "Marche Bastille, Boulevard Richard-Lenoir",
            "type": "dining",
        },
        {
            "title": "Sacré-Coeur and Place du Tertre",
            "description": "Visit the basilica terrace above Montmartre, then see the small artist square nearby.",
            "time": "Morning",
            "cost": "Free",
            "location": "Sacré-Coeur, 35 Rue du Chevalier de la Barre",
            "type": "sightseeing",
        },
        {
            "title": "Centre Pompidou",
            "description": "See modern and contemporary art inside the colorful high-tech landmark near Les Halles.",
            "time": "Afternoon",
            "cost": "$15-20",
            "location": "Centre Pompidou, Place Georges-Pompidou",
            "type": "museum",
        },
        {
            "title": "Palais Garnier",
            "description": "Tour the grand staircase, painted ceilings, and gilded foyers of Paris's historic opera house.",
            "time": "Morning",
            "cost": "$15-20",
            "location": "Palais Garnier, Place de l'Opera",
            "type": "culture",
        },
        {
            "title": "Pont Neuf and Square du Vert-Galant",
            "description": "Pause at Paris's oldest bridge and the small riverside garden at the tip of Ile de la Cite.",
            "time": "Evening",
            "cost": "Free",
            "location": "Pont Neuf, Square du Vert-Galant",
            "type": "sightseeing",
        },
    ],
    "lisbon": [
        {
            "title": "Mosteiro dos Jeronimos and Pasteis de Belem",
            "description": "Pair the Manueline monastery with warm custard tarts at the historic bakery a few minutes away.",
            "time": "Morning",
            "cost": "$12-25",
            "location": "Mosteiro dos Jeronimos, Belem",
            "type": "landmark",
        },
        {
            "title": "Alfama Walk to Miradouro de Santa Luzia",
            "description": "Climb through Alfama's lanes toward tiled viewpoints, small churches, and classic tram-lined corners.",
            "time": "Afternoon",
            "cost": "Free",
            "location": "Miradouro de Santa Luzia, Alfama",
            "type": "sightseeing",
        },
        {
            "title": "Time Out Market Lisboa Dinner",
            "description": "Try a range of Portuguese dishes from curated local vendors in the Mercado da Ribeira food hall.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Time Out Market Lisboa, Cais do Sodre",
            "type": "dining",
        },
    ],
    "rome": [
        {
            "title": "Colosseum and Roman Forum",
            "description": "Walk through Rome's most important ancient arena and the nearby Forum ruins, pairing the headline monument with the civic heart of ancient Rome.",
            "time": "Morning",
            "cost": "$18-30",
            "location": "Colosseum, Piazza del Colosseo",
            "type": "landmark",
        },
        {
            "title": "Pantheon and Piazza della Rotonda",
            "description": "Visit the Pantheon's ancient dome, then pause around Piazza della Rotonda for coffee and people-watching.",
            "time": "Afternoon",
            "cost": "$5-15",
            "location": "Pantheon, Piazza della Rotonda",
            "type": "landmark",
        },
        {
            "title": "Campo de' Fiori Market",
            "description": "Browse produce, flowers, spices, and casual food stalls at one of Rome's classic open-air market squares.",
            "time": "Lunch",
            "cost": "$10-25",
            "location": "Campo de' Fiori, Piazza Campo de' Fiori",
            "type": "dining",
        },
        {
            "title": "Villa Borghese and Pincio Terrace",
            "description": "Slow down in Rome's central park, then walk to the Pincio Terrace for a view over Piazza del Popolo.",
            "time": "Afternoon",
            "cost": "Free",
            "location": "Villa Borghese, Viale del Museo Borghese",
            "type": "park",
        },
        {
            "title": "Trevi Fountain",
            "description": "Visit the Baroque fountain early or late to avoid the thickest crowds and see the sculptural details.",
            "time": "Evening",
            "cost": "Free",
            "location": "Trevi Fountain, Piazza di Trevi",
            "type": "sightseeing",
        },
        {
            "title": "Piazza Navona",
            "description": "See Bernini's Fountain of the Four Rivers and the long oval square built over Domitian's stadium.",
            "time": "Afternoon",
            "cost": "Free",
            "location": "Piazza Navona",
            "type": "sightseeing",
        },
        {
            "title": "Galleria Borghese",
            "description": "Book ahead for Bernini sculptures, Caravaggio paintings, and one of Rome's best compact museum visits.",
            "time": "Morning",
            "cost": "$18-30",
            "location": "Galleria Borghese, Piazzale Scipione Borghese",
            "type": "museum",
        },
        {
            "title": "Trastevere and Basilica di Santa Maria",
            "description": "Explore Trastevere around the basilica and stay for a casual dinner on nearby side streets.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Basilica di Santa Maria in Trastevere, Piazza di Santa Maria",
            "type": "dining",
        },
        {
            "title": "Orange Garden on Aventine Hill",
            "description": "Visit the small hilltop park for a calm city panorama and a short walk toward the Knights of Malta keyhole.",
            "time": "Morning",
            "cost": "Free",
            "location": "Giardino degli Aranci, Piazza Pietro d'Illiria",
            "type": "park",
        },
    ],
    "barcelona": [
        {
            "title": "Basílica de la Sagrada Família",
            "description": "Visit Gaudi's still-evolving basilica and focus on the facades, columns, and stained-glass interior.",
            "time": "Morning",
            "cost": "$25-40",
            "location": "Sagrada Família, Carrer de Mallorca 401",
            "type": "landmark",
        },
        {
            "title": "Park Güell Monumental Zone",
            "description": "Spend time among Gaudi's mosaics, viaducts, and city views in the ticketed monumental area.",
            "time": "Afternoon",
            "cost": "$12-20",
            "location": "Park Güell, Carrer d'Olot",
            "type": "park",
        },
        {
            "title": "Mercat de la Boqueria",
            "description": "Try fruit, seafood counters, tapas, and classic market snacks inside Barcelona's best-known food market.",
            "time": "Lunch",
            "cost": "$15-35",
            "location": "Mercat de la Boqueria, La Rambla 91",
            "type": "dining",
        },
    ],
}


def _is_valid_image(url: str) -> bool:
    if not url:
        return False
    low = url.lower()
    blocked = ("foursquare", "tripadvisor", "svg", "icon", "logo", "map")
    if any(item in low for item in blocked):
        return False
    if any(ext in low for ext in (".jpg", ".jpeg", ".png", ".webp")):
        return True
    image_hosts = ("images.unsplash.com", "cdn.", "images.", "media.", "assets.", "photo", "upload")
    return low.startswith("https://") and any(host in low for host in image_hosts)


def _search_image_sync(queries: list[str]) -> str | None:
    with DDGS() as ddgs:
        for query in queries:
            try:
                results = ddgs.images(query, max_results=20, safesearch="moderate")
            except Exception as exc:
                logger.debug(f"[img] DDGS query failed for '{query}': {exc}")
                continue
            for item in results:
                candidates = (
                    item.get("image"),
                    item.get("thumbnail"),
                    item.get("url"),
                )
                for candidate in candidates:
                    if _is_valid_image(candidate):
                        return candidate
    for query in queries:
        commons_image = _search_commons_image_sync(query)
        if commons_image:
            return commons_image
    return None


def _search_commons_image_sync(query: str) -> str | None:
    commons_query = query.replace('"', "").replace(" official photo", "").replace(" travel photography", "")
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": commons_query,
        "gsrnamespace": 6,
        "gsrlimit": 6,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                "https://commons.wikimedia.org/w/api.php",
                params=params,
                headers={"User-Agent": "VibeTripsPlanner/1.0 (contact@vibetrips.test)"},
            )
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.debug(f"[img] Wikimedia Commons image lookup failed for '{query}': {exc}")
        return None

    pages = (data.get("query") or {}).get("pages") or {}
    for page in pages.values():
        image_url = ((page.get("imageinfo") or [{}])[0]).get("url")
        if _is_valid_image(image_url):
            return image_url
    return None


def _search_destination_context_sync(query: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5, safesearch="moderate")
    snippets = []
    for item in results[:5]:
        title = item.get("title") or "Result"
        body = item.get("body") or item.get("snippet") or ""
        href = item.get("href") or item.get("url") or ""
        snippets.append(f"- {title}: {body} ({href})")
    return "\n".join(snippets)


def _city_key(destination: str) -> str:
    city = (destination or "").split(",")[0].strip().lower()
    return {"marrakech": "marrakesh"}.get(city, city)


def _place_key(value: str) -> str:
    head = (value or "").split(",")[0].lower()
    return re.sub(r"[^a-z0-9]+", " ", head).strip()


def _activity_key(activity: Activity | dict[str, str]) -> str:
    if isinstance(activity, Activity):
        title = activity.title
        location = activity.location
    else:
        title = activity.get("title", "")
        location = activity.get("location", "")
    return _place_key(title) or _place_key(location)


def _normalized_type(place: Activity | dict[str, str]) -> str:
    raw_type = place.type if isinstance(place, Activity) else place.get("type", "experience")
    type_map = {
        "culture": "culture",
        "museum": "museum",
        "landmark": "landmark",
        "sightseeing": "sightseeing",
        "park": "park",
        "dining": "dining",
        "shopping": "shopping",
        "nightlife": "nightlife",
        "beach": "park",
    }
    return type_map.get(str(raw_type or "experience").lower(), "experience")


def _dedupe_places(places: list[dict[str, str]]) -> list[dict[str, str]]:
    unique = []
    seen: set[str] = set()
    for place in places:
        key = _activity_key(place)
        if not key or key in seen:
            continue
        unique.append(place)
        seen.add(key)
    return unique


def _preferred_type_sequence(vibe: str) -> list[str]:
    vibe_text = (vibe or "").lower()
    if "beach" in vibe_text:
        return ["park", "dining", "sightseeing", "landmark", "shopping", "culture", "museum", "nightlife"]
    if "relax" in vibe_text:
        return ["park", "dining", "culture", "sightseeing", "landmark", "shopping", "museum", "nightlife"]
    if "food" in vibe_text or "culinary" in vibe_text:
        return ["dining", "shopping", "landmark", "park", "culture", "sightseeing", "museum", "nightlife"]
    return ["landmark", "park", "dining", "sightseeing", "museum", "shopping", "culture", "nightlife"]


def _select_mixed_catalog(places: list[dict[str, str]], count: int, vibe: str = "") -> list[dict[str, str]]:
    unique = _dedupe_places(places)
    if len(unique) <= count:
        return unique

    buckets: dict[str, list[dict[str, str]]] = {}
    for place in unique:
        buckets.setdefault(_normalized_type(place), []).append(place)

    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    sequence = _preferred_type_sequence(vibe)

    while len(selected) < count:
        made_progress = False
        for desired_type in sequence:
            options = buckets.get(desired_type, [])
            next_place = next((place for place in options if _activity_key(place) not in seen), None)
            if not next_place:
                continue
            selected.append(next_place)
            seen.add(_activity_key(next_place))
            made_progress = True
            if len(selected) >= count:
                break
        if not made_progress:
            break

    for place in unique:
        if len(selected) >= count:
            break
        key = _activity_key(place)
        if key not in seen:
            selected.append(place)
            seen.add(key)

    return selected


def _clean_place_name(raw_name: str, destination: str) -> str:
    name = re.sub(r"\s+", " ", raw_name or "").strip(" -|,")
    if not name:
        return destination.split(",")[0].strip() or "Local place"
    blacklist = ("tripadvisor", "viator", "getyourguide", "things to do", "best ", "top ")
    low = name.lower()
    if any(term in low for term in blacklist):
        return destination.split(",")[0].strip() or name
    return name[:90]


def _address_from_nominatim(item: dict) -> str:
    address = item.get("address") or {}
    parts = [
        address.get("road") or address.get("pedestrian") or address.get("footway"),
        address.get("suburb") or address.get("neighbourhood") or address.get("quarter"),
        address.get("city") or address.get("town") or address.get("village"),
        address.get("country"),
    ]
    compact = [part for part in parts if part]
    if compact:
        return ", ".join(dict.fromkeys(compact))
    return item.get("display_name", "")


def _activity_type_for_place(item: dict, fallback: str) -> str:
    place_class = (item.get("class") or "").lower()
    place_type = (item.get("type") or "").lower()
    if place_type in {"museum", "gallery"}:
        return "museum"
    if place_type in {"restaurant", "cafe", "marketplace"}:
        return "dining"
    if place_type in {"park", "garden"}:
        return "park"
    if place_class in {"historic", "tourism"}:
        return "landmark"
    return fallback


def _is_visit_worthy_place(item: dict) -> bool:
    place_class = (item.get("class") or "").lower()
    place_type = (item.get("type") or "").lower()
    name = (item.get("name") or (item.get("namedetails") or {}).get("name") or "").lower()
    blocked_types = {
        "social_facility",
        "community_centre",
        "residential",
        "apartments",
        "office",
        "company",
        "parking",
        "toilets",
        "school",
        "kindergarten",
        "clinic",
        "doctors",
    }
    blocked_name_terms = ("senior", "anziani", "parking", "garage", "pharmacy", "supermarket")
    if place_type in blocked_types or any(term in name for term in blocked_name_terms):
        return False
    allowed_classes = {"tourism", "historic", "amenity", "leisure", "shop", "place"}
    allowed_types = {
        "museum",
        "gallery",
        "attraction",
        "viewpoint",
        "artwork",
        "monument",
        "memorial",
        "archaeological_site",
        "castle",
        "palace",
        "ruins",
        "place_of_worship",
        "marketplace",
        "restaurant",
        "cafe",
        "park",
        "garden",
        "square",
        "pedestrian",
    }
    return place_class in allowed_classes or place_type in allowed_types


async def _nominatim_search(query: str) -> list[dict]:
    global _last_place_search
    elapsed = monotonic() - _last_place_search
    if elapsed < _PLACE_SEARCH_COOLDOWN:
        await asyncio.sleep(_PLACE_SEARCH_COOLDOWN - elapsed)
    _last_place_search = monotonic()

    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "namedetails": 1,
        "limit": 4,
    }
    headers = {"User-Agent": "VibeTripsPlanner/1.0 (contact@vibetrips.test)"}
    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_real_place_catalog(destination: str, vibe: str, target_count: int) -> list[dict[str, str]]:
    """
    Build a concrete place catalog using keyless OpenStreetMap/Nominatim lookups.

    The local model is good at prose but unreliable at exact venues under time pressure,
    so we give it verified names/addresses and also use the same list to repair vague output.
    """
    curated = _catalog_for_destination(destination)
    if len(_dedupe_places(curated)) >= target_count:
        return _select_mixed_catalog(curated, target_count, vibe)
    target_pool_size = max(target_count * 2, target_count + 6)

    city = destination.split(",")[0].strip()
    searches = [
        ("landmark", "historic attraction"),
        ("park", "garden park"),
        ("dining", "market food hall restaurant"),
        ("museum", "museum"),
        ("shopping", "market souk"),
        ("sightseeing", "square viewpoint"),
        ("park", "public park"),
        ("landmark", "monument"),
        ("dining", "local market"),
        ("culture", vibe or "cultural attraction"),
    ]
    places: list[dict[str, str]] = list(curated)
    seen = {_activity_key(item) for item in places}

    country = destination.split(",")[-1].strip() if "," in destination else ""
    for fallback_type, term in searches:
        if len(_dedupe_places(places)) >= target_pool_size:
            break
        query_variants = [
            f"{term} in {destination or city}",
            f"{city} {term} {country}".strip(),
            f"{term}, {destination or city}",
        ]
        results = []
        for query in query_variants:
            try:
                results = await _nominatim_search(query)
            except Exception as exc:
                logger.warning(f"[places] Nominatim lookup failed for '{query}': {exc}")
                continue
            if results:
                break

        for item in results:
            if not _is_visit_worthy_place(item):
                continue
            namedetails = item.get("namedetails") or {}
            name = _clean_place_name(namedetails.get("name") or item.get("name") or item.get("display_name", "").split(",")[0], destination)
            key = _place_key(name)
            if not name or key in seen or key == city.lower():
                continue
            address = _address_from_nominatim(item)
            activity_type = _activity_type_for_place(item, fallback_type)
            places.append({
                "title": name,
                "description": f"Visit {name}, a real {activity_type} stop in {city}, and plan the activity around the venue rather than a broad neighborhood walk.",
                "time": "Morning" if len(places) % 3 == 0 else "Afternoon" if len(places) % 3 == 1 else "Evening",
                "cost": "Varies",
                "location": f"{name}, {address}" if address and name not in address else address or name,
                "type": activity_type,
            })
            seen.add(key)
            if len(_dedupe_places(places)) >= target_pool_size:
                break

    return _select_mixed_catalog(places, target_count, vibe)


def _format_place_catalog(places: list[dict[str, str]]) -> str:
    if not places:
        return "No verified place catalog available."
    lines = []
    for idx, place in enumerate(places, start=1):
        lines.append(
            f"{idx}. {place['title']} | address/area: {place['location']} | type: {place.get('type', 'experience')}"
        )
    return "\n".join(lines)


async def fetch_destination_web_context(destination: str, vibe: str) -> str:
    """Collect a compact keyless web-search context for the local model."""
    query = f"{destination} best things to do neighborhoods food culture {vibe} travel"
    try:
        return await asyncio.to_thread(_search_destination_context_sync, query)
    except Exception as exc:
        logger.warning(f"[search] Destination context search failed for '{query}': {exc}")
        return "No live web context available; rely on local travel knowledge."


async def fetch_image_for_activity(activity_name: str, destination: str, location: str | None = None) -> str:
    """
    Fetch an activity image through DuckDuckGo image search.

    This keeps image enrichment keyless. If search fails or returns blocked links,
    the UI still gets a stable fallback image.
    """
    global _image_search_available, _last_image_search
    if not _image_search_available:
        return STATIC_FALLBACK

    city = (destination or "").split(",")[0].strip()
    clean_activity = re.sub(r"\s+", " ", activity_name or "").strip()
    clean_location = re.sub(r"\s+", " ", location or "").strip()
    queries = [
        f'"{clean_location or clean_activity}" "{city}" photo',
        f'"{clean_activity}" "{city}" photo',
        f"{clean_location or clean_activity} {destination} landmark",
        f"{clean_activity} {destination} official photo",
        f"{clean_activity} {destination} travel photography",
        f"{clean_activity} landmark photo",
        f"{city} {clean_activity} image",
    ]

    async with search_lock:
        elapsed = monotonic() - _last_image_search
        if elapsed < _IMAGE_SEARCH_COOLDOWN:
            await asyncio.sleep(_IMAGE_SEARCH_COOLDOWN - elapsed)
        _last_image_search = monotonic()

        try:
            image_url = await asyncio.to_thread(_search_image_sync, queries)
            if image_url:
                logger.info(f"[img] Found keyless DDGS image for '{clean_activity} / {city}'")
                return image_url
        except Exception as exc:
            logger.warning(f"[img] DDGS image search failed for '{clean_activity} / {city}': {exc}")

    return STATIC_FALLBACK


def _catalog_for_destination(destination: str) -> list[dict[str, str]]:
    return REAL_LOCATION_CATALOG.get(_city_key(destination), [])


def _activity_is_too_broad(activity: Activity) -> bool:
    text = f"{activity.title} {activity.location}".lower()
    broad_terms = (
        "orientation walk",
        "local food stop",
        "highlight experience",
        "evening in",
        "central ",
        "food district",
        "local district",
        "highlights",
        "city center",
        "city centre",
        "hidden gems",
        "neighborhood walk",
        "neighbourhood walk",
        "walk through",
        "local neighborhood",
        "local neighbourhood",
        "old town",
        "downtown",
    )
    if any(term in text for term in broad_terms):
        return True
    location = (activity.location or "").strip()
    if not location or len(location.split()) < 2:
        return True
    title = (activity.title or "").strip().lower()
    if title.startswith(("explore ", "discover ", "walk through ", "wander ")):
        return True
    return False


def _fallback_experience(user_input: UserInput, place_catalog: list[dict[str, str]] | None = None) -> AgentOneOutput:
    destination = user_input.destination or "the destination"
    city = destination.split(",")[0].strip()
    vibe = user_input.vacationType or user_input.lifestyle or "balanced"
    budget = user_input.budget or "medium"
    catalog = _select_mixed_catalog(
        place_catalog or _catalog_for_destination(destination),
        user_input.trip_days * 3,
        f"{user_input.vacationType} {user_input.lifestyle}",
    )
    days: list[DailyItinerary] = []

    for day_number in range(1, user_input.trip_days + 1):
        if catalog:
            offset = ((day_number - 1) * 3) % len(catalog)
            selected = [catalog[(offset + idx) % len(catalog)] for idx in range(3)]
            activities = [Activity(**item, image_url="") for item in selected]
        else:
            activities = [
                Activity(
                    title=f"{city} main landmark visit",
                    description=f"Visit a named landmark, museum, market, or garden in {city}. Regenerate once local search is available for more precise venues.",
                    time="Morning",
                    cost="Varies",
                    location=f"{city}",
                    image_url="",
                    type="sightseeing",
                ),
                Activity(
                    title=f"{city} museum or market stop",
                    description=f"Choose a real museum, market, or cultural venue in {city} that matches the requested vibe and budget.",
                    time="Afternoon",
                    cost="Varies",
                    location=f"{city}",
                    image_url="",
                    type="culture",
                ),
                Activity(
                    title=f"{city} dinner near a named neighborhood",
                    description=f"End the day with food around a real neighborhood or square in {city}.",
                    time="Evening",
                    cost="Varies",
                    location=f"{city}",
                    image_url="",
                    type="dining",
                ),
            ]
        days.append(DailyItinerary(day_number=day_number, activities=activities))

    return AgentOneOutput(
        trip_title=f"{city} {vibe.title()} Escape",
        vibe_summary=f"A {user_input.trip_days}-day {vibe} itinerary for {destination}, tuned for a {budget} budget and {user_input.travelers} traveler(s).",
        itinerary=days,
    )


async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """Generate itinerary locally, then enrich every activity with a keyless scraped image."""
    try:
        logger.info(f"Starting local itinerary generation for: {user_input.destination}")
        web_context = await fetch_destination_web_context(
            user_input.destination or "",
            user_input.vacationType or user_input.lifestyle or "",
        )
        place_catalog = await fetch_real_place_catalog(
            user_input.destination or "",
            user_input.vacationType or user_input.lifestyle or "",
            max(3, user_input.trip_days * 3),
        )
        compact_web_context = web_context[:700]
        user_prompt = (
            f"Create a {user_input.trip_days}-day itinerary.\n"
            f"Destination: {user_input.destination}\n"
            f"Travel dates: {user_input.start_date} to {user_input.end_date}\n"
            f"Origin: {user_input.origin}\n"
            f"Travelers: {user_input.travelers}\n"
            f"Lifestyle: {user_input.lifestyle}\n"
            f"Vacation type / vibe: {user_input.vacationType}\n"
            f"Budget tier: {user_input.budget}\n"
            f"Price range per person: {user_input.price_range_per_person or 'not specified'}\n"
            f"Verified real places. Build the itinerary from these exact names and address/area values:\n"
            f"{_format_place_catalog(place_catalog)}\n"
            f"Keyless web-search context:\n{compact_web_context}\n"
            "Remember: raw JSON only."
        )

        try:
            data = await generate_local_json(
                EXPERIENCE_SYSTEM_PROMPT,
                user_prompt,
                timeout=25,
                temperature=0.25,
                num_predict=650,
            )
            parsed = AgentOneOutput(**data)
            logger.info(f"Local experience agent completed with model {local_model_name()}.")
        except Exception as exc:
            logger.warning(f"Local experience agent unavailable or invalid; using deterministic fallback. {exc}")
            parsed = _fallback_experience(user_input, place_catalog)

        catalog = _select_mixed_catalog(
            place_catalog or _catalog_for_destination(user_input.destination or ""),
            user_input.trip_days * 3,
            f"{user_input.vacationType} {user_input.lifestyle}",
        )
        if catalog:
            repaired_days = []
            used_place_keys: set[str] = set()
            replacement_cursor = 0
            for day_idx, day in enumerate(parsed.itinerary[: user_input.trip_days]):
                repaired_activities = []
                day_activities = list(day.activities[:3])
                while len(day_activities) < 3:
                    replacement = catalog[(day_idx * 3 + len(day_activities)) % len(catalog)]
                    day_activities.append(Activity(**replacement, image_url=""))
                for idx, act in enumerate(day_activities):
                    act_key = _activity_key(act)
                    type_count_for_day = sum(1 for item in repaired_activities if _normalized_type(item) == _normalized_type(act))
                    should_replace = (
                        _activity_is_too_broad(act)
                        or not act_key
                        or act_key in used_place_keys
                        or type_count_for_day >= 2
                    )
                    if should_replace:
                        replacement = None
                        for _ in range(len(catalog)):
                            candidate = catalog[replacement_cursor % len(catalog)]
                            replacement_cursor += 1
                            candidate_key = _activity_key(candidate)
                            candidate_type_count = sum(
                                1 for item in repaired_activities if _normalized_type(item) == _normalized_type(candidate)
                            )
                            if candidate_key not in used_place_keys and candidate_type_count < 2:
                                replacement = candidate
                                break
                        replacement = replacement or catalog[(day_idx * 3 + idx) % len(catalog)]
                        repaired_activities.append(Activity(**replacement, image_url=act.image_url or ""))
                    else:
                        repaired_activities.append(act)
                    used_place_keys.add(_activity_key(repaired_activities[-1]))
                repaired_days.append(day.model_copy(update={"activities": repaired_activities}))
            while len(repaired_days) < user_input.trip_days:
                day_idx = len(repaired_days)
                activities = []
                for idx in range(3):
                    replacement = None
                    for _ in range(len(catalog)):
                        candidate = catalog[replacement_cursor % len(catalog)]
                        replacement_cursor += 1
                        candidate_key = _activity_key(candidate)
                        if candidate_key not in used_place_keys:
                            replacement = candidate
                            break
                    replacement = replacement or catalog[(day_idx * 3 + idx) % len(catalog)]
                    activities.append(Activity(**replacement, image_url=""))
                    used_place_keys.add(_activity_key(replacement))
                repaired_days.append(DailyItinerary(day_number=day_idx + 1, activities=activities))
            parsed = parsed.model_copy(update={"itinerary": repaired_days})

        normalized_days = []
        for day in parsed.itinerary:
            image_tasks = [
                fetch_image_for_activity(act.title, user_input.destination or "", act.location)
                for act in day.activities
            ]
            image_urls = await asyncio.gather(*image_tasks)
            normalized_acts = [
                act.model_copy(update={"image_url": image_url})
                for act, image_url in zip(day.activities, image_urls)
            ]
            normalized_days.append(day.model_copy(update={"activities": normalized_acts}))

        return parsed.model_copy(update={"itinerary": normalized_days})

    except Exception as exc:
        logger.error(f"Itinerary generation failed: {exc}")
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=str(exc))
