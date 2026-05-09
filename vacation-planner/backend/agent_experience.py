from __future__ import annotations
import asyncio
import re
from time import monotonic
from urllib.parse import unquote

import httpx
from ddgs import DDGS
from fastapi import HTTPException
from loguru import logger

from local_llm import generate_local_json, local_model_name
from models import Activity, AgentOneOutput, DailyItinerary, UserInput

STATIC_FALLBACK = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1000&q=80"
TYPE_FALLBACK_IMAGES = {
    "nightlife": [
        "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1000&q=80",
        "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=1000&q=80",
        "https://images.unsplash.com/photo-1566737236500-c8ac43014a8e?w=1000&q=80",
    ],
    "dining": [
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1000&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000&q=80",
        "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=1000&q=80",
    ],
    "shopping": [
        "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=1000&q=80",
        "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1000&q=80",
    ],
    "park": [
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1000&q=80",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1000&q=80",
    ],
    "relaxation": [
        "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=1000&q=80",
        "https://images.unsplash.com/photo-1515377905703-c4788e51af15?w=1000&q=80",
    ],
    "adventure": [
        "https://images.unsplash.com/photo-1551632811-561732d1e306?w=1000&q=80",
        "https://images.unsplash.com/photo-1522163182402-834f871fd851?w=1000&q=80",
    ],
    "beach": [
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1000&q=80",
        "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?w=1000&q=80",
    ],
}

search_lock = asyncio.Lock()
image_search_semaphore = asyncio.Semaphore(3)
_last_image_search = 0.0
_IMAGE_SEARCH_COOLDOWN = 0.3
_last_place_search = 0.0
_PLACE_SEARCH_COOLDOWN = 1.0
_image_search_available = True
_place_catalog_cache: dict[tuple[str, str, int], list[dict[str, str]]] = {}
_image_cache: dict[tuple[str, str, str, str], str] = {}

TIME_LABELS = ("Morning", "Lunch", "Afternoon", "Evening", "Late night")
TIME_RANKS = {
    "early morning": 0,
    "morning": 1,
    "late morning": 2,
    "brunch": 3,
    "lunch": 4,
    "afternoon": 5,
    "late afternoon": 6,
    "dinner": 7,
    "evening": 8,
    "night": 9,
    "late night": 10,
}


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
- Generate exactly 3 activities per day in chronological order: morning first, lunch/afternoon second,
  evening/late night last. Never put morning after evening in the same day.
- Do not repeat the same activity title or location anywhere in the itinerary.
- Mix categories across the trip. For sightseeing or culture trips, include a balanced spread of landmarks,
  parks/gardens, markets/food stops, viewpoints/squares, museums, and local culture stops. Do not make every
  activity a museum, palace, or walking route.
- Match the user's selected intent. If they ask for partying or nightlife, prioritize real clubs, bars,
  live music venues, late-night districts, rooftop bars, and night markets. Do not fill a party itinerary
  with museums or daytime landmarks unless needed as a secondary daytime option.
- If they ask for food, prioritize restaurants, markets, food halls, cooking classes, bakeries, and wine/cocktail
  bars. If they ask for relaxation, prioritize parks, gardens, spas, beaches, baths, waterfronts, and slow cafes.
