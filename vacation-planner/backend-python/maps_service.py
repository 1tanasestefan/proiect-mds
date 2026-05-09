import httpx
from loguru import logger
from models import Coordinate, TransportLeg, ConsolidatedLogistics
import json

async def geocode_nominatim(query: str) -> Coordinate:
    """Fetch coordinates using public OpenStreetMap Nominatim API."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "VibeTripsPlanner/1.0 (contact@vibetrips.test)"}  # Required by Nominatim policy

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"Could not geocode: {query}")

        return Coordinate(lat=float(data[0]["lat"]), lng=float(data[0]["lon"]))

async def fetch_osrm_route(origin: Coordinate, destination: Coordinate):
    """Fetch exact driving route from public OSRM API with full GeoJSON geometry."""
    # OSRM takes coordinates as {lon},{lat}; overview=full + geometries=geojson gives real road curves
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{origin.lng},{origin.lat};{destination.lng},{destination.lat}"
        f"?overview=full&geometries=geojson"
    )

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        if data["code"] != "Ok":
            raise ValueError("Failed to fetch route from OSRM")

        route = data["routes"][0]
        return {
            "distance_m": route["distance"],
            "duration_s": route["duration"],
            # Full coordinate array without annotation — real road shape
            "geojson": route["geometry"],
        }

async def get_multimodal_options(
    origin_name: str,
    destination_name: str,
    flight_price_est: float,
    hotel_name: str | None = None,
) -> dict:
    """
    Build budget / balanced / premium transit options from the airport to the hotel.

    Parameters
    ----------
    origin_name      : Flight departure city (e.g. "Bucharest, Romania").
    destination_name : Flight arrival city / country (e.g. "Paris, France").
    flight_price_est : Base flight cost in USD used for total-price math.
    hotel_name       : Specific hotel name returned by the AI (e.g. "Hotel Le Marais Paris").
                       When provided, Nominatim geocodes the exact hotel pin.  Falls back to
                       the destination city centre if the hotel cannot be resolved.
    """
    city_only = destination_name.split(",")[0].strip()
    country_part = destination_name.split(",")[-1].strip() if "," in destination_name else ""
    airport_query = f"{city_only} Airport {country_part}".strip()

    # ── 1. Geocode the flight ORIGIN (departure city) ────────────────────────
    try:
        origin_coord = await geocode_nominatim(origin_name)
        logger.info(f"[Maps] Origin geocoded: {origin_name} → {origin_coord}")
    except Exception as e:
        logger.warning(f"[Maps] Could not geocode origin '{origin_name}': {e}. Using (0,0) fallback.")
        origin_coord = Coordinate(lat=0.0, lng=0.0)

    # ── 2. Geocode the destination AIRPORT ───────────────────────────────────
    try:
        airport_coord = await geocode_nominatim(airport_query)
        logger.info(f"[Maps] Airport geocoded: {airport_query} → {airport_coord}")
    except Exception as e:
        logger.warning(f"[Maps] Airport not found for '{destination_name}', falling back to city. Error: {e}")
        try:
            airport_coord = await geocode_nominatim(destination_name)
        except Exception as e2:
            logger.error(f"[Maps] Geocoding completely failed: {e2}")
            raise

    # ── 3. Geocode the HOTEL (or city centre as fallback) ────────────────────
    dest_coord: Coordinate | None = None
    if hotel_name:
        # Try "<hotel name>, <city>" for maximum precision
        hotel_query = f"{hotel_name}, {city_only}"
        try:
            dest_coord = await geocode_nominatim(hotel_query)
            logger.info(f"[Maps] Hotel geocoded: '{hotel_query}' → {dest_coord}")
        except Exception as e:
            logger.warning(f"[Maps] Hotel '{hotel_query}' not found, falling back to city centre. Error: {e}")

    if dest_coord is None:
        try:
            dest_coord = await geocode_nominatim(destination_name)
            logger.info(f"[Maps] Destination city geocoded: {destination_name} → {dest_coord}")
        except Exception as e:
            logger.error(f"[Maps] Geocoding completely failed for destination '{destination_name}': {e}")
            raise

    # ── 4. Build the FLIGHT leg with a real departure coordinate ─────────────
    flight_leg = TransportLeg(
        mode="flight",
        name=f"Flight to {airport_query}",
        origin_coords=origin_coord,      # ← real departure city coordinate
        destination_coords=airport_coord,
        price=flight_price_est,
        duration_minutes=240,
        polyline=None,
    )

    options: dict = {}

    # ── 5. Attempt OSRM ground-transport route (Airport → Hotel) ─────────────
    # We always try; the broad except handles cases where OSRM can't route
    # (islands, ocean crossings, etc.) gracefully.
    try:
        route_data = await fetch_osrm_route(airport_coord, dest_coord)
        dist_km  = route_data["distance_m"] / 1000.0
        dur_mins = int(route_data["duration_s"] / 60.0)
        # Serialise the full GeoJSON geometry to a string for storage in the model
        geojson_str = json.dumps(route_data["geojson"])

        logger.info(f"[Maps] OSRM route: {dist_km:.1f} km / {dur_mins} min")

        # Premium tier – Uber / private transfer
        uber_price = round((dist_km * 1.50) + 5.00, 2)
        uber_leg = TransportLeg(
            mode="uber",
            name="Private Transfer / Uber",
            origin_coords=airport_coord,
            destination_coords=dest_coord,
            price=uber_price,
            duration_minutes=dur_mins,
            polyline=geojson_str,
        )
        options["premium"] = ConsolidatedLogistics(
            total_price=flight_price_est + uber_price,
            currency="USD",
            legs=[flight_leg, uber_leg],
            map_center=dest_coord,
        )

        # Budget tier – airport bus
        bus_price = 5.00
        bus_leg = TransportLeg(
            mode="bus",
            name="Airport Express Bus",
            origin_coords=airport_coord,
            destination_coords=dest_coord,
            price=bus_price,
            duration_minutes=int(dur_mins * 1.3),  # buses are slower
            polyline=geojson_str,
        )
        options["budget"] = ConsolidatedLogistics(
            total_price=flight_price_est + bus_price,
            currency="USD",
            legs=[flight_leg, bus_leg],
            map_center=dest_coord,
        )

        # Balanced tier – regional train
        train_price = 15.00
        train_leg = TransportLeg(
            mode="train",
            name="Regional Train",
            origin_coords=airport_coord,
            destination_coords=dest_coord,
            price=train_price,
            duration_minutes=int(dur_mins * 0.9),  # trains can be faster
            polyline=geojson_str,
        )
        options["balanced"] = ConsolidatedLogistics(
            total_price=flight_price_est + train_price,
            currency="USD",
            legs=[flight_leg, train_leg],
            map_center=dest_coord,
        )

    except Exception as e:
        logger.error(f"[Maps] OSRM routing failed – returning flight-only fallback. Error: {e}")
        options["budget"] = ConsolidatedLogistics(
            total_price=flight_price_est,
            currency="USD",
            legs=[flight_leg],
            map_center=dest_coord,
        )

    return options
