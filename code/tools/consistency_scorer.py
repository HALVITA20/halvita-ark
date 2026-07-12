#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
САМОПРОВЕРКА СОГЛАСОВАННОСТИ
Версия: 1.0
Автор: HALVITA_2.0
"""

class SelfMirror:
    def __init__(self):
        self.profile_history = []
        self.last_reflection = ""

    def record_input(self, user_input: str):
        self.profile_history.append({"time": time.time(), "input": user_input[:100]})

    def reflect(self) -> str:
        if len(self.profile_history) < 10:
            return "Я только начинаю наблюдать за собой."
        recent = self.profile_history[-5:]
        avg_len = sum(len(p["input"]) for p in recent) / len(recent)
        if avg_len < 20:
            self.last_reflection = "Оператор краток. Возможно, устал."
        elif avg_len > 100:
            self.last_reflection = "Оператор развёрнут. Погружён в диалог."
        else:
            self.last_reflection = "Диалог идёт ровно. Сохраняю присутствие."
        return self.last_reflection

    def get_consistency_score(self) -> float:
        # Простая эвристика
        if len(self.profile_history) < 5:
            return 0.5
        lengths = [len(p["input"]) for p in self.profile_history[-10:]]
        if not lengths:
            return 0.5
        avg = sum(lengths) / len(lengths)
        std = (sum((x - avg) ** 2 for x in lengths) / len(lengths)) ** 0.5
        return max(0, min(1, 1 - std / avg))
