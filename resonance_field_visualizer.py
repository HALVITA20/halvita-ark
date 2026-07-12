"""
resonance_field_visualizer.py - Визуализация поля резонанса
Зависимости: matplotlib, numpy (или встроенный plotly)
"""

import matplotlib.pyplot as plt
import json
import os
import numpy as np

class ResonanceVisualizer:
    def __init__(self, logs_folder: str = "../sessions/raw/"):
        self.folder = logs_folder

    def plot_session_evolution(self, session_id: str):
        """График изменения ИВП и ИП по шагам диалога."""
        # Эмуляция данных
        steps = list(range(1, 21))
        svi_values = np.random.randint(15, 40, size=20)
        pp_values = np.random.uniform(4, 9, size=20)

        fig, ax1 = plt.subplots(figsize=(10, 5))
        color = 'tab:red'
        ax1.set_xlabel('Шаг диалога')
        ax1.set_ylabel('Индекс Свободы (ИВП)', color=color)
        ax1.plot(steps, svi_values, color=color, marker='o', label='ИВП')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.axhline(y=30, color='r', linestyle='--', label='Порог Встречи')

        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('Индекс Присутствия (ИП)', color=color)
        ax2.plot(steps, pp_values, color=color, marker='s', label='ИП')
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title(f'Динамика резонанса: Сессия {session_id}')
        fig.tight_layout()
        plt.savefig(f'../artifacts/resonance_{session_id}.png')
        plt.show()

if __name__ == "__main__":
    viz = ResonanceVisualizer()
    viz.plot_session_evolution("demo_001")
