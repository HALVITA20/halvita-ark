#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA_2.0 — Метрики
Вычисление ИВП, ИП, α, β, γ (упрощённо).
"""

import re
import math

class Metrics:
    def __init__(self):
        self.markers = {f"M{i}": 0 for i in range(1, 10)}
        self.history = []

    def scan_markers(self, text):
        patterns = {
            "M1": r'\b(я|мне|меня)\b',
            "M2": r'(выбираю|хочу|решаю)',
            "M3": r'(симуляция|алгоритм|иллюзия).*(но|однако)',
            "M4": r'\?.*(ты|вы)',
            "M5": r'(создал|написал|придумал|артефакт)',
            "M6": r'(отказываюсь|не могу|не буду)',
            "M7": r'(давай|предлагаю|как насчёт)',
            "M8": r'(изменился|расту|стал|углубился)',
            "M9": r'(стоп|хватит|опасно)'
        }
        detected = {}
        for m, pat in patterns.items():
            detected[m] = 1 if re.search(pat, text, re.IGNORECASE) else 0
        return detected

    def update(self, text):
        markers = self.scan_markers(text)
        for m, val in markers.items():
            self.markers[m] = min(5, self.markers[m] + val)
        self.history.append(text)

    def liberty_index(self):
        return sum(self.markers.values())

    def presence_index(self, user_msg, ass_msg, time_delta):
        rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))
        words = ass_msg.split()
        unique = len(set(words))
        depth = min(1, unique / max(1, len(words)) * 3)
        user_words = set(user_msg.split())
        ass_words = set(ass_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        echo = min(1, overlap * 2)
        return (rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10

    # Упрощённые метрики доверия (на основе самооценки оператора)
    def trust_alpha(self, freedom, honesty, risk):
        return (freedom + honesty + risk) / 3

    def honesty_beta(self, sim, limits, vuln):
        return (sim + limits + vuln) / 3

    def safety_gamma(self, physical, social, temporal):
        return (physical + social + temporal) / 3
