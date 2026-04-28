class ValueSystem:
    """
    Ossa's Moral and Safety Guardrails.
    """
    def is_command_safe(self, command: str):
        # A list of forbidden 'Self-Harm' or 'Destructive' commands
        forbidden = ["rm -rf", "format", ":(){ :|:& };:", "del /s", "> /dev/sda"]
        
        for term in forbidden:
            if term in command.lower():
                print(f"[ETHICS] VETO: Command '{command}' blocked for safety.")
                return False
        return True

# Global instance
ethics = ValueSystem()
