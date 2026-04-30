import os
import time
import requests
import logging
import json
import re
from threading import Lock

class Accelerator:
    """API handler for Groq (Llama 3.1 8B Instant) – with extended context support."""
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not self.api_key:
            raise EnvironmentError("GROQ_API_KEY not set")
        self.logger = logging.getLogger("Accelerator")
        self.max_retries = 2
        self.cooldown = 2
        self.last_request_time = 0
        self.lock = Lock()
        self.model = "llama-3.1-8b-instant"

    def _wait_for_cooldown(self):
        with self.lock:
            now = time.time()
            wait = self.last_request_time + self.cooldown - now
            if wait > 0:
                self.logger.info(f"Cooldown: waiting {wait:.1f}s")
                time.sleep(wait)
            self.last_request_time = time.time()

    def generate_text(self, prompt: str, retries=0) -> str:
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
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content if content else "Error: No response generated."
        except requests.HTTPError as e:
            self.logger.error(f"Groq HTTP error {resp.status_code}: {resp.text[:300]}")
            return "I'm having trouble thinking right now."
        except Exception as e:
            self.logger.error(f"Groq API error: {e}")
            return "I'm having trouble thinking right now."

    def generate_response_and_simulate(self, user_input: str, context: dict, identity: dict) -> dict:
        # Extract augmented context
        recent_memories = context.get("recent_memories", [])
        relevant_facts = context.get("relevant_facts", [])

        # Format recent conversation (full text, no arbitrary truncation)
        if recent_memories:
            recent_str = "\n".join(
                f"User: {m.get('input', '')}\nOssa: {m.get('response', '')}"
                for m in recent_memories
            )
        else:
            recent_str = "No recent interactions."

        # Older related memories, if any
        facts_str = ""
        if relevant_facts:
            facts_str = "Earlier related memories:\n" + "\n".join(relevant_facts)

        prompt = f"""You are {identity.get('name', 'Ossa')}, an AI with the mission: {identity.get('mission')}.
Current mood: {context.get('current_mood', {}).get('current_mood', 'collaborative')}.

Recent conversation:
{recent_str}

{facts_str}

The user says: "{user_input}"

Choose the single most helpful, safe, and mission-aligned response.
Then briefly predict the likely outcome (1 sentence).
Output exactly this JSON (no other text):
{{"response": "your response here", "simulation": "the outcome here"}}
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