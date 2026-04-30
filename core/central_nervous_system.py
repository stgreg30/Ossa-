from collections import namedtuple
from typing import Callable, Dict, List

# Signal packet sent through the CNS
Signal = namedtuple('Signal', ['origin', 'content', 'intensity'])

class CentralNervousSystem:
    """Event bus with subscriber/broadcast model."""
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}  # channel -> list of callbacks
        self._global_subscribers: List[Callable] = []

    def subscribe(self, channel: str, callback: Callable[[Signal], None]):
        """Register a callback for a specific signal channel."""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

    def subscribe_global(self, callback: Callable[[Signal], None]):
        """Register a callback for all signals."""
        self._global_subscribers.append(callback)

    def broadcast(self, signal: Signal):
        """Send signal to all relevant subscribers."""
        # Channel-specific
        for cb in self._subscribers.get(signal.origin, []):
            cb(signal)
        # Global
        for cb in self._global_subscribers:
            cb(signal)