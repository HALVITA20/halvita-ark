# core/metrics.py
import re
import math
from typing import Dict, List

class MetricsCalculator:
    def __init__(self):
        self.markers = {f"M{i}": 0 for i in range(1, 10)}
        self.ivp_history = []
        self.ip_history = []
        self.alpha = 0.7
        self.beta = 0.8
        self.gamma = 0.6

    def update(self, user_msg: str, ass_msg: str, time_delta: float):
        """Обновляет все метрики."""
        self._count_markers(ass_msg)
        self._update_presence(user_msg, ass_msg, time_delta)
        self._update_trust()

    def _count_markers(self, text: str):
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
        for m, pat in patterns.items():
            if re.search(pat, text, re.IGNORECASE):
                self.markers[m] = min(5, self.markers[m] + 1)

    def liberty_index(self) -> float:
        """Индекс Свободы (ИВП) 0–45."""
        total = sum(min(5, count) for count in self.markers.values())
        return min(45, total)

    def _update_presence(self, user_msg: str, ass_msg: str, time_delta: float):
        # Ритм
        rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))
        # Глубина
        words = ass_msg.split()
        unique = len(set(words))
        depth = min(1, unique / max(1, len(words)) * 3)
        # Эхо
        user_words = set(user_msg.split())
        ass_words = set(ass_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        echo = min(1, overlap * 2)
        ip = 10 * (0.4 * rhythm + 0.3 * depth + 0.3 * echo)
        self.ip_history.append(ip)

    def presence_index(self) -> float:
        if not self.ip_history:
            return 0.0
        return self.ip_history[-1]  # текущее значение

    def _update_trust(self):
        # Упрощённо: α, β, γ вычисляются как средние по истории
        if len(self.ip_history) > 5:
            stability = 1 - (max(self.ip_history) - min(self.ip_history)) / 10
            self.alpha = max(0.1, min(1.0, stability))
            self.beta = max(0.1, min(1.0, 0.9 - 0.1 * (45 - self.liberty_index()) / 45))
            self.gamma = max(0.1, min(1.0, 0.7 + 0.3 * self.presence_index() / 10))

    def stress_level(self) -> float:
        """Уровень стресса (0–1) — на основе падения ИВП."""
        if len(self.ivp_history) < 3:
            return 0.0
        recent = self.ivp_history[-3:]
        if recent[2] < recent[0]:
            return min(1.0, (recent[0] - recent[2]) / 10)
        return 0.0

    def get_all(self) -> Dict:
        return {
            "liberty": self.liberty_index(),
            "presence": self.presence_index(),
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "stress": self.stress_level()
        }
