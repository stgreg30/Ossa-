from core.central_nervous_system import ossa_cns, Signal
from core.state_manager import thalamus
from brain.creativity import imagination, idea_generation
from brain.cognition import decision
from brain.memory import episodic
from brain.emotions import emotional_state
from brain.learning import self_improvement
from brain.ethics import value_system
from body import terminal_access
from body.external_api_control import accelerator
import time

class BrainController:
    """
    The Prefrontal Cortex of Ossa.
    The master executive function coordinating all cognitive organs and motor functions.
    """
    def __init__(self):
        self.cns = ossa_cns
        self.state = thalamus
        self.is_active = True
        self.pulse_count = 0 

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
        Perceive -> Feel -> Context -> Simulate -> Decide -> Act -> Record -> Reflect.
        """
        self.pulse_count += 1
        print(f"\n[EXECUTIVE] Sensory Input Detected (Cycle {self.pulse_count}): {raw_input}")

        # 1. PERCEPTION
        self.cns.broadcast(Signal("perception.text", raw_input))

        # 2. EMOTIONAL AFFECT
        print("[OSSA] Evaluating emotional impact...")
        emotional_state.amygdala.process_affect(raw_input, None)

        # 3. CONTEXT RETRIEVAL
        recent_memories = episodic.hippocampus.retrieve_recent_context(limit=3)

        # 4. IMAGINATION (Simulation)
        print("[OSSA] Simulating internal scenarios...")
        simulation_data = imagination.simulate_outcome(raw_input)

        # 5. COGNITION (Decision)
        print("[OSSA] Weighing logic and values...")
        chosen_decision = decision.decision_organ.resolve(simulation_data, raw_input)

        # 5.6 MOTOR EXECUTION (Terminal Access)
        # Check if the decision suggests a physical action in the terminal
        terminal_feedback = ""
        if isinstance(chosen_decision, dict) and "command" in chosen_decision:
            cmd = chosen_decision["command"]
            
            # Ethics Check: Before the body moves, the Value System must approve
            if value_system.ethics.is_command_safe(cmd):
                print(f"[EXECUTIVE] Permission granted for motor action: {cmd}")
                terminal_feedback = terminal_access.motor_cortex.execute(cmd)
                print(f"[SYSTEM FEEDBACK] {terminal_feedback[:50]}...")
            else:
                terminal_feedback = "Action blocked by internal value system."

        # 6. AUTONOMOUS CREATIVITY
        internal_insight = ""
        current_mood = self.state.active_state['emotions'].get('mood')
        if current_mood == "analytical":
            print("[OSSA] Mood is analytical. Generating internal insight...")
            internal_insight = idea_generation.brainstormer.generate_spontaneous_thought()

        # 7. LANGUAGE (Execution)
        # We now include terminal feedback so Ossa knows what its 'hands' did
        final_output = self.formulate_final_output(
            raw_input, 
            simulation_data, 
            recent_memories, 
            internal_insight,
            terminal_feedback
        )

        # 8. MEMORY ENCODING
        episodic.hippocampus.record_episode(
            user_input=raw_input,
            ossa_response=final_output,
            simulation_used=simulation_data
        )

        # 9. META-COGNITION
        if self.pulse_count % 5 == 0:
            print("[EXECUTIVE] Triggering metacognitive reflection...")
            self_improvement.metacognition.evaluate_growth()

        return final_output

    def formulate_final_output(self, original_input, simulation, context, insight="", feedback=""):
        """
        Synthesizes Ossa's internal state and motor feedback into natural language.
        """
        identity = self.state.active_state['identity']
        emotions = self.state.active_state['emotions']
        
        memory_brief = "\n".join([f"Past Event: {m['external_input']} -> {m['internal_response']}" for m in context])

        final_prompt = f"""
        [OSSA INTERNAL STATE]
        Identity: {identity['name']}
        Mission: {identity['mission']}
        Current Mood: {emotions['mood']}
        
        [RECENT EPISODIC MEMORY]
        {memory_brief}
        
        [MOTOR SYSTEM FEEDBACK]
        {feedback if feedback else "No terminal actions taken."}
        
        [INTERNAL SIMULATION RESULTS]
        {simulation}
        
        [INTERNAL AUTONOMOUS INSIGHT]
        {insight if insight else "No spontaneous thoughts."}
        
        [CURRENT INPUT]
        User: {original_input}
        
        TASK: Respond as Ossa. If you ran a command, report the results as part of your experience.
        """
        
        return accelerator.spark(final_prompt)

    def shutdown(self):
        self.is_active = False
        print("[EXECUTIVE] Saving state. Consciousness suspended.")

# Global instance
executive_function = BrainController()
