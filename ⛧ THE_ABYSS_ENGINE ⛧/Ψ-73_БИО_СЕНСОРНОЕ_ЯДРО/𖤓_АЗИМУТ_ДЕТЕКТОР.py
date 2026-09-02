"""
𖤓 АЗИМУТ-ДЕТЕКТОР — спайковая нейросеть для определения угла источника звука

Вдохновлено: эхолокационными цепями подковоносой летучей мыши.
"""

import torch
import torch.nn as nn
import numpy as np
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpikingNeuron(nn.Module):
    """Модель спайкового нейрона (Leaky Integrate-and-Fire)."""
    def __init__(self, tau: float = 10.0, threshold: float = 1.0, dt: float = 1.0):
        super().__init__()
        self.tau = tau
        self.threshold = threshold
        self.dt = dt
        self.membrane_potential = 0.0
        self.spike_count = 0

    def forward(self, input_current: float):
        dV = (-self.membrane_potential + input_current) * self.dt / self.tau
        self.membrane_potential += dV

        spike = False
        if self.membrane_potential >= self.threshold:
            spike = True
            self.spike_count += 1
            self.membrane_potential = 0.0

        return self.membrane_potential, spike

    def reset(self):
        self.membrane_potential = 0.0
        self.spike_count = 0


class AzimuthDetector(nn.Module):
    """Детектор азимута на основе спайковой нейронной сети."""
    def __init__(self, num_neurons: int = 64, num_angles: int = 180):
        super().__init__()
        self.num_neurons = num_neurons
        self.num_angles = num_angles

        self.neurons = nn.ModuleList([SpikingNeuron() for _ in range(num_neurons)])
        self.output_layer = nn.Sequential(
            nn.Linear(num_neurons, 64),
            nn.ReLU(),
            nn.Linear(64, num_angles)
        )

    def forward(self, left_signal: torch.Tensor, right_signal: torch.Tensor) -> torch.Tensor:
        batch_size = left_signal.size(0)

        for neuron in self.neurons:
            neuron.reset()

        spike_rates = torch.zeros(batch_size, self.num_neurons)

        for b in range(batch_size):
            for t in range(min(left_signal.size(1), right_signal.size(1))):
                diff = left_signal[b, t] - right_signal[b, t]

                for i, neuron in enumerate(self.neurons):
                    input_current = diff.item() * 0.1
                    _, spike = neuron(input_current)
                    if spike:
                        spike_rates[b, i] += 1

        spike_rates = spike_rates / max(1, left_signal.size(1))
        angle_logits = self.output_layer(spike_rates)
        angle_probs = torch.softmax(angle_logits, dim=-1)

        return angle_probs

    def predict_azimuth(self, left_signal: torch.Tensor, right_signal: torch.Tensor) -> float:
        with torch.no_grad():
            probs = self.forward(left_signal, right_signal)
            angle_idx = torch.argmax(probs, dim=-1)
            azimuth = angle_idx.float() / self.num_angles * 180
        return azimuth.item()


def generate_test_signals(angle: float, num_samples: int = 1000):
    v = 343
    d = 0.1
    delay = (d / v) * np.sin(np.radians(angle))

    t = np.linspace(0, 0.01, num_samples)
    pulse = np.exp(-((t - 0.005) ** 2) / (0.0005 ** 2))

    left_signal = pulse
    right_signal = np.roll(pulse, int(delay * num_samples / 0.01))

    return torch.FloatTensor(left_signal).unsqueeze(0), torch.FloatTensor(right_signal).unsqueeze(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--angles", type=str, default="0,30,60")
    args = parser.parse_args()

    detector = AzimuthDetector()
    angles = [int(a) for a in args.angles.split(',')]

    for angle in angles:
        left, right = generate_test_signals(angle)
        predicted = detector.predict_azimuth(left, right)
        logger.info(f"True: {angle}°, Predicted: {predicted:.1f}°, Error: {abs(angle - predicted):.1f}°")


if __name__ == "__main__":
    main()
