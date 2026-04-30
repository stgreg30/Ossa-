"""
ExecutiveFunction – The Brain Controller
=========================================
Orchestrates Ossa's full cognitive cycle:

Perceive → Feel → Context → Simulate+Decide → Act → Record → Reflect

All modules are wired together via the Central Nervous System (CNS)
and the Thalamus (state manager). A background Heartbeat handles
homeostasis and periodic metacognitive reflection.
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
from body.external_api_control import Accelerator
from body.terminal_access import MotorCortex

# Configure logging here to avoid duplicate handlers
logger = logging.getLogger("BrainController")

class ExecutiveFunction:
    """
    Central orchestrator for Ossa's cognitive cycle.

    Attributes:
        cns: Central Nervous System event bus.
        thalamus: Thread‑safe persistent state manager.
        amygdala: Mood analyzer.
        hippocampus: Episodic memory store.
        accelerator: LLM API handler (Groq).
        imagination: Outcome simulator (legacy, kept for future use).
        decision_engine: Action evaluator (legacy, kept for future use).
        metacognition: Self‑reflection module.
        motor_cortex: Secure shell command executor.
        heartbeat: Background homeostasis and reflection loop.
    """

    def __init__(self) -> None:
        self.cns = CentralNervousSystem()
        self.thalamus = Thalamus()

        # Cognitive organs
        self.amygdala = Amygdala(self.thalamus)
        self.hippocampus = Hippocampus(self.thalamus)
        self.accelerator = Accelerator()
        self.imagination = Imagination(self.accelerator)
        self.decision_engine = DecisionEngine(self.thalamus)
        self.metacognition = Metacognition(self.thalamus, self.accelerator)

        # Motor cortex – whitelist safe commands for production
        self.motor_cortex = MotorCortex(
            allowed_commands=[
                "echo", "ls", "cat", "head", "tail",
                "pwd", "whoami", "date", "mkdir"
            ]
        )

        # Heartbeat runs every 10 seconds
        self.heartbeat = Heartbeat(self.cns, self, interval=10)

        # Wire CNS signals
        self.cns.subscribe("input_received", self._on_input_received)
        self.cns.subscribe("response_generated", self._on_response_generated)

        logger.info("ExecutiveFunction initialized – all modules loaded.")

    def initialize_brain(self) -> None:
        """Start the background heartbeat after all modules are ready."""
        self.heartbeat.start()
        logger.info("Ossa brain initialized with heartbeat.")

    def pulse(self, raw_input: str) -> str:
        """
        Run one full cognitive cycle on raw user input.

        Args:
            raw_input: The text received from the user.

        Returns:
            The final response string to send back.
        """
        try:
            # 1. Terminal command bypass – direct shell execution
            if raw_input.startswith("!"):
                return self._handle_terminal_command(raw_input)

            # 2. Perceive
            self.cns.broadcast(Signal("input_received", {"text": raw_input}, 0.8))
            logger.info(f"Perceived: {raw_input}")

            # 3. Feel – analyze tone, update mood
            mood_update = self.amygdala.analyze_tone(raw_input)
            logger.info(f"Mood shift: {mood_update}")

            # 4. Context – retrieve recent episodic memories
            recent_memories = self.hippocampus.get_recent_context(5)
            context = {
                "recent_memories": recent_memories,
                "current_mood": self.thalamus.get_emotion()
            }
            logger.debug(f"Context: {context}")

            # 5. Generate + Simulate (single API call)
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

            # 6. Act (backup inline command detection)
            if response.startswith("!"):
                final_response = self._execute_inline_command(response)
            else:
                final_response = response

            # 7. Record episode in long‑term memory
            self._record_episode(
                input_text=raw_input,
                response=final_response,
                simulation=simulation_outcome
            )

            # 8. Broadcast response signal
            self.cns.broadcast(
                Signal("response_generated", {"response": final_response}, 0.9)
            )

            return final_response

        except Exception as e:
            logger.error(f"Unhandled error in pulse: {e}", exc_info=True)
            return "I encountered an internal error. Please try again."

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_terminal_command(self, raw_input: str) -> str:
        """Execute a direct terminal command (starts with '!')."""
        command = raw_input[1:].strip()
        if not command:
            return "No command provided."
        result = self.motor_cortex.execute(command)
        final_response = f"Command executed:\n{result}"
        self._record_episode(
            input_text=raw_input,
            response=final_response,
            simulation="terminal command"
        )
        return final_response

    def _execute_inline_command(self, response: str) -> str:
        """Handle a command embedded in the LLM's response."""
        command = response[1:].strip()
        output = self.motor_cortex.execute(command)
        return f"Command executed:\n{output}"

    def _record_episode(
        self,
        input_text: str,
        response: str,
        simulation: str = ""
    ) -> None:
        """Store an interaction snapshot in the hippocampus."""
        episode = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "response": response,
            "mood": self.thalamus.get_emotion().get("current_mood"),
            "simulation": simulation
        }
        self.hippocampus.add_episode(episode)
        logger.debug("Episode recorded.")

    # ------------------------------------------------------------------
    # CNS callbacks
    # ------------------------------------------------------------------

    def _on_input_received(self, signal: Signal) -> None:
        logger.debug(f"CNS input signal: {signal}")

    def _on_response_generated(self, signal: Signal) -> None:
        logger.debug(f"CNS response signal: {signal}")