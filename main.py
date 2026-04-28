import sys
import threading
from core.operating_loop import OperatingLoop
from core.brain_controller import executive_function

def start_ossa():
    """
    The bootstrap function for the Ossa Cognitive Organism.
    """
    print("""
    ========================================
    |           OSSA COGNITIVE SYSTEM      |
    |          Status: Initializing...     |
    ========================================
    """)

    # 1. Initialize the Heartbeat (Operating Loop)
    life_cycle = OperatingLoop()

    # 2. Start the heartbeat in a separate background thread.
    # This allows Ossa to 'breathe' and 'think' while the main 
    # thread waits for your input.
    heartbeat_thread = threading.Thread(target=life_cycle.start, daemon=True)
    heartbeat_thread.start()

    print("[SYSTEM] Ossa is running in background thread.")
    print("[SYSTEM] Type 'exit' to shut down or 'status' for diagnostics.\n")

    # 3. Perception Input Loop (The 'Primary Sensor')
    try:
        while True:
            user_input = input(">> ")
            
            if user_input.lower() == 'exit':
                life_cycle.stop()
                break
            
            if user_input.lower() == 'status':
                # Quick diagnostic check of current state
                state = executive_function.state.get_context_snapshot()
                print(f"[DIAGNOSTIC] Current State: {state}")
                continue

            # Send raw input to the Brain Controller's pulse
            response = executive_function.pulse(user_input)
            print(f"\n{response}\n")

    except KeyboardInterrupt:
        life_cycle.stop()
        sys.exit()

if __name__ == "__main__":
    start_ossa()
