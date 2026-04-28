import time
import uuid
from typing import Any, Callable, Dict, List

class Signal:
    """
    A discrete packet of 'neural' information traveling through Ossa.
    """
    def __init__(self, origin: str, content: Any, intensity: float = 1.0, metadata: Dict = None):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.origin = origin      # Which organ sent this? (e.g., 'perception.text')
        self.content = content    # The actual data
        self.intensity = intensity # Importance/Priority (0.0 to 1.0)
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<Signal {self.id[:8]} from {self.origin} (Int: {self.intensity})>"

class CNS:
    """
    The central synaptic pathway. Every organ in Ossa's brain 
    subscribes to this bus to listen for relevant signals.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.signal_log: List[Signal] = []
        self.max_log_size = 100

    def subscribe(self, topic: str, callback: Callable):
        """Allows an organ to listen for specific signal types."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        print(f"[CNS] Module attached to synapse: {topic}")

    def broadcast(self, signal: Signal):
        """Sends a signal through the nervous system."""
        self.signal_log.append(signal)
        if len(self.signal_log) > self.max_log_size:
            self.signal_log.pop(0)

        # Direct addressing (e.g., 'cognition.logic') or wildcard ('cognition.*')
        for topic, callbacks in self.subscribers.items():
            if topic == "*" or signal.origin.startswith(topic.replace(".*", "")):
                for callback in callbacks:
                    callback(signal)

# Global instance to be imported by all modules
ossa_cns = CNS()
