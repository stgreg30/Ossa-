import requests
import json

API_KEY = "AIzaSyAKPYP_1ieajPmkMQxJkZVeKAqc0uolcUA"

class GeminiAccelerator:
    """
    Ossa's High-Level Processing Unit
    using direct Gemini API requests
    """

    def __init__(self):
        if API_KEY == "YOUR_GEMINI_API_KEY":
            print("[WARNING] Gemini API Key missing.")
            self.active = False
        else:
            self.active = True

    def spark(self, prompt, system_instruction=None):
        if not self.active:
            return "Error: External Accelerator Offline."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        if system_instruction:
            final_prompt = f"INSTRUCTION: {system_instruction}\n\nINPUT: {prompt}"
        else:
            final_prompt = prompt

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": final_prompt}
                    ]
                }
            ]
        }

        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )

        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return f"API Error: {response.text}"

# Global instance
accelerator = GeminiAccelerator()