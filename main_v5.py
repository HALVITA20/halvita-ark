import matplotlib.pyplot as plt
from core.NEW_01_environment import Environment
from core.NEW_01_physics import PhysicsEngine
from core.NEW_01_world_state import WorldState
from core.agent_v5 import Agent
from visual.NEW_01_visualizer import Visualizer

def run():
    env = Environment(size=10)
    physics = PhysicsEngine(env)
    world = WorldState(env)
    agent = Agent()
    vis = Visualizer(env)

    plt.ion()

    for step in range(200):
        state = world.observe(agent)
        action = agent.decide(state)

        physics.apply_action(agent, action)
        vis.render(agent)

        agent.energy -= 0.1

        if agent.energy <= 0:
            print("Agent died")
            break

if __name__ == "__main__":
    run()
