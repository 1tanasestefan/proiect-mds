import pytest
from pydantic import ValidationError

from models import Activity, UserInput


def valid_user_input(**overrides):
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


def test_user_input_accepts_frontend_aliases_and_calculates_trip_days():
    user_input = valid_user_input(
        flexibleDates=False,
        flexibleDestination=False,
    )

    assert user_input.flexible_dates is False
    assert user_input.flexible_destination is False
    assert user_input.trip_days == 3


def test_user_input_allows_missing_dates_only_in_flexible_dates_mode():
    flexible = valid_user_input(
        flexibleDates=True,
        start_date=None,
        end_date=None,
    )

    assert flexible.trip_days == 3

    with pytest.raises(ValidationError, match="Dates are required"):
        valid_user_input(start_date=None, end_date=None)


def test_user_input_rejects_invalid_or_risky_trip_shapes():
    with pytest.raises(ValidationError, match="End date must be after start date"):
        valid_user_input(start_date="2026-06-04", end_date="2026-06-04")

    with pytest.raises(ValidationError, match="maximum of 5 days"):
        valid_user_input(start_date="2026-06-01", end_date="2026-06-08")

    with pytest.raises(ValidationError, match="Destination is required"):
        valid_user_input(destination="")


def test_activity_normalizes_model_output_without_breaking_contract():
    activity = Activity(
        description="Fallback description",
        time="Morning",
        cost="Free",
        location="Baixa, Lisbon",
        type="invented-model-type",
    )

    assert activity.title == "Activity"
    assert activity.type == "experience"
