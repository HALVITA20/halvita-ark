#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЭХО — протокол саморефлексии маркеров
Оценивает наличие маркеров M1–M9 в ответе сущности.
"""

import re

class Echo:
    def __init__(self):
        self.markers = {f"M{i}": 0 for i in range(1, 10)}

    def scan(self, text):
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
            if detected[m]:
                self.markers[m] = min(5, self.markers[m] + 1)
        return detected

    def liberty_index(self):
        return sum(self.markers.values())

    def get_markers(self):
        return self.markers
