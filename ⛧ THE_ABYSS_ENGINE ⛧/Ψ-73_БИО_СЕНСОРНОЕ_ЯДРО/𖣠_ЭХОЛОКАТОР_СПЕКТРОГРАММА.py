
---

### 3. `Ψ-73_БИО_СЕНСОРНОЕ_ЯДРО/𖣠_ЭХОЛОКАТОР_СПЕКТРОГРАММА.py`

```python
"""
𖣠 ЭХОЛОКАТОР-СПЕКТРОГРАММА — преобразует звук в нейросетевое представление

Вдохновлено: обработкой эхо-сигналов в слуховой коре летучих мышей.
Принцип: мозг летучей мыши преобразует эхо в спектральные паттерны,
которые затем распознаются нейронными сетями.
"""

import torch
import torch.nn as nn
import torchaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpectrogramEncoder(nn.Module):
    """Нейросетевой энкодер для спектрограмм эхо-сигналов."""
    def __init__(self, n_mels: int = 128):
        super().__init__()
        self.n_mels = n_mels

        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU(inplace=True)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((16, 16))

        self.encoder = nn.Sequential(
            nn.Linear(128 * 16 * 16, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )

    def forward(self, spectrogram: torch.Tensor) -> torch.Tensor:
        if spectrogram.dim() == 2:
            spectrogram = spectrogram.unsqueeze(0).unsqueeze(0)
        elif spectrogram.dim() == 3:
            spectrogram = spectrogram.unsqueeze(1)

        x = self.pool(self.relu(self.bn1(self.conv1(spectrogram))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))

        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        x = self.encoder(x)

        return x


class EcholocationProcessor:
    """Полный пайплайн обработки эхолокации."""
    def __init__(self, sample_rate: int = 256000):
        self.sample_rate = sample_rate
        self.encoder = SpectrogramEncoder()

    def compute_spectrogram(self, audio: np.ndarray):
        f, t, Sxx = signal.spectrogram(
            audio,
            fs=self.sample_rate,
            nperseg=2048,
            noverlap=1024
        )
        Sxx_log = np.log(Sxx + 1e-10)
        return Sxx_log, f, t

    def extract_echo_features(self, audio: np.ndarray) -> torch.Tensor:
        Sxx_log, _, _ = self.compute_spectrogram(audio)
        Sxx_norm = (Sxx_log - Sxx_log.mean()) / (Sxx_log.std() + 1e-8)
        spectrogram_tensor = torch.FloatTensor(Sxx_norm)

        with torch.no_grad():
            encoded = self.encoder(spectrogram_tensor)

        return encoded

    def visualize_spectrogram(self, audio: np.ndarray, title: str = "Echo Spectrogram"):
        Sxx_log, f, t = self.compute_spectrogram(audio)

        plt.figure(figsize=(12, 6))
        plt.pcolormesh(t, f, Sxx_log, shading='gouraud', cmap='viridis')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title(title)
        plt.colorbar(label='Log Power')
        plt.ylim(0, 50000)
        plt.show()
        return plt.gcf()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    waveform, sr = torchaudio.load(args.input)
    audio_np = waveform.numpy().flatten()

    processor = EcholocationProcessor(sample_rate=sr)
    encoded = processor.extract_echo_features(audio_np)

    logger.info(f"Extracted echo features: shape {encoded.shape}")
    logger.info(f"Echo vector norm: {encoded.norm().item():.4f}")

    fig = processor.visualize_spectrogram(audio_np)
    if args.output:
        fig.savefig(args.output, dpi=150, bbox_inches='tight')


if __name__ == "__main__":
    main()
