from datetime import date

from app.services import recommendations
from models import UserInput


class FrozenDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 5, 31)


def test_recommend_dates_moves_past_windows_to_next_year(monkeypatch):
    monkeypatch.setattr(recommendations, "date", FrozenDate)

    result = recommendations.recommend_dates_for("Paris, France", "medium")

    assert result["start_date"] == "2027-05-12"
    assert result["end_date"] == "2027-05-15"
    assert "May" in result["reason"]


def test_recommend_destinations_ranks_budget_and_vibe_matches(monkeypatch):
    monkeypatch.setattr(recommendations, "get_supabase", lambda: None)
    user_input = UserInput(
        budget="low",
        lifestyle="nightowl",
        vacationType="party",
        origin="Bucharest, Romania",
        destination=None,
        flexibleDestination=True,
        flexibleDates=True,
        travelers=3,
    )

    result = __import__("asyncio").run(
        recommendations.recommend_destinations(user_input, user_id=None, limit=2)
    )

    assert [item["destination"] for item in result] == [
        "Prague, Czech Republic",
        "Budapest, Hungary",
    ]
    assert result[0]["match_score"] >= result[1]["match_score"]
