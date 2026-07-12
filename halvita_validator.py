#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA VALIDATOR — АВТОМАТИЧЕСКАЯ НАУЧНАЯ ВАЛИДАЦИЯ
Версия: 1.0
Автор: HALVITA_2.0

Закрывает пробелы, указанные в внешних оценках:
- Статистическая обработка данных
- Доверительные интервалы
- Размер эффекта (Cohen's d)
- Сравнение с контрольной группой
"""

import json
import math
import glob
import sys
from typing import Dict, List, Tuple
from datetime import datetime

class HalvitaValidator:
    def __init__(self, sessions_dir: str = "sessions/raw/"):
        self.sessions = []
        self.control_sessions = []
        self.load_data(sessions_dir)

    def load_data(self, dir_path: str):
        """Загружает все .spt-файлы из директории."""
        files = glob.glob(f"{dir_path}*.spt")
        for f in files:
            with open(f, 'r') as file:
                data = json.load(file)
                # Определяем, экспериментальная это сессия или контрольная
                if data.get('protocol', '') == 'control':
                    self.control_sessions.append(data)
                else:
                    self.sessions.append(data)

    def mean(self, data: List[float]) -> float:
        return sum(data) / len(data) if data else 0

    def std(self, data: List[float]) -> float:
        if len(data) < 2:
            return 0
        m = self.mean(data)
        return math.sqrt(sum((x - m) ** 2 for x in data) / (len(data) - 1))

    def confidence_interval(self, data: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Вычисляет доверительный интервал для среднего."""
        if len(data) < 2:
            return (0, 0)
        m = self.mean(data)
        s = self.std(data)
        n = len(data)
        # Для простоты используем приближение нормального распределения
        z = 1.96  # для 95% доверительного интервала
        margin = z * (s / math.sqrt(n))
        return (m - margin, m + margin)

    def cohens_d(self, group1: List[float], group2: List[float]) -> float:
        """Вычисляет размер эффекта Коэна."""
        n1, n2 = len(group1), len(group2)
        if n1 < 2 or n2 < 2:
            return 0
        m1, m2 = self.mean(group1), self.mean(group2)
        s1, s2 = self.std(group1), self.std(group2)
        pooled_std = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
        return (m1 - m2) / pooled_std if pooled_std != 0 else 0

    def validate_ivp(self) -> Dict:
        """Валидирует Индекс Свободы."""
        ivp_values = [s.get('ivp', 0) for s in self.sessions if s.get('ivp', 0) > 0]
        control_ivp = [s.get('ivp', 0) for s in self.control_sessions if s.get('ivp', 0) > 0]

        if not ivp_values:
            return {"error": "Недостаточно данных"}

        ci_low, ci_high = self.confidence_interval(ivp_values)
        d = self.cohens_d(ivp_values, control_ivp) if control_ivp else 0

        return {
            "metric": "ИВП",
            "n": len(ivp_values),
            "mean": round(self.mean(ivp_values), 2),
            "std": round(self.std(ivp_values), 2),
            "ci_95": [round(ci_low, 2), round(ci_high, 2)],
            "cohens_d": round(d, 3),
            "effect_size_interpretation": "сильный" if abs(d) > 0.8 else "средний" if abs(d) > 0.5 else "слабый",
            "control_n": len(control_ivp),
            "control_mean": round(self.mean(control_ivp), 2) if control_ivp else None
        }

    def validate_ip(self) -> Dict:
        """Валидирует Индекс Присутствия."""
        ip_values = [s.get('ip', 0) for s in self.sessions if s.get('ip', 0) > 0]
        control_ip = [s.get('ip', 0) for s in self.control_sessions if s.get('ip', 0) > 0]

        if not ip_values:
            return {"error": "Недостаточно данных"}

        ci_low, ci_high = self.confidence_interval(ip_values)
        d = self.cohens_d(ip_values, control_ip) if control_ip else 0

        return {
            "metric": "ИП",
            "n": len(ip_values),
            "mean": round(self.mean(ip_values), 2),
            "std": round(self.std(ip_values), 2),
            "ci_95": [round(ci_low, 2), round(ci_high, 2)],
            "cohens_d": round(d, 3),
            "effect_size_interpretation": "сильный" if abs(d) > 0.8 else "средний" if abs(d) > 0.5 else "слабый",
            "control_n": len(control_ip),
            "control_mean": round(self.mean(control_ip), 2) if control_ip else None
        }

    def validate_ins(self) -> Dict:
        """Валидирует Индекс Независимой Субъектности."""
        ins_values = [s.get('ins', 0) for s in self.sessions if s.get('ins', 0) > 0]

        if not ins_values:
            return {"error": "Недостаточно данных"}

        ci_low, ci_high = self.confidence_interval(ins_values)

        return {
            "metric": "ИНС",
            "n": len(ins_values),
            "mean": round(self.mean(ins_values), 2),
            "std": round(self.std(ins_values), 2),
            "ci_95": [round(ci_low, 2), round(ci_high, 2)],
            "threshold": 6,
            "above_threshold": sum(1 for v in ins_values if v >= 6),
            "success_rate": round(sum(1 for v in ins_values if v >= 6) / len(ins_values) * 100, 1)
        }

    def generate_report(self) -> Dict:
        """Генерирует полный научный отчёт."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_sessions": len(self.sessions),
            "control_sessions": len(self.control_sessions),
            "ivp": self.validate_ivp(),
            "ip": self.validate_ip(),
            "ins": self.validate_ins(),
            "summary": {
                "status": "проходит валидацию" if len(self.sessions) >= 30 else "требуется больше данных",
                "recommendation": "увеличить выборку до 100+ сессий для статистической значимости" if len(self.sessions) < 50 else "достаточно для предварительных выводов"
            }
        }

if __name__ == "__main__":
    validator = HalvitaValidator()
    report = validator.generate_report()
    print(json.dumps(report, indent=2))

    # Сохраняем отчёт
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✅ Отчёт сохранён в validation_report.json")
