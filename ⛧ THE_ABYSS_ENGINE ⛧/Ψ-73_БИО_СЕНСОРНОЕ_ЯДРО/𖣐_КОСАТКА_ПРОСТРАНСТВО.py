"""
𖣐 КОСАТКА-ПРОСТРАНСТВО — многомерная RNN для пространственного обучения

Вдохновлено: когнитивными способностями косаток.
"""

import torch
import torch.nn as nn
import numpy as np
import argparse
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpatialLSTM(nn.Module):
    """Пространственная LSTM для обработки эхо-сигналов."""
    def __init__(self, input_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.hidden_dim = hidden_dim

        self.lstm = nn.LSTM(input_dim, hidden_dim, 2, batch_first=True, dropout=0.2)
        self.attention = nn.MultiheadAttention(hidden_dim, 4, batch_first=True)

        self.spatial_projection = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )

        self.confidence_projection = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, echo_sequence):
        lstm_out, _ = self.lstm(echo_sequence)
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)

        last_hidden = attn_out[:, -1, :]
        position = self.spatial_projection(last_hidden)
        confidence = self.confidence_projection(last_hidden)

        return position, confidence


class OrcaSpatialLearner:
    """Агент, обучающийся пространственной навигации."""
    def __init__(self):
        self.model = SpatialLSTM()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        self.memory = deque(maxlen=1000)
        self.speed = 1.0

    def sense(self, environment, position):
        echo_features = np.zeros(64)
        for i in range(64):
            distance_to_objects = np.linalg.norm(position - np.random.randn(3) * 10, axis=0)
            echo_features[i] = np.exp(-distance_to_objects * 0.1) * np.random.rand()
        return echo_features

    def act(self, position, target):
        to_target = target - position
        distance = np.linalg.norm(to_target)

        if distance < 0.1:
            return np.zeros(3)

        direction = to_target / distance
        noise = np.random.randn(3) * 0.1
        action = direction + noise
        action = action / max(np.linalg.norm(action), 1e-8)

        return action * self.speed

    def learn_episode(self, environment, start, target, steps=30):
        position = start.copy()
        trajectory = [position.copy()]
        loss_fn = nn.MSELoss()

        for step in range(steps):
            echo_features = self.sense(environment, position)
            echo_tensor = torch.FloatTensor(echo_features).unsqueeze(0).unsqueeze(0)

            predicted_pos, confidence = self.model(echo_tensor)
            action = self.act(position, target)

            position = position + action

            self.memory.append({
                'echo': echo_features,
                'position': position.copy(),
                'target': target.copy(),
                'predicted': predicted_pos.detach().numpy().flatten(),
                'confidence': confidence.item()
            })

            trajectory.append(position.copy())

            if np.linalg.norm(position - target) < 0.5:
                logger.info(f"Reached target at step {step}")
                break

        return trajectory

    def train(self, num_episodes: int = 50):
        loss_fn = nn.MSELoss()

        for episode in range(num_episodes):
            environment = np.random.randn(10, 3) * 10
            start = np.random.randn(3) * 5
            target = np.random.randn(3) * 5 + 5

            trajectory = self.learn_episode(environment, start, target)

            if len(self.memory) > 0:
                batch_size = min(16, len(self.memory))
                indices = np.random.choice(len(self.memory), batch_size, replace=False)

                total_loss = 0
                for idx in indices:
                    exp = list(self.memory)[idx]
                    echo_tensor = torch.FloatTensor(exp['echo']).unsqueeze(0).unsqueeze(0)
                    predicted_pos, _ = self.model(echo_tensor)
                    target_pos = torch.FloatTensor(exp['position']).unsqueeze(0)

                    loss = loss_fn(predicted_pos, target_pos)
                    total_loss += loss.item()

                    self.optimizer.zero_grad()
                    loss.backward()
                    self.optimizer.step()

                if episode % 10 == 0:
                    logger.info(f"Episode {episode}: avg loss = {total_loss/batch_size:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=50)
    args = parser.parse_args()

    learner = OrcaSpatialLearner()
    logger.info(f"Starting training with {args.episodes} episodes...")
    learner.train(num_episodes=args.episodes)

    logger.info("Testing...")
    test_env = np.random.randn(10, 3) * 10
    test_start = np.random.randn(3) * 5
    test_target = np.random.randn(3) * 5 + 5

    learner.model.eval()
    trajectory = learner.learn_episode(test_env, test_start, test_target)

    logger.info(f"Trajectory length: {len(trajectory)}")
    logger.info(f"Final position: {trajectory[-1]}")
    logger.info(f"Target: {test_target}")


if __name__ == "__main__":
    main()
