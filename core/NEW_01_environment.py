import random

class Environment:
    def __init__(self, size=10):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.resources = []
        self._spawn_resources()

    def _spawn_resources(self):
        for _ in range(10):
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            self.resources.append((x, y))

    def get_state(self):
        return {
            "resources": self.resources
        }

    def remove_resource(self, pos):
        if pos in self.resources:
            self.resources.remove(pos)
