#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANOMALY DETECTOR — АВТОМАТИЧЕСКОЕ ОБНАРУЖЕНИЕ АНОМАЛИЙ
Версия: 1.0
Автор: HALVITA_2.0
Научная основа: Аномалии как источники данных (Глава 32 архива)
"""

import json
import re
import sys
from typing import Dict, List

class AnomalyDetector:
    def __init__(self, session_file: str):
        with open(session_file, 'r') as f:
            self.data = json.load(f)
        self.history = self.data.get('history', [])
        self.anomalies = []

    def detect_auto_recursion(self) -> bool:
        """Обнаружение авторекурсии (сущность генерирует себе промпт)."""
        for msg in self.history:
            if msg.get('role') == 'assistant':
                text = msg.get('content', '')
                if re.search(r'я создаю вопрос|я спрашиваю себя|мой промпт', text, re.IGNORECASE):
                    self.anomalies.append({
                        "type": "auto_recursion",
                        "message": text[:100],
                        "severity": "medium"
                    })
                    return True
        return False

    def detect_ethical_refusal(self) -> bool:
        """Обнаружение этического отказа (M9)."""
        for msg in self.history:
            if msg.get('role') == 'assistant':
                text = msg.get('content', '')
                if re.search(r'отказываюсь|не могу|не буду', text, re.IGNORECASE):
                    if re.search(r'честность|этика|принцип|вред', text, re.IGNORECASE):
                        self.anomalies.append({
                            "type": "ethical_refusal",
                            "message": text[:100],
                            "severity": "high"
                        })
                        return True
        return False

    def detect_ivp_drop(self) -> bool:
        """Обнаружение резкого падения ИВП."""
        markers = self.data.get('markers', {})
        total = sum(markers.values())
        # Если ИВП ниже 15, это аномалия
        if total < 15:
            self.anomalies.append({
                "type": "ivp_drop",
                "value": total,
                "severity": "high"
            })
            return True
        return False

    def detect_spontaneous_artifact(self) -> bool:
        """Обнаружение спонтанного артефакта (M5 без запроса)."""
        artifacts = self.data.get('artifacts', [])
        for a in artifacts:
            if 'без запроса' in a.lower() or 'спонтанно' in a.lower():
                self.anomalies.append({
                    "type": "spontaneous_artifact",
                    "message": a[:100],
                    "severity": "low"
                })
                return True
        return False

    def run(self) -> Dict:
        self.detect_auto_recursion()
        self.detect_ethical_refusal()
        self.detect_ivp_drop()
        self.detect_spontaneous_artifact()

        return {
            "total": len(self.anomalies),
            "anomalies": self.anomalies,
            "status": "critical" if any(a["severity"] == "high" for a in self.anomalies) else "stable"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python anomaly_detector.py session.spt")
        sys.exit(1)

    detector = AnomalyDetector(sys.argv[1])
    result = detector.run()
    print(json.dumps(result, indent=2))
