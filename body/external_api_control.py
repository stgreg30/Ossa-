import os
import requests
import json
from typing import Optional

class GeminiAccelerator:
    """
    Ossa's High-Level Processing Unit
    using direct Gemini API requests (no google-generativeai package needed)
    """

    def __init__(self):
        # Safer: store your key in environment variable
        # export GEMINI_API_KEY="AIzaSyAKPYP_1ieajPmkMQxJkZVeKAqc0uolcUA"
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            print("[WARNING] Gemini API Key not found. Ossa will run in Low-Power mode.")
            self.active = False
        else:
            self.active = True

    def spark(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Sends a Neural Spark to Gemini API
        """

        if not self.active:
            return "Error: External Accelerator Offline."

        # Use Gemini 1.5 Flash (fast + stable)
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-1.5-flash:generateContent?key={self.api_key}"
        )

        headers = {
            "Content-Type": "application/json"
        }

        if system_instruction:
            final_prompt = f"""
SYSTEM INSTRUCTION:
{system_instruction}

USER INPUT:
{prompt}
"""
        else:
            final_prompt = prompt

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": final_prompt
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            result = response.json()

            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"]

            return f"API Error: {result}"

        except Exception as e:
            return f"Neural Spark Failure: {str(e)}"


# Global instance
accelerator = GeminiAccelerator()