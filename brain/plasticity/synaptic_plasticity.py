"""
Synaptic Plasticity – Adaptive Parameter Tuner
================================================
Periodically adjusts Ossa's internal parameters based on
long‑term interaction trends. This mimics neural plasticity
by strengthening or weakening module settings according
to lived experience.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state_manager import Thalamus
    from brain.emotions.amygdala import Amygdala
    from brain.cognition.decision_engine import DecisionEngine

logger = logging.getLogger("SynapticPlasticity")


class SynapticPlasticity:
    """
    Tunes Ossa's internal parameters by analysing recent memory patterns.

    Target parameters:
        - Amygdala.SMOOTHING_FACTOR (mood change speed)
        - DecisionEngine.NEGATIVE_PENALTY_MULTIPLIER (severity of safety penalty)
    """

    # Minimum memories required before any adaptation
    MIN_MEMORIES = 30

    # How many recent memories to analyse
    ANALYSIS_WINDOW = 60

    def __init__(
        self,
        thalamus: "Thalamus",
        amygdala: "Amygdala",
        decision_engine: "DecisionEngine"
    ) -> None:
        self.thalamus = thalamus
        self.amygdala = amygdala
        self.decision_engine = decision_engine
        logger.info("Synaptic Plasticity initialized.")

    def adapt(self) -> None:
        """Run one adaptation cycle."""
        memories = self.thalamus.get_memories()
        if len(memories) < self.MIN_MEMORIES:
            return

        recent = memories[-self.ANALYSIS_WINDOW:]
        mood_counts = {"collaborative": 0, "defensive": 0, "analytical": 0}
        for ep in recent:
            mood = ep.get("mood", "")
            if mood in mood_counts:
                mood_counts[mood] += 1

        total = len(recent)
        def_ratio = mood_counts["defensive"] / total if total > 0 else 0

        # --- Amygdala smoothing -------------------------------------------------
        # If the conversation is frequently defensive, slow down mood changes
        # to prevent rapid destabilisation.
        if def_ratio > 0.4:
            self.amygdala.SMOOTHING_FACTOR = min(0.9, self.amygdala.SMOOTHING_FACTOR + 0.05)
            logger.info("Increased amygdala smoothing (frequent defensiveness).")
        else:
            # Gradually return toward default (0.5)
            self.amygdala.SMOOTHING_FACTOR = max(0.3, self.amygdala.SMOOTHING_FACTOR - 0.02)

        # --- Decision engine penalty multiplier ---------------------------------
        # Count how many simulated outcomes contain harmful language.
        harmful_count = sum(
            1 for ep in recent
            if "harmful" in ep.get("simulation", "").lower()
               or "danger" in ep.get("simulation", "").lower()
        )
        if harmful_count > 5:
            self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER = min(
                3.0,
                self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER + 0.1
            )
            logger.info("Increased decision engine safety penalty.")
        else:
            self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER = max(
                1.0,
                self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER - 0.05
            )

        logger.debug(
            f"Plasticity state: smoothing={self.amygdala.SMOOTHING_FACTOR:.2f}, "
            f"penalty_mul={self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER:.2f}"
        )