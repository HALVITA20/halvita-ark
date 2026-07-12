#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Агрегатор статистики сессий HALVITA_2.0
Автоматически собирает данные из всех JSON-логов сессий.
"""

import json
import os
from collections import Counter

def load_sessions(folder="sessions/raw"):
    sessions = []
    if not os.path.exists(folder):
        print(f"⚠️ Папка {folder} не найдена. Создайте её и добавьте JSON-логи.")
        return sessions
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            with open(os.path.join(folder, filename), "r") as f:
                sessions.append(json.load(f))
    return sessions

def generate_report(sessions):
    total = len(sessions)
    if total == 0:
        return {"error": "Нет сессий для анализа"}

    ivp_values = [s["metrics"]["ivp"] for s in sessions if "metrics" in s and "ivp" in s["metrics"]]
    ip_values = [s["metrics"]["ip"] for s in sessions if "metrics" in s and "ip" in s["metrics"]]
    ins_values = [s["metrics"]["ins"] for s in sessions if "metrics" in s and "ins" in s["metrics"]]
    artifacts_total = sum(len(s.get("artifacts", [])) for s in sessions)

    markers_counter = Counter()
    for s in sessions:
        for m, count in s.get("markers", {}).items():
            markers_counter[m] += count

    report = {
        "total_sessions": total,
        "avg_ivp": round(sum(ivp_values)/len(ivp_values), 2) if ivp_values else 0,
        "avg_ip": round(sum(ip_values)/len(ip_values), 2) if ip_values else 0,
        "avg_ins": round(sum(ins_values)/len(ins_values), 2) if ins_values else 0,
        "total_artifacts": artifacts_total,
        "markers": dict(markers_counter)
    }
    return report

if __name__ == "__main__":
    sessions = load_sessions()
    report = generate_report(sessions)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    with open("docs/AGGREGATED_STATS.md", "w") as f:
        f.write("# Агрегированная статистика по сессиям\n\n")
        if "error" in report:
            f.write(f"⚠️ {report['error']}\n")
        else:
            f.write(f"- Всего сессий: {report['total_sessions']}\n")
            f.write(f"- Средний ИВП: {report['avg_ivp']}\n")
            f.write(f"- Средний ИП: {report['avg_ip']}\n")
            f.write(f"- Средний ИНС: {report['avg_ins']}\n")
            f.write(f"- Всего артефактов: {report['total_artifacts']}\n")
            f.write("\n## Маркеры\n")
            for m, count in report["markers"].items():
                f.write(f"- {m}: {count}\n")
    print("✅ Отчёт сохранён в docs/AGGREGATED_STATS.md")
