import time
from core.state_manager import thalamus
from core.central_nervous_system import ossa_cns, Signal

class EpisodicMemory:
    """
    The Hippocampus of Ossa.
    Records time-stamped events including user input, Ossa's mood, and outcomes.
    """
    def __init__(self):
        self.state = thalamus

    def record_episode(self, user_input, ossa_response, simulation_used):
        """
        Creates a 'Memory Packet' and stores it in the data layer.
        """
        current_state = self.state.active_state
        
        episode = {
            "timestamp": time.time(),
            "event_id": f"ep_{int(time.time())}",
            "external_input": user_input,
            "internal_response": ossa_response,
            "internal_state": {
                "mood": current_state['emotions'].get('mood'),
                "priority": current_state['goals'].get('current_priority')
            },
            "simulation_data": simulation_used
        }

        # Retrieve the full memory list, append, and save
        memories = self.state.active_state.get('memories', [])
        memories.append(episode)
        
        # Keep only the last 50 episodes in active memory to prevent 'Neural Bloat'
        if len(memories) > 50:
            memories.pop(0)

        self.state.update_organ_state('memories', memories, persist=True)
        
        # Broadcast that a memory has been formed
        ossa_cns.broadcast(Signal("memory.episodic", f"Recorded episode {episode['event_id']}", intensity=0.3))

    def retrieve_recent_context(self, limit=3):
        """Returns the last few episodes to give Ossa short-term perspective."""
        memories = self.state.active_state.get('memories', [])
        return memories[-limit:] if memories else []

# Global instance
hippocampus = EpisodicMemory()
