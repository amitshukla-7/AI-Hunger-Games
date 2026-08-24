from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio

from db import DatabaseManager, init_db
from tournament import TournamentEngine

app = FastAPI(title="AI Hunger Games Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

engine = TournamentEngine()
active_tournament_id = 1

@app.on_event("startup")
async def startup_event():
    init_db()

class StartTournamentRequest(BaseModel):
    name: Optional[str] = "AI Hunger Games Arena"
    models: Optional[List[str]] = ["llama3:latest", "mistral:latest", "phi3:latest", "gemma:latest"]

def get_active_tid(override_tid: Optional[int] = None) -> int:
    global active_tournament_id
    if override_tid:
        return override_tid
    latest = DatabaseManager.get_latest_tournament_id()
    if latest:
        active_tournament_id = latest
        return latest
    return active_tournament_id

@app.get("/api/state")
async def get_state(tournament_id: Optional[int] = None):
    tid = get_active_tid(tournament_id)
    data = DatabaseManager.get_full_tournament_data(tid)
    if not data or not data.get("tournament"):
        tid = await engine.initialize_tournament("AI Hunger Games - Season 1")
        data = DatabaseManager.get_full_tournament_data(tid)
    return data

@app.post("/api/tournament/start")
async def start_tournament(req: StartTournamentRequest):
    global active_tournament_id
    tid = await engine.initialize_tournament(req.name, req.models)
    active_tournament_id = tid
    await manager.broadcast({"event": "season_start", "tournament_id": tid})
    return {"message": "Tournament initialized", "tournament_id": tid}

class StepRequest(BaseModel):
    tournament_id: Optional[int] = None
    custom_prompt: Optional[str] = None
    prompt_type: Optional[str] = "User Challenge"

@app.post("/api/tournament/step")
async def step_tournament(req: Optional[StepRequest] = None):
    tournament_id = req.tournament_id if req else None
    custom_prompt = req.custom_prompt if req else None
    prompt_type = req.prompt_type if req else None
    
    tid = get_active_tid(tournament_id)
    data = DatabaseManager.get_full_tournament_data(tid)
    if not data or not data.get("tournament"):
        tid = await engine.initialize_tournament("AI Hunger Games - Season 1")
    try:
        res = await engine.execute_round(tid, custom_prompt=custom_prompt, prompt_type=prompt_type)
        await manager.broadcast({"event": "round_complete", "result": res})
        return {"status": "success", "result": res}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics(tournament_id: Optional[int] = None):
    tid = get_active_tid(tournament_id)
    data = DatabaseManager.get_full_tournament_data(tid)
    votes = data.get("votes", [])

    if not votes:
        return {
            "same_model_avg": 0,
            "cross_model_avg": 0,
            "bias_factor": 0,
            "total_votes": 0,
            "model_matrix": {}
        }

    same_model_scores = [v['score_given'] for v in votes if v['same_model'] == 1]
    cross_model_scores = [v['score_given'] for v in votes if v['same_model'] == 0]

    same_avg = round(sum(same_model_scores) / len(same_model_scores), 2) if same_model_scores else 0
    cross_avg = round(sum(cross_model_scores) / len(cross_model_scores), 2) if cross_model_scores else 0
    bias = round(same_avg - cross_avg, 2)

    # Matrix: voter_model -> candidate_model -> average score
    matrix: Dict[str, Dict[str, List[int]]] = {}
    for v in votes:
        vm = v['voter_model']
        cm = v['candidate_model']
        if vm not in matrix:
            matrix[vm] = {}
        if cm not in matrix[vm]:
            matrix[vm][cm] = []
        matrix[vm][cm].append(v['score_given'])

    matrix_avg = {}
    for vm, cm_map in matrix.items():
        matrix_avg[vm] = {}
        for cm, scores in cm_map.items():
            matrix_avg[vm][cm] = round(sum(scores) / len(scores), 2)

    return {
        "same_model_avg": same_avg,
        "cross_model_avg": cross_avg,
        "bias_factor": bias,
        "total_votes": len(votes),
        "model_matrix": matrix_avg
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
