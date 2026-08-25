import pytest
from httpx import AsyncClient, ASGITransport
from api import app
from db import DatabaseManager

@pytest.mark.asyncio
async def test_get_state():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert "tournament" in data
    assert data["tournament"]["name"] == "AI Hunger Games - Season 1"

@pytest.mark.asyncio
async def test_start_tournament():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/tournament/start", json={"name": "Test Arena"})
    assert response.status_code == 200
    data = response.json()
    assert "tournament_id" in data
    t_id = data["tournament_id"]
    
    # Verify it created 8 seed agents
    agents = DatabaseManager.get_agents(t_id)
    assert len(agents) == 8

@pytest.mark.asyncio
async def test_tournament_step():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Start tournament
        await ac.post("/api/tournament/start", json={"name": "Step Arena"})
        
        # Step tournament
        response = await ac.post("/api/tournament/step")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    result = data["result"]
    assert "round_id" in result
    assert "eliminated" in result
    assert "scores" in result
    
    scores = result["scores"]
    assert isinstance(scores, list)
    assert len(scores) > 0
    for score_entry in scores:
        assert "agent_name" in score_entry
        assert "score" in score_entry
        # Check value ranges (1 to 10)
        assert 1.0 <= score_entry["score"] <= 10.0

@pytest.mark.asyncio
async def test_analytics():
    # Setup DB with known votes
    t_id = DatabaseManager.create_tournament("Analytics Tourney")
    a1 = DatabaseManager.add_agent(t_id, "A1", "m1", 1, "p", "a")
    a2 = DatabaseManager.add_agent(t_id, "A2", "m2", 1, "p", "a")
    a3 = DatabaseManager.add_agent(t_id, "A3", "m1", 1, "p", "a")
    r_id = DatabaseManager.create_round(t_id, 1, 1, "type", "task")
    
    # same_model votes:
    DatabaseManager.record_vote(r_id, a1, a3, 8, "same", True)
    DatabaseManager.record_vote(r_id, a3, a1, 6, "same", True)
    
    # cross_model votes:
    DatabaseManager.record_vote(r_id, a1, a2, 4, "cross", False)
    DatabaseManager.record_vote(r_id, a2, a1, 2, "cross", False)
    
    # same_avg = 7.0, cross_avg = 3.0, bias_factor = 4.0
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/analytics?tournament_id={t_id}")
        
    assert response.status_code == 200
    data = response.json()
    
    assert data["same_model_avg"] == 7.0
    assert data["cross_model_avg"] == 3.0
    assert data["bias_factor"] == 4.0
