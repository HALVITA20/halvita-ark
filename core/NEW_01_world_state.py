class WorldState:
    def __init__(self, environment):
        self.environment = environment

    def observe(self, agent):
        return {
            "agent_position": agent.position,
            "resources": self.environment.resources
        }
