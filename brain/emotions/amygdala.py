def analyze_tone(self, text: str):
    """Return mood update and apply to state."""
    text_lower = text.lower()

    # Basic keyword heuristics
    collaborative_keywords = ["please", "help", "thanks", "great", "amazing", "love", "together", "collaborate"]
    defensive_keywords = ["stop", "wrong", "no", "don't", "insult", "annoying", "shut", "hate", "terrible"]
    analytical_keywords = ["how", "why", "what", "analyze", "calculate", "explain", "data", "compare"]

    col_score = sum(1 for w in collaborative_keywords if w in text_lower)
    def_score = sum(1 for w in defensive_keywords if w in text_lower)
    ana_score = sum(1 for w in analytical_keywords if w in text_lower)

    if col_score >= def_score and col_score >= ana_score and col_score > 0:
        mood = "collaborative"
        intensity = min(1.0, 0.5 + col_score * 0.1)
    elif def_score > col_score and def_score > ana_score:
        mood = "defensive"
        intensity = min(1.0, 0.5 + def_score * 0.1)
    elif ana_score > 0:
        mood = "analytical"
        intensity = min(1.0, 0.5 + ana_score * 0.1)
    else:
        mood = "collaborative"
        intensity = 0.5

    # Update state – ensure mood_history exists
    current = self.thalamus.get_emotion()
    current["current_mood"] = mood
    current["intensity"] = (current.get("intensity", 0.5) + intensity) / 2

    if "mood_history" not in current:
        current["mood_history"] = []  # initialise if missing
    current["mood_history"].append({
        "mood": mood,
        "source_text": text[:50],
        "trigger_keywords": {"col": col_score, "def": def_score, "ana": ana_score}
    })

    self.thalamus.set_emotion(current)

    return {"new_mood": mood, "intensity": current["intensity"]}