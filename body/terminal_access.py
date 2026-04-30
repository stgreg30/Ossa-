import subprocess
import logging

class MotorCortex:
    """Executes shell commands (use with caution)."""
    def __init__(self, allowed_commands=None):
        # Optionally restrict commands
        self.allowed = allowed_commands
        self.logger = logging.getLogger("MotorCortex")

    def execute(self, command: str, timeout=10) -> str:
        """Run a shell command and return stdout/stderr."""
        if self.allowed and command.split()[0] not in self.allowed:
            return f"Command '{command.split()[0]}' not allowed."
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout + result.stderr
            self.logger.info(f"Executed: {command} -> {output[:100]}")
            return output or "Command executed with no output."
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Execution error: {str(e)}"