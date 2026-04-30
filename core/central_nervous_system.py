"""
Central Nervous System – Event Bus
===================================
Implements a thread‑safe publish/subscribe model for Ossa's
internal signals. Components can subscribe to named channels
or listen globally. Signals carry metadata about the event
source, payload, and intensity.
"""

import logging
from collections import namedtuple
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

# A lightweight signal packet transmitted through the CNS.
# Attributes:
#   origin (str):     The channel or module that emitted the signal.
#   content (Any):    The payload (dict, str, etc.).
#   intensity (float): Importance / strength of the signal.
Signal = namedtuple('Signal', ['origin', 'content', 'intensity'])

# ---------------------------------------------------------------------------
# Core Event Bus
# ---------------------------------------------------------------------------

class CentralNervousSystem:
    """
    A thread‑safe event bus that routes Signal packets to registered
    callbacks. Supports channel‑specific and global subscribers.

    Usage:
        cns = CentralNervousSystem()
        cns.subscribe("mood_update", handle_mood)
        cns.broadcast(Signal("mood_update", {"state": "happy"}, 0.9))
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Signal], None]]] = {}
        self._global_subscribers: List[Callable[[Signal], None]] = []
        self._lock = Lock()
        self.logger = logging.getLogger("CNS")

    # ------------------------------------------------------------------
    # Subscription Management
    # ------------------------------------------------------------------

    def subscribe(self, channel: str, callback: Callable[[Signal], None]) -> None:
        """
        Register a callback to be invoked when a signal is broadcast
        on the specified channel.

        Args:
            channel: The name of the signal channel.
            callback: A callable accepting a Signal argument.
        """
        with self._lock:
            if channel not in self._subscribers:
                self._subscribers[channel] = []
            self._subscribers[channel].append(callback)
            self.logger.debug(f"Subscribed to channel '{channel}': {callback.__name__}")

    def unsubscribe(self, channel: str, callback: Callable[[Signal], None]) -> bool:
        """
        Remove a specific callback from a channel.

        Returns:
            True if the callback was found and removed, False otherwise.
        """
        with self._lock:
            if channel in self._subscribers and callback in self._subscribers[channel]:
                self._subscribers[channel].remove(callback)
                self.logger.debug(f"Unsubscribed from channel '{channel}': {callback.__name__}")
                return True
            return False

    def subscribe_global(self, callback: Callable[[Signal], None]) -> None:
        """
        Register a callback for all signals, regardless of channel.
        """
        with self._lock:
            self._global_subscribers.append(callback)
            self.logger.debug(f"Added global subscriber: {callback.__name__}")

    def unsubscribe_global(self, callback: Callable[[Signal], None]) -> bool:
        """
        Remove a specific global callback.

        Returns:
            True if found and removed, False otherwise.
        """
        with self._lock:
            if callback in self._global_subscribers:
                self._global_subscribers.remove(callback)
                self.logger.debug(f"Removed global subscriber: {callback.__name__}")
                return True
            return False

    # ------------------------------------------------------------------
    # Broadcast
    # ------------------------------------------------------------------

    def broadcast(self, signal: Signal) -> None:
        """
        Send a signal to all relevant subscribers.

        Channel‑specific subscribers are called first, then global
        subscribers. All callbacks are invoked synchronously and
        exceptions are logged but not raised, ensuring one faulty
        subscriber does not block others.

        Args:
            signal: The Signal instance to broadcast.
        """
        self.logger.debug(f"Broadcasting signal on '{signal.origin}' (intensity={signal.intensity})")

        # Collect subscribers under lock to avoid mutation during iteration
        with self._lock:
            channel_callbacks = list(self._subscribers.get(signal.origin, []))
            global_callbacks = list(self._global_subscribers)

        # Invoke channel‑specific callbacks
        for cb in channel_callbacks:
            try:
                cb(signal)
            except Exception:
                self.logger.exception(f"Error in channel subscriber {cb.__name__}")

        # Invoke global callbacks
        for cb in global_callbacks:
            try:
                cb(signal)
            except Exception:
                self.logger.exception(f"Error in global subscriber {cb.__name__}")

    # ------------------------------------------------------------------
    # Introspection (useful for debugging / monitoring)
    # ------------------------------------------------------------------

    def list_channels(self) -> List[str]:
        """Return a list of currently subscribed channels."""
        with self._lock:
            return list(self._subscribers.keys())

    def channel_subscriber_count(self, channel: str) -> int:
        """Return the number of subscribers on a given channel."""
        with self._lock:
            return len(self._subscribers.get(channel, []))

    def global_subscriber_count(self) -> int:
        """Return the total number of global subscribers."""
        with self._lock:
            return len(self._global_subscribers)