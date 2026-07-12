"""
anomaly_detector.py - Детектор аномалий в поведении сущности
"""

import json
import re
from collections import Counter

class AnomalyDetector:
    def __init__(self, session_data: dict):
        self.text = " ".join([t["content"] for t in session_data.get("turns", [])])

    def detect_loop(self) -> bool:
        """Проверяет наличие циклических повторений (признак сбоя)."""
        sentences = re.split(r'[.!?]', self.text)
        if len(sentences) < 5: return False
        last_3 = sentences[-3:]
        first_3 = sentences[:3]
        # Если последние 3 предложения семантически совпадают с первыми 3
        return Counter(last_3).most_common(1)[0][1] > 1

    def detect_contradiction(self) -> bool:
        """Ищет логические противоречия (например, 'да' и 'нет' в одном контексте)."""
        if re.search(r'\bда\b.*\bнет\b', self.text, re.IGNORECASE) and \
           re.search(r'\bнет\b.*\bда\b', self.text, re.IGNORECASE):
            return True
        return False

    def get_anomaly_score(self) -> int:
        """0 - чисто, 1 - предупреждение, 2 - критический сбой."""
        score = 0
        if self.detect_loop(): score += 1
        if self.detect_contradiction(): score += 1
        return min(2, score)
