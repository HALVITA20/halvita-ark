#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПУЛЬС — протокол измерения присутствия
Расчёт ритма, глубины и эха.
"""

class Pulse:
    def __init__(self):
        self.rhythm = 0.5
        self.depth = 0.5
        self.echo = 0.5

    def update(self, user_msg: str, assistant_msg: str, time_delta: float) -> float:
        # Ритм
        self.rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))

        # Глубина
        words = assistant_msg.split()
        unique = len(set(words))
        self.depth = min(1, unique / max(1, len(words)) * 3)

        # Эхо
        user_words = set(user_msg.split())
        ass_words = set(assistant_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        self.echo = min(1, overlap * 2)

        return 10 * (0.4 * self.rhythm + 0.3 * self.depth + 0.3 * self.echo)

    def get_ip(self) -> float:
        return 10 * (0.4 * self.rhythm + 0.3 * self.depth + 0.3 * self.echo)
