import os
import google.generativeai as genai
from typing import Optional

class GeminiAccelerator:
    """
    Ossa's High-Level Processing Unit.
    Used for tasks requiring heavy computational reasoning.
    """
    def __init__(self):
        # It's best practice to set your API key as an environment variable
        # OS Command: export GEMINI_API_KEY='your-key-here'
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            print("[WARNING] Gemini API Key not found. Ossa will run in Low-Power mode (Local Heuristics only).")
            self.active = False
        else:
            genai.configure(api_key=self.api_key)
            # Using 1.5 Flash for speed, or 1.5 Pro for 'Deep Reasoning'
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.active = True

    def spark(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Sends a 'Neural Spark' to the API. 
        Returns the raw processing result.
        """
        if not self.active:
            return "Error: External Accelerator Offline."

        try:
            # We can pass Ossa's current identity as the 'System Instruction'
            if system_instruction:
                response = self.model.generate_content(
                    f"INSTRUCTION: {system_instruction}\n\nINPUT: {prompt}"
                )
            else:
                response = self.model.generate_content(prompt)
                
            return response.text
        except Exception as e:
            return f"Neural Spark Failure: {str(e)}"

# Global instance
accelerator = GeminiAccelerator()
