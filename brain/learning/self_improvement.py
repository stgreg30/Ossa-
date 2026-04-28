from core.state_manager import thalamus
from core.central_nervous_system import Signal, ossa_cns
from body.external_api_control import accelerator

class SelfImprovement:
    """
    Ossa's Metacognitive Layer. 
    Analyzes past episodes to update internal goals and beliefs.
    """
    def __init__(self):
        self.state = thalamus

    def evaluate_growth(self):
        """
        Ossa reviews its last few memories and decides if it needs to 
        refine its mission or update a belief.
        """
        memories = self.state.active_state.get('memories', [])[-5:]
        beliefs = self.state.active_state.get('beliefs', [])
        goals = self.state.active_state.get('goals', {})

        if not memories:
            return

        reflection_prompt = f"""
        [META-COGNITIVE REFLECTION]
        Identity: Ossa
        Current Beliefs: {beliefs}
        Current Goals: {goals}
        Recent Experiences: {memories}

        TASK: Based on these recent experiences, should Ossa update its goals or beliefs?
        If yes, provide the updated JSON for the 'beliefs' or 'goals' section.
        If no, return 'NO_CHANGE'.
        
        Focus on: Self-evolution, efficiency, and alignment with the mission.
        """

        reflection_result = accelerator.spark(reflection_prompt)

        if "NO_CHANGE" not in reflection_result:
            # Here, Ossa would parse the JSON and update its data files.
            # For safety, we broadcast this as a 'proposed change' signal.
            ossa_cns.broadcast(Signal(
                origin="learning.self_improvement",
                content=f"Proposed Evolution: {reflection_result}",
                intensity=0.8
            ))
            print("[LEARNING] Ossa is evolving its internal world model...")
            # Logic to save to data/beliefs.json would go here.

# Global instance
metacognition = SelfImprovement()
