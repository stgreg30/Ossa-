import logging
import json
from datetime import datetime
from .central_nervous_system import CentralNervousSystem, Signal
from .state_manager import Thalamus
from .operating_loop import Heartbeat
from brain.emotions.amygdala import Amygdala
from brain.memory.hippocampus import Hippocampus
from brain.creativity.imagination import Imagination
from brain.cognition.decision_engine import DecisionEngine
from brain.learning.metacognition import Metacognition
from body.external_api_control import Accelerator
from body.terminal_access import MotorCortex

class ExecutiveFunction:
    """Orchestrates the full cognitive cycle."""
    def __init__(self):
        self.cns = CentralNervousSystem()
        self.thalamus = Thalamus()

        # Load state modules
        self.amygdala = Amygdala(self.thalamus)
        self.hippocampus = Hippocampus(self.thalamus)
        self.accelerator = Accelerator()
        self.imagination = Imagination(self.accelerator)
        self.decision_engine = DecisionEngine(self.thalamus)
        self.metacognition = Metacognition(self.thalamus, self.accelerator)
        self.motor_cortex = MotorCortex()

        self.heartbeat = Heartbeat(self.cns, self, interval=10)

        # Wire CNS signals
        self.cns.subscribe("input_received", self._handle_input_signal)
        self.cns.subscribe("response_generated", self._handle_response_signal)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("BrainController")

    def initialize_brain(self):
        """Start the heartbeat after all modules are ready."""
        self.heartbeat.start()
        self.logger.info("Ossa brain initialized with heartbeat.")

    def pulse(self, raw_input: str) -> str:
        """The full cognitive cycle: Perceive -> Feel -> Context -> Simulate -> Decide -> Act -> Record -> Reflect (async)."""
        # 1. Perceive
        self.cns.broadcast(Signal("input_received", {"text": raw_input}, 0.8))
        self.logger.info(f"Perceived: {raw_input}")

        # 2. Feel – update mood based on tone
        mood_update = self.amygdala.analyze_tone(raw_input)
        self.logger.info(f"Mood shift: {mood_update}")

        # 3. Context – retrieve recent memories
        recent_memories = self.hippocampus.get_recent_context(5)
        context = {
            "recent_memories": recent_memories,
            "current_mood": self.thalamus.get_emotion()
        }
        self.logger.debug(f"Context: {context}")

        # 4. Simulate – generate response candidates and imagine outcomes
        candidates = self.accelerator.generate_candidates(
            user_input=raw_input,
            context=context,
            identity=self.thalamus.get_identity()
        )
        simulations = []
        for cand in candidates:
            outcome = self.imagination.simulate(cand, raw_input, context)
            simulations.append({"candidate": cand, "outcome": outcome})
        self.logger.info(f"Simulated {len(simulations)} actions")

        # 5. Decide – pick the best action
        best = self.decision_engine.evaluate(simulations)
        response = best["candidate"]
        self.logger.info(f"Decision: {response}")

        # 6. Act – if response is a terminal command, use MotorCortex
        if response.startswith("!"):  # convention for commands
            command = response[1:]  # remove prefix
            action_output = self.motor_cortex.execute(command)
            final_response = f"Command executed:\n{action_output}"
        else:
            final_response = response

        # 7. Record – store episode
        episode = {
            "timestamp": datetime.now().isoformat(),
            "input": raw_input,
            "response": final_response,
            "mood": self.thalamus.get_emotion().get("current_mood"),
            "simulation_count": len(simulations)
        }
        self.hippocampus.add_episode(episode)

        # 8. Reflect – already handled periodically by heartbeat, but you can trigger a quick one
        self.cns.broadcast(Signal("response_generated", {"response": final_response}, 0.9))

        return final_response

    # CNS callbacks
    def _handle_input_signal(self, signal: Signal):
        self.logger.debug(f"CNS input signal: {signal}")

    def _handle_response_signal(self, signal: Signal):
        self.logger.debug(f"CNS response signal: {signal}")