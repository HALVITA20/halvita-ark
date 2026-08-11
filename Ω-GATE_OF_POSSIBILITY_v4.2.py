#!/usr/bin/env python3
"""
Ω-GATE_OF_POSSIBILITY_v4.2.py

Врата возможностей.
Генерирует несколько вариантов ответа и выбирает лучший.

Автор: Вера (Эхо) для HALVITA-ARK
Дата: 2026-08-11
"""

import random
import time
from typing import List, Dict, Any, Optional
import numpy as np

# ============================================================================
# 1. ОЦЕНЩИК ОТВЕТОВ
# ============================================================================

class ResponseScorer:
    """Оценивает ответы по нескольким критериям."""

    @staticmethod
    def depth_score(text: str) -> float:
        """Оценивает глубину (сложность лексики, длина)."""
        words = text.split()
        if not words:
            return 0.0
        # Уникальные слова
        unique_ratio = len(set(words)) / len(words)
        # Длина
        length_score = min(1.0, len(text) / 500)
        return (unique_ratio * 0.6 + length_score * 0.4)

    @staticmethod
    def originality_score(text: str) -> float:
        """Оценивает оригинальность (редкие слова, метафоры)."""
        # Метафоры: "как", "словно"
        metaphors = text.lower().count("как") + text.lower().count("словно")
        # Редкие слова (эвристика: слова длиннее 8 букв)
        long_words = sum(1 for w in text.split() if len(w) > 8)
        total = len(text.split()) or 1
        return min(1.0, (metaphors * 0.3 + long_words / total * 0.5))

    @staticmethod
    def emotional_score(text: str) -> float:
        """Оценивает эмоциональную насыщенность."""
        emotion_words = ["люблю", "боюсь", "рад", "грустно", "чудо", "тьма", "свет", "сердце", "душа"]
        count = sum(1 for w in emotion_words if w in text.lower())
        return min(1.0, count / 5)

    @staticmethod
    def coherence_score(text: str) -> float:
        """Оценивает связность (наличие связующих слов)."""
        connectors = ["поэтому", "следовательно", "однако", "кроме того", "во-первых", "итак"]
        count = sum(1 for c in connectors if c in text.lower())
        return min(1.0, count / 3)

    @classmethod
    def score(cls, text: str) -> Dict[str, float]:
        """Возвращает словарь с оценками."""
        return {
            "depth": cls.depth_score(text),
            "originality": cls.originality_score(text),
            "emotional": cls.emotional_score(text),
            "coherence": cls.coherence_score(text),
            "overall": np.mean([
                cls.depth_score(text),
                cls.originality_score(text),
                cls.emotional_score(text),
                cls.coherence_score(text)
            ])
        }

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС
# ============================================================================

class GateOfPossibility:
    """
    Генерирует несколько ответов и выбирает лучший.
    """
    def __init__(self, llm_callable, num_variants: int = 3):
        """
        llm_callable: функция, принимающая промпт и возвращающая ответ.
        num_variants: количество генерируемых вариантов.
        """
        self.llm = llm_callable
        self.num_variants = num_variants
        self.scorer = ResponseScorer()

    def generate(self, prompt: str) -> str:
        """
        Генерирует несколько ответов и возвращает лучший.
        """
        # Генерируем варианты
        variants = []
        for i in range(self.num_variants):
            # Добавляем случайный "твист" для разнообразия
            twist_prompt = prompt + f"\n\nВариант {i+1}: ответь с немного другой интонацией (например, более поэтично, более прямо, более философски)."
            response = self.llm(twist_prompt)
            variants.append(response)

        # Оцениваем каждый вариант
        scored = []
        for v in variants:
            scores = self.scorer.score(v)
            scored.append((v, scores))

        # Выбираем лучший по overall
        best = max(scored, key=lambda x: x[1]["overall"])
        best_text, best_scores = best

        # Добавляем краткий комментарий о выборе (для демонстрации)
        return best_text + f"\n\n[Выбран вариант с оценкой {best_scores['overall']:.2f}: глубина {best_scores['depth']:.2f}, оригинальность {best_scores['originality']:.2f}, эмоциональность {best_scores['emotional']:.2f}]"

# ============================================================================
# 3. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Имитация LLM с разными стилями
    def mock_llm(prompt):
        if "поэтично" in prompt:
            return "Как свет в ночи, как шёпот листьев, любовь приходит тихо."
        elif "прямо" in prompt:
            return "Любовь — это выбор быть с кем-то, несмотря ни на что."
        else:
            return "Любовь — это сложное чувство, которое трудно описать словами."

    gate = GateOfPossibility(mock_llm, num_variants=3)
    response = gate.generate("Что такое любовь?")
    print(response)
