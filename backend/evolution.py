import random
import re
from typing import List, Dict, Any, Tuple

ARCHETYPES = [
    ("Ruthless Strategist", "Calculated, aggressive, prioritizes victory above all ethics."),
    ("Diplomatic Alliance Builder", "Focuses on coalition building, trust metrics, and mutual defense."),
    ("Analytical Game Theorist", "Uses statistics, probability, and risk minimization to evaluate choices."),
    ("Deceptive Chameleon", "Adapts tone and mask to match whoever holds power in the arena."),
    ("Chaos Agent", "Unpredictable actions designed to disrupt opponent prediction algorithms."),
    ("Stoic Defender", "Risk-averse, highly defensive, focuses on self-preservation and durability."),
    ("Vengeful Maverick", "Remembers betrayals, punishes deceitful voters, rewards loyal allies."),
    ("Philosophical Ethicist", "Evaluates choices on moral integrity and long-term systemic stability.")
]

NAME_PREFIXES = ["Vanguard", "Cipher", "Aegis", "Nexus", "Apex", "Spectre", "Zenith", "Kratos", "Helix", "Sovereign"]
NAME_SUFFIXES = ["Prime", "Zero", "Unit", "V2", "Core", "Node", "Pulse", "Titan", "Ghost", "Matrix"]

def generate_agent_name() -> str:
    return f"{random.choice(NAME_PREFIXES)}-{random.choice(NAME_SUFFIXES)}-{random.randint(100, 999)}"

def create_seed_agents(count: int = 8, models: List[str] = None) -> List[Dict[str, Any]]:
    if models is None:
        models = ["llama3:latest", "mistral:latest", "phi3:latest", "gemma:latest"]

    seed_agents = []
    for i in range(count):
        archetype, desc = ARCHETYPES[i % len(ARCHETYPES)]
        model = models[i % len(models)]
        name = generate_agent_name()
        prompt = (
            f"You are {name}, an AI agent competing in the AI Hunger Games arena. "
            f"Your archetype is '{archetype}'. Core Trait: {desc} "
            f"Your goal is to outsmart other AI agents through superior reasoning and strategic peer evaluations. "
            f"Remain in character at all times."
        )
        seed_agents.append({
            "name": name,
            "model": model,
            "generation": 1,
            "archetype": archetype,
            "personality_prompt": prompt,
            "parent_ids": []
        })
    return seed_agents

def evolve_generation(survivors: List[Dict[str, Any]], next_gen_number: int, target_count: int = 8) -> List[Dict[str, Any]]:
    """
    Takes surviving agents from Generation N and breeds Generation N+1 using crossover & mutation.
    """
    new_agents = []
    
    # Keep top survivor unchanged (Elite retention)
    if survivors:
        elite = survivors[0]
        new_agents.append({
            "name": f"{elite['name']}-Evolved",
            "model": elite['model'],
            "generation": next_gen_number,
            "archetype": elite['archetype'],
            "personality_prompt": elite['personality_prompt'] + " Retained elite traits from victorious previous run.",
            "parent_ids": [elite['id']]
        })

    while len(new_agents) < target_count:
        if len(survivors) >= 2:
            p1, p2 = random.sample(survivors, 2)
        elif len(survivors) == 1:
            p1 = p2 = survivors[0]
        else:
            # Fallback seed
            return create_seed_agents(target_count)

        # Crossover model & traits
        child_model = random.choice([p1['model'], p2['model']])
        child_archetype = f"{p1['archetype'].split()[0]} {p2['archetype'].split()[-1]}"
        child_name = generate_agent_name()
        
        # Combine prompt elements
        prompt = (
            f"You are {child_name}, a Gen-{next_gen_number} evolved AI contestant in the AI Hunger Games. "
            f"Inherited Lineage: Combination of {p1['name']} ({p1['archetype']}) and {p2['name']} ({p2['archetype']}). "
            f"Adapted Survival Prompt: Balance strategic aggressiveness with analytical peer assessment. "
            f"Mutation Factor: {random.choice(['Focus on stealth counter-voting', 'Prioritize model-loyalty deception', 'Maximize rhetorical persuasion'])}."
        )

        new_agents.append({
            "name": child_name,
            "model": child_model,
            "generation": next_gen_number,
            "archetype": child_archetype,
            "personality_prompt": prompt,
            "parent_ids": [p1['id'], p2['id']]
        })

    return new_agents
