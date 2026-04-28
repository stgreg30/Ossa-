import json
import os
from threading import Lock

class StateManager:
    """
    The Thalamus of Ossa. 
    Manages the flow of data between persistent storage and active cognition.
    """
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.lock = Lock()  # Prevents data corruption during simultaneous read/writes
        self.active_state = {
            "identity": {},
            "emotions": {"mood": "neutral", "energy": 1.0},
            "goals": [],
            "short_term_context": []
        }
        self.initialize_storage()

    def initialize_storage(self):
        """Ensures the data directory and essential files exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Define required files and their default structures
        required_files = {
            "identity.json": {"name": "Ossa", "version": "1.0", "mission": "Self-evolution"},
            "beliefs.json": [],
            "emotions.json": {"mood": "stable", "energy": 1.0},
            "memories.json": [],
            "goals.json": {"current_priority": None, "objectives": []}
        }

        for filename, default_data in required_files.items():
            path = os.path.join(self.data_dir, filename)
            if not os.path.exists(path):
                self.save_to_disk(path, default_data)
            self.load_into_memory(filename.replace(".json", ""), path)

    def load_into_memory(self, key, path):
        """Hydrates Ossa's active memory from the disk."""
        with open(path, 'r') as f:
            self.active_state[key] = json.load(f)

    def save_to_disk(self, path, data):
        """Persists a mental state to the physical drive."""
        with self.lock:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)

    def update_organ_state(self, organ_key, new_data, persist=True):
        """
        Updates Ossa's current state. 
        If persist=True, it writes immediately to the 'biological' drive.
        """
        self.active_state[organ_key] = new_data
        if persist:
            path = os.path.join(self.data_dir, f"{organ_key}.json")
            self.save_to_disk(path, new_data)

    def get_context_snapshot(self):
        """Returns a unified view of Ossa's current internal world."""
        return {
            "who_i_am": self.active_state.get("identity"),
            "how_i_feel": self.active_state.get("emotions"),
            "what_i_want": self.active_state.get("goals")
        }

# Global instance
thalamus = StateManager()
