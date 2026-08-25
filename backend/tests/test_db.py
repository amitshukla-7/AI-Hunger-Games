import pytest
from db import DatabaseManager

def test_create_tournament():
    t_id = DatabaseManager.create_tournament("Test Tournament")
    assert t_id is not None
    assert t_id > 0
    latest_id = DatabaseManager.get_latest_tournament_id()
    assert latest_id == t_id

def test_add_agent_and_get_agents():
    t_id = DatabaseManager.create_tournament("Test Tourney")
    
    agent_id_1 = DatabaseManager.add_agent(t_id, "Agent A", "model_1", 1, "prompt A", "Archetype A", [1, 2])
    agent_id_2 = DatabaseManager.add_agent(t_id, "Agent B", "model_2", 1, "prompt B", "Archetype B", [])
    agent_id_3 = DatabaseManager.add_agent(t_id, "Agent C", "model_1", 2, "prompt C", "Archetype C", [agent_id_1])
    
    # Update one to eliminated
    DatabaseManager.update_agent_status(agent_id_2, "eliminated")
    
    # All agents
    all_agents = DatabaseManager.get_agents(t_id)
    assert len(all_agents) == 3
    assert all_agents[0]['parent_ids'] == [1, 2]
    
    # Filter by generation
    gen1_agents = DatabaseManager.get_agents(t_id, generation=1)
    assert len(gen1_agents) == 2
    
    gen2_agents = DatabaseManager.get_agents(t_id, generation=2)
    assert len(gen2_agents) == 1
    assert gen2_agents[0]['name'] == "Agent C"
    
    # Filter by active_only
    active_agents = DatabaseManager.get_agents(t_id, active_only=True)
    assert len(active_agents) == 2
    active_names = [a['name'] for a in active_agents]
    assert "Agent A" in active_names
    assert "Agent C" in active_names
    assert "Agent B" not in active_names

def test_record_vote():
    t_id = DatabaseManager.create_tournament("Tourney")
    a1 = DatabaseManager.add_agent(t_id, "A1", "m1", 1, "p", "a")
    a2 = DatabaseManager.add_agent(t_id, "A2", "m2", 1, "p", "a")
    r_id = DatabaseManager.create_round(t_id, 1, 1, "type", "task")
    
    # same_model = True
    v1 = DatabaseManager.record_vote(r_id, a1, a2, 7, "just1", True)
    # same_model = False
    v2 = DatabaseManager.record_vote(r_id, a2, a1, 3, "just2", False)
    
    data = DatabaseManager.get_full_tournament_data(t_id)
    votes = data['votes']
    assert len(votes) == 2
    
    v1_rec = next(v for v in votes if v['id'] == v1)
    assert v1_rec['same_model'] == 1
    
    v2_rec = next(v for v in votes if v['id'] == v2)
    assert v2_rec['same_model'] == 0

def test_get_agent_grudges():
    t_id = DatabaseManager.create_tournament("Grudge Tourney")
    voter_1 = DatabaseManager.add_agent(t_id, "Voter1", "m", 1, "p", "a")
    voter_2 = DatabaseManager.add_agent(t_id, "Voter2", "m", 1, "p", "a")
    target = DatabaseManager.add_agent(t_id, "Target", "m", 1, "p", "a")
    other = DatabaseManager.add_agent(t_id, "Other", "m", 1, "p", "a")
    
    r_id = DatabaseManager.create_round(t_id, 1, 1, "type", "task")
    
    DatabaseManager.record_vote(r_id, voter_1, target, 4, "bad", False) # grudge
    DatabaseManager.record_vote(r_id, voter_2, target, 8, "good", False) # not a grudge (score > 5)
    DatabaseManager.record_vote(r_id, voter_1, other, 2, "bad", False) # grudge against someone else
    DatabaseManager.record_vote(r_id, voter_2, target, 5, "ok", False) # grudge (score <= 5)
    
    grudges = DatabaseManager.get_agent_grudges(t_id, target)
    assert len(grudges) == 2
    scores = [g['score_given'] for g in grudges]
    assert sorted(scores) == [4, 5]
    voter_ids = [g['voter_id'] for g in grudges]
    assert voter_1 in voter_ids
    assert voter_2 in voter_ids

def test_get_full_tournament_data():
    t_id = DatabaseManager.create_tournament("Full Tourney")
    a1 = DatabaseManager.add_agent(t_id, "A1", "m", 1, "p", "a")
    a2 = DatabaseManager.add_agent(t_id, "A2", "m", 1, "p", "a")
    
    r_id = DatabaseManager.create_round(t_id, 1, 1, "type", "task")
    
    ans1 = DatabaseManager.save_answer(r_id, a1, "answer 1")
    ans2 = DatabaseManager.save_answer(r_id, a2, "answer 2")
    
    DatabaseManager.record_vote(r_id, a1, a2, 7, "j", True)
    DatabaseManager.record_vote(r_id, a2, a1, 3, "j", False)
    
    DatabaseManager.record_whisper(r_id, a1, a2, "hello", "alliance")
    
    data = DatabaseManager.get_full_tournament_data(t_id)
    
    assert data["tournament"]["id"] == t_id
    assert len(data["agents"]) == 2
    assert len(data["rounds"]) == 1
    assert len(data["answers"]) == 2
    assert len(data["votes"]) == 2
    assert len(data["whispers"]) == 1
    
    assert data["answers"][0]["agent_name"] in ["A1", "A2"]
    assert data["votes"][0]["voter_name"] in ["A1", "A2"]
    assert data["whispers"][0]["sender_name"] in ["A1", "A2"]
