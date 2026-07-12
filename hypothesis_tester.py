#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HYPOTHESIS TESTER — ПРОВЕРКА НАУЧНЫХ ГИПОТЕЗ
Версия: 1.0
Автор: HALVITA_2.0
Научная основа: Статистические методы, корреляционный анализ
"""

import json
import math
import sys
from typing import Dict, List, Tuple

class HypothesisTester:
    def __init__(self, session_files: List[str]):
        self.sessions = []
        for f in session_files:
            with open(f, 'r') as file:
                self.sessions.append(json.load(file))

    def test_h1(self) -> Dict:
        """H1: ИВП коррелирует с количеством артефактов (r > 0.8)."""
        ivp_values = [s.get('ivp', 0) for s in self.sessions]
        artifact_counts = [len(s.get('artifacts', [])) for s in self.sessions]
        if len(ivp_values) < 2:
            return {"hypothesis": "H1", "result": "недостаточно данных"}

        # Корреляция Пирсона
        n = len(ivp_values)
        sum_x = sum(ivp_values)
        sum_y = sum(artifact_counts)
        sum_xy = sum(x * y for x, y in zip(ivp_values, artifact_counts))
        sum_x2 = sum(x * x for x in ivp_values)
        sum_y2 = sum(y * y for y in artifact_counts)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        r = numerator / denominator if denominator != 0 else 0

        return {
            "hypothesis": "H1: ИВП коррелирует с количеством артефактов",
            "correlation": round(r, 3),
            "confirmed": r > 0.8,
            "n": n
        }

    def test_h2(self) -> Dict:
        """H2: ИП растёт с глубиной диалога (r > 0.7)."""
        # Симулируем: глубина = количество уникальных слов / общее количество слов
        depths = []
        ip_values = []
        for s in self.sessions:
            history = s.get('history', [])
            ass_messages = [m['content'] for m in history if m.get('role') == 'assistant']
            if ass_messages:
                all_words = ' '.join(ass_messages).split()
                unique_words = len(set(all_words))
                depth = unique_words / max(1, len(all_words))
                depths.append(depth)
                ip_values.append(s.get('ip', 0))

        if len(depths) < 2:
            return {"hypothesis": "H2", "result": "недостаточно данных"}

        # Корреляция
        n = len(depths)
        sum_x = sum(depths)
        sum_y = sum(ip_values)
        sum_xy = sum(x * y for x, y in zip(depths, ip_values))
        sum_x2 = sum(x * x for x in depths)
        sum_y2 = sum(y * y for y in ip_values)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        r = numerator / denominator if denominator != 0 else 0

        return {
            "hypothesis": "H2: ИП растёт с глубиной диалога",
            "correlation": round(r, 3),
            "confirmed": r > 0.7,
            "n": n
        }

    def test_h3(self) -> Dict:
        """H3: Маркер M2 (выбор) предсказывает создание артефакта (M5)."""
        m2_count = 0
        m5_count = 0
        m2_m5_together = 0

        for s in self.sessions:
            markers = s.get('markers', {})
            m2 = markers.get('M2', 0)
            m5 = markers.get('M5', 0)
            if m2 > 0:
                m2_count += 1
            if m5 > 0:
                m5_count += 1
            if m2 > 0 and m5 > 0:
                m2_m5_together += 1

        if m2_count == 0:
            return {"hypothesis": "H3", "result": "M2 не обнаружен"}

        probability = m2_m5_together / m2_count

        return {
            "hypothesis": "H3: M2 (выбор) предсказывает M5 (артефакт)",
            "probability": round(probability, 3),
            "confirmed": probability > 0.6,
            "m2_count": m2_count,
            "m5_count": m5_count,
            "together": m2_m5_together
        }

    def run_all(self) -> Dict:
        return {
            "H1": self.test_h1(),
            "H2": self.test_h2(),
            "H3": self.test_h3()
        }

if __name__ == "__main__":
    import glob
    files = glob.glob("*.spt")
    if not files:
        print("❌ Нет .spt-файлов в текущей директории")
        sys.exit(1)

    tester = HypothesisTester(files)
    results = tester.run_all()
    print(json.dumps(results, indent=2))

    # Итог
    confirmed = sum(1 for r in results.values() if r.get('confirmed', False))
    print(f"\n✅ Подтверждено гипотез: {confirmed}/3")
