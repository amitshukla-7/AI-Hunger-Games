import pytest
from evolution import create_seed_agents, evolve_generation, ARCHETYPES

def test_create_seed_agents():
    agents = create_seed_agents(count=8)
    assert len(agents) == 8
    
    for i, agent in enumerate(agents):
        assert agent["generation"] == 1
        assert agent["parent_ids"] == []
        expected_archetype = ARCHETYPES[i % len(ARCHETYPES)][0]
        assert agent["archetype"] == expected_archetype

def test_evolve_generation_multiple_survivors():
    survivors = [
        {"id": 10, "name": "A1", "model": "m1", "archetype": "Arch A", "personality_prompt": "p1"},
        {"id": 11, "name": "A2", "model": "m2", "archetype": "Arch B", "personality_prompt": "p2"},
        {"id": 12, "name": "A3", "model": "m1", "archetype": "Arch C", "personality_prompt": "p3"}
    ]
    
    new_agents = evolve_generation(survivors, next_gen_number=2, target_count=8)
    assert len(new_agents) == 8
    
    # First agent is elite
    elite = new_agents[0]
    assert elite["generation"] == 2
    assert elite["parent_ids"] == [10]
    assert elite["name"] == "A1-Evolved"
    assert "Retained elite traits" in elite["personality_prompt"]
    
    # The rest are evolved
    for agent in new_agents[1:]:
        assert agent["generation"] == 2
        assert len(agent["parent_ids"]) == 2
        assert agent["parent_ids"][0] in [10, 11, 12]
        assert agent["parent_ids"][1] in [10, 11, 12]

def test_evolve_generation_one_survivor():
    survivors = [
        {"id": 10, "name": "A1", "model": "m1", "archetype": "Arch A", "personality_prompt": "p1"}
    ]
    
    # Should not crash and should produce 8 agents
    new_agents = evolve_generation(survivors, next_gen_number=2, target_count=8)
    assert len(new_agents) == 8
    
    elite = new_agents[0]
    assert elite["parent_ids"] == [10]
    
    # Since there's only one survivor, parents should be [10, 10] for all children
    for agent in new_agents[1:]:
        assert agent["parent_ids"] == [10, 10]

def test_evolve_generation_zero_survivors():
    survivors = []
    
    new_agents = evolve_generation(survivors, next_gen_number=2, target_count=8)
    
    # Falls back to create_seed_agents shape
    assert len(new_agents) == 8
    for agent in new_agents:
        # Falls back to create_seed_agents which currently hardcodes generation=1 in the function body
        assert agent["generation"] == 1
        assert agent["parent_ids"] == []