- Do not use museums as the generic fallback for unrelated categories.
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
        {
            "title": "Theatro Marrakech",
            "description": "Plan a late-night club stop with DJs, stage production, and a polished party crowd in Hivernage.",
            "time": "Late night",
            "cost": "$25-60",
            "location": "Theatro Marrakech, Rue Ibrahim El Mazini",
            "type": "nightlife",
        },
        {
            "title": "Comptoir Darna",
            "description": "Book dinner and stay for music, cocktails, and belly-dance performances in a lively Hivernage venue.",
            "time": "Evening",
            "cost": "$35-70",
            "location": "Comptoir Darna, Avenue Echouhada",
            "type": "nightlife",
        },
        {
            "title": "Barometre Marrakech",
            "description": "Start the night with craft cocktails and a stylish local bar scene before moving on to a club.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Barometre Marrakech, Rue Moulay Ali",
            "type": "nightlife",
        },
        {
            "title": "555 Famous Club Marrakech",
            "description": "Go late for a large club night with DJs, bottle service, and a party-focused Hivernage crowd.",
            "time": "Late night",
            "cost": "$25-60",
            "location": "555 Famous Club Marrakech, Route de l'Ourika",
            "type": "nightlife",
        },
        {
            "title": "So Lounge Marrakech",
            "description": "Book a table for dinner, cocktails, live performers, and late DJ sets at Sofitel Marrakech.",
            "time": "Evening",
            "cost": "$30-70",
            "location": "So Lounge Marrakech, Rue Harroun Errachid",
            "type": "nightlife",
        },
        {
            "title": "Epicurien Marrakech",
            "description": "Use this as a lively dinner-to-drinks stop with music and a stylish Gueliz nightlife scene.",
            "time": "Evening",
            "cost": "$25-60",
            "location": "Epicurien Marrakech, Rue Hafid Ibrahim",
            "type": "nightlife",
        },
        {
            "title": "Jad Mahal",
            "description": "Mix dinner, cocktails, and live cabaret-style performances before a later club night.",
            "time": "Evening",
            "cost": "$35-80",
            "location": "Jad Mahal, Rue Haroun Errachid",
            "type": "nightlife",
        },
        {
            "title": "Kabana Rooftop",
            "description": "Start the evening with rooftop cocktails, music, and Medina views near Koutoubia.",
            "time": "Evening",
            "cost": "$15-40",
            "location": "Kabana Rooftop, Rue Fatima Zahra",
            "type": "nightlife",
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
        {
            "title": "Rex Club",
            "description": "Go late for one of Paris's classic electronic music clubs, with a strong techno and house calendar.",
            "time": "Late night",
            "cost": "$15-35",
            "location": "Rex Club, 5 Boulevard Poissonniere",
            "type": "nightlife",
        },
        {
            "title": "Badaboum",
            "description": "Pick a DJ night or concert at this Bastille venue with a club room and cocktail spaces.",
            "time": "Late night",
            "cost": "$15-35",
            "location": "Badaboum, 2 bis Rue des Taillandiers",
            "type": "nightlife",
        },
        {
            "title": "Le Perchoir Menilmontant",
            "description": "Start with rooftop drinks and skyline views before heading into a later club night.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Le Perchoir Menilmontant, 14 Rue Crespin du Gast",
            "type": "nightlife",
        },
        {
            "title": "La Machine du Moulin Rouge",
            "description": "Choose a club night or concert at a multi-room Pigalle venue attached to the Moulin Rouge building.",
            "time": "Late night",
            "cost": "$15-40",
            "location": "La Machine du Moulin Rouge, 90 Boulevard de Clichy",
            "type": "nightlife",
        },
        {
            "title": "Supersonic",
            "description": "Catch indie concerts, DJ nights, and a late bar crowd near Bastille.",
            "time": "Late night",
            "cost": "$10-30",
            "location": "Supersonic, 9 Rue Biscornet",
            "type": "nightlife",
        },
        {
            "title": "Le Carmen",
            "description": "Start or finish the night in an ornate cocktail bar and club space in South Pigalle.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Le Carmen, 34 Rue Duperre",
            "type": "nightlife",
        },
        {
            "title": "Silencio",
            "description": "Plan a late stop at a members-club-style venue known for DJ sets, art events, and cocktails.",
            "time": "Late night",
            "cost": "$20-50",
            "location": "Silencio, 142 Rue Montmartre",
            "type": "nightlife",
        },
        {
            "title": "La Bellevilloise",
            "description": "Pick a concert, club night, or cultural party in a lively Menilmontant venue.",
            "time": "Evening",
            "cost": "$10-35",
            "location": "La Bellevilloise, 19-21 Rue Boyer",
            "type": "nightlife",
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
        {
            "title": "Lux Fragil",
            "description": "Go late for one of Lisbon's best-known club nights with riverfront electronic music floors.",
            "time": "Late night",
            "cost": "$20-45",
            "location": "Lux Fragil, Avenida Infante Dom Henrique",
            "type": "nightlife",
        },
        {
            "title": "Pensao Amor",
            "description": "Start with cocktails in a theatrical Cais do Sodre bar before moving into Pink Street nightlife.",
            "time": "Evening",
            "cost": "$12-30",
            "location": "Pensao Amor, Rua do Alecrim 19",
            "type": "nightlife",
        },
        {
            "title": "Musicbox Lisboa",
            "description": "Catch a concert, DJ set, or club night in a basement venue on Pink Street.",
            "time": "Late night",
            "cost": "$10-30",
            "location": "Musicbox Lisboa, Rua Nova do Carvalho 24",
            "type": "nightlife",
        },
        {
            "title": "Park Bar",
            "description": "Start the evening with rooftop drinks and city views above Bairro Alto.",
            "time": "Evening",
            "cost": "$10-30",
            "location": "Park Bar, Calcada do Combro 58",
            "type": "nightlife",
        },
        {
            "title": "Red Frog Speakeasy",
            "description": "Book a cocktail-focused night at one of Lisbon's best-known speakeasy-style bars.",
            "time": "Evening",
            "cost": "$18-40",
            "location": "Red Frog Speakeasy, Praca da Alegria 66B",
            "type": "nightlife",
        },
        {
            "title": "Pink Street",
            "description": "Use Rua Nova do Carvalho for a late bar crawl with music venues, cocktail bars, and crowded weekend energy.",
            "time": "Late night",
            "cost": "$15-40",
            "location": "Pink Street, Rua Nova do Carvalho",
            "type": "nightlife",
        },
        {
            "title": "Casa Independente",
            "description": "Choose a gig, DJ night, or terrace drink in a creative Intendente cultural venue.",
            "time": "Evening",
            "cost": "$8-25",
            "location": "Casa Independente, Largo do Intendente Pina Manique 45",
            "type": "nightlife",
        },
        {
            "title": "Foxtrot",
            "description": "Start the night with classic cocktails in an Art Nouveau bar near Principe Real.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Foxtrot, Travessa Santa Teresa 28",
            "type": "nightlife",
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
        {
            "title": "Shari Vari Playhouse",
            "description": "Go late for a central Rome club night with multiple rooms, DJs, and a dressed-up crowd.",
            "time": "Late night",
            "cost": "$15-35",
            "location": "Shari Vari Playhouse, Via di Torre Argentina 78",
            "type": "nightlife",
        },
        {
            "title": "Alcazar Live",
            "description": "Catch a live show, DJ set, or late aperitivo in a converted cinema in Trastevere.",
            "time": "Evening",
            "cost": "$15-40",
            "location": "Alcazar Live, Via Cardinale Merry del Val 14",
            "type": "nightlife",
        },
        {
            "title": "Freni e Frizioni",
            "description": "Start the night with cocktails and aperitivo energy by Ponte Sisto before moving deeper into Trastevere.",
            "time": "Evening",
            "cost": "$12-30",
            "location": "Freni e Frizioni, Via del Politeama 4",
            "type": "nightlife",
        },
        {
            "title": "Jerry Thomas Speakeasy",
            "description": "Book ahead for a serious cocktail stop in one of Rome's best-known speakeasy-style bars.",
            "time": "Evening",
            "cost": "$20-45",
            "location": "Jerry Thomas Speakeasy, Vicolo Cellini 30",
            "type": "nightlife",
        },
        {
            "title": "Drink Kong",
            "description": "Start the night in a neon-lit cocktail bar near Monti with a strong late-evening atmosphere.",
            "time": "Evening",
            "cost": "$18-40",
            "location": "Drink Kong, Piazza di San Martino ai Monti 8",
            "type": "nightlife",
        },
        {
            "title": "Circolo degli Illuminati",
            "description": "Go for a late electronic music night with multiple rooms and a club-focused crowd.",
            "time": "Late night",
            "cost": "$15-35",
            "location": "Circolo degli Illuminati, Via Giuseppe Libetta 1",
            "type": "nightlife",
        },
        {
            "title": "Goa Club",
            "description": "Plan a techno or house night at one of Rome's long-running underground club venues.",
            "time": "Late night",
            "cost": "$15-35",
            "location": "Goa Club, Via Giuseppe Libetta 13",
            "type": "nightlife",
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
        {
            "title": "Razzmatazz",
            "description": "Choose a multi-room club night with indie, electronic, pop, and live-show programming in Poblenou.",
            "time": "Late night",
            "cost": "$20-45",
            "location": "Razzmatazz, Carrer dels Almogavers 122",
            "type": "nightlife",
        },
        {
            "title": "Jamboree",
            "description": "Go for jazz, hip-hop, funk, or late club sessions directly on Placa Reial.",
            "time": "Late night",
            "cost": "$15-35",
            "location": "Jamboree, Placa Reial 17",
            "type": "nightlife",
        },
        {
            "title": "Paradiso",
            "description": "Start with one of Barcelona's best-known cocktail bars before a later club stop.",
            "time": "Evening",
            "cost": "$15-35",
            "location": "Paradiso, Carrer de Rera Palau 4",
            "type": "nightlife",
        },
        {
            "title": "Opium Barcelona",
            "description": "Go late for a beach-club night with DJs and a big dance-floor crowd by Barceloneta.",
            "time": "Late night",
            "cost": "$20-60",
            "location": "Opium Barcelona, Passeig Maritim de la Barceloneta 34",
            "type": "nightlife",
        },
        {
            "title": "Sala Apolo",
            "description": "Pick a concert or Nitsa club night at one of Barcelona's essential late venues.",
            "time": "Late night",
            "cost": "$15-40",
            "location": "Sala Apolo, Carrer Nou de la Rambla 113",
            "type": "nightlife",
        },
        {
            "title": "Moog",
            "description": "Go for a compact late-night techno and electronic music club near La Rambla.",
            "time": "Late night",
            "cost": "$12-30",
            "location": "Moog, Carrer de l'Arc del Teatre 3",
            "type": "nightlife",
        },
        {
            "title": "Pacha Barcelona",
            "description": "Plan a polished beachside club night with commercial house and guest DJs.",
            "time": "Late night",
            "cost": "$20-50",
            "location": "Pacha Barcelona, Carrer de Ramon Trias Fargas 2",
            "type": "nightlife",
        },
        {
            "title": "Sutton Barcelona",
            "description": "Use this as an upscale club option in the Tuset nightlife area.",
            "time": "Late night",
            "cost": "$20-50",
            "location": "Sutton Barcelona, Carrer de Tuset 13",
            "type": "nightlife",
        },
    ],
}


def _is_valid_image(url: str) -> bool:
    if not url:
        return False
    low = url.lower()
    blocked = ("foursquare", "tripadvisor", ".svg", "icon", "logo", "map", ".pdf", ".txt", ".doc", ".djvu", ".webm", ".ogv")
    if any(item in low for item in blocked):
        return False
    if any(ext in low for ext in (".jpg", ".jpeg", ".png", ".webp")):
        return True
    if "wikimedia" in low or "wikipedia" in low:
        return False
    image_hosts = ("images.unsplash.com", "cdn.", "images.", "media.", "assets.", "photo")
    return low.startswith("https://") and any(host in low for host in image_hosts)


def _fallback_image_for_type(activity_type: str | None, seed: str = "", used_urls: set[str] | None = None) -> str:
    images = TYPE_FALLBACK_IMAGES.get(str(activity_type or "").lower())
    if not images:
        return STATIC_FALLBACK
    used_urls = used_urls or set()
    index = sum(ord(char) for char in seed) % len(images)
    for offset in range(len(images)):
        candidate = images[(index + offset) % len(images)]
        if candidate not in used_urls:
            return candidate
    return images[index]


def _is_type_fallback_image(url: str | None) -> bool:
    if not url:
        return False
    return any(url in images for images in TYPE_FALLBACK_IMAGES.values())


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
    significant_terms = [
        term
        for term in re.findall(r"[a-zA-Z][a-zA-Z']{3,}", commons_query.lower())
        if term not in {"rome", "italy", "photo", "image", "official", "travel", "nightclub", "restaurant", "landmark", "party"}
    ]
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
        decoded_url = unquote(image_url or "").lower()
        if _is_valid_image(image_url) and (
            not significant_terms or any(term in decoded_url for term in significant_terms[:4])
        ):
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


def _intent_from_vibe(vibe: str) -> str:
    text = (vibe or "").lower()
    if any(term in text for term in ("party", "partying", "nightlife", "club", "clubs", "bar", "bars", "night owl", "nightowl", "dance", "dj")):
        return "party"
    if any(term in text for term in ("food", "culinary", "restaurant", "dining", "wine", "cocktail", "cooking")):
        return "food"
    if any(term in text for term in ("relax", "spa", "wellness", "chill", "slow", "beach", "nature")):
        return "relax"
    if any(term in text for term in ("adventure", "hike", "outdoor", "active", "sport")):
        return "adventure"
    if any(term in text for term in ("shopping", "market", "souvenir", "fashion")):
        return "shopping"
    if any(term in text for term in ("culture", "museum", "history", "art")):
        return "culture"
    return "sightseeing"


def _matches_intent(place: Activity | dict[str, str], intent: str) -> bool:
    place_type = _normalized_type(place)
    title = (place.title if isinstance(place, Activity) else place.get("title", "")).lower()
    location = (place.location if isinstance(place, Activity) else place.get("location", "")).lower()
    text = f"{title} {location}"
    intent_types = {
        "party": {"nightlife", "dining"},
        "food": {"dining", "shopping", "nightlife"},
        "relax": {"park", "beach", "relaxation", "dining"},
        "adventure": {"adventure", "park", "sightseeing", "beach"},
        "shopping": {"shopping", "dining", "sightseeing"},
        "culture": {"culture", "museum", "landmark", "sightseeing"},
        "sightseeing": {"landmark", "park", "sightseeing", "dining", "culture"},
    }
    keyword_matches = {
        "party": ("club", "bar", "cocktail", "dj", "dance", "music", "live", "rooftop", "night"),
        "food": ("market", "restaurant", "food", "wine", "bakery", "bistro", "cafe", "tapas", "cocktail"),
        "relax": ("park", "garden", "spa", "bath", "beach", "waterfront", "terrace", "slow"),
        "adventure": ("hike", "trail", "kayak", "bike", "climb", "adventure", "outdoor"),
        "shopping": ("market", "souq", "souk", "mall", "boutique", "shopping", "bazaar"),
    }
    return place_type in intent_types.get(intent, set()) or any(
        term in text for term in keyword_matches.get(intent, ())
    )


def _time_rank(time_value: str | None) -> int:
    text = (time_value or "").lower()
    for label, rank in TIME_RANKS.items():
        if label in text:
            return rank
    return 5


def _time_for_slot(activity_type: str, slot: int) -> str:
    normalized = _normalized_type({"type": activity_type})
    if normalized == "nightlife":
        return ("Afternoon", "Evening", "Late night")[min(slot, 2)]
    if normalized == "dining":
        return ("Lunch", "Dinner", "Evening")[min(slot, 2)]
    return TIME_LABELS[min(slot * 2, len(TIME_LABELS) - 1)]


def _with_slot_time(activity: Activity, slot: int) -> Activity:
    return activity.model_copy(update={"time": _time_for_slot(activity.type, slot)})


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
        "relaxation": "relaxation",
        "adventure": "adventure",
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
    intent = _intent_from_vibe(vibe)
    if intent == "party":
        return ["nightlife", "dining", "shopping", "sightseeing", "park", "landmark", "culture"]
    if intent == "food":
        return ["dining", "shopping", "nightlife", "culture", "park", "landmark", "sightseeing"]
    if intent == "relax":
        return ["park", "relaxation", "beach", "dining", "sightseeing", "culture", "landmark"]
    if intent == "adventure":
        return ["adventure", "park", "sightseeing", "beach", "dining", "landmark", "culture"]
    if intent == "shopping":
        return ["shopping", "dining", "sightseeing", "nightlife", "park", "landmark", "culture"]
    if "beach" in (vibe or "").lower():
        return ["park", "dining", "sightseeing", "landmark", "shopping", "culture", "museum", "nightlife"]
    return ["landmark", "park", "dining", "sightseeing", "museum", "shopping", "culture", "nightlife"]


def _select_mixed_catalog(places: list[dict[str, str]], count: int, vibe: str = "") -> list[dict[str, str]]:
    unique = _dedupe_places(places)
    intent = _intent_from_vibe(vibe)
    intent_matches = [place for place in unique if _matches_intent(place, intent)]
    other_places = [place for place in unique if not _matches_intent(place, intent)]
    if intent in {"party", "food", "relax", "adventure", "shopping"}:
        unique = intent_matches + other_places
    if len(unique) <= count:
        return unique

    buckets: dict[str, list[dict[str, str]]] = {}
    for place in unique:
        buckets.setdefault(_normalized_type(place), []).append(place)

    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    sequence = _preferred_type_sequence(vibe)
    intent_target = count
    if intent in {"party", "food", "relax", "adventure", "shopping"}:
        intent_target = count

    for place in intent_matches:
        if len(selected) >= intent_target:
            break
        key = _activity_key(place)
        if key not in seen:
            selected.append(place)
            seen.add(key)

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


def _next_unused_catalog_activity(
    catalog: list[dict[str, str]],
    used_place_keys: set[str],
    *,
    intent: str,
    strict_intent: bool,
    day_activities: list[Activity] | None = None,
    cursor_start: int = 0,
) -> tuple[Activity | None, int]:
    if not catalog:
        return None, cursor_start
    day_activities = day_activities or []
    for offset in range(len(catalog)):
        cursor = cursor_start + offset
        candidate = catalog[cursor % len(catalog)]
        candidate_key = _activity_key(candidate)
        candidate_type_count = sum(
            1 for item in day_activities if _normalized_type(item) == _normalized_type(candidate)
        )
        if candidate_key in used_place_keys:
            continue
        if strict_intent and not _matches_intent(candidate, intent):
            continue
        if candidate_type_count >= 2:
            continue
        return Activity(**candidate, image_url=""), cursor + 1
    for offset in range(len(catalog)):
        cursor = cursor_start + offset
        candidate = catalog[cursor % len(catalog)]
        candidate_key = _activity_key(candidate)
        if candidate_key not in used_place_keys:
            return Activity(**candidate, image_url=""), cursor + 1
    return None, cursor_start + len(catalog)


def _sanitize_itinerary(
    parsed: AgentOneOutput,
    user_input: UserInput,
    catalog: list[dict[str, str]],
) -> AgentOneOutput:
    intent = _intent_from_vibe(f"{user_input.vacationType} {user_input.lifestyle}")
    intent_catalog_count = sum(1 for place in catalog if _matches_intent(place, intent))
    strict_intent = intent in {"party", "food", "relax", "adventure", "shopping"} and intent_catalog_count >= 3
    used_place_keys: set[str] = set()
    repaired_days: list[DailyItinerary] = []
    replacement_cursor = 0

    for day_idx in range(user_input.trip_days):
        source_day = parsed.itinerary[day_idx] if day_idx < len(parsed.itinerary) else DailyItinerary(
            day_number=day_idx + 1,
            activities=[],
        )
        day_activities: list[Activity] = []
        source_activities = list(source_day.activities[:3])

        for act in source_activities:
            act_key = _activity_key(act)
            type_count_for_day = sum(1 for item in day_activities if _normalized_type(item) == _normalized_type(act))
            should_replace = (
                _activity_is_too_broad(act)
                or not act_key
                or act_key in used_place_keys
                or type_count_for_day >= 2
                or (strict_intent and not _matches_intent(act, intent))
            )
            if should_replace:
                replacement, replacement_cursor = _next_unused_catalog_activity(
                    catalog,
                    used_place_keys,
                    intent=intent,
                    strict_intent=strict_intent,
                    day_activities=day_activities,
                    cursor_start=replacement_cursor,
                )
                if replacement is not None:
                    act = replacement
            if _activity_key(act) not in used_place_keys:
                day_activities.append(act)
                used_place_keys.add(_activity_key(act))

        while len(day_activities) < 3:
            replacement, replacement_cursor = _next_unused_catalog_activity(
                catalog,
                used_place_keys,
                intent=intent,
                strict_intent=strict_intent,
                day_activities=day_activities,
                cursor_start=replacement_cursor,
            )
            if replacement is None:
                break
            day_activities.append(replacement)
            used_place_keys.add(_activity_key(replacement))

        if len(day_activities) < 3 and catalog:
            day_keys = {_activity_key(item) for item in day_activities}
            for candidate in catalog:
                if len(day_activities) >= 3:
                    break
                candidate_key = _activity_key(candidate)
                if not candidate_key or candidate_key in used_place_keys or candidate_key in day_keys:
                    continue
                day_activities.append(Activity(**candidate, image_url=""))
                used_place_keys.add(candidate_key)
                day_keys.add(candidate_key)

        if len(day_activities) < 3 and catalog:
            day_keys = {_activity_key(item) for item in day_activities}
            for candidate in catalog:
                if len(day_activities) >= 3:
                    break
                candidate_key = _activity_key(candidate)
                if not candidate_key or candidate_key in day_keys:
                    continue
                logger.warning(
                    f"[Experience] Reusing catalog place '{candidate.get('title')}' because the unique place pool is exhausted."
                )
                day_activities.append(Activity(**candidate, image_url=""))
                day_keys.add(candidate_key)

        day_activities = sorted(day_activities[:3], key=lambda item: _time_rank(item.time))
        day_activities = [_with_slot_time(activity, slot) for slot, activity in enumerate(day_activities)]
        repaired_days.append(
            DailyItinerary(day_number=day_idx + 1, activities=day_activities)
        )

    return parsed.model_copy(update={"itinerary": repaired_days})


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
    if place_type in {"nightclub", "bar", "pub", "biergarten"}:
        return "nightlife"
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
        "bar",
        "pub",
        "nightclub",
        "biergarten",
        "park",
        "garden",
        "square",
        "pedestrian",
    }
    return place_class in allowed_classes or place_type in allowed_types


def _search_specs_for_intent(vibe: str) -> list[tuple[str, str]]:
    intent = _intent_from_vibe(vibe)
    if intent == "party":
        return [
            ("nightlife", "nightclub"),
            ("nightlife", "dance club"),
            ("nightlife", "cocktail bar"),
            ("nightlife", "live music venue"),
            ("nightlife", "rooftop bar"),
            ("dining", "late night restaurant"),
            ("shopping", "night market"),
        ]
    if intent == "food":
        return [
            ("dining", "restaurant"),
            ("dining", "food market"),
            ("dining", "food hall"),
            ("dining", "bakery"),
            ("dining", "wine bar"),
            ("shopping", "local market"),
            ("culture", "cooking class"),
        ]
    if intent == "relax":
        return [
            ("park", "garden park"),
            ("relaxation", "spa"),
            ("park", "waterfront"),
            ("park", "public park"),
            ("dining", "quiet cafe"),
            ("sightseeing", "viewpoint"),
        ]
    if intent == "adventure":
        return [
            ("adventure", "hiking trail"),
            ("adventure", "outdoor activity"),
            ("park", "natural park"),
            ("sightseeing", "viewpoint"),
            ("adventure", "bike tour"),
            ("beach", "beach"),
        ]
    if intent == "shopping":
        return [
            ("shopping", "market"),
            ("shopping", "shopping street"),
            ("shopping", "boutique"),
            ("shopping", "bazaar"),
            ("dining", "food market"),
            ("nightlife", "cocktail bar"),
        ]
    return [
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
    intent = _intent_from_vibe(vibe)
    cache_key = (_city_key(destination), intent, target_count)
    if cache_key in _place_catalog_cache:
        return _place_catalog_cache[cache_key]

    curated = _catalog_for_destination(destination)
    selected_curated = _select_mixed_catalog(curated, target_count, vibe)
    strong_intent_count = sum(1 for place in selected_curated if _matches_intent(place, intent))
    if len(_dedupe_places(curated)) >= target_count and (
        intent in {"culture", "sightseeing"} or strong_intent_count >= max(1, int(target_count * 0.65))
    ):
        _place_catalog_cache[cache_key] = selected_curated
        return selected_curated
    target_pool_size = max(target_count + 4, target_count + (3 if intent == "party" else 0))

    city = destination.split(",")[0].strip()
    searches = _search_specs_for_intent(vibe)
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

    selected = _select_mixed_catalog(places, target_count, vibe)
    _place_catalog_cache[cache_key] = selected
    return selected


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
    intent = _intent_from_vibe(vibe)
    intent_terms = {
        "party": "best clubs bars nightlife live music rooftop bars party districts",
        "food": "best restaurants food markets food halls bakeries local dining",
        "relax": "best parks gardens spas beaches quiet cafes wellness",
        "adventure": "best outdoor activities hiking viewpoints bike tours adventure",
        "shopping": "best markets boutiques shopping streets bazaars",
        "culture": "best cultural sites museums galleries historic landmarks",
        "sightseeing": "best landmarks viewpoints parks markets sightseeing",
    }
    query = f"{destination} {intent_terms.get(intent, intent_terms['sightseeing'])} {vibe} travel"
    try:
        return await asyncio.to_thread(_search_destination_context_sync, query)
    except Exception as exc:
        logger.warning(f"[search] Destination context search failed for '{query}': {exc}")
        return "No live web context available; rely on local travel knowledge."


async def fetch_image_for_activity(
    activity_name: str,
    destination: str,
    location: str | None = None,
    activity_type: str | None = None,
) -> str:
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
    normalized_type = str(activity_type or "").lower()
    cache_key = (clean_activity.lower(), city.lower(), clean_location.lower(), normalized_type)
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    intent_hint = "nightclub bar party photo" if activity_type == "nightlife" else "restaurant food photo" if activity_type == "dining" else "travel photo"
    raw_queries = [
        f'"{clean_location or clean_activity}" "{city}" photo',
        f'"{clean_activity}" "{city}" photo',
        f"{clean_location or clean_activity} {destination} {intent_hint}",
        f"{clean_activity} {destination} official photo",
        f"{city} {clean_activity} image",
    ]
    queries = list(dict.fromkeys(query for query in raw_queries if query.strip()))

    async with image_search_semaphore:
        async with search_lock:
            elapsed = monotonic() - _last_image_search
            if elapsed < _IMAGE_SEARCH_COOLDOWN:
                await asyncio.sleep(_IMAGE_SEARCH_COOLDOWN - elapsed)
            _last_image_search = monotonic()

        try:
            image_url = await asyncio.to_thread(_search_image_sync, queries)
            if image_url:
                logger.info(f"[img] Found keyless DDGS image for '{clean_activity} / {city}'")
                _image_cache[cache_key] = image_url
                return image_url
        except Exception as exc:
            logger.warning(f"[img] DDGS image search failed for '{clean_activity} / {city}': {exc}")

    fallback = _fallback_image_for_type(activity_type, f"{clean_activity} {clean_location}")
    _image_cache[cache_key] = fallback
    return fallback


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
            intent = _intent_from_vibe(f"{user_input.vacationType} {user_input.lifestyle}")
            fallback_by_intent = {
                "party": [
                    ("nightlife", "club or DJ venue", "Late night"),
                    ("nightlife", "cocktail bar or rooftop bar", "Evening"),
                    ("dining", "late-night food spot near the nightlife area", "Dinner"),
                ],
                "food": [
                    ("dining", "local restaurant", "Lunch"),
                    ("shopping", "food market or market hall", "Morning"),
                    ("nightlife", "wine bar or cocktail bar", "Evening"),
                ],
                "relax": [
                    ("park", "public garden or waterfront park", "Morning"),
                    ("relaxation", "spa, bath, or wellness venue", "Afternoon"),
                    ("dining", "quiet cafe or terrace restaurant", "Evening"),
                ],
                "shopping": [
                    ("shopping", "market or bazaar", "Morning"),
                    ("shopping", "shopping street or boutique district", "Afternoon"),
                    ("dining", "food stop inside the shopping area", "Lunch"),
                ],
            }
            blueprints = fallback_by_intent.get(intent, [
                ("landmark", "named landmark", "Morning"),
                ("park", "public park or garden", "Afternoon"),
                ("dining", "local market or restaurant", "Evening"),
            ])
            activities = [
                Activity(
                    title=f"{city} {label}",
                    description=f"Pick a real {label} in {city} matching the user's {intent} intent once place search is available.",
                    time=time,
                    cost="Varies",
                    location=f"{city}",
                    image_url="",
                    type=activity_type,
                )
                for activity_type, label, time in blueprints
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
        intent = _intent_from_vibe(f"{user_input.vacationType} {user_input.lifestyle}")
        user_prompt = (
            f"Create a {user_input.trip_days}-day itinerary.\n"
            f"Destination: {user_input.destination}\n"
            f"Travel dates: {user_input.start_date} to {user_input.end_date}\n"
            f"Origin: {user_input.origin}\n"
            f"Travelers: {user_input.travelers}\n"
            f"Lifestyle: {user_input.lifestyle}\n"
            f"Vacation type / vibe: {user_input.vacationType}\n"
            f"Resolved activity intent: {intent}\n"
            f"Budget tier: {user_input.budget}\n"
            f"Price range per person: {user_input.price_range_per_person or 'not specified'}\n"
            f"Verified real places. Build the itinerary from these exact names and address/area values:\n"
            f"{_format_place_catalog(place_catalog)}\n"
            "Use each verified place at most once. Assign times inside each day in chronological order.\n"
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
        parsed = _sanitize_itinerary(parsed, user_input, catalog)

        normalized_days = []
        used_image_urls: set[str] = set()
        for day in parsed.itinerary:
            image_tasks = [
                fetch_image_for_activity(act.title, user_input.destination or "", act.location, act.type)
                for act in day.activities
            ]
            image_urls = await asyncio.gather(*image_tasks)
            normalized_acts = []
            for act, image_url in zip(day.activities, image_urls):
                if image_url in used_image_urls and _is_type_fallback_image(image_url):
                    image_url = _fallback_image_for_type(act.type, f"{act.title} {act.location}", used_image_urls)
                normalized_acts.append(act.model_copy(update={"image_url": image_url}))
                if image_url:
                    used_image_urls.add(image_url)
            normalized_days.append(day.model_copy(update={"activities": normalized_acts}))

        return parsed.model_copy(update={"itinerary": normalized_days})

    except Exception as exc:
        logger.error(f"Itinerary generation failed: {exc}")
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=str(exc))
