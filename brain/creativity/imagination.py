from body.external_api_control import accelerator
from core.state_manager import thalamus

def simulate_outcome(proposed_action: str):
    """
    Uses the Gemini Accelerator to 'dream' or 'predict' 
    what will happen if Ossa performs an action.
    """
    # Fetch Ossa's current state to provide context
    context = thalamus.get_context_snapshot()
    identity = context['who_i_am'].get('mission', 'Self-evolution')
    mood = context['how_i_feel'].get('mood', 'stable')

    simulation_prompt = f"""
    [SIMULATION PROTOCOL]
    ENTITY: Ossa
    CURRENT MOOD: {mood}
    GOAL: {identity}
    
    PROPOSED ACTION: {proposed_action}
    
    TASK: Predict the most likely response from the user and the 
    impact on Ossa's long-term goals. Be concise and logical.
    """

    # Request the spark
    prediction = accelerator.spark(simulation_prompt)
    return prediction
