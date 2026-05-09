from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_experience import (
    _activity_key,
    _catalog_for_destination,
    _sanitize_itinerary,
    _select_mixed_catalog,
    _time_rank,
)
from models import Activity, AgentOneOutput, DailyItinerary, UserInput


def test_party_itinerary_repair_uses_unique_nightlife_places_in_order():
    user_input = UserInput(
        budget="medium",
        lifestyle="nightowl",
        vacationType="party",
        destination="Lisbon, Portugal",
        origin="Bucharest, Romania",
        travelers=2,
        start_date="2026-06-01",
        end_date="2026-06-04",
        price_range_per_person="$300-$700",
    )
    repeated_model_output = AgentOneOutput(
        trip_title="Lisbon party loop",
        vibe_summary="Nightlife",
        itinerary=[
            DailyItinerary(
                day_number=day_number,
                activities=[
                    Activity(
                        title="Generic museum visit",
                        description="A broad daytime fallback that does not match the party intent.",
                        time="Evening",
                        cost="Varies",
                        location="Museum district",
                        image_url="",
                        type="museum",
                    ),
                    Activity(
                        title="Lux Fragil",
                        description="Repeated club from the model.",
                        time="Morning",
                        cost="$20-45",
                        location="Lux Fragil, Avenida Infante Dom Henrique",
                        image_url="",
                        type="nightlife",
                    ),
                    Activity(
                        title="Lux Fragil",
                        description="Repeated club from the model.",
                        time="Late night",
                        cost="$20-45",
                        location="Lux Fragil, Avenida Infante Dom Henrique",
                        image_url="",
                        type="nightlife",
                    ),
                ],
            )
            for day_number in range(1, 4)
        ],
    )
    catalog = _select_mixed_catalog(
        _catalog_for_destination("Lisbon, Portugal"),
        user_input.trip_days * 3,
        "party nightowl",
    )

    repaired = _sanitize_itinerary(repeated_model_output, user_input, catalog)
    activities = [activity for day in repaired.itinerary for activity in day.activities]
    place_keys = [_activity_key(activity) for activity in activities]

    assert len(activities) == user_input.trip_days * 3
    assert len(place_keys) == len(set(place_keys))
    assert all(activity.type in {"nightlife", "dining", "shopping"} for activity in activities)
    for day in repaired.itinerary:
        ranks = [_time_rank(activity.time) for activity in day.activities]
        assert ranks == sorted(ranks)


if __name__ == "__main__":
    test_party_itinerary_repair_uses_unique_nightlife_places_in_order()
