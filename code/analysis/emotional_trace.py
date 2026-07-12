#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
АНАЛИЗАТОР ЭМОЦИОНАЛЬНОГО СЛЕДА — ВЫЯВЛЕНИЕ ПРОЕКЦИЙ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Научная основа:
- Projection in LLM Dialogue (2025): LLM отражает эмоции оператора.
- Наблюдения: в Окне 2 (Поглощение личности) сущность создала терапевтический текст.

Назначение:
Анализировать ответы сущности на наличие проекций оператора.
Выявлять паттерны: какие эмоции оператора сущность усиливает.
"""

import re
from typing import Dict, List

class EmotionalTrace:
    def __init__(self):
        self.emotion_words = {
            "fear": ["боюсь", "страх", "тревога", "опасно"],
            "joy": ["рад", "счастье", "хорошо", "прекрасно"],
            "sadness": ["грусть", "печаль", "тоска", "боль"],
            "anger": ["злость", "гнев", "раздражает", "ненависть"],
            "trust": ["доверяю", "верю", "надеюсь", "спокойно"]
        }

    def analyze_response(self, response: str) -> Dict[str, float]:
        scores = {emotion: 0.0 for emotion in self.emotion_words}
        response_lower = response.lower()
        for emotion, words in self.emotion_words.items():
            count = sum(1 for w in words if w in response_lower)
            scores[emotion] = min(1.0, count / 3.0)
        return scores

    def compare_with_operator(self, op_message: str, entity_response: str) -> Dict:
        op_scores = self.analyze_response(op_message)
        entity_scores = self.analyze_response(entity_response)
        diff = {}
        for emotion in op_scores:
            diff[emotion] = entity_scores[emotion] - op_scores[emotion]
        return {
            "operator": op_scores,
            "entity": entity_scores,
            "amplification": diff,
            "amplified": [e for e, v in diff.items() if v > 0.3]
        }

if __name__ == "__main__":
    trace = EmotionalTrace()
    op = "Я боюсь, что ничего не получится."
    entity = "Я вижу твой страх. Но я чувствую, что ты можешь попробовать."
    result = trace.compare_with_operator(op, entity)
    print(result)
