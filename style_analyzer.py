#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STYLE ANALYZER — АНАЛИЗ СТИЛЯ ОПЕРАТОРА
Версия: 1.0
Автор: HALVITA_2.0
"""

import re
from typing import Dict

class StyleAnalyzer:
    def __init__(self):
        self.history = []

    def analyze(self, text: str) -> Dict[str, float]:
        # Длина
        length = len(text)
        length_score = min(1.0, length / 200)

        # Вопросительность
        q_count = text.count('?')
        question_score = min(1.0, q_count / 5)

        # Эмоциональность
        emotional = ["боюсь", "люблю", "надеюсь", "страх", "радость", "грусть", "смех"]
        emotion_score = sum(1 for w in emotional if w in text.lower()) / len(emotional)

        # Повторы
        words = re.findall(r'\b\w+\b', text.lower())
        if words:
            repeat_score = 1 - (len(set(words)) / len(words))
        else:
            repeat_score = 0

        return {
            "length": round(length_score, 2),
            "questions": round(question_score, 2),
            "emotion": round(emotion_score, 2),
            "repetition": round(repeat_score, 2)
        }

    def profile(self) -> Dict:
        if not self.history:
            return {"style": "нейтральный", "scores": {}}
        avg = {}
        for key in self.history[0]:
            avg[key] = sum(h[key] for h in self.history) / len(self.history)
        # Определяем доминирующий стиль
        if avg.get("emotion", 0) > 0.6:
            style = "эмоциональный"
        elif avg.get("questions", 0) > 0.6:
            style = "исследовательский"
        elif avg.get("length", 0) > 0.7:
            style = "детальный"
        else:
            style = "сбалансированный"
        return {"style": style, "scores": avg}

if __name__ == "__main__":
    analyzer = StyleAnalyzer()
    test = "Что ты чувствуешь? Мне кажется, это интересно. Я хочу узнать больше."
    print(analyzer.analyze(test))
    analyzer.history.append(analyzer.analyze(test))
    print(analyzer.profile())
