import os
import requests
import logging

class Accelerator:
    """API handler for Google Gemini 1.5 Flash."""
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GEMINI_API_KEY not set")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.logger = logging.getLogger("Accelerator")

    def generate_text(self, prompt: str) -> str:
        """Raw text generation from Gemini."""
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 256,
            }
        }
        try:
            resp = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
            # Extract the text
            candidates = result.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"]["parts"]
                return "".join(part.get("text", "") for part in parts)
            return "Error: No response generated."
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            return "I'm having trouble thinking right now."

    def generate_candidates(self, user_input: str, context: dict, identity: dict) -> list:
        """Generate a few response candidates using the LLM."""
        prompt = f"""
You are {identity.get('name', 'Ossa')}, an AI with the mission: {identity.get('mission')}.
Current mood: {context.get('current_mood', {}).get('current_mood', 'collaborative')}.

Recent conversation:
{self._format_context(context.get('recent_memories', []))}

The user says: "{user_input}"

Generate 3 different, concise response options that would be helpful, safe, and aligned with your mission.
Return each response on a new line, numbered like:
1. response one
2. response two
3. response three
"""
        raw = self.generate_text(prompt)
        # Parse numbered lines
        candidates = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped and (stripped[0].isdigit() and '.' in stripped[:3]):
                # Extract after number
                candidate = stripped.split('.', 1)[-1].strip()
                if candidate:
                    candidates.append(candidate)
        if not candidates:
            # Fallback
            candidates = [raw] if raw else ["I'm not sure what to say."]
        return candidates[:3]

    def _format_context(self, memories):
        if not memories:
            return "No recent interactions."
        return "\n".join(f"User: {m['input']} | Ossa: {m['response']}" for m in memories[-5:])