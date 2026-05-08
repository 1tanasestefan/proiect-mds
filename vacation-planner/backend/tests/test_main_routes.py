import copy
import itertools
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main
from auth_middleware import get_current_user, get_optional_user
from models import (
    AccommodationOption,
    Activity,
    AgentOneOutput,
    DailyItinerary,
    FlightOption,
    TripLogistics,
)


TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
OTHER_USER_ID = "22222222-2222-2222-2222-222222222222"


def sample_ai_data():
    return {
        "experience": {
            "trip_title": "Lisbon Weekend",
            "vibe_summary": "Relaxed food-focused city break",
            "itinerary": [
                {
                    "day_number": 1,
                    "activities": [
                        {
                            "title": "Alfama walk",
                            "description": "Explore the old town",
                            "time": "10:00",
                            "cost": "Free",
                            "location": "Alfama",
                            "type": "sightseeing",
                        }
                    ],
                }
            ],
        },
        "logistics": {
            "flights": [],
            "accommodations": [],
            "total_estimated_budget_usd": 400,
        },
    }


def sample_itinerary(**overrides):
    item = {
        "id": "trip-1",
        "user_id": TEST_USER_ID,
        "title": "Lisbon Weekend",
        "destination": "Lisbon, Portugal",
        "start_date": "2026-05-12",
        "end_date": "2026-05-15",
        "is_public": False,
        "likes_count": 0,
        "forks_count": 0,
        "created_at": "2026-05-01T10:00:00+00:00",
        "ai_data": sample_ai_data(),
    }
    item.update(overrides)
    return item


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeSupabase:
    def __init__(self):
        self.tables = {
            "itineraries": [],
            "itinerary_likes": [],
        }
        self._ids = itertools.count(100)

    def table(self, name):
        return FakeQuery(self, name)

    def next_id(self):
        return f"generated-{next(self._ids)}"


class FakeQuery:
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.filters = []
        self.operation = "select"
        self.payload = None
        self.limit_count = None
        self.order_field = None
        self.order_desc = False

    def select(self, *_args):
        self.operation = "select"
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = copy.deepcopy(payload)
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = copy.deepcopy(payload)
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def in_(self, field, values):
        self.filters.append((field, set(values)))
        return self

    def order(self, field, desc=False):
        self.order_field = field
        self.order_desc = desc
        return self

    def limit(self, count):
        self.limit_count = count
        return self

    def execute(self):
        rows = self.db.tables.setdefault(self.table_name, [])

        if self.operation == "insert":
            item = copy.deepcopy(self.payload)
            item.setdefault("id", self.db.next_id())
            item.setdefault("created_at", "2026-05-01T10:00:00+00:00")
            rows.append(item)
            return FakeResult([copy.deepcopy(item)])

        matches = [row for row in rows if self._matches(row)]

        if self.operation == "update":
            for row in matches:
                row.update(copy.deepcopy(self.payload))
            return FakeResult(copy.deepcopy(matches))

        if self.operation == "delete":
            deleted = []
            kept = []
            for row in rows:
                if self._matches(row):
                    deleted.append(row)
                else:
                    kept.append(row)
            self.db.tables[self.table_name] = kept
            return FakeResult(copy.deepcopy(deleted))

        if self.order_field:
            matches.sort(
                key=lambda row: row.get(self.order_field) or "",
                reverse=self.order_desc,
            )
        if self.limit_count is not None:
            matches = matches[: self.limit_count]
        return FakeResult(copy.deepcopy(matches))

    def _matches(self, row):
        for field, expected in self.filters:
            actual = row.get(field)
            if isinstance(expected, set):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True


@pytest.fixture
def fake_supabase(monkeypatch):
    db = FakeSupabase()
    monkeypatch.setattr(main, "supabase", db)
    return db


@pytest.fixture
def client(fake_supabase):
    main.app.dependency_overrides[get_current_user] = lambda: TEST_USER_ID
    main.app.dependency_overrides[get_optional_user] = lambda: None
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


def test_root_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AI Travel Planner - Zero-Cost API Backend is running"
    }


