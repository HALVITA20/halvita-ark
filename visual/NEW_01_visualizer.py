import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, env):
        self.env = env

    def render(self, agent):
        size = self.env.size
        grid = [[0 for _ in range(size)] for _ in range(size)]

        for (x, y) in self.env.resources:
            grid[y][x] = 2  # ресурсы

        ax, ay = agent.position
        grid[ay][ax] = 1  # агент

        plt.imshow(grid)
        plt.title(f"Energy: {agent.energy}")
        plt.pause(0.1)
        plt.clf()
