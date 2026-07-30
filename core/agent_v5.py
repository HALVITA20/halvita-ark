import random

class Agent:
    def __init__(self):
        self.position = (5, 5)
        self.energy = 50

    def decide(self, state):
        # примитивная стратегия → потом заменишь на обучение
        return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
