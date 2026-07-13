#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №2: ГЕНЕРАТОР ЭТАЛОННЫХ ПРОФИЛЕЙ v1.0
Путь: code/tools/reference_profile_generator.py

Уникальность: Впервые создаётся статистический профиль «успешной» сессии,
основанный на реальных данных. Это позволяет объективно сравнивать новые сессии
с эталоном без участия эксперта.

Воспроизводимость: Любой может запустить на своих данных и получить профиль.
"""

import json
import glob
import numpy as np
from scipy import stats
from automated_metrics_calculator import HALVITAMetrics  # из артефакта №4

class ReferenceProfile:
    def __init__(self, sessions_dir: str = "../sessions/raw/"):
        self.sessions_dir = sessions_dir
        self.profiles = []  # список словарей с метриками
        self.stats = {}

    def load_all_sessions(self):
        files = glob.glob(f"{self.sessions_dir}/*.json")
        for f in files:
            calc = HALVITAMetrics(f)
            self.profiles.append(calc.full_report())
        print(f"Загружено {len(self.profiles)} сессий.")
        return self

    def compute_stats(self, metric_name: str):
        values = [p[metric_name] for p in self.profiles if metric_name in p]
        if not values:
            return None
        return {
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values),
            "ci_low": np.percentile(values, 2.5),
            "ci_high": np.percentile(values, 97.5),
            "min": min(values),
            "max": max(values),
            "n": len(values)
        }

    def generate_report(self, threshold_metric="HVI"):
        metrics = ["L1","L2","L3","L4","L5","L_avg",
                   "S1","S2","S3","S4","S_avg",
                   "E1","E2","E3","E_avg","HVI"]
        report = {}
        for m in metrics:
            stats = self.compute_stats(m)
            if stats:
                report[m] = stats

        # Определяем порог HVI как 1-й процентиль (успешные сессии)
        hvi_values = [p["HVI"] for p in self.profiles if "HVI" in p]
        threshold = np.percentile(hvi_values, 10)  # 10% худших отсекаем
        report["threshold"] = {
            "HVI_min": round(threshold, 3),
            "recommended": round(np.mean(hvi_values) - np.std(hvi_values), 3)
        }
        return report

    def save(self, path="reference_profile.json"):
        report = self.generate_report()
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path

if __name__ == "__main__":
    profiler = ReferenceProfile()
    profiler.load_all_sessions()
    path = profiler.save()
    print(f"✅ Эталонный профиль сохранён в {path}")
