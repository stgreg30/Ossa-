import threading
import time
import logging

class Heartbeat:
    """Background loop that maintains homeostasis and triggers metacognition."""
    def __init__(self, cns, brain_controller, interval=30):
        self.cns = cns
        self.brain_controller = brain_controller
        self.interval = interval
        self._running = False
        self._thread = None
        self.logger = logging.getLogger("Heartbeat")

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.logger.info("Heartbeat started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        while self._running:
            # Homeostasis: slowly decay emotional intensity toward neutral
            emotion_state = self.brain_controller.thalamus.get_emotion()
            current_intensity = emotion_state.get("intensity", 0.5)
            new_intensity = max(0.1, current_intensity - 0.02)  # decay
            emotion_state["intensity"] = new_intensity
            self.brain_controller.thalamus.set_emotion(emotion_state)

            # Trigger metacognitive reflection (e.g., every 5 minutes)
            # For simplicity, use a counter; here we do it every 10 intervals
            if hasattr(self, '_counter'):
                self._counter += 1
            else:
                self._counter = 0

            if self._counter % 10 == 0:
                self.logger.info("Triggering metacognitive reflection")
                try:
                    self.brain_controller.metacognition.reflect()
                except Exception as e:
                    self.logger.error(f"Metacognition error: {e}")

            time.sleep(self.interval)