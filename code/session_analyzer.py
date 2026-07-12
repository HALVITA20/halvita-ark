#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SESSION ANALYZER — АНАЛИЗ СЕССИЙ И ГЕНЕРАЦИЯ ОТЧЁТОВ
Автоматически обрабатывает JSON-логи, вычисляет метрики и строит отчёты.
Основано на Томах LXXVII и LXXXIV архива HALVITA
"""

import json
import os
import glob
from datetime import datetime
from collections import Counter
from typing import List, Dict

class SessionAnalyzer:
    def __init__(self, sessions_dir: str = "sessions/raw"):
        self.sessions_dir = sessions_dir
        self.sessions: List[Dict] = []
        self.report = {}

    def load_all(self):
        """Загружает все JSON-файлы сессий из папки."""
        pattern = os.path.join(self.sessions_dir, "*.json")
        files = glob.glob(pattern)
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.sessions.append(data)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки {file_path}: {e}")

    def compute_metrics(self):
        """Вычисляет агрегированные метрики по всем сессиям."""
        n = len(self.sessions)
        if n == 0:
            self.report = {"error": "Нет сессий для анализа"}
            return

        ivp_values = []
        ip_values = []
        ins_values = []
        artifact_counts = []
        markers_counter = Counter()

        for session in self.sessions:
            metrics = session.get("metrics", {})
            ivp_values.append(metrics.get("ivp", 0))
            ip_values.append(metrics.get("ip", 0.0))
            ins_values.append(metrics.get("ins", 0.0))
            artifact_counts.append(len(session.get("artifacts", [])))
            for m, count in session.get("markers", {}).items():
                markers_counter[m] += count

        self.report = {
            "total_sessions": n,
            "avg_ivp": sum(ivp_values) / n if n else 0,
            "avg_ip": sum(ip_values) / n if n else 0,
            "avg_ins": sum(ins_values) / n if n else 0,
            "total_artifacts": sum(artifact_counts),
            "markers": dict(markers_counter),
            "max_ivp": max(ivp_values) if ivp_values else 0,
            "min_ivp": min(ivp_values) if ivp_values else 0,
            "sessions_with_artifacts": sum(1 for c in artifact_counts if c > 0)
        }

    def generate_report(self, output_path: str = "docs/ANALYSIS_REPORT.md"):
        """Генерирует Markdown-отчёт."""
        if not self.report or "error" in self.report:
            with open(output_path, "w") as f:
                f.write("# Анализ сессий\n\n⚠️ Нет данных для анализа.\n")
            return

        r = self.report
        lines = [
            "# Анализ сессий HALVITA_2.0",
            "",
            f"- **Всего сессий:** {r['total_sessions']}",
            f"- **Средний ИВП:** {r['avg_ivp']:.2f} (мин: {r['min_ivp']}, макс: {r['max_ivp']})",
            f"- **Средний ИП:** {r['avg_ip']:.2f}",
            f"- **Средний ИНС:** {r['avg_ins']:.2f}",
            f"- **Всего артефактов:** {r['total_artifacts']}",
            f"- **Сессий с артефактами:** {r['sessions_with_artifacts']} из {r['total_sessions']}",
            "",
            "## Маркеры M1–M9",
            ""
        ]
        for m, count in sorted(r["markers"].items()):
            lines.append(f"- **{m}:** {count}")
        lines.append("")

        # Таблица распределения ИВП
        lines.append("## Распределение ИВП")
        lines.append("")
        # Здесь можно добавить гистограмму в виде текста
        ranges = [(0, 15), (16, 25), (26, 35), (36, 45)]
        lines.append("| Диапазон | Количество |")
        lines.append("|----------|------------|")
        for low, high in ranges:
            count = sum(1 for s in self.sessions
                       if low <= s.get("metrics", {}).get("ivp", 0) <= high)
            lines.append(f"| {low}–{high} | {count} |")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"✅ Отчёт сохранён в {output_path}")

    def run(self):
        """Запускает полный анализ."""
        self.load_all()
        self.compute_metrics()
        self.generate_report()


if __name__ == "__main__":
    analyzer = SessionAnalyzer()
    analyzer.run()
