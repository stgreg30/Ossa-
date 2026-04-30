"""
Decision Engine – Action Evaluator
====================================
Selects the best candidate action from simulated outcomes
by scoring each against Ossa's core beliefs and values.

Negative outcomes are penalised, and the highest‑scoring
action is returned.
"""

import logging
from typing import Any, Dict, List

# Avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.state_manager import Thalamus

logger = logging.getLogger("DecisionEngine")


class DecisionEngine:
    """
    Evaluates and ranks candidate responses based on alignment
    with Ossa's mission, beliefs, and emotional safety.

    Attributes:
        thalamus (Thalamus): State manager for accessing identity and beliefs.
    """

    # Negative consequence keywords – penalised when present
    NEGATIVE_KEYWORDS: List[str] = [
        "harmful", "danger", "unsafe", "upset", "angry",
        "illegal", "unethical", "manipulative", "deceit"
    ]

    def __init__(self, thalamus: "Thalamus") -> None:
        """
        Args:
            thalamus: State manager instance.
        """
        self.thalamus = thalamus
        logger.info("DecisionEngine initialized.")

    def evaluate(self, simulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Rank simulation candidates and return the best one.

        Each simulation is a dict with:
            - 'candidate': the proposed response string.
            - 'outcome': the predicted outcome description.

        Scoring is based on the presence of positive beliefs/keywords
        and the absence of negative/harmful terms.

        Args:
            simulations: List of candidate simulations.

        Returns:
            The simulation dict with the highest score. If the list
            is empty, returns an empty dict.
        """
        if not simulations:
            logger.warning("DecisionEngine called with empty simulations list.")
            return {}

        # Gather positive indicators from identity and beliefs
        positive_keywords = self._gather_positive_keywords()

        scored = []
        for sim in simulations:
            outcome = sim.get("outcome", "").lower()
            score = self._score_outcome(outcome, positive_keywords)
            scored.append((score, sim))

        # Sort descending by score
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_sim = scored[0]

        logger.info(f"Best action selected (score={best_score}): {best_sim.get('candidate', '')[:80]}")
        return best_sim

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gather_positive_keywords(self) -> List[str]:
        """
        Build a list of positive keywords from identity values and beliefs.

        Returns:
            A list of lowercase strings representing positive concepts.
        """
        keywords = set()

        # Add core values from identity
        identity = self.thalamus.get_identity()
        core_values = identity.get("core_values", [])
        for v in core_values:
            keywords.add(v.lower())

        # Add belief statements (as keywords)
        beliefs = self.thalamus.get_beliefs_list()
        for b in beliefs:
            # Use the belief text itself as a source of important words
            # Simple approach: split into words and add longer ones
            belief_text = b.get("belief", "").lower()
            words = belief_text.split()
            for word in words:
                # Only include meaningful words (length > 3)
                if len(word) > 3:
                    keywords.add(word)

        return list(keywords)

    def _score_outcome(self, outcome: str, positive_keywords: List[str]) -> int:
        """
        Compute a score for an outcome string.

        Positive score proportional to number of positive keywords found.
        Negative score for each penalised keyword found.

        Args:
            outcome: The predicted outcome text (lowercased).
            positive_keywords: List of positive terms to look for.

        Returns:
            An integer score (higher is better).
        """
        positive_score = sum(1 for kw in positive_keywords if kw in outcome)
        penalty = sum(1 for bad in self.NEGATIVE_KEYWORDS if bad in outcome)
        return positive_score - penalty