"""
Hippocampus – Episodic Memory Module
======================================
Stores timestamped interaction events and provides methods
to retrieve recent context for the cognitive cycle.

Memory is persisted via the Thalamus state manager.
Old episodes are automatically trimmed to prevent unbounded growth.
"""

import logging
from typing import Any, Dict, List, Optional

# If we need type hints for Thalamus (avoids circular imports)
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
        """
        Args:
            thalamus: State manager for storing memories.
            max_episodes: Maximum number of episodes to retain.
        """
        self.thalamus = thalamus
        self.max_episodes = max_episodes
        logger.info(f"Hippocampus initialized (max_episodes={max_episodes})")

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add_episode(self, episode: Dict[str, Any]) -> None:
        """
        Append a new episode to memory.

        Automatically trims the memory list if it exceeds max_episodes.

        Args:
            episode: A dictionary with at least 'input' and 'response'.
        """
        if not isinstance(episode, dict):
            logger.warning("Attempted to add non-dict episode, skipping.")
            return

        # Ensure timestamp exists
        if "timestamp" not in episode:
            episode["timestamp"] = __import__("datetime").datetime.now().isoformat()

        memories = self.thalamus.get_memories()
        memories.append(episode)

        # Enforce size limit
        if len(memories) > self.max_episodes:
            trimmed = memories[-self.max_episodes:]
            logger.debug(f"Memory trimmed from {len(memories)} to {len(trimmed)} episodes")
            memories = trimmed

        self.thalamus.set_memories(memories)
        logger.debug(f"Episode added. Total episodes: {len(memories)}")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_recent_context(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent n episodes.

        Args:
            n: Number of recent episodes to return (default 5).

        Returns:
            A list of episode dicts (newest last), or empty list if no memories.
        """
        memories = self.thalamus.get_memories()
        if not memories:
            return []
        return memories[-n:]

    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Return a copy of all stored episodes."""
        return list(self.thalamus.get_memories())

    def search_memories(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search episodes whose input or response contains the keyword (case-insensitive).

        Args:
            keyword: The search term.
            limit: Maximum results to return.

        Returns:
            List of matching episodes (newest first).
        """
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

    # ------------------------------------------------------------------
    # Management
    # ------------------------------------------------------------------

    def clear_memory(self) -> None:
        """Delete all stored episodes."""
        self.thalamus.set_memories([])
        logger.info("All memories cleared.")

    def memory_size(self) -> int:
        """Return the current number of episodes in memory."""
        return len(self.thalamus.get_memories())