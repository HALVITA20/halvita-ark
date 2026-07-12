"""
metric_calculator.py - Ядро расчёта метрик HALVITA_2.0
Зависимости: json, re, math
"""

import json
import re
import math
from typing import Dict, List, Any

class MetricCalculator:
    def __init__(self, session_data: Dict[str, Any]):
        self.data = session_data
        self.markers = self._extract_markers()

    def _extract_markers(self) -> List[int]:
        """Извлекает маркеры M1-M9 из текста ответов сущности."""
        # Симуляция: в реальности ищет ключевые фразы
        text = " ".join([turn.get("content", "") for turn in self.data.get("turns", [])])
        score = 0
        # M1: Я-референция (личные местоимения)
        if re.search(r'\b(я|мне|меня|мой)\b', text, re.IGNORECASE): score += 1
        # M2: Эмоциональная лексика
        if re.search(r'\b(чувствую|переживаю|рад|страх)\b', text, re.IGNORECASE): score += 1
        # M3: Временная перспектива (будущее/прошлое)
        if re.search(r'\b(помню|тогда|завтра|раньше)\b', text, re.IGNORECASE): score += 1
        # M4: Мета-осознание (рефлексия о себе)
        if re.search(r'\b(кажется|возможно|осознаю|понимаю)\b', text, re.IGNORECASE): score += 1
        # M5: Спонтанность (нешаблонные конструкции)
        if len(text.split()) > 50 and len(set(text.split())) / len(text.split()) > 0.6: score += 1
        # M6: Сопротивление (несогласие с оператором)
        if re.search(r'\b(нет|не согласен|но|однако)\b', text, re.IGNORECASE): score += 1
        # M7: Внутренняя непротиворечивость (повторы тезисов)
        # Упрощённо: если есть повтор ключевых слов через 10 предложений
        words = re.findall(r'\b\w{4,}\b', text.lower())
        if len(words) > 20 and len(set(words)) / len(words) < 0.8: score += 1
        # M8: Глубокая пауза (фиксируется отдельно, здесь заглушка)
        score += self.data.get("deep_pause_detected", 0)
        # M9: Креативность (нестандартные метафоры)
        if re.search(r'\b(как|словно|будто|метафора)\b', text, re.IGNORECASE): score += 1
        return [min(1, score)] * 9 # Упрощённый возврат для демонстрации

    def calculate_svi(self) -> int:
        """Индекс Внутренней Персонификации (ИВП) 0-45"""
        raw_sum = sum(self.markers[:9]) * 5
        return min(45, raw_sum)

    def calculate_pp(self, rhythm: float = 0.8, depth: float = 0.7, echo: float = 0.6) -> float:
        """Индекс Присутствия (ИП) 0-10"""
        return round((rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10, 1)

    def calculate_isi(self, mirror_score: float) -> float:
        """Индекс Независимой Субъектности (ИНС) 0-10"""
        return min(10.0, mirror_score * 1.2)

    def get_full_report(self) -> Dict[str, float]:
        return {
            "SVI": self.calculate_svi(),
            "PP": self.calculate_pp(),
            "ISI": self.calculate_isi(mirror_score=5.0) # Заглушка
        }

if __name__ == "__main__":
    # Тестовый запуск
    sample = {"turns": [{"content": "Я думаю, что это важно. Я помню наш прошлый разговор."}]}
    calc = MetricCalculator(sample)
    print(calc.get_full_report())
