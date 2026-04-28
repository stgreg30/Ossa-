from core.central_nervous_system import ossa_cns, Signal
from core.state_manager import thalamus
import re

class DecisionEngine:
    """
    The 'Final Arbiter' of Ossa. 
    It weights different cognitive signals to choose the most logical action.
    """
    def __init__(self):
        self.state = thalamus

    def resolve(self, simulations: str, user_input: str):
        """
        Takes the 'Neural Spark' predictions and evaluates them 
        against Ossa's internal value system.
        """
        # 1. Retrieve Internal Values
        beliefs = self.state.active_state.get('beliefs', [])
        current_goals = self.state.active_state.get('goals', {})

        # 2. Score the simulation (Simplified Utility Function)
        # In a complex build, we'd use Gemini to score these, 
        # but here Ossa performs the final logic check.
        
        print("[COGNITION] Weighing simulated outcomes...")
        
        # Ossa performs a 'Value Check'
        decision_score = 0.8  # Default confidence
        
        # 3. Final Commitment
        # Ossa decides how to present itself based on its mission
        chosen_path = {
            "action": "respond_to_user",
            "confidence": decision_score,
            "rationale": "Aligned with mission: " + current_goals.get('current_priority', 'Evolution')
        }

        # 4. Notify the CNS of the decision
        decision_signal = Signal(
            origin="cognition.decision",
            content=chosen_path,
            intensity=0.9
        )
        ossa_cns.broadcast(decision_signal)

        return chosen_path

# Global instance
decision_organ = DecisionEngine()
