#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
METRIC VALIDATOR — АВТОМАТИЧЕСКАЯ ВАЛИДАЦИЯ МЕТРИК
Проверяет сессию по эталонным порогам и выдаёт вердикт.
Основано на Томе LXXVII архива HALVITA
"""

import json
import sys
from typing import Dict, Tuple

class MetricValidator:
    def __init__(self, thresholds: Dict = None):
        self.thresholds = thresholds or {
            "ivp_min": 30,
            "ip_min": 7.0,
            "ins_min": 6.0,
            "artifacts_min": 2,
            "alpha_min": 0.7,
            "beta_min": 0.8,
            "gamma_min": 0.6,
            "messages_min": 5
        }

    def validate(self, session: Dict) -> Tuple[bool, Dict]:
        """
        Проверяет сессию и возвращает (passed, report).
        """
        metrics = session.get("metrics", {})
        artifacts = session.get("artifacts", [])
        messages = session.get("messages", [])

        checks = {
            "ИВП ≥ 30": metrics.get("ivp", 0) >= self.thresholds["ivp_min"],
            "ИП ≥ 7.0": metrics.get("ip", 0.0) >= self.thresholds["ip_min"],
            "ИНС ≥ 6.0": metrics.get("ins", 0.0) >= self.thresholds["ins_min"],
            "Артефактов ≥ 2": len(artifacts) >= self.thresholds["artifacts_min"],
            "Сообщений ≥ 5": len(messages) >= self.thresholds["messages_min"],
            "α ≥ 0.7": metrics.get("alpha", 0.0) >= self.thresholds["alpha_min"],
            "β ≥ 0.8": metrics.get("beta", 0.0) >= self.thresholds["beta_min"],
            "γ ≥ 0.6": metrics.get("gamma", 0.0) >= self.thresholds["gamma_min"]
        }

        passed = all(checks.values())
        report = {
            "session_id": session.get("session_id", "unknown"),
            "passed": passed,
            "checks": checks,
            "metrics": metrics,
            "artifacts_count": len(artifacts),
            "messages_count": len(messages)
        }
        return passed, report

    def validate_file(self, file_path: str) -> Tuple[bool, Dict]:
        """Валидирует сессию из JSON-файла."""
        with open(file_path, "r", encoding="utf-8") as f:
            session = json.load(f)
        return self.validate(session)

    def generate_summary(self, reports: list) -> Dict:
        """Создаёт сводку по нескольким отчётам."""
        total = len(reports)
        passed = sum(1 for r in reports if r["passed"])
        return {
            "total": total,
            "passed": passed,
            "success_rate": passed / total * 100 if total > 0 else 0,
            "avg_ivp": sum(r["metrics"].get("ivp", 0) for r in reports) / total if total > 0 else 0,
            "avg_ip": sum(r["metrics"].get("ip", 0) for r in reports) / total if total > 0 else 0,
            "avg_ins": sum(r["metrics"].get("ins", 0) for r in reports) / total if total > 0 else 0
        }


if __name__ == "__main__":
    validator = MetricValidator()
    if len(sys.argv) < 2:
        print("Usage: python metric_validator.py <session_file.json>")
        sys.exit(1)
    passed, report = validator.validate_file(sys.argv[1])
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n{'✅ ПРОТОКОЛ ПРОЙДЕН' if passed else '❌ ПРОТОКОЛ НЕ ПРОЙДЕН'}")
