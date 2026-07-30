class PhysicsEngine:
    def __init__(self, environment):
        self.env = environment

    def apply_action(self, agent, action):
        x, y = agent.position

        if action == "UP":
            y -= 1
        elif action == "DOWN":
            y += 1
        elif action == "LEFT":
            x -= 1
        elif action == "RIGHT":
            x += 1

        x = max(0, min(self.env.size - 1, x))
        y = max(0, min(self.env.size - 1, y))

        agent.position = (x, y)

        # взаимодействие с ресурсом
        if agent.position in self.env.resources:
            agent.energy += 10
            self.env.remove_resource(agent.position)
