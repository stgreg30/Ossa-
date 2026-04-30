"""
Imagination – Outcome Simulator
=================================
Generates a short prediction about what would happen
if a particular response were given.

Currently in standby – the main cognitive cycle uses
a combined generate+simulate API call, but this module
is kept for future multi‑step reasoning or testing.
"""

import logging
from typing import Any, Dict, Optional

# Avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from body.external_api_control import Accelerator

logger = logging.getLogger("Imagination")


class Imagination:
    """
    Simulates the likely consequence of a candidate response.

    Uses the LLM to predict whether an action would lead to
    a positive, negative, or neutral outcome, helping the
    decision engine choose more wisely.

    Attributes:
        accelerator (Accelerator): LLM API handler.
    """

    # Maximum length of user input to include in the simulation prompt
    MAX_USER_INPUT_LENGTH = 200

    # Maximum number of recent memories to include as context
    MAX_CONTEXT_MEMORIES = 2

    def __init__(self, accelerator: "Accelerator") -> None:
        """
        Args:
            accelerator: The LLM API handler for text generation.
        """
        self.accelerator = accelerator
        logger.info("Imagination module initialized (standby mode).")

    def simulate(
        self,
        action: str,
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Predict the likely consequence of a proposed response.

        Args:
            action: The candidate response being considered.
            user_input: The original message from the user.
            context: Dictionary with 'current_mood' and 'recent_memories'.

        Returns:
            A 1-2 sentence outcome prediction, or an empty string on failure.
        """
        # Build a safe, trimmed prompt
        prompt = self._build_simulation_prompt(action, user_input, context)

        try:
            raw = self.accelerator.generate_text(prompt)
            outcome = raw.strip() if raw else ""
            if outcome:
                logger.debug(f"Simulation outcome: {outcome[:100]}")
            else:
                logger.warning("Imagination returned an empty outcome.")
            return outcome

        except Exception:
            logger.exception("Imagination simulation failed.")
            return ""

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_simulation_prompt(
        self,
        action: str,
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build a compact prompt for the simulation.

        Trims long inputs and large memory lists to stay within
        token limits.
        """
        # Trim user input
        trimmed_input = user_input[:self.MAX_USER_INPUT_LENGTH]

        # Extract mood safely
        current_mood = context.get("current_mood", {})
        mood_str = current_mood.get("current_mood", "neutral") \
            if isinstance(current_mood, dict) else str(current_mood)

        # Trim recent memories
        memories = context.get("recent_memories", [])
        if not isinstance(memories, list):
            memories = []
        trimmed_memories = memories[-self.MAX_CONTEXT_MEMORIES:]
        memories_str = self._format_memories(trimmed_memories)

        return f"""You are simulating the outcome of an AI assistant's response.
User input: {trimmed_input}
Current emotional state: {mood_str}
Recent conversation: {memories_str}

The assistant is considering saying: "{action}"
What would be the likely immediate consequence of that response? Describe briefly in 1-2 sentences.
"""

    @staticmethod
    def _format_memories(memories: list) -> str:
        """Format a short list of memories for the prompt."""
        if not memories:
            return "No recent interactions."
        lines = []
        for m in memories:
            inp = m.get("input", "")[:80]
            resp = m.get("response", "")[:80]
            lines.append(f"User: {inp} | Assistant: {resp}")
        return "\n".join(lines)