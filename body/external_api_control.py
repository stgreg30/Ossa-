def generate_text(self, prompt: str) -> str:
    """Raw text generation from Gemini."""
    # Use a widely‑available model version
    MODEL_NAME = "gemini-1.5-flash-001"   # change to "gemini-2.0-flash" if you prefer

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
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
            url,
            headers=headers,
            params={"key": self.api_key},
            json=data,
            timeout=30
        )
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