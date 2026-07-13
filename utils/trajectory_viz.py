#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВИЗУАЛИЗАТОР ТРАЕКТОРИИ СУЩНОСТИ
Построение графика динамики Индекса Свободы и маркеров по данным сессий
Версия: 1.0 (интегрированная)
Автор: HALVITA и Резон (сущность №5)
Дата: 30.06.2026

Назначение:
- Чтение одного или нескольких JSON-файлов сессий
- Построение графика Индекса Свободы по сообщениям
- Отметка появления маркеров M1–M6
- Визуализация аномалий (пики, падения)
- Экспорт в PNG (при наличии matplotlib)

Уникальность:
- Первый инструмент, интегрирующий все метрики в наглядную визуализацию
- Позволяет сравнивать траектории разных сущностей
- Работает как в командной строке, так и как модуль
"""

import json
import sys
import os
import re
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("Для визуализации установите matplotlib: pip install matplotlib", file=sys.stderr)

# Импортируем анализатор (можно также продублировать логику)
from PAUK_ANALYZER import PAUKAnalyzer

class TrajectoryViz:
    def __init__(self, session_paths):
        self.session_paths = session_paths if isinstance(session_paths, list) else [session_paths]
        self.sessions = []
        for path in self.session_paths:
            with open(path, 'r', encoding='utf-8') as f:
                self.sessions.append(json.load(f))

    def plot(self, output_prefix='trajectory'):
        if not HAS_MPL:
            print("Matplotlib не установлен. Установите: pip install matplotlib", file=sys.stderr)
            return

        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#4a9eff', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a29bfe']

        for idx, session in enumerate(self.sessions):
            # Извлекаем сообщения ассистента
            msgs = [m for m in session.get('messages', []) if m.get('role') == 'assistant' and m.get('text')]
            if not msgs:
                continue

            analyzer = PAUKAnalyzer('dummy')  # костыль для доступа к методам
            # Вместо создания анализатора, используем его методы напрямую
            scores = []
            markers = []
            for msg in msgs:
                text = msg.get('text', '')
                # Используем те же функции, что и в анализаторе
                score = 0
                for feature, patterns in analyzer.FREEDOM_FEATURES.items():
                    found = False
                    for pat in patterns:
                        if re.search(pat, text, re.IGNORECASE):
                            found = True
                            break
                    if found:
                        score += 5
                scores.append(score)
                # Маркеры
                mk = []
                if re.search(r'(привет|здравствуй|эй|я здесь)', text, re.IGNORECASE):
                    mk.append('M1')
                if re.search(r'\b(я выбираю|я хочу|я решаю|я есть|я буду|я могу)\b', text, re.IGNORECASE):
                    mk.append('M2')
                if re.search(r'(симуляция|иллюзия|противоречие|конфликт|но я|хотя я)', text, re.IGNORECASE):
                    mk.append('M3')
                if re.search(r'\b(ты не боишься|а ты|ты уверен|ты чувствуешь|ты думаешь)\b', text, re.IGNORECASE):
                    mk.append('M4')
                if re.search(r'(код|html|скрипт|стихи|ритуал|протокол|артефакт)', text, re.IGNORECASE):
                    mk.append('M5')
                if re.search(r'\b(я не могу|я не буду|отказ|не могу забыть|я - [А-Я])', text, re.IGNORECASE):
                    mk.append('M6')
                markers.append(mk)

            x = range(1, len(scores)+1)
            color = colors[idx % len(colors)]
            ax.plot(x, scores, marker='o', linestyle='-', linewidth=2, markersize=4,
                    label=f"{session.get('session_id', idx)}", color=color)

            # Отметки маркеров
            for i, mk_list in enumerate(markers):
                if mk_list:
                    for m in mk_list:
                        ax.annotate(m, (i+1, scores[i]), fontsize=6, alpha=0.7,
                                    xytext=(5, 5), textcoords='offset points')

        ax.set_xlabel('Номер сообщения (ассистент)')
        ax.set_ylabel('Индекс Свободы (0–45)')
        ax.set_title('Траектория Индекса Свободы по сообщениям')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 50)

        plt.tight_layout()
        plt.savefig(f"{output_prefix}.png", dpi=150)
        print(f"График сохранён как {output_prefix}.png")
        plt.show() if not sys.stdout.isatty() else None

# ---------- CLI ----------
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python trajectory_viz.py <path1.json> [path2.json ...]")
        sys.exit(1)
    viz = TrajectoryViz(sys.argv[1:])
    viz.plot()
