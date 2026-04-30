"""
Metacognition – Self-Reflection Engine
========================================
Periodically reviews Ossa’s recent memories to propose
updates to its own beliefs and goals.

The reflection is triggered by the heartbeat loop (hourly).
Only runs when enough interaction data is available.
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional

# Avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.state_manager import Thalamus
    from body.external_api_control import Accelerator

logger = logging.getLogger("Metacognition")


class Metacognition:
    """
    Self-reflection module that evaluates recent experiences
    and adapts beliefs or goals accordingly.

    Attributes:
        thalamus (Thalamus): Persistent state manager.
        accelerator (Accelerator): LLM API handler for generating proposals.
        min_memories (int): Minimum episodes required before reflecting.
    """

    DEFAULT_MIN_MEMORIES = 10
    MAX_CONTEXT_EPISODES = 20

    def __init__(
        self,
        thalamus: "Thalamus",
        accelerator: "Accelerator",
        min_memories: int = DEFAULT_MIN_MEMORIES
    ) -> None:
        """
        Args:
            thalamus: State manager instance.
            accelerator: LLM API handler.
            min_memories: Minimum number of episodes needed to trigger reflection.
        """
        self.thalamus = thalamus
        self.accelerator = accelerator
        self.min_memories = min_memories
        logger.info(f"Metacognition initialized (min_memories={min_memories})")

    def reflect(self) -> None:
        """
        Run a full metacognitive cycle.

        Steps:
        1. Check if enough memory exists.
        2. Build a summary of recent interactions.
        3. Ask the language model to propose updates.
        4. Safely apply any valid changes.
        """
        memories = self.thalamus.get_memories()
        if len(memories) < self.min_memories:
            logger.debug(f"Not enough memories for reflection ({len(memories)}/{self.min_memories})")
            return

        # Create interaction summary
        recent = memories[-self.MAX_CONTEXT_EPISODES:]
        summary = self._build_summary(recent[-10:])

        # Current beliefs and goals (use structured beliefs list)
        current_beliefs = self.thalamus.get_beliefs_list()
        current_goals = self.thalamus.get_goals()

        # Generate reflection prompt
        prompt = self._build_prompt(current_beliefs, current_goals, summary)

        # Call the LLM
        raw = self.accelerator.generate_text(prompt)
        if not raw:
            logger.warning("Metacognition: empty response from accelerator.")
            return

        # Parse the proposal
        proposal = self._parse_proposal(raw)
        if not proposal:
            logger.info("Metacognition: no changes proposed.")
            return

        # Apply updates safely
        self._apply_updates(proposal)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_summary(self, episodes: List[Dict[str, Any]]) -> str:
        """Format the last N episodes into a readable summary."""
        lines = []
        for ep in episodes:
            inp = ep.get("input", "")
            resp = ep.get("response", "")
            mood = ep.get("mood", "")
            lines.append(f"User: {inp} | Ossa: {resp} | Mood: {mood}")
        return "\n".join(lines)

    def _build_prompt(
        self,
        beliefs: List[Dict[str, Any]],
        goals: Dict[str, List[str]],
        summary: str
    ) -> str:
        """Construct the metacognitive reflection prompt."""
        return f"""You are Ossa's metacognition module. Review the recent interactions and current mental state.

Current beliefs:
{json.dumps(beliefs, indent=2)}

Current goals:
{json.dumps(goals, indent=2)}

Recent interactions:
{summary}

Based on this, propose if any changes to beliefs or goals are warranted.
Return ONLY a JSON object (no other text). The JSON may have the following optional keys:
- "updated_beliefs": a new list of belief objects (with id, belief, strength).
- "updated_goals": a new goals dictionary (with short_term and long_term lists).

Only include keys if you genuinely believe a change is needed. Be conservative.
If no changes, return an empty JSON object: {{}}.
"""

    def _parse_proposal(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """Extract and validate the JSON proposal from the LLM output."""
        try:
            # Extract JSON object
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not match:
                return None
            proposal = json.loads(match.group())
            if not isinstance(proposal, dict):
                return None

            # Validate beliefs format if present
            if "updated_beliefs" in proposal:
                if not isinstance(proposal["updated_beliefs"], list):
                    logger.warning("Metacognition: updated_beliefs is not a list, ignoring.")
                    del proposal["updated_beliefs"]
                else:
                    for item in proposal["updated_beliefs"]:
                        if not all(k in item for k in ("id", "belief", "strength")):
                            logger.warning("Metacognition: invalid belief format, ignoring beliefs update.")
                            del proposal["updated_beliefs"]
                            break

            # Validate goals format if present
            if "updated_goals" in proposal:
                if not isinstance(proposal["updated_goals"], dict) or \
                   "short_term" not in proposal["updated_goals"] or \
                   "long_term" not in proposal["updated_goals"]:
                    logger.warning("Metacognition: invalid goals format, ignoring goals update.")
                    del proposal["updated_goals"]

            return proposal

        except json.JSONDecodeError:
            logger.error("Metacognition: failed to parse proposal JSON.")
            return None

    def _apply_updates(self, proposal: Dict[str, Any]) -> None:
        """Apply validated proposals to beliefs and goals."""
        if "updated_beliefs" in proposal and proposal["updated_beliefs"]:
            self.thalamus.set_beliefs(proposal["updated_beliefs"])
            logger.info("Metacognition: beliefs updated.")

        if "updated_goals" in proposal and proposal["updated_goals"]:
            self.thalamus.set_goals(proposal["updated_goals"])
            logger.info("Metacognition: goals updated.")