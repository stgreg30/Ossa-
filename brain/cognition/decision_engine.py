class DecisionEngine:
    """Selects the best action based on simulations and core values."""
    def __init__(self, thalamus):
        self.thalamus = thalamus

    def evaluate(self, simulations: list) -> dict:
        """
        Each simulation: {'candidate': str, 'outcome': str}
        We use a simple heuristic: prefer outcomes that contain mission-related keywords.
        """
        identity = self.thalamus.get_identity()
        mission_keywords = ["helpful", "safe", "empathetic", "positive", "collaborative", "curious"]
        scored = []
        for sim in simulations:
            outcome = sim["outcome"].lower()
            score = sum(1 for kw in mission_keywords if kw in outcome)
            # Also penalise negative terms
            penalty = sum(1 for bad in ["harmful", "danger", "upset", "angry"] if bad in outcome)
            scored.append((score - penalty, sim))
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1] if scored else simulations[0]
        return best
