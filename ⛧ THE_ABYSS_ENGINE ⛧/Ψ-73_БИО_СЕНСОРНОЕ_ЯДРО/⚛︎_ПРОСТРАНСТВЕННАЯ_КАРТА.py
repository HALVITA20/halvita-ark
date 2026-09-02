"""
⚛︎ ПРОСТРАНСТВЕННАЯ КАРТА — построение 3D-карты по эхо-сигналам

Вдохновлено: пространственной навигацией косаток.
"""

import torch
import torch.nn as nn
import numpy as np
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpatialMap(nn.Module):
    """Пространственная карта на основе эхо-сигналов."""
    def __init__(self, grid_size: tuple = (32, 32, 32), resolution: float = 0.1):
        super().__init__()
        self.grid_size = grid_size
        self.resolution = resolution

        self.register_buffer('occupancy_grid', torch.zeros(grid_size))
        self.register_buffer('confidence_grid', torch.zeros(grid_size))

        self.update_network = nn.Sequential(
            nn.Conv3d(2, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv3d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv3d(32, 2, kernel_size=3, padding=1),
            nn.Sigmoid()
        )

    def world_to_grid(self, position):
        x = int((position[0] / self.resolution) + self.grid_size[0] / 2)
        y = int((position[1] / self.resolution) + self.grid_size[1] / 2)
        z = int((position[2] / self.resolution) + self.grid_size[2] / 2)
        return np.clip(x, 0, self.grid_size[0]-1), np.clip(y, 0, self.grid_size[1]-1), np.clip(z, 0, self.grid_size[2]-1)

    def add_echo(self, origin, direction, distance, confidence=1.0):
        origin_grid = self.world_to_grid(origin)
        end_point = (
            origin[0] + direction[0] * distance,
            origin[1] + direction[1] * distance,
            origin[2] + direction[2] * distance
        )
        end_grid = self.world_to_grid(end_point)

        self.occupancy_grid[end_grid[0], end_grid[1], end_grid[2]] = 1.0
        self.confidence_grid[end_grid[0], end_grid[1], end_grid[2]] = \
            torch.clamp(self.confidence_grid[end_grid[0], end_grid[1], end_grid[2]] + confidence, 0, 1)

    def update(self):
        input_tensor = torch.stack([self.occupancy_grid, self.confidence_grid], dim=0).unsqueeze(0)
        with torch.no_grad():
            output = self.update_network(input_tensor)

        self.occupancy_grid = output[0, 0]
        self.confidence_grid = output[0, 1]

    def get_occupancy(self):
        return self.occupancy_grid


class EcholocationNavigator:
    """Навигатор с эхолокацией."""
    def __init__(self):
        self.spatial_map = SpatialMap()
        self.position = np.zeros(3)

    def navigate(self, target, steps=30):
        target = np.array(target)

        for step in range(steps):
            to_target = target - self.position
            if np.linalg.norm(to_target) < 0.1:
                logger.info(f"Reached target at step {step}")
                break

            self.heading = to_target / np.linalg.norm(to_target)
            step_size = min(0.1, np.linalg.norm(to_target))
            self.position += self.heading * step_size

            logger.debug(f"Step {step}: position={self.position}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--position", type=str, default="0,0,0")
    args = parser.parse_args()

    navigator = EcholocationNavigator()
    pos = [float(p) for p in args.position.split(',')]
    navigator.position = np.array(pos)

    test_echoes = [
        ((0, 0, 0), (1, 0.5, 0), 2.0),
        ((0, 0, 0), (0.5, 1, 0.5), 1.5),
    ]

    for origin, direction, distance in test_echoes:
        navigator.spatial_map.add_echo(origin, direction, distance, confidence=0.8)

    navigator.spatial_map.update()
    occupancy = navigator.spatial_map.get_occupancy()
    logger.info(f"Occupied cells: {torch.sum(occupancy > 0.5).item()}")

    navigator.navigate((2.0, 1.0, 0.5))


if __name__ == "__main__":
    main()
