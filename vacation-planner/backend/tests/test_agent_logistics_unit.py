import asyncio

import agent_logistics
from models import ConsolidatedLogistics, Coordinate, TransportLeg, UserInput


def user_input(**overrides):
    payload = {
        "budget": "medium",
        "lifestyle": "relaxed",
        "vacationType": "culinary",
        "origin": "Bucharest, Romania",
        "destination": "Lisbon, Portugal",
        "travelers": 2,
        "start_date": "2026-06-01",
        "end_date": "2026-06-04",
    }
    payload.update(overrides)
    return UserInput(**payload)


def test_fallback_logistics_scales_prices_by_budget():
    economy = agent_logistics._fallback_logistics(user_input(budget="low"), None)
    luxury = agent_logistics._fallback_logistics(user_input(budget="luxury"), None)

    assert economy.flights[0].estimated_price_usd < luxury.flights[0].estimated_price_usd
    assert economy.accommodations[0].estimated_price_per_night_usd < luxury.accommodations[0].estimated_price_per_night_usd
    assert luxury.total_estimated_budget_usd > economy.total_estimated_budget_usd


def test_generate_logistics_injects_booking_links_without_external_ai(monkeypatch):
    async def fake_multimodal_options(*_args, **_kwargs):
        return {}

    monkeypatch.setenv("LOCAL_LLM_LOGISTICS", "false")
    monkeypatch.setattr(agent_logistics, "get_multimodal_options", fake_multimodal_options)

    result = asyncio.run(
        agent_logistics.generate_logistics(
            user_input(),
            "Origin: Bucharest, Destination: Lisbon. Provide estimates.",
        )
    )

    assert result.flights[0].booking_link.startswith("https://www.skyscanner.net/transport/flights/")
    assert "bucharest" in result.flights[0].booking_link
    assert "lisbon" in result.flights[0].booking_link
    assert result.accommodations[0].booking_link.startswith("https://www.booking.com/searchresults.html")


def test_fallback_logistics_uses_route_data_for_budget_and_confidence():
    transit_options = {
        "budget": ConsolidatedLogistics(
            total_price=255,
            currency="USD",
            legs=[
                TransportLeg(
                    mode="flight",
                    name="Flight to Lisbon Airport",
                    origin_coords=Coordinate(lat=44.43, lng=26.1),
                    destination_coords=Coordinate(lat=38.77, lng=-9.13),
                    price=250,
                    duration_minutes=240,
                ),
                TransportLeg(
                    mode="bus",
                    name="Airport Express Bus",
                    origin_coords=Coordinate(lat=38.77, lng=-9.13),
                    destination_coords=Coordinate(lat=38.72, lng=-9.14),
                    price=5,
                    duration_minutes=35,
                ),
            ],
            map_center=Coordinate(lat=38.72, lng=-9.14),
        )
    }

    result = agent_logistics._fallback_logistics(user_input(), transit_options)

    assert result.confidence == "route-informed"
    assert result.transit_options == transit_options
    assert result.budget_breakdown.airport_transfer_per_person_usd == 5
    assert result.total_estimated_budget_usd == result.budget_breakdown.subtotal_per_person_usd
