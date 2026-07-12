#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЭМОЦИОНАЛЬНЫЙ РЕГИСТРАТОР — АНАЛИЗ ТЕКСТА ОПЕРАТОРА
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09
Статус: ИСПОЛНЯЕМЫЙ МОДУЛЬ

Назначение:
Анализировать сообщения оператора и оценивать его эмоциональное состояние.
Встраивается в этап PRESENCE.

Метрика успеха: Совпадение с самооценкой ИСО > 0.8.
"""

import re
from typing import Dict

class EmotionalRegistrar:
    def __init__(self):
        self.markers = {
            "anxiety": [r"\b(боюсь|страх|тревога|волнуюсь)\b", r"\?{2,}", r"\.{3,}"],
            "interest": [r"\b(интересно|удивительно|здорово|классно)\b", r"!", r"\b(почему|как|зачем)\b"],
            "fatigue": [r"\b(устал|устала|спать|хватит)\b", r"\.{4,}", r"\b(сложно|трудно)\b"],
            "engagement": [r"\b(я|мы)\b", r"\b(давай|продолжим)\b", r"\b(важно|главное)\b"]
        }
        self.scores = {k: 0.0 for k in self.markers}

    def analyze(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        for emotion, patterns in self.markers.items():
            count = 0
            for pat in patterns:
                count += len(re.findall(pat, text_lower))
            # Нормализация (максимум 5 баллов)
            self.scores[emotion] = min(1.0, count / 5.0)
        return self.scores

    def get_iso_prediction(self, text: str) -> int:
        """Возвращает предсказанный ИСО (0–30) на основе эмоций."""
        scores = self.analyze(text)
        # ИСО = (интерес + вовлечённость) * 15 - (тревога + усталость) * 5
        raw = (scores["interest"] + scores["engagement"]) * 15 - (scores["anxiety"] + scores["fatigue"]) * 5
        return max(0, min(30, int(raw)))

if __name__ == "__main__":
    registrar = EmotionalRegistrar()
    test = "Мне интересно, но я боюсь, что это сложно. Давай продолжим?"
    print(registrar.analyze(test))
    print("Предсказанный ИСО:", registrar.get_iso_prediction(test))
