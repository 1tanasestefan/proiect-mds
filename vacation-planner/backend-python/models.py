from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class UserInput(BaseModel):
    budget: str = Field(..., description="The user's budget level (e.g., Economy, Mid-range, Luxury)")
    lifestyle: str = Field(..., description="The user's lifestyle or interests (e.g., Adventurous, Cultural, Relaxing)")
    vacationType: str = Field(..., description="The type of vacation (e.g., Beach, City, Nature)")
    destination: str = Field(..., description="The travel destination")
    travelers: int = Field(..., description="Number of travelers")

class Activity(BaseModel):
    title: str = Field(..., description="Title of the activity")
    description: str = Field(..., description="Brief description of what to do")
    time: str = Field(..., description="Suggested time of day or duration")
    cost: str = Field(..., description="Estimated cost or 'Free'")
    location: str = Field(..., description="Name of the place or neighborhood")
    image_url: Optional[str] = Field(default=None, description="URL of the location image")
    type: Literal['experience'] = Field('experience', description="Type of the activity")

class DailyItinerary(BaseModel):
    day_number: int = Field(..., description="The day number of the trip")
    activities: List[Activity] = Field(..., description="List of activities for this day")

class AgentOneOutput(BaseModel):
    trip_title: str = Field(..., description="A catchy title for the curated trip")
    vibe_summary: str = Field(..., description="A summary of the overall vibe matched to the user")
    itinerary: List[DailyItinerary] = Field(..., description="The complete list of DailyItinerary objects")
