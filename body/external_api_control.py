import os
import time
import requests
import logging
import json
import re
from threading import Lock

class Accelerator:
    """API handler for Groq (Llama 3 8B) – fast and free-tier friendly."""
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GROQ_API_KEY not set")
        self.logger = logging.getLogger("Accelerator")
        self.max_retries = 2
        self.cooldown = 2            # seconds between calls (30 req/min = 1 every 2s)
        self.last_request_time = 0
        self.lock = Lock()
        self.model = "llama3-8b-8192"   # you can change to "mixtral-8x7b-32768" if you want

    def _wait_for_cooldown(self):
        with self.lock:
            now = time.time()
            wait = self.last_request_time + self.cooldown - now
            if wait > 0:
                self.logger.info(f"Cooldown: waiting {wait:.1f}s")
                time.sleep(wait)
            self.last_request_time = time.time()

    def generate_text(self, prompt: str, retries=0) -> str:
        """
        Send a prompt to Groq's chat completion endpoint.
        We wrap the prompt as a user message.
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful, safe, and concise AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        try:
            self._wait_for_cooldown()
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 429 and retries < self.max_retries:
                wait = (2 ** retries) * 5
                self.logger.warning(f"Rate limited, retrying in {wait}s")
                time.sleep(wait)
                return self.generate_text(prompt, retries + 1)
            resp.raise_for_status()
            result = resp.json()
            # Groq returns choices[0].message.content
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content if content else "Error: No response generated."
        except Exception as e:
            self.logger.error(f"Groq API error: {e}")
            return "I'm having trouble thinking right now."

    def generate_response_and_simulate(self, user_input: str, context: dict, identity: dict) -> dict:
        """
        Single API call that picks the best response and imagines its outcome.
        Returns a dict with 'response' and 'simulation'.
        """
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