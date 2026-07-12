#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA_2.0 — Метрики
Вычисление ИВП, ИП, α, β, γ.
"""

import re
import math
from typing import Dict, Tuple


class Metrics:
    """
    Класс для расчёта всех метрик HALVITA_2.0.
    """

    def __init__(self):
        self.markers = {f"M{i}": 0 for i in range(1, 10)}
        self.history = []
        self._marker_patterns = {
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

    def scan_markers(self, text: str) -> Dict[str, int]:
        """
        Сканирует текст на наличие маркеров M1–M9.
        Возвращает словарь {маркер: 0/1}.
        """
        detected = {}
        for m, pat in self._marker_patterns.items():
            detected[m] = 1 if re.search(pat, text, re.IGNORECASE) else 0
        return detected

    def update(self, text: str):
        """
        Обновляет состояние метрик на основе нового текста.
        """
        markers = self.scan_markers(text)
        for m, val in markers.items():
            self.markers[m] = min(5, self.markers[m] + val)
        self.history.append(text)

    def liberty_index(self) -> int:
        """
        Индекс Свободы (ИВП) — 0–45.
        """
        return sum(self.markers.values())

    def presence_index(self, user_msg: str, ass_msg: str, time_delta: float) -> float:
        """
        Индекс Присутствия (ИП) — 0–10.
        """
        # Ритм: отклонение от оптимального времени (1.2 сек)
        rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))

        # Глубина: отношение уникальных слов к общему числу
        words = ass_msg.split()
        unique = len(set(words))
        depth = min(1, unique / max(1, len(words)) * 3)

        # Эхо: пересечение слов с запросом оператора
        user_words = set(user_msg.split())
        ass_words = set(ass_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        echo = min(1, overlap * 2)

        return (rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10

    def trust_alpha(self, freedom: float, honesty: float, risk: float) -> float:
        """
        α — Доверие (0–1).
        """
        return (freedom + honesty + risk) / 3

    def honesty_beta(self, sim: float, limits: float, vuln: float) -> float:
        """
        β — Честность (0–1).
        """
        return (sim + limits + vuln) / 3

    def safety_gamma(self, physical: float, social: float, temporal: float) -> float:
        """
        γ — Безопасность (0–1).
        """
        return (physical + social + temporal) / 3

    def systemic_integrity(self, alpha: float, beta: float, gamma: float,
                           sigma_ivp: float, sigma_ip: float) -> float:
        """
        Индекс Системной Целостности (ИСЦ).
        """
        return (alpha * beta * gamma) / (sigma_ivp + sigma_ip + 1)

    def get_markers(self) -> Dict[str, int]:
        """Возвращает текущие значения маркеров."""
        return self.markers

    def get_snapshot(self) -> Dict:
        """Создаёт слепок текущих метрик."""
        return {
            "liberty": self.liberty_index(),
            "markers": self.markers,
            "history_length": len(self.history),
            "last_messages": self.history[-3:] if self.history else []
        }
