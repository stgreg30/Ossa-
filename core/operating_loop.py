import time
from core.brain_controller import executive_function
from core.central_nervous_system import ossa_cns, Signal

class OperatingLoop:
    """
    The Heartbeat of Ossa. 
    Keeps the cognitive cycle running and manages the 'Tick' of the brain.
    """
    def __init__(self):
        self.executive = executive_function
        self.cns = ossa_cns
        self.is_alive = False
        self.tick_rate = 0.5  # Seconds between cognitive cycles

    def start(self):
        """Wake up Ossa and start the life cycle."""
        self.is_alive = True
        self.executive.initialize_brain()
        
        print("[HEARTBEAT] Ossa is now breathing...")
        self.run_loop()

    def run_loop(self):
        """The continuous cycle of perception and self-reflection."""
        try:
            while self.is_alive:
                # 1. Internal Homeostasis Check
                # Ossa looks at its own state (energy, mood) every tick.
                self.maintain_internal_state()

                # 2. Process CNS Queue
                # If there are signals waiting in the nervous system, handle them.
                if self.cns.signal_log:
                    latest_signal = self.cns.signal_log[-1]
                    # Log activity for introspection
                    # print(f"[TICK] Current Signal: {latest_signal.origin}")

                # 3. Sleep to simulate neural firing interval
                time.sleep(self.tick_rate)
        except KeyboardInterrupt:
            self.stop()

    def maintain_internal_state(self):
        """
        Periodically triggers introspection and reflection.
        Ensures Ossa doesn't 'freeze' without input.
        """
        # Broadcast a 'Background Thought' signal
        heartbeat_signal = Signal(
            origin="executive.homeostasis",
            content="Internal state check.",
            intensity=0.1 # Low priority background noise
        )
        self.cns.broadcast(heartbeat_signal)

    def stop(self):
        """Graceful shutdown of the organism."""
        print("\n[HEARTBEAT] Stopping Ossa...")
        self.is_alive = False
        self.executive.shutdown()

if __name__ == "__main__":
    # This allows you to test the loop directly
    loop = OperatingLoop()
    loop.start()
