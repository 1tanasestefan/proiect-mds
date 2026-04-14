from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal
from datetime import date, datetime


# ── Agent 1 (Experience Guide) Contracts ─────────────────────────

class UserInput(BaseModel):
    budget: str = Field(..., description="The user's budget level (e.g., Economy, Mid-range, Luxury)")
    lifestyle: str = Field(..., description="The user's lifestyle or interests (e.g., Adventurous, Cultural, Relaxing)")
    vacationType: str = Field(..., description="The type of vacation (e.g., Beach, City, Nature)")
    destination: str = Field(..., description="The travel destination")
    origin: str = Field(..., description="The departure / origin city")
    travelers: int = Field(..., description="Number of travelers")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")

    @model_validator(mode="after")
    def validate_dates(self):
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format.")

        delta = (end - start).days
        if delta <= 0:
            raise ValueError("End date must be after start date.")
        if delta > 5:
            raise ValueError("Trips are limited to a maximum of 5 days.")
        return self

    @property
    def trip_days(self) -> int:
        start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        return (end - start).days


class Activity(BaseModel):
    title: str = Field(..., description="Title of the activity")
    description: str = Field(..., description="Brief description of what to do")
    time: str = Field(..., description="Suggested time of day or duration")
    cost: str = Field(..., description="Estimated cost or 'Free'")
    location: str = Field(..., description="Name of the place or neighborhood")
    image_url: Optional[str] = Field(default=None, description="URL of the location image")
    type: Literal['experience', 'dining', 'tour', 'cruise', 'cookingclass', 'festival', 'adventure', 'culture', 'relaxation', 'shopping', 'nightlife', 'transport'] = Field('experience', description="Type of the activity")

class DailyItinerary(BaseModel):
    day_number: int = Field(..., description="The day number of the trip")
    activities: List[Activity] = Field(..., description="List of activities for this day")

class AgentOneOutput(BaseModel):
    trip_title: str = Field(..., description="A catchy title for the curated trip")
    vibe_summary: str = Field(..., description="A summary of the overall vibe matched to the user")
    itinerary: List[DailyItinerary] = Field(..., description="The complete list of DailyItinerary objects")


# ── Agent 2 (Logistics & Booking) Contracts ──────────────────────
from typing import Dict, Any

class Coordinate(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class TransportLeg(BaseModel):
    mode: Literal['flight', 'train', 'bus', 'uber'] = Field(..., description="Transport mode")
    name: str = Field(..., description="Name of the service (e.g., 'British Airways', 'Eurostar', 'UberX')")
    origin_coords: Coordinate = Field(..., description="Starting coordinates for this leg")
    destination_coords: Coordinate = Field(..., description="Ending coordinates for this leg")
    price: float = Field(..., description="Estimated cost of this leg")
    duration_minutes: int = Field(..., description="Duration in minutes")
    polyline: Optional[str] = Field(default=None, description="Encoded path or GeoJSON for map rendering")

class ConsolidatedLogistics(BaseModel):
    total_price: float = Field(..., description="Total cost of all legs combined")
    currency: str = Field(default="USD", description="Currency for the prices")
    legs: List[TransportLeg] = Field(..., description="Ordered list of transportation segments")
    map_center: Coordinate = Field(..., description="Recommended focal center for the map view")


class FlightOption(BaseModel):
    airline_type: str = Field(..., description="Category of airline (e.g., 'Low Cost', 'Premium', 'Charter')")
    estimated_price_usd: float = Field(..., description="Estimated round-trip price per person in USD")
    description: str = Field(..., description="Brief description of the flight option")
    booking_link: str = Field(..., description="Deep-link URL to Skyscanner or Google Flights search")

class AccommodationOption(BaseModel):
    name: str = Field(..., description="Specific name of the hotel or accommodation")
    type: str = Field(..., description="Type of stay (e.g., 'Boutique Hotel', 'Budget Hostel', 'Airbnb Apartment')")
    neighborhood: str = Field(..., description="Recommended neighborhood derived from the itinerary")
    estimated_price_per_night_usd: float = Field(..., description="Estimated price per night in USD")
    booking_link: str = Field(..., description="Deep-link URL to Booking.com or Airbnb search")

class TripLogistics(BaseModel):
    flights: List[FlightOption] = Field(..., description="2-3 flight options at different price tiers")
    accommodations: List[AccommodationOption] = Field(..., description="2-3 accommodation options")
    total_estimated_budget_usd: float = Field(..., description="Total estimated trip budget per person in USD")
    transit_options: Optional[Dict[str, ConsolidatedLogistics]] = Field(default=None, description="Multimodal transit choices (budget, premium, etc)")

class FinalTripPlan(BaseModel):
    experience: AgentOneOutput = Field(..., description="The curated itinerary from Agent 1")
    logistics: TripLogistics = Field(..., description="Logistics & booking data from Agent 2")
