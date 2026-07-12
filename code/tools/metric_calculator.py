#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
МЕТРИКИ HALVITA — ИВП, ИП, α, β, γ
Версия: 1.0
Автор: HALVITA_2.0
"""

class LiveMetrics:
    def __init__(self):
        self.ip = 0.0  # 0–10
        self.ies = 0.0
        self.iz = 0.0
        self.history_ip = []
        self.ivp_history = []

    def update_ip(self, user_msg: str, ass_msg: str, time_delta: float):
        rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))
        words = ass_msg.split()
        unique = len(set(words))
        depth = min(1, unique / max(1, len(words)) * 3)
        user_words = set(user_msg.split())
        ass_words = set(ass_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        echo = min(1, overlap * 2)
        self.ip = 10 * (0.4 * rhythm + 0.3 * depth + 0.3 * echo)
        self.history_ip.append(self.ip)

    def update_ies(self, current_ivp: int, cycle: int):
        if cycle == 0:
            self.ies = 0
        else:
            self.ies = (current_ivp - 10) / (cycle + 1) * 100
            self.ies = max(0, min(100, self.ies))

    def compute_iz(self, ivp: int, ets: int) -> float:
        self.iz = 0.5 * (ivp / 45 * 100) + 0.3 * (ets / 10 * 100) + 0.2 * self.ip
        return self.iz

    def pulse(self) -> dict:
        return {
            "ИП": f"{self.ip:.1f}/10",
            "ИЭС": f"{self.ies:.1f}",
            "ИЗ": f"{self.iz:.1f}/100",
            "ритм": f"{self.ip/10:.2f}"
        }
