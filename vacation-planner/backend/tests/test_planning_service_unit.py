import asyncio

from app.services import planning
from models import (
    AccommodationOption,
    Activity,
    AgentOneOutput,
    DailyItinerary,
    FlightOption,
    TripLogistics,
    UserInput,
)


def test_generate_trip_plan_resolves_flexible_destination_and_dates(monkeypatch):
    captured = {}

    async def fake_recommend_destination(user_input, user_id):
        captured["recommend_user_id"] = user_id
        assert user_input.flexible_destination is True
        return "Paris, France"

    def fake_recommend_dates_for(destination, budget):
        assert destination == "Paris, France"
        assert budget == "medium"
        return {
            "start_date": "2026-06-09",
            "end_date": "2026-06-12",
            "reason": "test window",
        }

    async def fake_experience(user_input):
        captured["experience_input"] = user_input
        return AgentOneOutput(
            trip_title="Paris Food Weekend",
            vibe_summary="Relaxed culinary city break",
            itinerary=[
                DailyItinerary(
                    day_number=1,
                    activities=[
                        Activity(
                            title="Marché Bastille",
                            description="Taste local produce.",
                            time="Morning",
                            cost="$10-20",
                            location="Boulevard Richard-Lenoir",
                            type="dining",
                        )
                    ],
                )
            ],
        )

    async def fake_logistics(user_input, context, experience_result=None):
        captured["logistics_input"] = user_input
        captured["logistics_context"] = context
        captured["logistics_experience"] = experience_result
        return TripLogistics(
            flights=[
                FlightOption(
                    airline_type="Standard",
                    estimated_price_usd=300,
                    description="Estimated fare",
                    booking_link="https://example.com/flights",
                )
            ],
            accommodations=[
                AccommodationOption(
                    name="Central Stay",
                    type="Hotel",
                    neighborhood="Le Marais",
                    estimated_price_per_night_usd=150,
                    booking_link="https://example.com/hotel",
                )
            ],
            total_estimated_budget_usd=750,
        )

    monkeypatch.setattr(planning, "recommend_destination", fake_recommend_destination)
    monkeypatch.setattr(planning, "recommend_dates_for", fake_recommend_dates_for)
    monkeypatch.setattr(planning, "generate_experience_itinerary", fake_experience)
    monkeypatch.setattr(planning, "generate_logistics", fake_logistics)

    user_input = UserInput(
        budget="medium",
        lifestyle="relaxed",
        vacationType="culinary",
        origin="Bucharest, Romania",
        destination="",
        flexibleDestination=True,
        flexibleDates=True,
        travelers=2,
    )

    result = asyncio.run(planning.generate_trip_plan(user_input, user_id="user-123"))

    assert captured["recommend_user_id"] == "user-123"
    assert captured["experience_input"].destination == "Paris, France"
    assert captured["logistics_input"].start_date == "2026-06-09"
    assert "Destination: Paris, France" in captured["logistics_context"]
    assert "Marché Bastille" in captured["logistics_context"]
    assert captured["logistics_experience"].trip_title == "Paris Food Weekend"
    assert result.experience.trip_title == "Paris Food Weekend"
    assert result.destination == "Paris, France"
    assert result.start_date == "2026-06-09"
    assert result.logistics.total_estimated_budget_usd == 750
