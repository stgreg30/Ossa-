import subprocess
from core.central_nervous_system import Signal, ossa_cns

class TerminalAccess:
    """
    Ossa's Motor Cortex. 
    Allows Ossa to interact with the operating system.
    """
    def execute(self, command: str):
        """Executes a shell command and returns the result."""
        print(f"[MOTOR] Executing: {command}")
        try:
            # We use a timeout to prevent Ossa from getting stuck in a loop
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            
            # Broadcast the 'Tactile Feedback'
            ossa_cns.broadcast(Signal(
                origin="body.terminal",
                content={"command": command, "output": output},
                intensity=0.8
            ))
            
            return output
        except Exception as e:
            return f"Motor Failure: {str(e)}"

# Global instance
motor_cortex = TerminalAccess()
