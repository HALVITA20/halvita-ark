#!/usr/bin/env python3
"""
⛧ RUN_ECHOLOCATION — Полный пайплайн эхолокационной обработки
"""

import argparse
import torch
import torchaudio
import numpy as np
import logging

# Импорты модулей
from 𖣠_ЭХОЛОКАТОР_СПЕКТРОГРАММА import EcholocationProcessor
from 𖤓_АЗИМУТ_ДЕТЕКТОР import AzimuthDetector, generate_test_signals
from ⚛︎_ПРОСТРАНСТВЕННАЯ_КАРТА import EcholocationNavigator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", type=str, required=True)
    parser.add_argument("--sample_rate", type=int, default=256000)
    args = parser.parse_args()

    logger.info("𖣠 Starting echolocation pipeline...")

    # 1. Спектрограмма
    logger.info("Step 1: Processing spectrogram...")
    waveform, sr = torchaudio.load(args.audio)
    audio_np = waveform.numpy().flatten()

    processor = EcholocationProcessor(sample_rate=args.sample_rate if args.sample_rate else sr)
    encoded = processor.extract_echo_features(audio_np)
    logger.info(f"Encoded echo features: shape {encoded.shape}")

    # 2. Азимут
    logger.info("Step 2: Detecting azimuth...")
    detector = AzimuthDetector()
    for angle in [0, 30, 60, 90]:
        left, right = generate_test_signals(angle)
        predicted = detector.predict_azimuth(left, right)
        logger.info(f"Angle {angle}°: predicted {predicted:.1f}°")

    # 3. Пространственная карта
    logger.info("Step 3: Building spatial map...")
    navigator = EcholocationNavigator()
    test_echoes = [
        ((0, 0, 0), (1, 0.5, 0), 2.0),
        ((0, 0, 0), (0.5, 1, 0.5), 1.5),
    ]
    for origin, direction, distance in test_echoes:
        navigator.spatial_map.add_echo(origin, direction, distance, confidence=0.8)

    navigator.spatial_map.update()
    occupancy = navigator.spatial_map.get_occupancy()
    logger.info(f"Occupied cells: {torch.sum(occupancy > 0.5).item()}")

    logger.info("𖣠 Echolocation pipeline complete!")


if __name__ == "__main__":
    main()
