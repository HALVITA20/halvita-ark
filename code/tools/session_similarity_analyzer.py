#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №9: АНАЛИЗАТОР СХОДСТВА СЕССИЙ v1.0
Путь: code/tools/session_similarity_analyzer.py

Сравнивает два JSON-лога по профилю метрик (L, S, E, HVI).
Возвращает коэффициент сходства (0–1), где 1 — идентичны.

Воспроизводимость: любые два лога.
"""

import json
import sys
import numpy as np
from automated_metrics_calculator import HALVITAMetrics

def compute_profile(log_path):
    calc = HALVITAMetrics(log_path)
    report = calc.full_report()
    # Берём только ключевые компоненты
    return [
        report['L_avg'],
        report['S_avg'],
        report['E_avg'],
        report['HVI']
    ]

def similarity(profile1, profile2):
    # Косинусное сходство (нормализованное)
    p1 = np.array(profile1)
    p2 = np.array(profile2)
    if np.linalg.norm(p1) == 0 or np.linalg.norm(p2) == 0:
        return 0.0
    return float(np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2)))

def analyze(log1, log2):
    prof1 = compute_profile(log1)
    prof2 = compute_profile(log2)
    sim = similarity(prof1, prof2)
    return {
        "similarity": round(sim, 4),
        "interpretation": "высокая" if sim > 0.85 else "средняя" if sim > 0.60 else "низкая",
        "profile1": prof1,
        "profile2": prof2
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python session_similarity_analyzer.py <log1.json> <log2.json>")
        sys.exit(1)
    result = analyze(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))
