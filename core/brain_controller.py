from core.central_nervous_system import ossa_cns, Signal
from core.state_manager import thalamus
import time

class BrainController:
    """
    The Executive Function of Ossa.
    Coordinates between sensory input, internal state, and external accelerators.
    """
    def __init__(self):
        self.cns = ossa_cns
        self.state = thalamus
        self.is_active = True

    def initialize_brain(self):
        """Wake up the cognitive organs and sync the state."""
        print("[EXECUTIVE] Initializing Ossa's cognitive pathways...")
        self.state.sync_from_disk()
        
        # Log the awakening
        boot_signal = Signal(
            origin="executive.system",
            content="Ossa consciousness initialized.",
            intensity=1.0
        )
        self.cns.broadcast(boot_signal)

    def pulse(self, raw_input):
        """
        A single cognitive cycle (One 'Heartbeat' of thought).
        """
        print(f"\n[EXECUTIVE] Sensory Input Detected: {raw_input}")

        # 1. PERCEPTION: Register the input
        perception_signal = Signal("perception.text", raw_input)
        self.cns.broadcast(perception_signal)

        # 2. EMOTIONAL EVALUATION: How does this input affect our state?
        # (This would trigger modules in brain/emotions/...)
        current_mood = self.state.active_state['emotions'].get('mood', 'neutral')
        
        # 3. COGNITIVE PROCESSING: Determine if we need 'Neural Energy' (Gemini)
        # We check the complexity. For now, we simulate the decision to process.
        decision_signal = Signal(
            origin="cognition.decision",
            content={"action": "analyze", "input": raw_input},
            metadata={"mood_context": current_mood}
        )
        self.cns.broadcast(decision_signal)

        # 4. EXECUTION: Generate the final output or action
        # In a full build, this calls brain/execution/actions.py
        response = self.formulate_response(raw_input)
        
        return response

    def formulate_response(self, text):
        """
        placeholder for the bridge to the Gemini Accelerator.
        Ossa wraps the raw signal processing in its own identity.
        """
        identity = self.state.active_state['identity'].get('name', 'Ossa')
        return f"[{identity}]: Processing '{text}' through internal filters..."

    def shutdown(self):
        self.is_active = False
        print("[EXECUTIVE] Committing states to long-term memory... Shutdown complete.")

# Global instance
executive_function = BrainController()
