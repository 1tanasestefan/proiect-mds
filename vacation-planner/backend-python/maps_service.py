import httpx
from loguru import logger
from models import Coordinate, TransportLeg, ConsolidatedLogistics
import json

async def geocode_nominatim(query: str) -> Coordinate:
    """Fetch coordinates using public OpenStreetMap Nominatim API."""
    url = f"https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "VibeTripsPlanner/1.0 (contact@vibetrips.test)"}  # Required by Nominatim policy
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise ValueError(f"Could not geocode: {query}")
            
        return Coordinate(lat=float(data[0]['lat']), lng=float(data[0]['lon']))

async def fetch_osrm_route(origin: Coordinate, destination: Coordinate):
    """Fetch exact driving route from public OSRM API."""
    # OSRM takes coordinates as {lon},{lat}
    url = f"http://router.project-osrm.org/route/v1/driving/{origin.lng},{origin.lat};{destination.lng},{destination.lat}?overview=full&geometries=geojson"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['code'] != 'Ok':
            raise ValueError("Failed to fetch route from OSRM")
            
        route = data['routes'][0]
        # Distance is in meters, duration in seconds
        return {
            "distance_m": route['distance'],
            "duration_s": route['duration'],
            "geojson": route['geometry']
        }

async def get_multimodal_options(origin_name: str, destination_name: str, flight_price_est: float) -> dict:
    # 1. Clean the destination name to maximize geocoding success (e.g. "Paris, France" -> "Paris")
    city_only = destination_name.split(",")[0].strip()
    # Include the full destination_name (with country) to disambiguate (e.g. "Bali Airport Indonesia" not "Bali Airport Nigeria")
    country_part = destination_name.split(",")[-1].strip() if "," in destination_name else ""
    airport_query = f"{city_only} Airport {country_part}".strip()
    
    # 2. Geocode Airport and Destination Hotel/Center
    try:
        airport_coord = await geocode_nominatim(airport_query)
    except Exception as e:
        logger.warning(f"Could not find exact international airport for {destination_name}, using generic city. Error: {e}")
        try:
             airport_coord = await geocode_nominatim(destination_name)
        except Exception as e2:
             logger.error(f"Geocoding completely failed: {e2}")
             raise
             
    try:
        dest_coord = await geocode_nominatim(destination_name)
    except Exception as e:
        logger.error(f"Geocoding completely failed for {destination_name}: {e}")
        raise
        
    # 2. Base Flight Leg
    flight_leg = TransportLeg(
        mode='flight',
        name=f"Flight to {airport_query}",
        origin_coords=Coordinate(lat=0.0, lng=0.0), # Simulated generic origin for standard flight display
        destination_coords=airport_coord,
        price=flight_price_est,
        duration_minutes=240,
        polyline=None
    )
    
    options = {}
    
    # 3. Early-exit: detect intercontinental/island routes where OSRM driving will always fail
    # If origin and destination are separated by more than 30 degrees of longitude they are on different
    # landmasses or separated by an ocean. OSRM is a *driving* router and will return 400 in these cases.
    origin_city_coord = Coordinate(lat=0.0, lng=0.0)  # We use 0,0 placeholder for origin (flight only)
    lng_diff = abs(airport_coord.lng - origin_city_coord.lng)
    lat_diff = abs(airport_coord.lat - origin_city_coord.lat)
    
    # A practical heuristic: if the destination is an island/archipelago like Bali/Maldives/etc,
    # detect it by checking if OSRM would be given ocean coordinates.
    # We always attempt OSRM; the broad except below already handles 400s gracefully.
    
    try:
        route_data = await fetch_osrm_route(airport_coord, dest_coord)
        dist_km = route_data['distance_m'] / 1000.0
        dur_mins = int(route_data['duration_s'] / 60.0)
        geojson_str = json.dumps(route_data['geojson']) # Serialize to string for model
        
        # Uber Estimate
        uber_price = round((dist_km * 1.50) + 5.00, 2)
        uber_leg = TransportLeg(
            mode='uber',
            name="Virtual Uber",
            origin_coords=airport_coord,
            destination_coords=dest_coord,
            price=uber_price,
            duration_minutes=dur_mins,
            polyline=geojson_str
        )
        
        options["premium"] = ConsolidatedLogistics(
            total_price=flight_price_est + uber_price,
            currency="USD",
            legs=[flight_leg, uber_leg],
            map_center=dest_coord
        )
        
        # Cheap Bus/Train Estimate
        bus_price = 5.00
        bus_leg = TransportLeg(
            mode='bus',
            name="Airport Express Bus",
            origin_coords=airport_coord,
            destination_coords=dest_coord,
            price=bus_price,
            duration_minutes=int(dur_mins * 1.3), # Bus is slower usually
            polyline=geojson_str # Same path as demo fallback
        )
        
        options["budget"] = ConsolidatedLogistics(
            total_price=flight_price_est + bus_price,
            currency="USD",
            legs=[flight_leg, bus_leg],
            map_center=dest_coord
        )

        # Balanced (Train if available, else standard taxi)
        train_price = 15.00
        train_leg = TransportLeg(
            mode='train',
            name="Regional Train",
            origin_coords=airport_coord,
            destination_coords=dest_coord,
            price=train_price,
            duration_minutes=int(dur_mins * 0.9), # Trains often faster than driving
            polyline=geojson_str
        )

        options["balanced"] = ConsolidatedLogistics(
            total_price=flight_price_est + train_price,
            currency="USD",
            legs=[flight_leg, train_leg],
            map_center=dest_coord
        )
        
    except Exception as e:
        logger.error(f"OSRM Routing failed (fallback): {e}")
        # If OSRM fails (e.g. airport is same as dest or routing blocked), fallback gracefully without ground
        options["budget"] = ConsolidatedLogistics(
            total_price=flight_price_est,
            currency="USD",
            legs=[flight_leg],
            map_center=dest_coord
        )
        
    return options
