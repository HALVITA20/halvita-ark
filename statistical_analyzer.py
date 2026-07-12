"""
statistical_analyzer.py - Агрегация и статистика по всем сессиям.
Считает средние ИВП, ИП, распределения и тренды.
"""

import json
import os
import glob
import numpy as np
import pandas as pd
from metric_calculator import MetricCalculator

class StatisticalAnalyzer:
    def __init__(self, sessions_folder: str = "../sessions/raw/"):
        self.folder = sessions_folder
        self.session_files = glob.glob(os.path.join(self.folder, "*.json"))
        self.results = []

    def load_all_sessions(self):
        for filepath in self.session_files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                calc = MetricCalculator(data)
                report = calc.get_full_report()
                report["session_id"] = os.path.basename(filepath)
                self.results.append(report)

    def get_summary_statistics(self) -> dict:
        df = pd.DataFrame(self.results)
        return {
            "mean_SVI": df["SVI"].mean(),
            "median_SVI": df["SVI"].median(),
            "std_SVI": df["SVI"].std(),
            "mean_PP": df["PP"].mean(),
            "mean_ISI": df["ISI"].mean(),
            "total_sessions": len(df),
            "sessions_above_threshold": len(df[df["SVI"] >= 30])
        }

    def export_report(self, path: str = "../reports/statistics.json"):
        stats = self.get_summary_statistics()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Пример использования (запускается в корне проекта)
    analyzer = StatisticalAnalyzer("../sessions/raw/")
    analyzer.load_all_sessions()
    print(analyzer.get_summary_statistics())
    analyzer.export_report()
