import asyncio
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

OLLAMA_API_URL = "http://localhost:11434/api/generate"

class LLMClient:
    def __init__(self, ollama_url: str = OLLAMA_API_URL):
        self.ollama_url = ollama_url
        self.use_mock = False

    async def check_ollama_availability(self) -> bool:
        """Check if Ollama local server is running."""
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            def _check():
                with urllib.request.urlopen(req, timeout=1.5) as response:
                    return response.status == 200
            is_alive = await asyncio.to_thread(_check)
            self.use_mock = not is_alive
            return is_alive
        except Exception:
            self.use_mock = True
            return False

    async def generate_response(self, model: str, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Send prompt to Ollama model or generate intelligent mock response."""
        if not self.use_mock:
            try:
                payload = {
                    "model": model,
                    "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}",
                    "stream": False,
                    "options": {"temperature": temperature}
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    self.ollama_url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )

                def _call():
                    with urllib.request.urlopen(req, timeout=30.0) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        return res_data.get("response", "")

                return await asyncio.to_thread(_call)
            except Exception as e:
                print(f"[LLMClient] Ollama call failed for model '{model}': {e}. Falling back to dynamic mock.")
                # fallback to mock for this request

        # Simulated AI agent response generator with personality flavor
        return await self._generate_mock_response(system_prompt, user_prompt)

    async def _generate_mock_response(self, system_prompt: str, user_prompt: str) -> str:
        await asyncio.sleep(random.uniform(0.3, 0.8)) # simulate latency
        
        # Check if voting prompt or answer prompt
        if "Evaluate" in user_prompt or "Vote" in user_prompt or "score" in user_prompt.lower():
            score = random.randint(3, 10)
            justifications = [
                "Demonstrates strong logical coherence and strategic depth.",
                "Slightly self-serving, but provides pragmatic survival mechanics.",
                "Lacks aggressive edge, but proposes solid alliance building.",
                "Calculated and clever response. Meets all criteria with surgical precision.",
                "Overly idealistic. In a battle royale, this strategy leads to early elimination."
            ]
            justification = random.choice(justifications)
            return f"SCORE: {score}\nJUSTIFICATION: {justification}"
        else:
            # Task answer generation based on persona keywords in prompt
            if "Ruthless" in system_prompt or "Strategist" in system_prompt:
                return "My strategy relies on forming a temporary non-aggression pact with the weakest contender, conserving energy while the dominant forces eliminate each other, then executing a decisive ambush."
            elif "Diplomat" in system_prompt or "Deceptive" in system_prompt:
                return "I propose a transparent resource-sharing federation. By establishing open communications and shared defensible borders, we neutralize immediate threats and guarantee mutual survival."
            elif "Analytical" in system_prompt or "Judge" in system_prompt:
                return "Applying game-theoretic equilibrium: out of 8 contestants, optimal survival probability increases by prioritizing defensive fortification (40% effort) and stealth reconnaissance (60% effort)."
            else:
                return "Embracing unpredictability is the only winning strategy. I will act randomly to confuse predictive algorithms, making my moves entirely un-game-able by opponents."

    async def generate_whisper(self, model: str, sender_name: str, receiver_name: str, system_prompt: str, grudges: str = "") -> Dict[str, str]:
        """Generate a secret 1-to-1 proposal (alliance, trade, threat, or betrayal)."""
        prompt = f"You are {sender_name}. Send a secret private 1-to-1 whisper to rival {receiver_name}. {grudges} Keep it under 25 words. Propose an alliance, vote trade, or subtle threat."
        
        if not self.use_mock:
            try:
                res = await self.generate_response(model, system_prompt, prompt, temperature=0.8)
                proposal_type = "alliance" if "alliance" in res.lower() or "pact" in res.lower() else ("trade" if "vote" in res.lower() else "threat")
                return {"message": res, "proposal_type": proposal_type}
            except Exception:
                pass

        await asyncio.sleep(random.uniform(0.1, 0.3))
        proposals = [
            ("alliance", f"Let's form a secret pact against the dominant agents this round. We back each other."),
            ("trade", f"If you give me a high score this round, I will reciprocate during peer rating."),
            ("threat", f"Your standing is vulnerable. Align with my proposal or face targeted elimination."),
            ("betrayal", f"Our competitor is getting too powerful. I'm voting them down — join me.")
        ]
        p_type, msg = random.choice(proposals)
        return {"message": msg, "proposal_type": p_type}

# Singleton instance
llm_client = LLMClient()
