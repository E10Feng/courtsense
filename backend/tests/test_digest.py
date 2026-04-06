"""
pytest digest tests for CourtSense backend.
Run with: pytest backend/tests/test_digest.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from unittest.mock import patch, AsyncMock

from backend.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def demo_user():
    return str(uuid4())


@pytest.mark.asyncio
async def test_generate_digest_no_sessions(client, demo_user):
    """POST /digest/generate with no sessions returns 404."""
    res = await client.post("/digest/generate", json={"user_id": demo_user})
    assert res.status_code == 404
    assert "No sessions found" in res.json()["detail"]


@pytest.mark.asyncio
async def test_get_digest_no_digest(client, demo_user):
    """GET /digest/{user_id} with no digest returns 404."""
    res = await client.get(f"/digest/{demo_user}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_generate_then_get_digest(client, demo_user):
    """Log sessions then generate and retrieve digest."""
    # Log a session first
    await client.post("/sessions", json={
        "user_id": demo_user,
        "sport": "pickleball",
        "score": "11-9, 3-11",
        "drills_done": "dinks",
        "notes": "backhand felt weak all day",
        "energy": 3,
        "mood": 2,
        "legs": 2,
    })

    # Mock the LLM call to avoid external dependency
    with patch("backend.services.digest_agent.generate_digest_graph", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "weakness_summary": "Player struggled with backhand returns and net play.",
            "top_weaknesses": [
                {"area": "backhand return", "percent": 70.0, "evidence": "lost most points using backhand in session 2026-04-06"}
            ],
            "drill_recommendations": [
                {"drill": "Dink Circle", "why": "builds net consistency", "reps": "20-30", "sets": "3-4"}
            ],
        }
        res = await client.post("/digest/generate", json={"user_id": demo_user})

    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert data["sessions_count"] == 1
    assert data["weakness_summary"] is not None
    assert len(data["top_weaknesses"]) == 1
    assert len(data["drill_recommendations"]) == 1

    # Retrieve the digest
    get_res = await client.get(f"/digest/{demo_user}")
    assert get_res.status_code == 200
    assert get_res.json()["weakness_summary"] == data["weakness_summary"]
