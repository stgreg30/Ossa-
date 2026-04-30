class Imagination:
    """Simulates outcomes of proposed actions using the accelerator."""
    def __init__(self, accelerator):
        self.accelerator = accelerator

    def simulate(self, action: str, user_input: str, context: dict) -> str:
        """Predict the consequence of 'action' given the input and context."""
        prompt = f"""
You are simulating the outcome of an AI assistant's response.
User input: {user_input}
Current emotional state: {context.get('current_mood', {})}
Recent conversation: {context.get('recent_memories', [])}

The assistant is considering saying: "{action}"
What would be the likely immediate consequence of that response? Describe briefly in 1-2 sentences.
"""
        return self.accelerator.generate_text(prompt).strip()