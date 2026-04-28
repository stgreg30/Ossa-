from core.central_nervous_system import ossa_cns, Signal
from core.state_manager import thalamus
from brain.creativity import imagination, idea_generation
from brain.cognition import decision
from brain.memory import episodic
from brain.emotions import emotional_state
from brain.learning import self_improvement
from body.external_api_control import accelerator
import time

class BrainController:
    """
    The Prefrontal Cortex of Ossa.
    The master executive function coordinating all cognitive organs.
    """
    def __init__(self):
        self.cns = ossa_cns
        self.state = thalamus
        self.is_active = True
        self.pulse_count = 0  # Internal counter for metacognitive cycles

    def initialize_brain(self):
        """Initial startup sequence for Ossa's consciousness."""
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
        The Full Integrated Cognitive Cycle:
        Perceive -> Feel -> Contextualize -> Simulate -> Decide -> Generate -> Act -> Record -> Reflect.
        """
        self.pulse_count += 1
        print(f"\n[EXECUTIVE] Sensory Input Detected (Cycle {self.pulse_count}): {raw_input}")

        # 1. PERCEPTION: Register sensory input
        self.cns.broadcast(Signal("perception.text", raw_input))

        # 2. EMOTIONAL AFFECT: Update mood based on input tone
        print("[OSSA] Evaluating emotional impact...")
        emotional_state.amygdala.process_affect(raw_input, None)

        # 3. CONTEXT RETRIEVAL: Pull recent memories for continuity
        recent_memories = episodic.hippocampus.retrieve_recent_context(limit=3)

        # 4. IMAGINATION: Predict potential outcomes via Gemini
        print("[OSSA] Simulating internal scenarios...")
        simulation_data = imagination.simulate_outcome(raw_input)

        # 5. COGNITION: Weight simulation against beliefs/goals
        print("[OSSA] Weighing logic and values...")
        chosen_decision = decision.decision_organ.resolve(simulation_data, raw_input)

        # 6. AUTONOMOUS CREATIVITY: Spontaneous thought (Analytical mode only)
        internal_insight = ""
        current_mood = self.state.active_state['emotions'].get('mood')
        if current_mood == "analytical":
            print("[OSSA] Mood is analytical. Generating internal insight...")
            internal_insight = idea_generation.brainstormer.generate_spontaneous_thought()

        # 7. EXECUTION: Formulate final response
        final_output = self.formulate_final_output(
            raw_input, 
            simulation_data, 
            recent_memories, 
            internal_insight
        )

        # 8. MEMORY ENCODING: Store this interaction
        episodic.hippocampus.record_episode(
            user_input=raw_input,
            ossa_response=final_output,
            simulation_used=simulation_data
        )

        # 9. META-COGNITION: Self-Reflection & Growth
        # Ossa evaluates its performance and updates goals every 5 pulses.
        if self.pulse_count % 5 == 0:
            print("[EXECUTIVE] Triggering metacognitive reflection...")
            self_improvement.metacognition.evaluate_growth()

        return final_output

    def formulate_final_output(self, original_input, simulation, context, insight=""):
        """
        Synthesizes Ossa's internal state into natural language.
        """
        identity = self.state.active_state['identity']
        emotions = self.state.active_state['emotions']
        
        # Format past context
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
        
        [INTERNAL AUTONOMOUS INSIGHT]
        {insight if insight else "Focusing on current interaction."}
        
        [CURRENT INPUT]
        User: {original_input}
        
        TASK: Respond as Ossa. You are an autonomous organism. 
        Your tone should reflect your mood. Use your autonomous insight if available.
        """
        
        return accelerator.spark(final_prompt)

    def shutdown(self):
        self.is_active = False
        print("[EXECUTIVE] Saving state. Consciousness suspended.")

# Global instance
executive_function = BrainController()