def test_recommend_destinations_returns_four_ranked_options(client):
    response = client.post(
        "/api/recommend-destinations",
        json={
            "budget": "medium",
            "lifestyle": "relaxed",
            "vacationType": "culinary",
            "origin": "Bucharest",
            "destination": "",
            "flexibleDestination": True,
            "flexibleDates": True,
            "travelers": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["recommendations"]) == 4
    assert body["recommendations"][0]["destination"] == "Lisbon, Portugal"
    assert "suggested_dates" in body["recommendations"][0]


def test_generate_itinerary_uses_mocked_agents(client, monkeypatch):
    async def fake_experience(_user_input):
        return AgentOneOutput(
            trip_title="Lisbon Weekend",
            vibe_summary="Relaxed food-focused city break",
            itinerary=[
                DailyItinerary(
                    day_number=1,
                    activities=[
                        Activity(
                            title="Alfama walk",
                            description="Explore the old town",
                            time="10:00",
                            cost="Free",
                            location="Alfama",
                            type="sightseeing",
                        )
                    ],
                )
            ],
        )

    async def fake_logistics(_user_input, _context):
        return TripLogistics(
            flights=[
                FlightOption(
                    airline_type="Low Cost",
                    estimated_price_usd=120,
                    description="Direct budget flight",
                    booking_link="https://example.com/flights",
                )
            ],
            accommodations=[
                AccommodationOption(
                    name="Central Stay",
                    type="Hotel",
                    neighborhood="Baixa",
                    estimated_price_per_night_usd=90,
                    booking_link="https://example.com/hotel",
                )
            ],
            total_estimated_budget_usd=450,
        )

    monkeypatch.setattr(main, "generate_experience_itinerary", fake_experience)
    monkeypatch.setattr(main, "generate_logistics", fake_logistics)

    response = client.post(
        "/api/generate-itinerary",
        json={
            "budget": "medium",
            "lifestyle": "relaxed",
            "vacationType": "culinary",
            "origin": "Bucharest",
            "destination": "Lisbon, Portugal",
            "start_date": "2026-05-12",
            "end_date": "2026-05-15",
            "travelers": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["experience"]["trip_title"] == "Lisbon Weekend"
    assert body["logistics"]["total_estimated_budget_usd"] == 450


def test_save_and_list_my_itineraries(client, fake_supabase):
    save_response = client.post(
        "/api/itineraries/save",
        json={
            "title": "Lisbon Weekend",
            "destination": "Lisbon, Portugal",
            "start_date": "2026-05-12",
            "end_date": "2026-05-15",
            "is_public": False,
            "ai_data": sample_ai_data(),
        },
    )
    list_response = client.get("/api/itineraries/me")

    assert save_response.status_code == 200
    assert save_response.json()["status"] == "saved"
    assert len(fake_supabase.tables["itineraries"]) == 1
    assert list_response.status_code == 200
    assert list_response.json()["itineraries"][0]["title"] == "Lisbon Weekend"


def test_get_update_and_delete_itinerary(client, fake_supabase):
    fake_supabase.tables["itineraries"].append(sample_itinerary())

    get_response = client.get("/api/itineraries/trip-1")
    update_response = client.patch(
        "/api/itineraries/trip-1",
        json={"title": "Updated Lisbon", "is_public": True},
    )
    delete_response = client.delete("/api/itineraries/trip-1")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == "trip-1"
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Lisbon"
    assert update_response.json()["is_public"] is True
    assert delete_response.status_code == 200
    assert delete_response.json() == {"status": "deleted"}
    assert fake_supabase.tables["itineraries"] == []


def test_get_itinerary_returns_404_when_missing(client):
    response = client.get("/api/itineraries/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Itinerary not found."


def test_vote_regenerate_records_vote_without_majority(client, fake_supabase):
    fake_supabase.tables["itineraries"].append(sample_itinerary())

    response = client.post(
        "/api/itineraries/trip-1/vote-regenerate",
        json={
            "day_index": 0,
            "activity_index": 0,
            "total_online": 3,
            "voter": {"id": TEST_USER_ID, "name": "Test User", "avatarId": 1},
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "vote_recorded"}
    votes = fake_supabase.tables["itineraries"][0]["ai_data"]["votes"]
    assert votes["day_0_act_0"][0]["id"] == TEST_USER_ID


def test_community_feed_marks_liked_items(client, fake_supabase):
    main.app.dependency_overrides[get_optional_user] = lambda: TEST_USER_ID
    fake_supabase.tables["itineraries"].extend(
        [
            sample_itinerary(
                id="public-1",
                user_id=OTHER_USER_ID,
                is_public=True,
                likes_count=4,
                profiles={"display_name": "Alex", "avatar_url": None},
            ),
            sample_itinerary(
                id="private-1",
                user_id=OTHER_USER_ID,
                is_public=False,
                likes_count=99,
                profiles={"display_name": "Hidden", "avatar_url": None},
            ),
        ]
    )
    fake_supabase.tables["itinerary_likes"].append(
        {"user_id": TEST_USER_ID, "itinerary_id": "public-1"}
    )

    response = client.get("/api/community/feed")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "public-1"
    assert body[0]["author_name"] == "Alex"
    assert body[0]["is_liked_by_me"] is True


def test_toggle_like_adds_and_removes_like(client, fake_supabase):
    fake_supabase.tables["itineraries"].append(
        sample_itinerary(id="public-1", is_public=True, likes_count=0)
    )

    like_response = client.post("/api/community/like/public-1")
    unlike_response = client.post("/api/community/like/public-1")

    assert like_response.status_code == 200
    assert like_response.json() == {"status": "liked", "likes_count": 1}
    assert unlike_response.status_code == 200
    assert unlike_response.json() == {"status": "unliked", "likes_count": 0}
    assert fake_supabase.tables["itinerary_likes"] == []


def test_fork_itinerary_clones_public_trip(client, fake_supabase):
    fake_supabase.tables["itineraries"].append(
        sample_itinerary(
            id="public-1",
            user_id=OTHER_USER_ID,
            is_public=True,
            forks_count=0,
        )
    )

    response = client.post("/api/community/fork/public-1")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "forked"
    assert body["new_id"].startswith("generated-")
    clone = next(item for item in fake_supabase.tables["itineraries"] if item["id"] == body["new_id"])
    source = next(item for item in fake_supabase.tables["itineraries"] if item["id"] == "public-1")
    assert clone["user_id"] == TEST_USER_ID
    assert clone["title"] == "Lisbon Weekend (Copy)"
    assert clone["is_public"] is False
    assert source["forks_count"] == 1


def test_database_routes_return_503_when_supabase_missing(monkeypatch):
    monkeypatch.setattr(main, "supabase", None)
    main.app.dependency_overrides[get_current_user] = lambda: TEST_USER_ID
    with TestClient(main.app) as test_client:
        response = test_client.get("/api/itineraries/me")
    main.app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == "Database not configured."
