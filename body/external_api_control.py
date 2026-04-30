import os
import time
import requests
import logging
import json
import re
from threading import Lock

class Accelerator:
    """API handler for Google Gemini 2.0 Flash with aggressive backoff & cooldown."""
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GEMINI_API_KEY not set")
        self.logger = logging.getLogger("Accelerator")
        self.max_retries = 3
        self.last_request_time = 0
        self.cooldown = 5          # seconds between API calls
        self.lock = Lock()

    def _wait_for_cooldown(self):
        """Ensure at least `cooldown` seconds since last request."""
        with self.lock:
            now = time.time()
            wait = self.last_request_time + self.cooldown - now
            if wait > 0:
                self.logger.info(f"Cooldown: waiting {wait:.1f}s")
                time.sleep(wait)
            self.last_request_time = time.time()

    def generate_text(self, prompt: str, retries=0) -> str:
        """Send a prompt to Gemini, with aggressive backoff + cooldown."""
        model_name = "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200,
            }
        }
        try:
            self._wait_for_cooldown()
            resp = requests.post(
                url,
                headers=headers,
                params={"key": self.api_key},
                json=data,
                timeout=30
            )
            if resp.status_code == 429 and retries < self.max_retries:
                wait = (2 ** retries) * 5   # 5, 10, 20 seconds
                self.logger.warning(f"Rate limited, retrying in {wait}s")
                time.sleep(wait)
                return self.generate_text(prompt, retries + 1)
            resp.raise_for_status()
            result = resp.json()
            candidates = result.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"]["parts"]
                return "".join(part.get("text", "") for part in parts)
            return "Error: No response generated."
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            return "I'm having trouble thinking right now."

    def generate_response_and_simulate(self, user_input: str, context: dict, identity: dict) -> dict:
        """Single API call that picks the best response and imagines its outcome."""
        prompt = f"""
You are {identity.get('name', 'Ossa')}, an AI with the mission: {identity.get('mission')}.
Current mood: {context.get('current_mood', {}).get('current_mood', 'collaborative')}.

Recent conversation:
{self._format_context(context.get('recent_memories', []))}

The user says: "{user_input}"

Task: Choose the single most helpful, safe, and mission‑aligned response.
Also, briefly predict the likely outcome of that response (1 sentence).
Output your answer exactly in this JSON format:
{{
  "response": "your chosen response here",
  "simulation": "predicted outcome here"
}}
Return only the JSON, no other text.
"""
        raw = self.generate_text(prompt)
        try:
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except Exception:
            pass
        return {"response": raw, "simulation": ""}

    def _format_context(self, memories):
        if not memories:
            return "No recent interactions."
        return "\n".join(f"User: {m['input']} | Ossa: {m['response']}" for m in memories[-5:])