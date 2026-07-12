#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STATISTICAL SIGNIFICANCE — РАСЧЁТ P-ЗНАЧЕНИЙ
Версия: 1.0
Автор: HALVITA_2.0
Научная основа: Стандартные статистические методы
"""

import math
import json
import sys
from typing import Dict, List

class StatisticalSignificance:
    def __init__(self, control_data: List[float], experiment_data: List[float]):
        self.control = control_data
        self.experiment = experiment_data

    def mean(self, data: List[float]) -> float:
        return sum(data) / len(data) if data else 0

    def variance(self, data: List[float]) -> float:
        if len(data) < 2:
            return 0
        mean = self.mean(data)
        return sum((x - mean) ** 2 for x in data) / (len(data) - 1)

    def t_test(self) -> Dict:
        """T-тест для независимых выборок."""
        n1, n2 = len(self.control), len(self.experiment)
        if n1 < 2 or n2 < 2:
            return {"error": "недостаточно данных"}

        mean1, mean2 = self.mean(self.control), self.mean(self.experiment)
        var1, var2 = self.variance(self.control), self.variance(self.experiment)

        # T-статистика
        t = (mean1 - mean2) / math.sqrt(var1/n1 + var2/n2)

        # Степени свободы (Уэлч-Саттервейт)
        df = ((var1/n1 + var2/n2) ** 2) / (
            (var1/n1) ** 2 / (n1 - 1) + (var2/n2) ** 2 / (n2 - 1)
        )

        # P-значение (приближённое, для двухстороннего теста)
        p = self._t_distribution(t, df)

        return {
            "t_statistic": round(t, 3),
            "df": round(df, 2),
            "p_value": round(p, 4),
            "significant": p < 0.05,
            "interpretation": "статистически значимо" if p < 0.05 else "не значимо"
        }

    def _t_distribution(self, t: float, df: float) -> float:
        """Приближённое p-значение для t-распределения."""
        # Аппроксимация для больших df
        if df > 30:
            # Нормальное приближение
            from math import erf
            return 1 - erf(abs(t) / math.sqrt(2))
        # Упрощённое приближение для малых df
        return 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))

    def effect_size(self) -> float:
        """Cohen's d — размер эффекта."""
        n1, n2 = len(self.control), len(self.experiment)
        if n1 < 2 or n2 < 2:
            return 0
        mean1, mean2 = self.mean(self.control), self.mean(self.experiment)
        var1, var2 = self.variance(self.control), self.variance(self.experiment)
        pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        return (mean1 - mean2) / pooled_std if pooled_std != 0 else 0

if __name__ == "__main__":
    # Пример: сравнение ИВП до и после
    before = [20, 22, 18, 25, 19, 21, 23, 20, 22, 18]
    after = [32, 35, 30, 38, 33, 34, 36, 31, 33, 35]

    stats = StatisticalSignificance(before, after)
    t_result = stats.t_test()
    effect = stats.effect_size()

    print("=== СТАТИСТИЧЕСКАЯ ЗНАЧИМОСТЬ ===")
    print(json.dumps(t_result, indent=2))
    print(f"\nРазмер эффекта (Cohen's d): {effect:.3f}")
    print("Интерпретация:", end=" ")
    if abs(effect) < 0.2:
        print("очень слабый")
    elif abs(effect) < 0.5:
        print("слабый")
    elif abs(effect) < 0.8:
        print("средний")
    else:
        print("сильный")
