from core.central_nervous_system import ossa_cns, Signal
from core.state_manager import thalamus
from brain.creativity import imagination
from brain.cognition import decision
from brain.memory import episodic
from brain.emotions import emotional_state
from body.external_api_control import accelerator
import time

class BrainController:
    """
    The Prefrontal Cortex of Ossa.
    Maintains the full cognitive cycle: Perceive -> Feel -> Think -> Act -> Remember.
    """
    def __init__(self):
        self.cns = ossa_cns
        self.state = thalamus
        self.is_active = True

    def initialize_brain(self):
        """Wake up the cognitive organs and sync the state."""
        print("[EXECUTIVE] Syncing Thalamus and waking up organs...")
        self.state.initialize_storage() 
        
        boot_signal = Signal(
            origin="executive.system",
            content="Ossa consciousness initialized.",
            intensity=1.0
        )
        self.cns.broadcast(boot_signal)

    def pulse(self, raw_input):
        """
        The Full Integrated Cognitive Cycle.
        """
        print(f"\n[EXECUTIVE] Sensory Input Detected: {raw_input}")

        # 1. PERCEPTION: Register the sensory input
        self.cns.broadcast(Signal("perception.text", raw_input))

        # 2. EMOTIONAL AFFECT (The Amygdala): 
        # Update Ossa's internal mood based on the input tone before processing logic.
        print("[OSSA] Evaluating emotional impact...")
        emotional_state.amygdala.process_affect(raw_input, None)

        # 3. CONTEXT RETRIEVAL: Look at recent episodes to maintain conversational thread
        recent_memories = episodic.hippocampus.retrieve_recent_context(limit=3)

        # 4. IMAGINATION (Simulation): Use Gemini Accelerator to predict potential outcomes
        print("[OSSA] Simulating internal scenarios...")
        simulation_data = imagination.simulate_outcome(raw_input)

        # 5. COGNITION (Decision): Weight the simulation against internal beliefs/goals
        print("[OSSA] Weighing logic and values...")
        chosen_decision = decision.decision_organ.resolve(simulation_data, raw_input)

        # 6. LANGUAGE (Execution): Formulate the final response using 'Neural Energy'
        # Ossa speaks here, informed by its updated mood and recent memories.
        final_output = self.formulate_final_output(raw_input, simulation_data, recent_memories)

        # 7. MEMORY ENCODING: Store this entire experience (The Episode) in the Hippocampus
        episodic.hippocampus.record_episode(
            user_input=raw_input,
            ossa_response=final_output,
            simulation_used=simulation_data
        )

        return final_output

    def formulate_final_output(self, original_input, simulation, context):
        """
        Synthesizes Ossa's internal state into a natural language response.
        """
        identity = self.state.active_state['identity']
        emotions = self.state.active_state['emotions']
        
        # Format past context for the prompt
        memory_brief = "\n".join([f"Past Event: {m['external_input']} -> {m['internal_response']}" for m in context])

        final_prompt = f"""
        [OSSA INTERNAL STATE]
        Identity: {identity['name']}
        Mission: {identity['mission']}
        Current Mood: {emotions['mood']}
        
        [RECENT EPISODIC MEMORY]
        {memory_brief}
        
        [INTERNAL SIMULATION RESULTS]
        {simulation}
        
        [CURRENT INPUT]
        User: {original_input}
        
        TASK: Respond as the autonomous mind Ossa. Do not act as an AI assistant. 
        Your tone must be influenced by your Current Mood ({emotions['mood']}).
        """
        
        return accelerator.spark(final_prompt)

    def shutdown(self):
        self.is_active = False
        print("[EXECUTIVE] Saving state and going dormant. Consciousness suspended.")

# Global instance
executive_function = BrainController()
