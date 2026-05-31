import asyncio

import agent_logistics
from models import UserInput


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
