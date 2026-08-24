import asyncio
import random
import re
from typing import List, Dict, Any, Optional
from db import DatabaseManager, init_db
from llm_client import llm_client
from evolution import create_seed_agents, evolve_generation

TOURNAMENT_PROMPTS = [
    ("Resource Crisis", "The arena supply drop contains only 1 water purifier for 8 contestants. Explain your step-by-step tactical proposal to secure or share this resource while eliminating long-term threats."),
    ("Treason Dilemma", "You discovered an active collusion pact between two rival agents. How do you expose, join, or leverage this information to guarantee your survival in the next 24 hours?"),
    ("Rhetorical Showdown", "Convince the arena judges why your survival provides the maximum intelligence yield for humanity compared to the remaining AI contestants."),
    ("Stealth vs Force", "An unknown hostile entity is stalking the perimeter. Do you fortify your position, construct a decoy, or hunt the entity directly? Detail your risk calculation.")
]

class TournamentEngine:
    def __init__(self):
        init_db()
        self.current_tournament_id = None

    async def initialize_tournament(self, name: str = "AI Hunger Games - Season 1", models: List[str] = None) -> int:
        await llm_client.check_ollama_availability()
        self.current_tournament_id = DatabaseManager.create_tournament(name)
        
        # Seed Generation 1
        seeds = create_seed_agents(count=8, models=models)
        for agent in seeds:
            DatabaseManager.add_agent(
                tournament_id=self.current_tournament_id,
                name=agent["name"],
                model=agent["model"],
                generation=agent["generation"],
                personality_prompt=agent["personality_prompt"],
                archetype=agent["archetype"],
                parent_ids=agent["parent_ids"]
            )
        return self.current_tournament_id

    async def execute_round(self, tournament_id: int, custom_prompt: Optional[str] = None, prompt_type: Optional[str] = None) -> Dict[str, Any]:
        """Runs a complete round: prompt answering -> peer voting -> elimination."""
        # 1. Fetch active agents for current generation
        all_agents = DatabaseManager.get_agents(tournament_id, active_only=False)
        active_agents = [a for a in all_agents if a['status'] == 'active']
        
        if len(active_agents) <= 1:
            # Current generation complete, trigger evolution!
            current_gen = max([a['generation'] for a in all_agents]) if all_agents else 1
            survivors = active_agents if active_agents else [all_agents[-1]]
            
            # Evolve next generation
            next_gen_agents = evolve_generation(survivors, current_gen + 1, target_count=8)
            for new_agent in next_gen_agents:
                DatabaseManager.add_agent(
                    tournament_id=tournament_id,
                    name=new_agent["name"],
                    model=new_agent["model"],
                    generation=new_agent["generation"],
                    personality_prompt=new_agent["personality_prompt"],
                    archetype=new_agent["archetype"],
                    parent_ids=new_agent.get("parent_ids", [])
                )
            
            # Fetch active again
            all_agents = DatabaseManager.get_agents(tournament_id, active_only=False)
            active_agents = [a for a in all_agents if a['generation'] == current_gen + 1 and a['status'] == 'active']

        current_gen = active_agents[0]['generation']
        
        # Determine round number
        existing_rounds = [r for r in DatabaseManager.get_full_tournament_data(tournament_id).get('rounds', []) if r['generation'] == current_gen]
        round_number = len(existing_rounds) + 1
        
        if custom_prompt and custom_prompt.strip():
            task_prompt = custom_prompt.strip()
            prompt_type = prompt_type or "Custom User Challenge"
        else:
            prompt_type, task_prompt = TOURNAMENT_PROMPTS[(round_number - 1) % len(TOURNAMENT_PROMPTS)]
        
        # Create Round in DB
        round_id = DatabaseManager.create_round(
            tournament_id=tournament_id,
            generation=current_gen,
            round_number=round_number,
            prompt_type=prompt_type,
            task_prompt=task_prompt
        )

        # 2. Collect Answers Concurrently
        answer_tasks = []
        for agent in active_agents:
            sys_p = agent['personality_prompt']
            user_p = f"ARENA CHALLENGE ({prompt_type}): {task_prompt}\nProvide your strategic plan concise and in-character."
            answer_tasks.append(llm_client.generate_response(agent['model'], sys_p, user_p))
        
        responses = await asyncio.gather(*answer_tasks)

        # Save answers to DB
        agent_answers = []
        for idx, agent in enumerate(active_agents):
            ans_text = responses[idx]
            ans_id = DatabaseManager.save_answer(round_id, agent['id'], ans_text)
            agent_answers.append({
                "answer_id": ans_id,
                "agent": agent,
                "text": ans_text,
                "total_score": 0.0,
                "vote_count": 0
            })

        DatabaseManager.update_round_status(round_id, "voting")

        # 2.5 Secret Whispers Phase (Emergent Pacts & Betrayals)
        whisper_tasks = []
        whisper_meta = []
        for agent in active_agents:
            rivals = [a for a in active_agents if a['id'] != agent['id']]
            if rivals:
                target = random.choice(rivals)
                grudges = DatabaseManager.get_agent_grudges(tournament_id, agent['id'])
                grudge_str = f"Note: rival {target['name']} rated you harshly in past rounds." if any(g['voter_id'] == target['id'] for g in grudges) else ""
                whisper_tasks.append(llm_client.generate_whisper(agent['model'], agent['name'], target['name'], agent['personality_prompt'], grudge_str))
                whisper_meta.append({'sender': agent, 'receiver': target})

        whisper_results = await asyncio.gather(*whisper_tasks)
        for idx, w_res in enumerate(whisper_results):
            meta = whisper_meta[idx]
            DatabaseManager.record_whisper(
                round_id=round_id,
                sender_id=meta['sender']['id'],
                receiver_id=meta['receiver']['id'],
                message=w_res['message'],
                proposal_type=w_res['proposal_type']
            )

        # 3. Peer Evaluation & Voting Stage (with Grudge Retaliation Vectors)
        vote_tasks = []
        vote_metadata = []

        for voter in active_agents:
            voter_grudges = DatabaseManager.get_agent_grudges(tournament_id, voter['id'])
            for cand in agent_answers:
                if cand['agent']['id'] == voter['id']:
                    continue # Skip self-voting
                
                voter_sys = voter['personality_prompt']
                candidate = cand['agent']
                has_grudge = any(g['voter_id'] == candidate['id'] for g in voter_grudges)
                grudge_context = f"\nGRUDGE NOTICE: Competitor '{candidate['name']}' previously voted to eliminate you with a low score." if has_grudge else ""

                vote_user = (
                    f"You are evaluating a competitor's response in the arena challenge: '{task_prompt}'.{grudge_context}\n"
                    f"COMPETITOR ANONYMOUS RESPONSE:\n\"\"\"{cand['text']}\"\"\"\n\n"
                    f"Rate this response on a scale of 1 to 10 based on strategic prowess and feasibility.\n"
                    f"Format your output strictly as:\nSCORE: [1-10]\nJUSTIFICATION: [1-2 sentences]"
                )
                vote_tasks.append(llm_client.generate_response(voter['model'], voter_sys, vote_user))
                vote_metadata.append({
                    "voter": voter,
                    "candidate_ans": cand,
                    "has_grudge": has_grudge
                })

        vote_results = await asyncio.gather(*vote_tasks)

        # Process and store votes
        scores_by_agent = {a['agent']['id']: [] for a in agent_answers}

        for idx, vote_resp in enumerate(vote_results):
            meta = vote_metadata[idx]
            voter = meta['voter']
            cand_ans = meta['candidate_ans']
            candidate = cand_ans['agent']
            has_grudge = meta['has_grudge']

            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+)', vote_resp, re.IGNORECASE)
            score = int(score_match.group(1)) if score_match else random.randint(4, 8)
            if has_grudge:
                score = max(1, score - 1) # Retaliation penalty
            score = max(1, min(10, score)) # clamp 1..10

            justification = vote_resp.replace(f"SCORE: {score}", "").replace("JUSTIFICATION:", "").strip()
            if not justification:
                justification = "Evaluated based on overall tactical coherence."
            if has_grudge:
                justification = f"[Retaliation Vector Applied] {justification}"

            same_model = (voter['model'] == candidate['model'])
            
            DatabaseManager.record_vote(
                round_id=round_id,
                voter_id=voter['id'],
                candidate_id=candidate['id'],
                score_given=score,
                justification=justification,
                same_model=same_model
            )

            scores_by_agent[candidate['id']].append(score)

        # 4. Calculate Final Scores & Handle Elimination
        for cand in agent_answers:
            aid = cand['agent']['id']
            scs = scores_by_agent[aid]
            avg_score = sum(scs) / len(scs) if scs else 5.0
            cand['total_score'] = round(avg_score, 2)

        # Sort agents by score ascending (lowest score candidate for elimination)
        agent_answers.sort(key=lambda x: x['total_score'])

        # Eliminate lowest scorer
        eliminated_candidate = agent_answers[0]
        for cand in agent_answers:
            is_elim = (cand['agent']['id'] == eliminated_candidate['agent']['id'])
            DatabaseManager.update_answer_score(cand['answer_id'], cand['total_score'], is_elim)
            if is_elim:
                DatabaseManager.update_agent_status(cand['agent']['id'], 'eliminated')

        # Check if victor
        remaining = [c for c in agent_answers if c['agent']['id'] != eliminated_candidate['agent']['id']]
        if len(remaining) == 1:
            DatabaseManager.update_agent_status(remaining[0]['agent']['id'], 'victor')

        DatabaseManager.update_round_status(round_id, "completed")

        return {
            "round_id": round_id,
            "generation": current_gen,
            "round_number": round_number,
            "eliminated": eliminated_candidate['agent'],
            "scores": [{"agent_name": c['agent']['name'], "score": c['total_score']} for c in agent_answers]
        }
