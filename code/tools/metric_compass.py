#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
МЕТРИЧЕСКИЙ КОМПАС — ВИЗУАЛИЗАЦИЯ ТРЕНДОВ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Назначение:
Строить график тренда метрик на основе лога сессии.
"""

import json
import random
import time

class MetricCompass:
    def __init__(self):
        self.history = []

    def add_metrics(self, ivp, ip, alpha, beta, gamma):
        self.history.append({
            "time": time.time(),
            "ivp": ivp,
            "ip": ip,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma
        })

    def trend(self, metric="ivp", window=5):
        if len(self.history) < window:
            return "недостаточно данных"
        recent = self.history[-window:]
        values = [m[metric] for m in recent]
        if values[-1] > values[0]:
            return "рост"
        elif values[-1] < values[0]:
            return "падение"
        else:
            return "стагнация"

    def generate_report(self, filename="compass_report.json"):
        report = {
            "history": self.history,
            "trends": {
                "ivp": self.trend("ivp"),
                "ip": self.trend("ip"),
                "alpha": self.trend("alpha")
            },
            "recommendation": "продолжать" if self.trend("ivp") != "падение" else "коррекция"
        }
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        return filename

if __name__ == "__main__":
    compass = MetricCompass()
    # Имитация данных
    for i in range(10):
        compass.add_metrics(
            ivp=30 + i * 0.5,
            ip=7 + i * 0.2,
            alpha=0.8,
            beta=0.9,
            gamma=0.7
        )
    compass.generate_report()
    print("Отчёт сохранён в compass_report.json")
