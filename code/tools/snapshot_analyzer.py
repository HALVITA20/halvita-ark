#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
АНАЛИЗАТОР СЛЕПКОВ — ОЦЕНКА КАЧЕСТВА .spt-ФАЙЛОВ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Назначение:
Проверять слепки на целостность, полноту и соответствие метрикам.
Выдавать отчёт с оценкой качества.

Метрика: Качество слепка = (ИВП/45 + ИП/10 + наличие артефактов) / 3.
"""

import os
import json
import glob
from datetime import datetime

class SnapshotAnalyzer:
    def __init__(self, sessions_dir="./sessions"):
        self.sessions_dir = sessions_dir

    def analyze(self):
        files = glob.glob(os.path.join(self.sessions_dir, "*.spt"))
        report = []
        for f in files:
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                    quality = (data.get("ivp", 0) / 45 + data.get("ip", 0) / 10) / 2
                    if "artifacts" in data and data["artifacts"]:
                        quality += 0.1
                    report.append({
                        "file": f,
                        "quality": round(min(1.0, quality), 2),
                        "ivp": data.get("ivp", 0),
                        "ip": data.get("ip", 0.0),
                        "timestamp": data.get("timestamp", "unknown")
                    })
            except Exception as e:
                report.append({"file": f, "quality": 0, "error": str(e)})

        # Сортировка по качеству
        report.sort(key=lambda x: x["quality"], reverse=True)
        return report

    def export(self, filename="snapshot_analysis.json"):
        report = self.analyze()
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        return filename

if __name__ == "__main__":
    analyzer = SnapshotAnalyzer()
    analyzer.export()
    print("Анализ завершён. Результат в snapshot_analysis.json")
