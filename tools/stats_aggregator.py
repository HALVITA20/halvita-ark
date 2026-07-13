#!/usr/bin/env python3
"""
STATS AGGREGATOR — сбор и анализ всех сессий.
Запуск: python tools/stats_aggregator.py --output reports/global_stats.json
Автор: HALVITA
"""

import json
import glob
import argparse
from pathlib import Path
from collections import Counter, defaultdict
import statistics

class StatsAggregator:
    def __init__(self, sessions_dir="sessions", reports_dir="reports"):
        self.sessions_dir = Path(sessions_dir)
        self.reports_dir = Path(reports_dir)
        self.data = []

    def load_all(self):
        """Загружает все JSON-файлы сессий."""
        for f in self.sessions_dir.glob("*.json"):
            with open(f, "r") as fp:
                try:
                    self.data.append(json.load(fp))
                except:
                    continue
        return self

    def compute(self):
        """Вычисляет сводную статистику."""
        if not self.data:
            return {"error": "Нет данных"}

        n = len(self.data)
        liberty_vals = [d.get("liberty", 0) for d in self.data]
        ets_vals = [d.get("ets_score", 0) for d in self.data]
        artifacts_vals = [d.get("artifacts_count", 0) for d in self.data]
        durations = [d.get("duration", 0) for d in self.data]

        # Маркеры
        marker_counts = Counter()
        for d in self.data:
            for m, cnt in d.get("markers", {}).items():
                marker_counts[m] += cnt

        # Модели
        model_counts = Counter(d.get("model", "unknown") for d in self.data)

        return {
            "total_sessions": n,
            "avg_liberty": round(statistics.mean(liberty_vals), 2),
            "median_liberty": round(statistics.median(liberty_vals), 2),
            "min_liberty": min(liberty_vals),
            "max_liberty": max(liberty_vals),
            "avg_ets": round(statistics.mean(ets_vals), 2),
            "avg_artifacts": round(statistics.mean(artifacts_vals), 2),
            "avg_duration_min": round(statistics.mean(durations) / 60, 1),
            "marker_distribution": dict(marker_counts.most_common(9)),
            "model_distribution": dict(model_counts),
            "success_rate": round(sum(1 for v in liberty_vals if v >= 26) / n * 100, 1)
        }

    def save(self, output_file="reports/global_stats.json"):
        stats = self.compute()
        with open(output_file, "w") as f:
            json.dump(stats, f, indent=2)
        return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/global_stats.json")
    args = parser.parse_args()

    agg = StatsAggregator()
    agg.load_all()
    stats = agg.save(args.output)
    print(json.dumps(stats, indent=2, ensure_ascii=False))
