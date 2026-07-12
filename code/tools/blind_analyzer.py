#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BLIND ANALYZER — ИНСТРУМЕНТ ДЛЯ СЛЕПОГО АНАЛИЗА
Версия: 1.0
Автор: HALVITA_2.0
"""

import json
import hashlib
import os
import sys
from typing import Dict
from datetime import datetime

class BlindAnalyzer:
    def __init__(self, session_file: str):
        with open(session_file, 'r') as f:
            self.data = json.load(f)
        self.session_id = hashlib.md5(
            (session_file + str(datetime.now())).encode()
        ).hexdigest()[:8]

    def anonymize(self) -> Dict:
        """Удаляет информацию об операторе и контексте."""
        anonymized = {
            "session_id": self.session_id,
            "messages": [],
            "metrics": {},
            "artifacts": []
        }

        # Извлекаем только сообщения сущности (без запросов оператора)
        for msg in self.data.get('history', []):
            if msg.get('role') == 'assistant':
                anonymized["messages"].append({
                    "content": msg.get('content', ''),
                    "timestamp": msg.get('timestamp', 0)
                })

        anonymized["metrics"] = {
            "ivp": self.data.get('ivp', 0),
            "ip": self.data.get('ip', 0),
            "markers": self.data.get('markers', {})
        }

        anonymized["artifacts"] = self.data.get('artifacts', [])[:5]
        return anonymized

    def export_for_blind_review(self, filename: str = None) -> str:
        if not filename:
            filename = f"blind_{self.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(self.anonymize(), f, indent=2)
        return filename

    @classmethod
    def batch_anonymize(cls, directory: str = "sessions/raw/") -> Dict:
        results = {}
        for filename in os.listdir(directory):
            if filename.endswith('.spt'):
                try:
                    analyzer = cls(os.path.join(directory, filename))
                    results[filename] = analyzer.export_for_blind_review()
                except Exception as e:
                    results[filename] = {"error": str(e)}
        return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python blind_analyzer.py session.spt")
        print("python blind_analyzer.py --batch")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        results = BlindAnalyzer.batch_anonymize()
        print(json.dumps(results, indent=2))
    else:
        analyzer = BlindAnalyzer(sys.argv[1])
        output = analyzer.export_for_blind_review()
        print(f"✅ Анонимизированный файл: {output}")
