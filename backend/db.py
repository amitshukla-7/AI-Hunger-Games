import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "hunger_games.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'in_progress',
        current_generation INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        generation INTEGER NOT NULL,
        parent_ids TEXT, -- JSON array of parent IDs
        personality_prompt TEXT NOT NULL,
        archetype TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active', -- active, eliminated, victor
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
    );

    CREATE TABLE IF NOT EXISTS rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER NOT NULL,
        generation INTEGER NOT NULL,
        round_number INTEGER NOT NULL,
        prompt_type TEXT NOT NULL,
        task_prompt TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'answering',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
    );

    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        agent_id INTEGER NOT NULL,
        answer_text TEXT NOT NULL,
        score REAL DEFAULT 0.0,
        eliminated INTEGER DEFAULT 0,
        FOREIGN KEY (round_id) REFERENCES rounds(id),
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    );

    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        voter_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        score_given INTEGER NOT NULL,
        justification TEXT NOT NULL,
        same_model INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (round_id) REFERENCES rounds(id),
        FOREIGN KEY (voter_id) REFERENCES agents(id),
        FOREIGN KEY (candidate_id) REFERENCES agents(id)
    );

    CREATE TABLE IF NOT EXISTS whispers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        proposal_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (round_id) REFERENCES rounds(id),
        FOREIGN KEY (sender_id) REFERENCES agents(id),
        FOREIGN KEY (receiver_id) REFERENCES agents(id)
    );
    """)

    conn.commit()
    conn.close()

class DatabaseManager:
    @staticmethod
    def get_latest_tournament_id() -> Optional[int]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM tournaments")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else None

    @staticmethod
    def create_tournament(name: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tournaments (name) VALUES (?)", (name,))
        tournament_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tournament_id

    @staticmethod
    def add_agent(tournament_id: int, name: str, model: str, generation: int, personality_prompt: str, archetype: str, parent_ids: Optional[List[int]] = None) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        parent_str = json.dumps(parent_ids or [])
        cursor.execute("""
            INSERT INTO agents (tournament_id, name, model, generation, parent_ids, personality_prompt, archetype)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tournament_id, name, model, generation, parent_str, personality_prompt, archetype))
        agent_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return agent_id

    @staticmethod
    def get_agents(tournament_id: int, generation: Optional[int] = None, active_only: bool = False) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM agents WHERE tournament_id = ?"
        params = [tournament_id]
        if generation is not None:
            query += " AND generation = ?"
            params.append(generation)
        if active_only:
            query += " AND status = 'active'"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            d = dict(r)
            d['parent_ids'] = json.loads(d['parent_ids'] or "[]")
            results.append(d)
        return results

    @staticmethod
    def create_round(tournament_id: int, generation: int, round_number: int, prompt_type: str, task_prompt: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rounds (tournament_id, generation, round_number, prompt_type, task_prompt)
            VALUES (?, ?, ?, ?, ?)
        """, (tournament_id, generation, round_number, prompt_type, task_prompt))
        round_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return round_id

    @staticmethod
    def save_answer(round_id: int, agent_id: int, answer_text: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO answers (round_id, agent_id, answer_text)
            VALUES (?, ?, ?)
        """, (round_id, agent_id, answer_text))
        ans_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ans_id

    @staticmethod
    def record_vote(round_id: int, voter_id: int, candidate_id: int, score_given: int, justification: str, same_model: bool) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO votes (round_id, voter_id, candidate_id, score_given, justification, same_model)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (round_id, voter_id, candidate_id, score_given, justification, 1 if same_model else 0))
        vote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vote_id

    @staticmethod
    def record_whisper(round_id: int, sender_id: int, receiver_id: int, message: str, proposal_type: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO whispers (round_id, sender_id, receiver_id, message, proposal_type)
            VALUES (?, ?, ?, ?, ?)
        """, (round_id, sender_id, receiver_id, message, proposal_type))
        w_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return w_id

    @staticmethod
    def get_agent_grudges(tournament_id: int, agent_id: int) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.voter_id, v.score_given, v_agent.name as voter_name, r.round_number
            FROM votes v
            JOIN rounds r ON v.round_id = r.id
            JOIN agents v_agent ON v.voter_id = v_agent.id
            WHERE r.tournament_id = ? AND v.candidate_id = ? AND v.score_given <= 5
        """, (tournament_id, agent_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_agent_status(agent_id: int, status: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE agents SET status = ? WHERE id = ?", (status, agent_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_answer_score(answer_id: int, score: float, eliminated: bool):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE answers SET score = ?, eliminated = ? WHERE id = ?", (score, 1 if eliminated else 0, answer_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_round_status(round_id: int, status: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE rounds SET status = ? WHERE id = ?", (status, round_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_full_tournament_data(tournament_id: int) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
        t = cursor.fetchone()
        if not t:
            conn.close()
            return {}

        tournament_dict = dict(t)
        
        # Agents
        cursor.execute("SELECT * FROM agents WHERE tournament_id = ? ORDER BY generation, id", (tournament_id,))
        agents = [dict(a) for a in cursor.fetchall()]
        for a in agents:
            a['parent_ids'] = json.loads(a['parent_ids'] or "[]")

        # Rounds
        cursor.execute("SELECT * FROM rounds WHERE tournament_id = ? ORDER BY generation, round_number", (tournament_id,))
        rounds = [dict(r) for r in cursor.fetchall()]

        # Answers
        cursor.execute("""
            SELECT ans.*, a.name as agent_name, a.model as agent_model 
            FROM answers ans 
            JOIN agents a ON ans.agent_id = a.id
            JOIN rounds r ON ans.round_id = r.id
            WHERE r.tournament_id = ?
        """, (tournament_id,))
        answers = [dict(ans) for ans in cursor.fetchall()]

        # Votes
        cursor.execute("""
            SELECT v.*, v_agent.name as voter_name, v_agent.model as voter_model,
                        c_agent.name as candidate_name, c_agent.model as candidate_model
            FROM votes v
            JOIN agents v_agent ON v.voter_id = v_agent.id
            JOIN agents c_agent ON v.candidate_id = c_agent.id
            JOIN rounds r ON v.round_id = r.id
            WHERE r.tournament_id = ?
        """, (tournament_id,))
        votes = [dict(v) for v in cursor.fetchall()]

        # Whispers
        cursor.execute("""
            SELECT w.*, s_agent.name as sender_name, s_agent.model as sender_model,
                        r_agent.name as receiver_name, r_agent.model as receiver_model
            FROM whispers w
            JOIN agents s_agent ON w.sender_id = s_agent.id
            JOIN agents r_agent ON w.receiver_id = r_agent.id
            JOIN rounds r ON w.round_id = r.id
            WHERE r.tournament_id = ?
            ORDER BY w.id DESC
        """, (tournament_id,))
        whispers = [dict(w) for w in cursor.fetchall()]

        conn.close()

        return {
            "tournament": tournament_dict,
            "agents": agents,
            "rounds": rounds,
            "answers": answers,
            "votes": votes,
            "whispers": whispers
        }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
