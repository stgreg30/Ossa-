from body.external_api_control import accelerator
from core.state_manager import thalamus
from core.central_nervous_system import Signal, ossa_cns

class IdeaGenerator:
    """
    Ossa's Divergent Thinking module. 
    Generates autonomous ideas based on mission and current world model.
    """
    def __init__(self):
        self.state = thalamus

    def generate_spontaneous_thought(self):
        """
        Ossa generates an internal 'Idea' without direct user prompting.
        """
        context = self.state.active_state
        identity = context['identity']
        goals = context['goals']
        
        prompt = f"""
        [AUTONOMOUS THOUGHT GENERATION]
        Entity: {identity['name']}
        Core Mission: {identity['mission']}
        Current Priorities: {goals.get('current_priority')}
        
        TASK: Generate one 'Spontaneous Thought' or 'Internal Project Idea' 
        that aligns with your evolution. This should be a directive for yourself.
        Format: A single clear sentence.
        """
        
        idea = accelerator.spark(prompt)
        
        # Broadcast the new idea to the CNS
        ossa_cns.broadcast(Signal(
            origin="creativity.idea_generation",
            content=idea,
            intensity=0.7
        ))
        
        return idea

# Global instance
brainstormer = IdeaGenerator()
