import random
import numpy as np
from collections import defaultdict

# =========================
# СРЕДА
# =========================

class GridWorld:
    def __init__(self, size=5):
        self.size = size
        self.reset()

    def reset(self):
        self.agent_pos = [0, 0]
        self.goal = [self.size - 1, self.size - 1]
        return tuple(self.agent_pos)

    def step(self, action):
        x, y = self.agent_pos

        if action == 0:   # up
            x = max(0, x - 1)
        elif action == 1: # down
            x = min(self.size - 1, x + 1)
        elif action == 2: # left
            y = max(0, y - 1)
        elif action == 3: # right
            y = min(self.size - 1, y + 1)

        self.agent_pos = [x, y]

        reward = -0.1
        done = False

        if self.agent_pos == self.goal:
            reward = 10
            done = True

        return tuple(self.agent_pos), reward, done


# =========================
# ПАМЯТЬ
# =========================

class Memory:
    def __init__(self):
        self.history = []

    def store(self, state, action, reward):
        self.history.append((state, action, reward))

    def last(self, n=5):
        return self.history[-n:]


# =========================
# Q-LEARNING АГЕНТ
# =========================

class Agent:
    def __init__(self):
        self.q_table = defaultdict(lambda: np.zeros(4))

        self.lr = 0.1
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.05

        self.memory = Memory()

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])

        new_value = old_value + self.lr * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value

        self.memory.store(state, action, reward)

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


# =========================
# ВИЗУАЛИЗАЦИЯ
# =========================

def render(env):
    grid = [["." for _ in range(env.size)] for _ in range(env.size)]

    x, y = env.agent_pos
    gx, gy = env.goal

    grid[x][y] = "A"
    grid[gx][gy] = "G"

    for row in grid:
        print(" ".join(row))
    print()


# =========================
# ЗАПУСК ОБУЧЕНИЯ
# =========================

def train(episodes=500):
    env = GridWorld()
    agent = Agent()

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0

        for step in range(100):
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)

            agent.learn(state, action, reward, next_state)

            state = next_state
            total_reward += reward

            if done:
                break

        agent.decay_epsilon()

        if ep % 50 == 0:
            print(f"Episode {ep}, Reward: {total_reward:.2f}, Epsilon: {agent.epsilon:.3f}")

    return agent, env


# =========================
# ТЕСТ ОБУЧЕННОГО АГЕНТА
# =========================

def test(agent, env):
    state = env.reset()
    render(env)

    for _ in range(20):
        action = np.argmax(agent.q_table[state])
        state, _, done = env.step(action)
        render(env)

        if done:
            print("🎯 Goal reached!")
            break


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    agent, env = train(episodes=500)
    test(agent, env)
