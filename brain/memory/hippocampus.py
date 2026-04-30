"""
Hippocampus – Episodic Memory Module
======================================
Stores timestamped interaction events and provides methods
to retrieve recent context for the cognitive cycle.

Now includes get_augmented_context() that surfaces related
older memories alongside recent episodes for better recall.
"""

import logging
from typing import Any, Dict, List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.state_manager import Thalamus

logger = logging.getLogger("Hippocampus")


class Hippocampus:
    """
    Manages Ossa's episodic memory. Each episode is a dictionary
    containing at least 'timestamp', 'input', and 'response'.

    Attributes:
        thalamus (Thalamus): The persistent state manager.
        max_episodes (int): Maximum episodes to keep in memory.
    """

    DEFAULT_MAX_EPISODES = 1000

    def __init__(self, thalamus: "Thalamus", max_episodes: int = DEFAULT_MAX_EPISODES) -> None:
        self.thalamus = thalamus
        self.max_episodes = max_episodes
        logger.info(f"Hippocampus initialized (max_episodes={max_episodes})")

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add_episode(self, episode: Dict[str, Any]) -> None:
        if not isinstance(episode, dict):
            logger.warning("Attempted to add non-dict episode, skipping.")
            return
        if "timestamp" not in episode:
            episode["timestamp"] = __import__("datetime").datetime.now().isoformat()

        memories = self.thalamus.get_memories()
        memories.append(episode)

        if len(memories) > self.max_episodes:
            trimmed = memories[-self.max_episodes:]
            logger.debug(f"Memory trimmed from {len(memories)} to {len(trimmed)} episodes")
            memories = trimmed

        self.thalamus.set_memories(memories)
        logger.debug(f"Episode added. Total episodes: {len(memories)}")

    # ------------------------------------------------------------------
    # Retrieval (legacy + new augmented)
    # ------------------------------------------------------------------

    def get_recent_context(self, n: int = 5) -> List[Dict[str, Any]]:
        memories = self.thalamus.get_memories()
        if not memories:
            return []
        return memories[-n:]

    def get_all_memories(self) -> List[Dict[str, Any]]:
        return list(self.thalamus.get_memories())

    def search_memories(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        memories = self.thalamus.get_memories()
        results = []
        keyword_lower = keyword.lower()
        for ep in reversed(memories):
            inp = str(ep.get("input", "")).lower()
            resp = str(ep.get("response", "")).lower()
            if keyword_lower in inp or keyword_lower in resp:
                results.append(ep)
                if len(results) >= limit:
                    break
        return results

    def get_augmented_context(self, current_input: str) -> Dict[str, Any]:
        """
        Build an enriched context dictionary for the cognitive cycle.
        Returns:
            dict with keys:
                'recent'            – last 5 episodes (full text)
                'relevant_facts'    – up to 3 older episodes related to the input
        """
        memories = self.thalamus.get_memories()
        if not memories:
            return {"recent": [], "relevant_facts": []}

        # 1. Recent: last 5 episodes (full content, no truncation here)
        recent = memories[-5:]

        # 2. Search older memories for facts related to current input
        relevant_facts = []
        if len(memories) > 5:
            older = memories[:-5]
            input_words = set(current_input.lower().split())
            for ep in reversed(older):
                ep_text = (ep.get("input", "") + " " + ep.get("response", "")).lower()
                if any(word in ep_text for word in input_words):
                    fact = (
                        f"User: {ep['input'][:150]} | "
                        f"Ossa: {ep['response'][:150]}"
                    )
                    relevant_facts.append(fact)
                    if len(relevant_facts) >= 3:
                        break

        return {
            "recent": recent,
            "relevant_facts": relevant_facts
        }

    # ------------------------------------------------------------------
    # Management
    # ------------------------------------------------------------------

    def clear_memory(self) -> None:
        self.thalamus.set_memories([])
        logger.info("All memories cleared.")

    def memory_size(self) -> int:
        return len(self.thalamus.get_memories())