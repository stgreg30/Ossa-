import json

class Metacognition:
    """Periodically reviews memories to propose belief/goal updates."""
    def __init__(self, thalamus, accelerator):
        self.thalamus = thalamus
        self.accelerator = accelerator

    def reflect(self):
        memories = self.thalamus.get_memories()
        if len(memories) < 10:
            return  # Not enough data

        # Create a summary of recent interactions
        recent = memories[-20:]
        summary = "\n".join(
            f"User: {m['input']} | Ossa: {m['response']} | Mood: {m['mood']}"
            for m in recent[-10:]
        )
        current_beliefs = self.thalamus.get_beliefs()
        current_goals = self.thalamus.get_goals()

        prompt = f"""
You are a metacognition module for an AI agent. Review the following recent interactions and current mental state.
Current beliefs: {json.dumps(current_beliefs)}
Current goals: {json.dumps(current_goals)}

Recent interactions:
{summary}

Based on these, propose if any changes to beliefs or goals are warranted. Return a JSON object with two optional keys: 'updated_beliefs' and 'updated_goals'. Only include keys if changes are suggested. Be conservative. If no changes, return empty JSON.
"""
        raw_response = self.accelerator.generate_text(prompt)
        try:
            # Attempt to parse JSON from the response
            # The LLM may output markdown, so extract JSON
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                proposal = json.loads(json_match.group())
            else:
                proposal = {}
        except Exception:
            return

        # Apply safe updates
        if "updated_beliefs" in proposal and proposal["updated_beliefs"]:
            self.thalamus.set_beliefs(proposal["updated_beliefs"])
        if "updated_goals" in proposal and proposal["updated_goals"]:
            self.thalamus.set_goals(proposal["updated_goals"])