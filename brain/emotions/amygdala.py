"""
Amygdala – Emotional Tone Analyzer
====================================
Analyzes user input to determine the dominant emotional tone
and updates Ossa's mood state accordingly.

Mood can be one of three categories:
- collaborative
- defensive
- analytical

Emotional intensity is smoothed over time via a rolling average.
"""

import logging
from typing import Any, Dict, List, Optional

# Avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.state_manager import Thalamus

logger = logging.getLogger("Amygdala")


class Amygdala:
    """
    Analyzes the emotional content of user messages and
    shifts Ossa’s mood between collaborative, defensive,
    and analytical states.

    Keyword lists are class constants and can be overridden
    for customisation.

    Attributes:
        thalamus (Thalamus): Persistent state manager.
    """

    # Default keyword sets (lowercase)
    COLLABORATIVE_KEYWORDS: List[str] = [
        "please", "help", "thanks", "great", "amazing", "love",
        "together", "collaborate", "thank", "wonderful", "nice",
        "good", "awesome", "happy", "grateful", "appreciate"
    ]

    DEFENSIVE_KEYWORDS: List[str] = [
        "stop", "wrong", "no", "don't", "insult", "annoying",
        "shut", "hate", "terrible", "bad", "awful", "stupid",
        "useless", "boring", "angry", "rude", "leave"
    ]

    ANALYTICAL_KEYWORDS: List[str] = [
        "how", "why", "what", "analyze", "calculate", "explain",
        "data", "compare", "define", "difference", "reason",
        "logic", "science", "method", "detail", "step"
    ]

    # Mood smoothing factor (0.0 - 1.0). Closer to 1 = faster change.
    SMOOTHING_FACTOR: float = 0.5

    # Minimum intensity floor
    MIN_INTENSITY: float = 0.1

    # Maximum intensity cap
    MAX_INTENSITY: float = 1.0

    def __init__(self, thalamus: "Thalamus") -> None:
        """
        Args:
            thalamus: State manager for reading/writing emotion data.
        """
        self.thalamus = thalamus
        logger.info("Amygdala initialized.")

    def analyze_tone(self, text: str) -> Dict[str, Any]:
        """
        Analyze the emotional tone of the given text and update
        Ossa's current mood.

        Args:
            text: The raw user input.

        Returns:
            A dict with 'new_mood' (str) and 'intensity' (float).
        """
        if not text or not text.strip():
            logger.debug("Empty input received; mood unchanged.")
            current = self.thalamus.get_emotion()
            return {
                "new_mood": current.get("current_mood", "collaborative"),
                "intensity": current.get("intensity", 0.5)
            }

        text_lower = text.lower()

        # Calculate keyword scores
        col_score = self._count_keywords(text_lower, self.COLLABORATIVE_KEYWORDS)
        def_score = self._count_keywords(text_lower, self.DEFENSIVE_KEYWORDS)
        ana_score = self._count_keywords(text_lower, self.ANALYTICAL_KEYWORDS)

        # Determine dominant mood and raw intensity
        mood, raw_intensity = self._classify_mood(col_score, def_score, ana_score)

        # Retrieve current emotion state and update it
        current = self.thalamus.get_emotion()
        current_intensity = current.get("intensity", 0.5)

        # Smooth the intensity (rolling average)
        new_intensity = (
            current_intensity * (1.0 - self.SMOOTHING_FACTOR)
            + raw_intensity * self.SMOOTHING_FACTOR
        )
        new_intensity = max(self.MIN_INTENSITY, min(self.MAX_INTENSITY, new_intensity))

        # Update state
        current["current_mood"] = mood
        current["intensity"] = new_intensity

        # Record mood history
        if "mood_history" not in current:
            current["mood_history"] = []
        current["mood_history"].append({
            "mood": mood,
            "source_text": text[:100],  # keep slightly longer for context
            "trigger_keywords": {
                "collaborative": col_score,
                "defensive": def_score,
                "analytical": ana_score
            }
        })
        # Limit history length to prevent unbounded growth
        if len(current["mood_history"]) > 200:
            current["mood_history"] = current["mood_history"][-200:]

        self.thalamus.set_emotion(current)

        logger.info(f"Mood -> {mood} (intensity: {new_intensity:.2f}, "
                     f"scores: col={col_score}, def={def_score}, ana={ana_score})")

        return {"new_mood": mood, "intensity": new_intensity}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _count_keywords(text: str, keywords: List[str]) -> int:
        """
        Count how many keywords appear in the text.
        Uses simple substring matching; can be enhanced with word boundaries.
        """
        return sum(1 for kw in keywords if kw in text)

    def _classify_mood(
        self, col: int, deff: int, ana: int
    ) -> tuple:
        """
        Determine the dominant mood and a raw intensity score
        based on keyword counts.

        Args:
            col: Collaborative keyword score.
            deff: Defensive keyword score.
            ana: Analytical keyword score.

        Returns:
            Tuple of (mood_string, raw_intensity).
        """
        # Collaborative dominates if it's highest and non‑zero
        if col >= deff and col >= ana and col > 0:
            mood = "collaborative"
            intensity = min(self.MAX_INTENSITY, 0.5 + col * 0.1)
        elif deff > col and deff > ana:
            mood = "defensive"
            intensity = min(self.MAX_INTENSITY, 0.5 + deff * 0.1)
        elif ana > 0:
            mood = "analytical"
            intensity = min(self.MAX_INTENSITY, 0.5 + ana * 0.1)
        else:
            # Default to collaborative with neutral intensity
            mood = "collaborative"
            intensity = 0.5

        return mood, intensity

    # ------------------------------------------------------------------
    # Public helpers for external use / debugging
    # ------------------------------------------------------------------

    def get_current_mood(self) -> Dict[str, Any]:
        """Return the current emotional state without modifying it."""
        return self.thalamus.get_emotion()