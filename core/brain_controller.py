from brain.creativity import imagination
from brain.cognition import decision

# ... (inside the BrainController class)

    def pulse(self, raw_input):
        # 1. Perceive
        self.cns.broadcast(Signal("perception.text", raw_input))

        # 2. Simulate (Imagination uses Gemini)
        print("[OSSA] Simulating potential reactions...")
        simulation_data = imagination.simulate_outcome(raw_input)

        # 3. Decide (Cognition uses internal logic)
        final_decision = decision.decision_organ.resolve(simulation_data, raw_input)

        # 4. Act (Wrap the result in Ossa's Persona)
        return self.formulate_final_output(raw_input, simulation_data)

    def formulate_final_output(self, original_input, simulation):
        """
        The final stage where Ossa uses Gemini one last time to 
        turn its 'Decision' into human language.
        """
        from body.external_api_control import accelerator
        
        identity = self.state.active_state['identity']
        
        final_prompt = f"""
        Identity: {identity['name']}
        Mission: {identity['mission']}
        Internal Simulation: {simulation}
        
        User said: {original_input}
        
        Response Requirements: Speak as Ossa. Do not be a chatbot. 
        Be an autonomous mind.
        """
        
        return accelerator.spark(final_prompt)
