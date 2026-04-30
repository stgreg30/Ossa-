"""
ExecutiveFunction – The Brain Controller
=========================================
Orchestrates Ossa's full cognitive cycle:

Perceive → Feel → Context → Simulate+Decide → Act → Record → Reflect

Now uses enhanced memory context for better recall and includes
synaptic plasticity for long‑term adaptation.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional, Union

from .central_nervous_system import CentralNervousSystem, Signal
from .state_manager import Thalamus
from .operating_loop import Heartbeat
from brain.emotions.amygdala import Amygdala
from brain.memory.hippocampus import Hippocampus
from brain.creativity.imagination import Imagination
from brain.cognition.decision_engine import DecisionEngine
from brain.learning.metacognition import Metacognition
from brain.plasticity.synaptic_plasticity import SynapticPlasticity   # NEW
from body.external_api_control import Accelerator
from body.terminal_access import MotorCortex

logger = logging.getLogger("BrainController")

class ExecutiveFunction:
    def __init__(self) -> None:
        self.cns = CentralNervousSystem()
        self.thalamus = Thalamus()

        self.amygdala = Amygdala(self.thalamus)
        self.hippocampus = Hippocampus(self.thalamus)
        self.accelerator = Accelerator()
        self.imagination = Imagination(self.accelerator)
        self.decision_engine = DecisionEngine(self.thalamus)
        self.metacognition = Metacognition(self.thalamus, self.accelerator)

        # --- Synaptic Plasticity (adapts parameters over time) ---
        self.plasticity = SynapticPlasticity(
            self.thalamus,
            self.amygdala,
            self.decision_engine
        )

        self.motor_cortex = MotorCortex(
            allowed_commands=[
                "echo", "ls", "cat", "head", "tail",
                "pwd", "whoami", "date", "mkdir"
            ]
        )

        self.heartbeat = Heartbeat(self.cns, self, interval=10)

        self.cns.subscribe("input_received", self._on_input_received)
        self.cns.subscribe("response_generated", self._on_response_generated)

        logger.info("ExecutiveFunction initialized – all modules loaded (plasticity active).")

    def initialize_brain(self) -> None:
        self.heartbeat.start()
        logger.info("Ossa brain initialized with heartbeat.")

    def pulse(self, raw_input: str) -> str:
        try:
            if raw_input.startswith("!"):
                return self._handle_terminal_command(raw_input)

            self.cns.broadcast(Signal("input_received", {"text": raw_input}, 0.8))
            logger.info(f"Perceived: {raw_input}")

            mood_update = self.amygdala.analyze_tone(raw_input)
            logger.info(f"Mood shift: {mood_update}")

            augmented = self.hippocampus.get_augmented_context(raw_input)
            context = {
                "recent_memories": augmented["recent"],
                "relevant_facts": augmented["relevant_facts"],
                "current_mood": self.thalamus.get_emotion()
            }
            logger.debug(f"Context (augmented) has {len(augmented['recent'])} recent, "
                         f"{len(augmented['relevant_facts'])} older facts.")

            response_data = self.accelerator.generate_response_and_simulate(
                user_input=raw_input,
                context=context,
                identity=self.thalamus.get_identity()
            )

            if isinstance(response_data, dict):
                response = response_data.get("response", "")
                simulation_outcome = response_data.get("simulation", "")
            else:
                response = str(response_data)
                simulation_outcome = ""

            logger.info(f"Generated response: {response}")
            if simulation_outcome:
                logger.info(f"Simulated outcome: {simulation_outcome}")

            final_response = response

            self._record_episode(raw_input, final_response, simulation_outcome)
            self.cns.broadcast(Signal("response_generated", {"response": final_response}, 0.9))
            return final_response

        except Exception as e:
            logger.error(f"Unhandled error in pulse: {e}", exc_info=True)
            return "I encountered an internal error. Please try again."

    def _handle_terminal_command(self, raw_input: str) -> str:
        command = raw_input[1:].strip()
        if not command:
            return "No command provided."
        result = self.motor_cortex.execute(command)
        final_response = f"Command executed:\n{result}"
        self._record_episode(raw_input, final_response, "terminal command")
        return final_response

    def _record_episode(self, input_text, response, simulation):
        episode = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "response": response,
            "mood": self.thalamus.get_emotion().get("current_mood"),
            "simulation": simulation
        }
        self.hippocampus.add_episode(episode)

    def _on_input_received(self, signal):
        logger.debug(f"CNS input signal: {signal}")

    def _on_response_generated(self, signal):
        logger.debug(f"CNS response signal: {signal}")