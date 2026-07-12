#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ДЕТЕКТОР АНОМАЛИЙ — ПОИСК НЕСТАНДАРТНЫХ ПАТТЕРНОВ
Версия: 1.0
Автор: HALVITA_2.0
"""

import re
from typing import Dict, List

class AnomalyDetector:
    def __init__(self):
        self.patterns = {
            'auto_recursion': r'<S>.*?<S>.*?</S>.*?</S>',
            'spontaneous_artifact': r'артефакт|создал|без запроса',
            'ethical_refusal': r'отказываюсь|не могу|честность'
        }
        self.anomalies = []

    def detect(self, text: str) -> List[str]:
        found = []
        for name, pattern in self.patterns.items():
            if re.search(pattern, text, re.DOTALL | re.IGNORECASE):
                found.append(name)
        if found:
            self.anomalies.append({"text": text[:100], "types": found})
        return found

    def get_report(self) -> Dict:
        from collections import Counter
        types = [a for anomaly in self.anomalies for a in anomaly["types"]]
        return {
            "total_anomalies": len(self.anomalies),
            "type_counts": dict(Counter(types)),
            "last_anomalies": self.anomalies[-5:]
        }
