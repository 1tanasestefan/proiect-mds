from __future__ import annotations
from pydantic import BaseModel, Field, AliasChoices, ConfigDict, model_validator
from typing import List, Optional, Literal, Any, Dict
from datetime import date, datetime


# ── Agent 1 (Experience Guide) Contracts ─────────────────────────

class UserInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    budget: str = Field(..., description="The user's budget level (e.g., Economy, Mid-range, Luxury)")
    lifestyle: str = Field(..., description="The user's lifestyle or interests (e.g., Adventurous, Cultural, Relaxing)")
    vacationType: str = Field(..., description="The type of vacation (e.g., Beach, City, Nature)")
    destination: Optional[str] = Field(default=None, description="The travel destination")
    price_range_per_person: Optional[str] = Field(
        default=None,
        description="Desired total price range per person for the trip",
    )
    flexible_dates: bool = Field(
        default=False,
        validation_alias=AliasChoices("flexible_dates", "flexibleDates"),
        description="Whether the backend should recommend travel dates based on budget and destination seasonality",
    )
    flexible_destination: bool = Field(
        default=False,
        validation_alias=AliasChoices("flexible_destination", "flexibleDestination"),
        description="Whether the backend should recommend the destination from previous user signals",
    )
    origin: str = Field(..., description="The departure / origin city")
    travelers: int = Field(..., description="Number of travelers")
    start_date: Optional[str] = Field(default=None, description="Trip start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="Trip end date (YYYY-MM-DD)")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.flexible_dates:
            return self
        if not self.start_date or not self.end_date:
            raise ValueError("Dates are required unless flexible dates mode is enabled.")
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
        if not self.flexible_destination and not (self.destination or "").strip():
            raise ValueError("Destination is required unless flexible destination mode is enabled.")
        return self

    @property
    def trip_days(self) -> int:
        if not self.start_date or not self.end_date:
            return 3
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
    type: Literal['experience', 'dining', 'tour', 'cruise', 'cookingclass', 'festival', 'adventure', 'culture', 'relaxation', 'shopping', 'nightlife', 'transport', 'arrival', 'departure', 'flight', 'hotel', 'sightseeing', 'museum', 'landmark', 'park', 'beach'] = Field('experience', description="Type of the activity")
    
    @model_validator(mode="before")
    @classmethod
    def normalize_activity_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Handle type validation gracefully (default to 'experience' if unknown)
            allowed_types = {
                'experience', 'dining', 'tour', 'cruise', 'cookingclass', 
                'festival', 'adventure', 'culture', 'relaxation', 'shopping', 
                'nightlife', 'transport', 'arrival', 'departure', 'flight', 'hotel',
                'sightseeing', 'museum', 'landmark', 'park', 'beach'
            }
            if "type" in data and data["type"] not in allowed_types:
                data["type"] = "experience"
            
            # 2. Ensure title is present (fallback for safety)
            if "title" not in data or not data["title"]:
                data["title"] = "Activity"
        return data

class DailyItinerary(BaseModel):
    day_number: int = Field(..., description="The day number of the trip")
    activities: List[Activity] = Field(..., description="List of activities for this day")

class AgentOneOutput(BaseModel):
    trip_title: str = Field(..., description="A catchy title for the curated trip")
    vibe_summary: str = Field(..., description="A summary of the overall vibe matched to the user")
    itinerary: List[DailyItinerary] = Field(..., description="The complete list of DailyItinerary objects")


# ── Agent 2 (Logistics & Booking) Contracts ──────────────────────

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
    reason: Optional[str] = Field(default=None, description="Why this stay area fits the generated itinerary")


class BudgetBreakdown(BaseModel):
    flight_per_person_usd: float = Field(..., description="Estimated round-trip flight cost per person")
    accommodation_per_person_usd: float = Field(..., description="Estimated accommodation cost per person")
    food_per_person_usd: float = Field(..., description="Estimated food and drinks cost per person")
    activities_per_person_usd: float = Field(..., description="Estimated activity cost per person")
    local_transport_per_person_usd: float = Field(..., description="Estimated local transport cost per person")
    airport_transfer_per_person_usd: float = Field(default=0, description="Estimated airport transfer cost per person")
    subtotal_per_person_usd: float = Field(..., description="Estimated total trip cost per person")
    total_group_usd: float = Field(..., description="Estimated total cost for the whole travel group")
    currency: str = Field(default="USD", description="Currency used for all budget values")

class TripLogistics(BaseModel):
    flights: List[FlightOption] = Field(..., description="2-3 flight options at different price tiers")
    accommodations: List[AccommodationOption] = Field(..., description="2-3 accommodation options")
    total_estimated_budget_usd: float = Field(..., description="Total estimated trip budget per person in USD")
    transit_options: Optional[Dict[str, ConsolidatedLogistics]] = Field(default=None, description="Multimodal transit choices (budget, premium, etc)")
    budget_breakdown: Optional[BudgetBreakdown] = Field(default=None, description="Itemized estimated trip budget")
    assumptions: List[str] = Field(default_factory=list, description="Human-readable assumptions used for the estimates")
    confidence: Literal["estimated", "route-informed", "ai-estimated"] = Field(default="estimated", description="How strong the logistics estimate is")

class FinalTripPlan(BaseModel):
    experience: AgentOneOutput = Field(..., description="The curated itinerary from Agent 1")
    logistics: TripLogistics = Field(..., description="Logistics & booking data from Agent 2")
    origin: Optional[str] = Field(default=None, description="Resolved departure city")
    destination: Optional[str] = Field(default=None, description="Resolved destination")
    start_date: Optional[str] = Field(default=None, description="Resolved trip start date")
    end_date: Optional[str] = Field(default=None, description="Resolved trip end date")
    travelers: Optional[int] = Field(default=None, description="Resolved number of travelers")
    budget: Optional[str] = Field(default=None, description="Selected budget tier")
    price_range_per_person: Optional[str] = Field(default=None, description="Desired total price range per person")
    flexible_dates: bool = Field(default=False, description="Whether the dates were resolved by the backend")
    flexible_destination: bool = Field(default=False, description="Whether the destination was resolved by the backend")

class ItineraryUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_public: Optional[bool] = None
    ai_data: Optional[Dict[str, Any]] = None

class VoteUser(BaseModel):
    id: str
    name: str
    avatarId: Optional[int] = None

class VoteRequest(BaseModel):
    day_index: int = Field(..., ge=0)
    activity_index: int = Field(..., ge=0)
    total_online: Optional[int] = None
    voter: Optional[VoteUser] = None


ActivityReactionType = Literal["heart", "fire", "wow", "down"]


class ActivityReactionRequest(BaseModel):
    day_index: int = Field(..., ge=0)
    activity_index: int = Field(..., ge=0)
    reaction_type: ActivityReactionType


class ActivityReactionSummary(BaseModel):
    day_index: int
    activity_index: int
    reaction_type: ActivityReactionType
    count: int
    reacted_by_me: bool = False


class Collaborator(BaseModel):
    user_id: str
    role: Literal["viewer", "editor"] = "viewer"
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    joined_at: Optional[str] = None


class ActivityVote(BaseModel):
    day_index: int
    activity_index: int
    user_id: str
    voter_name: str
    voter_avatar_id: Optional[int] = None
    created_at: Optional[str] = None


class CollaborationState(BaseModel):
    itinerary_id: str
    role: Literal["owner", "editor", "viewer", "public", "link_viewer"]
    can_edit: bool
    can_invite: bool
    eligible_voters: int
    collaborators: List[Collaborator]
    votes: List[ActivityVote]


class CreateInviteRequest(BaseModel):
    role: Literal["viewer", "editor"] = "viewer"
    expires_in_days: int = Field(default=7, ge=1, le=30)


class InviteResponse(BaseModel):
    token: str
    role: Literal["viewer", "editor"]
    expires_at: str


class AcceptInviteResponse(BaseModel):
    itinerary_id: str
    role: Literal["viewer", "editor"]


class CommunityItinerary(BaseModel):
    id: str
    user_id: str
    title: str
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    likes_count: int
    forks_count: int
    is_public: bool
    created_at: str
    ai_data: Dict[str, Any]
    author_name: str
    author_avatar: Optional[str] = None
    is_liked_by_me: Optional[bool] = False
