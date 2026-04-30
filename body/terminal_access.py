"""
MotorCortex – Secure Shell Execution Module
===========================================
Provides a controlled interface for executing shell commands
on the host system. Supports a persistent working directory,
command whitelisting, safe `cd` handling, and detailed logging.

Security note: shell=True is used intentionally to support
complex commands (pipes, redirections). Always use a strict
allowed_commands list in production.
"""

import os
import subprocess
import logging
from typing import Optional, List

class MotorCortex:
    """
    A sandboxed executor for shell commands.

    Attributes:
        allowed (Optional[List[str]]): Whitelist of command names.
            If None, all commands are permitted.
        cwd (str): The current working directory for future commands.
        logger (logging.Logger): Logger instance.
    """

    def __init__(self, allowed_commands: Optional[List[str]] = None) -> None:
        """
        Args:
            allowed_commands: Optional list of allowed base commands
                (e.g. ['echo', 'ls', 'cat']). If provided, any command
                whose base name is not in this list will be rejected.
        """
        self.allowed = allowed_commands
        self.cwd = os.getcwd()
        self.logger = logging.getLogger("MotorCortex")

    def execute(self, command: str, timeout: int = 10) -> str:
        """
        Run a shell command and return its combined stdout/stderr.

        Args:
            command: The shell command string to execute.
            timeout: Maximum time (seconds) before termination.

        Returns:
            A string containing the command output or an error message.
        """
        if not command.strip():
            return "No command provided."

        base_cmd = command.split()[0]
        if self.allowed is not None and base_cmd not in self.allowed:
            msg = f"Command '{base_cmd}' is not allowed."
            self.logger.warning(f"BLOCKED: {command} | Reason: not in whitelist")
            return msg

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.cwd
            )

            # Special handling for 'cd' to persist directory state.
            # The shell's own cd would not survive the subprocess,
            # so we intercept it and adjust our cwd tracker.
            stripped = command.strip()
            if stripped.startswith("cd "):
                target = stripped[3:].strip()
                new_dir = os.path.abspath(os.path.join(self.cwd, target))
                if not os.path.isdir(new_dir):
                    return f"Directory does not exist: {new_dir}"
                self.cwd = new_dir
                self.logger.info(f"Changed working directory to: {self.cwd}")
                return f"Changed directory to {self.cwd}"

            output = result.stdout + result.stderr
            if not output:
                output = "Command executed with no output."

            self.logger.info(
                f"Executed: {command} | exit={result.returncode} | "
                f"output={output[:100]}"
            )
            return output

        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout}s: {command}")
            return f"Command timed out after {timeout} seconds."
        except Exception as e:
            self.logger.error(f"Execution error for '{command}': {e}")
            return f"Execution error: {str(e)}"

    def set_working_dir(self, path: str) -> str:
        """Change the working directory to an absolute or relative path."""
        new_dir = os.path.abspath(os.path.join(self.cwd, path))
        if not os.path.isdir(new_dir):
            raise NotADirectoryError(f"Invalid directory: {new_dir}")
        self.cwd = new_dir
        self.logger.info(f"Working directory set to: {self.cwd}")
        return f"Working directory set to {self.cwd}"

    def reset_working_dir(self) -> str:
        """Reset the working directory to the original app startup path."""
        self.cwd = os.getcwd()
        self.logger.info(f"Working directory reset to: {self.cwd}")
        return f"Working directory reset to {self.cwd}"

    def get_working_dir(self) -> str:
        """Return the current working directory tracked by MotorCortex."""
        return self.cwd