"""
Heartbeat – Background Homeostasis & Reflection Loop
=====================================================
Runs as a daemon thread, performing two periodic tasks:
1. Emotional homeostasis – gently decays emotional intensity toward neutral.
2. Metacognitive reflection – triggers a self‑review of beliefs and goals.

The interval is adjustable; default is 10 seconds.
Reflection occurs every 360 cycles (once per hour with a 10s interval).
"""

import threading
import time
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .central_nervous_system import CentralNervousSystem
    from .brain_controller import ExecutiveFunction

logger = logging.getLogger("Heartbeat")

class Heartbeat:
    """
    A thread‑safe background loop that maintains Ossa's internal state.

    Attributes:
        cns (CentralNervousSystem): The event bus for broadcasting signals.
        brain_controller (ExecutiveFunction): Reference to the main controller.
        interval (int): Sleep duration between each cycle, in seconds.
        _running (bool): Thread safe flag to control the loop.
        _thread (Optional[threading.Thread]): The background thread object.
        _counter (int): Cycle counter, used to schedule periodic tasks.
    """

    def __init__(
        self,
        cns: "CentralNervousSystem",
        brain_controller: "ExecutiveFunction",
        interval: int = 10
    ) -> None:
        """
        Args:
            cns: Central Nervous System event bus.
            brain_controller: The main ExecutiveFunction instance.
            interval: Time between heartbeats, in seconds.
        """
        self.cns = cns
        self.brain_controller = brain_controller
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._counter = 0
        self._lock = threading.Lock()
        logger.info(f"Heartbeat initialized with interval={interval}s")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the heartbeat loop in a background daemon thread.
        If the loop is already running, this is a no‑op.
        """
        with self._lock:
            if self._running:
                logger.warning("Heartbeat already running")
                return
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True, name="heartbeat")
            self._thread.start()
            logger.info("Heartbeat thread started")

    def stop(self, timeout: float = 5.0) -> None:
        """
        Signal the loop to stop and wait for the thread to finish.

        Args:
            timeout: Maximum seconds to wait for the thread to join.
        """
        with self._lock:
            self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("Heartbeat thread did not terminate within timeout")
            else:
                logger.info("Heartbeat thread stopped")

    # ------------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        """Internal method that runs in the background thread."""
        logger.info("Heartbeat loop started")
        while self._running:
            try:
                self._homeostasis()
                self._maybe_reflect()
            except Exception:
                logger.exception("Unhandled error in heartbeat loop")
            self._sleep()

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    def _homeostasis(self) -> None:
        """
        Gradually decay emotional intensity toward a neutral baseline.
        This prevents emotional amplification over time.
        """
        try:
            emotion = self.brain_controller.thalamus.get_emotion()
            intensity = emotion.get("intensity", 0.5)
            # Decay toward 0.3, but never below 0.1
            new_intensity = max(0.1, intensity - 0.02)
            emotion["intensity"] = new_intensity
            self.brain_controller.thalamus.set_emotion(emotion)
            logger.debug(f"Homeostasis: intensity {intensity:.2f} -> {new_intensity:.2f}")
        except Exception:
            logger.exception("Homeostasis update failed")

    def _maybe_reflect(self) -> None:
        """
        Trigger metacognitive reflection on a fixed schedule.
        With interval=10s, 360 cycles = 1 hour.
        """
        self._counter += 1
        if self._counter % 360 == 0:
            logger.info("Triggering metacognitive reflection (hourly)")
            try:
                self.brain_controller.metacognition.reflect()
                logger.debug("Metacognition complete")
            except Exception as e:
                logger.error(f"Metacognition error: {e}")

    def _sleep(self) -> None:
        """Sleep between cycles, with early exit if stopped."""
        if self._running:
            time.sleep(self.interval)