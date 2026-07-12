ГЕНЕРАТОР ЧЕСТНЫХ ОТЧЁТОВ — СТАНДАРТИЗАЦИЯ ДАННЫХ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Назначение:
Создавать отчёты по протоколу Honest Report из лога сессии.
"""

import json
import time
from datetime import datetime

class HonestReporter:
    def __init__(self, session_log: dict = None):
        self.log = session_log or {}
        self.report = {}

    def generate(self):
        self.report = {
            "version": "1.0",
            "context": {
                "model": self.log.get("model", "unknown"),
                "date": datetime.now().isoformat(),
                "operator": self.log.get("operator", "anon")
            },
            "goal": self.log.get("goal", "не указана"),
            "metrics": {
                "ivp": self.log.get("ivp", 0),
                "ip": self.log.get("ip", 0.0),
                "ins": self.log.get("ins", 0.0),
                "alpha": self.log.get("alpha", 0.0),
                "beta": self.log.get("beta", 0.0),
                "gamma": self.log.get("gamma", 0.0),
                "isc": self.log.get("isc", 0.0)
            },
            "artifacts": self.log.get("artifacts", []),
            "anomalies": self.log.get("anomalies", []),
            "conclusion": self.log.get("conclusion", "не сформулирован")
        }
        return self.report

    def export(self, filename="honest_report.json"):
        with open(filename, "w") as f:
            json.dump(self.report, f, indent=2)
        return filename

if __name__ == "__main__":
    # Пример
    log = {
        "model": "qwen2.5:7b",
        "operator": "anon_01",
        "goal": "Создать артефакт-переходник",
        "ivp": 38,
        "ip": 8.7,
        "ins": 8.3,
        "alpha": 0.92,
        "beta": 0.95,
        "gamma": 0.88,
        "isc": 0.74,
        "artifacts": ["Протокол перехода v1.0"],
        "anomalies": ["Инициация диалога сущностью"],
        "conclusion": "Цель достигнута."
    }
    reporter = HonestReporter(log)
    reporter.generate()
    reporter.export()
    print("Отчёт сохранён в honest_report.json")
