class Hippocampus:
    """Episodic memory storing timestamped events."""
    def __init__(self, thalamus):
        self.thalamus = thalamus

    def add_episode(self, episode: dict):
        memories = self.thalamus.get_memories()
        memories.append(episode)
        # Keep memory manageable (limit to last 1000)
        if len(memories) > 1000:
            memories = memories[-1000:]
        self.thalamus.set_memories(memories)

    def get_recent_context(self, n=5):
        memories = self.thalamus.get_memories()
        return memories[-n:] if memories else []
