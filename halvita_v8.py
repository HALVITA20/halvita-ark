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
        self.agent = [0, 0]
        self.food = [self.size-1, self.size-1]
        self.enemy = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
        self.energy = 12
        return self.state()

    def state(self):
        return (
            self.agent[0], self.agent[1],
            self.food[0], self.food[1],
            self.enemy[0], self.enemy[1],
            self.energy
        )

    def step(self, action):
        reward = -0.1

        moves = [
            (-1,0),(1,0),(0,-1),(0,1),(0,0)
        ]

        dx, dy = moves[action]
        self.agent[0] = max(0, min(self.size-1, self.agent[0] + dx))
        self.agent[1] = max(0, min(self.size-1, self.agent[1] + dy))

        self.energy -= 1

        if self.agent == self.food:
            reward += 10
            self.food = [random.randint(0,self.size-1), random.randint(0,self.size-1)]

        if self.agent == self.enemy:
            reward -= 10

        if self.energy <= 0:
            reward -= 5

        done = self.energy <= 0
        return self.state(), reward, done

# =========================
# MEMORY
# =========================

class Memory:
    def __init__(self):
        self.short = deque(maxlen=100)
        self.long = defaultdict(float)

    def store(self, s, a, r):
        self.short.append((s,a,r))
        self.long[(s,a)] += r

    def bias(self, s, a):
        return self.long[(s,a)] * 0.01

# =========================
# WORLD MODEL
# =========================

class WorldModel:
    def __init__(self):
        self.model = {}

    def update(self, state, action, next_state):
        self.model[(state, action)] = next_state

    def predict(self, state, action):
        return self.model.get((state, action), state)

# =========================
# AGENT
# =========================

class Agent:
    def __init__(self):
        self.q = defaultdict(lambda: np.zeros(5))
        self.eps = 1.0
        self.lr = 0.1
        self.gamma = 0.95

        self.memory = Memory()
        self.world_model = WorldModel()

    def choose_action(self, state):
        if random.random() < self.eps:
            return random.randint(0,4)

        values = self.q[state].copy()

        # MEMORY BIAS
        for a in range(5):
            values[a] += self.memory.bias(state,a)

        # PLANNING (1-step lookahead)
        for a in range(5):
            predicted = self.world_model.predict(state, a)
            values[a] += np.max(self.q[predicted]) * 0.5

        return np.argmax(values)

    def learn(self, s, a, r, ns):
        best_next = np.max(self.q[ns])

        self.q[s][a] += self.lr * (
            r + self.gamma * best_next - self.q[s][a]
        )

        self.memory.store(s,a,r)
        self.world_model.update(s,a,ns)

    def decay(self):
        self.eps = max(0.05, self.eps * 0.995)

# =========================
# GOAL SYSTEM
# =========================

def intrinsic_reward(state):
    ax, ay, fx, fy, ex, ey, energy = state

    dist_food = abs(ax-fx) + abs(ay-fy)
    dist_enemy = abs(ax-ex) + abs(ay-ey)

    reward = 0

    # стремление к еде
    reward += 1 / (dist_food + 1)

    # избегание врага
    reward += dist_enemy * 0.1

    # экономия энергии
    reward += energy * 0.05

    return reward

# =========================
# TRAIN
# =========================

def train(episodes=600):
    env = World()
    agent = Agent()

    for ep in range(episodes):
        s = env.reset()
        total = 0

        while True:
            a = agent.choose_action(s)
            ns, r, done = env.step(a)

            # добавляем внутреннюю мотивацию
            r += intrinsic_reward(ns)

            agent.learn(s,a,r,ns)

            s = ns
            total += r

            if done:
                break

        agent.decay()

        if ep % 50 == 0:
            print(f"EP {ep} | reward {round(total,2)} | eps {round(agent.eps,2)}")

    return agent

# =========================
# RUN
# =========================

def run(agent):
    env = World()
    s = env.reset()

    for _ in range(30):
        a = agent.choose_action(s)
        s, r, done = env.step(a)

        print("STATE:", s, "ACTION:", a, "R:", round(r,2))

        if done:
            break

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    agent = train()
    run(agent)
