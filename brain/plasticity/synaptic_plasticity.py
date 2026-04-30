"""
Synaptic Plasticity – Adaptive Parameter Tuner
================================================
Periodically adjusts Ossa's internal parameters based
on long‑term interaction trends. This mimics neural
plasticity by strengthening or weakening connections
(parameters) according to experience.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from core.state_manager import Thalamus
    from brain.emotions.amygdala import Amygdala
    from brain.cognition.decision_engine import DecisionEngine

logger = logging.getLogger("SynapticPlasticity")

class SynapticPlasticity:
    """
    Tunes internal parameters of other modules based on
    recent memory patterns.

    Target parameters (example):
        - Amygdala.smoothing_factor (mood change speed)
        - DecisionEngine.negative_penalty (severity of negative keyword penalty)
        - Belief strengths (via Thalamus)
    """

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
        if len(memories) < 20:
            return

        # Analyse mood trends
        recent = memories[-50:]
        mood_counts = {"collaborative": 0, "defensive": 0, "analytical": 0}
        for ep in recent:
            mood = ep.get("mood", "")
            if mood in mood_counts:
                mood_counts[mood] += 1

        # If user is often defensive, increase amygdala smoothing to avoid rapid mood drops
        if mood_counts["defensive"] > len(recent) * 0.4:
            self.amygdala.SMOOTHING_FACTOR = min(0.9, self.amygdala.SMOOTHING_FACTOR + 0.05)
            logger.info("Increased amygdala smoothing factor due to frequent defensiveness.")
        else:
            # slowly return to default
            self.amygdala.SMOOTHING_FACTOR = max(0.3, self.amygdala.SMOOTHING_FACTOR - 0.02)

        # Adjust negative penalty in decision engine based on safety incidents
        # (simplistic: if many "harmful" simulated outcomes, increase penalty)
        harmful_count = sum(1 for ep in recent if "harmful" in ep.get("simulation", "").lower())
        if harmful_count > 5:
            self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER = \
                min(3.0, self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER + 0.1)
            logger.info("Increased negative penalty in decision engine.")
        else:
            self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER = \
                max(1.0, self.decision_engine.NEGATIVE_PENALTY_MULTIPLIER - 0.05)

        # Optionally adjust belief strengths based on recent conversations
        # (left for metacognition to handle explicitly)
