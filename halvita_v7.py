import random
import numpy as np
from collections import defaultdict, deque

# =========================
# ENVIRONMENT
# =========================

class World:
    def __init__(self, size=6):
        self.size = size
        self.reset()

    def reset(self):
        self.agent_pos = [0, 0]
        self.food = [self.size-1, self.size-1]
        self.enemy = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
        self.energy = 10
        return self.get_state()

    def get_state(self):
        return (
            self.agent_pos[0],
            self.agent_pos[1],
            self.food[0],
            self.food[1],
            self.enemy[0],
            self.enemy[1],
            self.energy
        )

    def step(self, action):
        reward = -0.1

        # movement
        if action == 0: self.agent_pos[0] = max(0, self.agent_pos[0]-1)  # up
        if action == 1: self.agent_pos[0] = min(self.size-1, self.agent_pos[0]+1)  # down
        if action == 2: self.agent_pos[1] = max(0, self.agent_pos[1]-1)  # left
        if action == 3: self.agent_pos[1] = min(self.size-1, self.agent_pos[1]+1)  # right
        if action == 4: pass  # stay

        self.energy -= 1

        # rewards
        if self.agent_pos == self.food:
            reward += 10
            self.food = [random.randint(0, self.size-1), random.randint(0, self.size-1)]

        if self.agent_pos == self.enemy:
            reward -= 10

        if self.energy <= 0:
            reward -= 5

        done = self.energy <= 0
        return self.get_state(), reward, done

# =========================
# MEMORY
# =========================

class Memory:
    def __init__(self):
        self.short_term = deque(maxlen=50)
        self.long_term = defaultdict(int)

    def store(self, state, action, reward):
        self.short_term.append((state, action, reward))

        key = (state, action)
        self.long_term[key] += reward

    def get_bias(self, state, action):
        return self.long_term[(state, action)] * 0.01

# =========================
# AGENT
# =========================

class Agent:
    def __init__(self):
        self.q = defaultdict(lambda: np.zeros(5))
        self.epsilon = 1.0
        self.lr = 0.1
        self.gamma = 0.95
        self.memory = Memory()

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 4)

        values = self.q[state].copy()

        # add memory bias
        for a in range(5):
            values[a] += self.memory.get_bias(state, a)

        return np.argmax(values)

    def learn(self, state, action, reward, next_state):
        best_next = np.max(self.q[next_state])

        self.q[state][action] += self.lr * (
            reward + self.gamma * best_next - self.q[state][action]
        )

        self.memory.store(state, action, reward)

    def decay(self):
        self.epsilon = max(0.05, self.epsilon * 0.995)

# =========================
# TRAIN LOOP
# =========================

def train(episodes=500):
    env = World()
    agent = Agent()

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0

        while True:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)

            agent.learn(state, action, reward, next_state)

            state = next_state
            total_reward += reward

            if done:
                break

        agent.decay()

        if ep % 50 == 0:
            print(f"Episode {ep}, reward: {total_reward:.2f}, epsilon: {agent.epsilon:.2f}")

    return agent

# =========================
# VISUALIZATION (simple)
# =========================

def render(env):
    grid = [["." for _ in range(env.size)] for _ in range(env.size)]

    x, y = env.agent_pos
    grid[x][y] = "A"

    fx, fy = env.food
    grid[fx][fy] = "F"

    ex, ey = env.enemy
    grid[ex][ey] = "E"

    for row in grid:
        print(" ".join(row))
    print()

# =========================
# RUN
# =========================

def run_trained(agent, steps=20):
    env = World()
    state = env.reset()

    for _ in range(steps):
        render(env)
        action = np.argmax(agent.q[state])
        state, _, done = env.step(action)
        if done:
            break

if __name__ == "__main__":
    agent = train()
    print("\n=== RUN TRAINED AGENT ===\n")
    run_trained(agent)
