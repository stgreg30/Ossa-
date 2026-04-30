import json
import os
import threading
from typing import Any, Dict

class Thalamus:
    """Thread‑safe state manager using JSON file persistence."""
    _lock = threading.Lock()
    DATA_DIR = "data"

    STATE_FILES = {
        "identity": "identity.json",
        "emotions": "emotions.json",
        "memories": "memories.json",
        "beliefs": "beliefs.json",
        "goals": "goals.json",
    }

    DEFAULTS = {
        "identity": {
            "name": "Ossa",
            "mission": "Be a helpful, empathetic, and safe cognitive companion.",
            "core_values": ["helpfulness", "safety", "curiosity"]
        },
        "emotions": {
            "current_mood": "collaborative",
            "intensity": 0.5,
            "mood_history": []
        },
        "memories": [],
        "beliefs": {
            "world_model": "User is a curious human seeking assistance."
        },
        "goals": {
            "short_term": ["Answer user query", "Maintain positive interaction"],
            "long_term": ["Learn from conversations", "Improve safety"]
        }
    }

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self._initialize_files()

    def _initialize_files(self):
        for key, filename in self.STATE_FILES.items():
            path = os.path.join(self.DATA_DIR, filename)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(self.DEFAULTS[key], f, indent=2)

    def _load(self, key: str) -> Dict[str, Any]:
        path = os.path.join(self.DATA_DIR, self.STATE_FILES[key])
        with self._lock:
            with open(path, 'r') as f:
                return json.load(f)

    def _save(self, key: str, data: Any):
        path = os.path.join(self.DATA_DIR, self.STATE_FILES[key])
        with self._lock:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

    def get_state(self, key: str) -> Any:
        return self._load(key)

    def update_state(self, key: str, new_data: Any):
        self._save(key, new_data)

    # Convenience methods
    def get_emotion(self):
        return self.get_state("emotions")

    def set_emotion(self, emotion_state):
        self.update_state("emotions", emotion_state)

    def get_memories(self):
        return self.get_state("memories")

    def set_memories(self, memories):
        self.update_state("memories", memories)

    def get_identity(self):
        return self.get_state("identity")

    def get_beliefs(self):
        return self.get_state("beliefs")

    def set_beliefs(self, beliefs):
        self.update_state("beliefs", beliefs)

    def get_goals(self):
        return self.get_state("goals")

    def set_goals(self, goals):
        self.update_state("goals", goals)