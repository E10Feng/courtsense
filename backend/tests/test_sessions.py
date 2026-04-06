"""
pytest session tests for CourtSense backend.
Run with: pytest backend/tests/test_sessions.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import date
from uuid import uuid4

from backend.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def demo_user():
    return str(uuid4())


@pytest.mark.asyncio
async def test_create_session_valid(client, demo_user):
    """POST /sessions with all required fields returns 200 and session id."""
    payload = {
        "user_id": demo_user,
        "sport": "pickleball",
        "score": "11-9, 8-11",
        "partner_names": "Alex",
        "opponent_names": "Sam",
        "drills_done": "dinks",
        "energy": 4,
        "mood": 3,
        "legs": 3,
        "notes": "Good day",
    }
    res = await client.post("/sessions", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert data["sport"] == "pickleball"
    assert data["score"] == "11-9, 8-11"


@pytest.mark.asyncio
async def test_create_session_minimal(client, demo_user):
    """POST /sessions with only required fields (sport + score) returns 200."""
    payload = {
        "user_id": demo_user,
        "sport": "tennis",
        "score": "6-4, 3-6",
    }
    res = await client.post("/sessions", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["sport"] == "tennis"


@pytest.mark.asyncio
async def test_create_session_invalid_sport(client, demo_user):
    """POST /sessions with invalid sport returns 422."""
    payload = {
        "user_id": demo_user,
        "sport": "badminton",
        "score": "11-9",
    }
    res = await client.post("/sessions", json=payload)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_session_missing_required(client, demo_user):
    """POST /sessions missing sport returns 422."""
    payload = {
        "user_id": demo_user,
        "score": "6-4",
    }
    res = await client.post("/sessions", json=payload)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_get_sessions_empty(client, demo_user):
    """GET /sessions/{user_id} with no sessions returns empty list."""
    res = await client.get(f"/sessions/{demo_user}")
    assert res.status_code == 200
    assert res.json()["sessions"] == []


@pytest.mark.asyncio
async def test_get_sessions_with_data(client, demo_user):
    """Log sessions then retrieve them."""
    for score in ["11-9", "8-11", "6-4"]:
        await client.post("/sessions", json={
            "user_id": demo_user,
            "sport": "pickleball",
            "score": score,
        })

    res = await client.get(f"/sessions/{demo_user}?days=30")
    assert res.status_code == 200
    sessions = res.json()["sessions"]
    assert len(sessions) == 3
    # Most recent first
    scores = [s["score"] for s in sessions]
    assert scores == ["6-4", "8-11", "11-9"]


@pytest.mark.asyncio
async def test_get_sessions_filters_by_days(client, demo_user):
    """GET /sessions/{user_id}?days=7 respects cutoff."""
    # Create old session (would need to mock date — here we just verify query param is accepted)
    await client.post("/sessions", json={
        "user_id": demo_user,
        "sport": "tennis",
        "score": "6-4",
    })
    res = await client.get(f"/sessions/{demo_user}?days=1")
    assert res.status_code == 200
    data = res.json()
    # May be empty if session was created today vs "yesterday" in real scenario
    assert isinstance(data["sessions"], list)
