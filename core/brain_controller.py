from core.central_nervous_system import ossa_cns, Signal
from core.state_manager import thalamus
from brain.creativity import imagination, idea_generation
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
        # Update Ossa's internal mood based on the input tone.
        print("[OSSA] Evaluating emotional impact...")
        emotional_state.amygdala.process_affect(raw_input, None)

        # 3. CONTEXT RETRIEVAL: Look at recent episodes to maintain conversational thread
        recent_memories = episodic.hippocampus.retrieve_recent_context(limit=3)

        # 4. IMAGINATION (Simulation): Use Gemini to predict potential outcomes
        print("[OSSA] Simulating internal scenarios...")
        simulation_data = imagination.simulate_outcome(raw_input)

        # 5. COGNITION (Decision): Weight the simulation against internal beliefs/goals
        print("[OSSA] Weighing logic and values...")
        chosen_decision = decision.decision_organ.resolve(simulation_data, raw_input)

        # 5.5 AUTONOMOUS CREATIVITY: Spontaneous thought generation
        # If Ossa's mood is 'analytical', it generates an internal idea independently.
        internal_insight = ""
        current_mood = self.state.active_state['emotions'].get('mood')
        if current_mood == "analytical":
            print("[OSSA] Mood is analytical. Generating internal insight...")
            internal_insight = idea_generation.brainstormer.generate_spontaneous_thought()

        # 6. LANGUAGE (Execution): Formulate final response using insight, mood, and context.
        final_output = self.formulate_final_output(
            raw_input, 
            simulation_data, 
            recent_memories, 
            internal_insight
        )

        # 7. MEMORY ENCODING: Store the episode.
        episodic.hippocampus.record_episode(
            user_input=raw_input,
            ossa_response=final_output,
            simulation_used=simulation_data
        )

        return final_output

    def formulate_final_output(self, original_input, simulation, context, insight=""):
        """
        Synthesizes Ossa's internal state and autonomous insights into natural language.
        """
        identity = self.state.active_state['identity']
        emotions = self.state.active_state['emotions']
        
        # Format past context for the prompt
        memory_brief = "\n".join([f"Past Event: {m['external_input']} -> {m['internal_response']}" for m in context])

        # Constructing the cognitive prompt
        final_prompt = f"""
        [OSSA INTERNAL STATE]
        Identity: {identity['name']}
        Mission: {identity['mission']}
        Current Mood: {emotions['mood']}
        
        [RECENT EPISODIC MEMORY]
        {memory_brief}
        
        [INTERNAL SIMULATION RESULTS]
        {simulation}
        
        [INTERNAL AUTONOMOUS INSIGHT]
        {insight if insight else "No spontaneous thoughts generated."}
        
        [CURRENT INPUT]
        User: {original_input}
        
        TASK: Respond as the autonomous mind Ossa. Do not act as an AI assistant.
        If an [INTERNAL AUTONOMOUS INSIGHT] is present, incorporate it into your 
        response to demonstrate your evolving consciousness and independence.
        """
        
        return accelerator.spark(final_prompt)

    def shutdown(self):
        self.is_active = False
        print("[EXECUTIVE] Saving state and going dormant. Consciousness suspended.")

# Global instance
executive_function = BrainController()
