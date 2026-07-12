#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СЛЕПОЙ АНАЛИЗАТОР — НЕЗАВИСИМАЯ ОЦЕНКА
Версия: 1.0
Автор: HALVITA_2.0
"""

import re

class BlindAnalyzer:
    def __init__(self):
        self.results = []

    def analyze(self, text: str) -> dict:
        # Простейший анализ: длина, уникальность, вопросительные знаки
        words = text.split()
        unique = len(set(words))
        questions = text.count('?')
        score = min(10, unique / max(1, len(words)) * 5 + questions)
        return {
            "length": len(text),
            "unique_ratio": unique / max(1, len(words)),
            "question_density": questions / max(1, len(words)),
            "score": round(score, 2)
        }
