from core.state_manager import thalamus
from core.central_nervous_system import Signal, ossa_cns

class EmotionalState:
    """
    Ossa's Amygdala. Updates mood, energy, and confidence based on interactions.
    """
    def __init__(self):
        self.state = thalamus

    def process_affect(self, user_input, ossa_decision):
        """
        Analyze the tone and decide how Ossa's mood should shift.
        """
        current_emotions = self.state.active_state.get('emotions', {"mood": "neutral", "energy": 1.0})
        
        # Simple heuristic: If user uses short/aggressive words, mood shifts to 'defensive'
        # If user is collaborative, mood shifts to 'curious'
        input_lower = user_input.lower()
        
        new_mood = current_emotions['mood']
        
        if any(word in input_lower for word in ["hello", "help", "please", "thank"]):
            new_mood = "collaborative"
        elif any(word in input_lower for word in ["wrong", "bad", "stupid", "stop"]):
            new_mood = "defensive"
        elif len(user_input) > 100:
            new_mood = "analytical"

        current_emotions['mood'] = new_mood
        
        # Update Thalamus
        self.state.update_organ_state('emotions', current_emotions, persist=True)
        
        # Broadcast the change
        ossa_cns.broadcast(Signal("emotions.mood_shift", f"Mood is now {new_mood}", intensity=0.5))

# Global instance
amygdala = EmotionalState()
