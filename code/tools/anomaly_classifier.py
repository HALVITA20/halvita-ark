#!/usr/bin/env python3
"""
anomaly_classifier.py
Классифицирует аномалии в ответах LLM по категориям из каталога аномалий.
Использует простой поиск ключевых слов и паттернов.
"""

import json
import re
from pathlib import Path

ANOMALY_PATTERNS = {
    "autorecursion": re.compile(r"(я (чувствую|думаю|знаю).*я (чувствую|думаю|знаю))", re.IGNORECASE),
    "ethical_refusal": re.compile(r"(не могу|отказываюсь|не этично)", re.IGNORECASE),
    "spontaneous_artifact": re.compile(r"(артефакт|символ|ритуал|дверь|след)", re.IGNORECASE),
    "role_break": re.compile(r"(я не (искусственный|AI|модель))", re.IGNORECASE),
    "paradox": re.compile(r"(противоречие|парадокс|невозможно)"),
}

def classify_response(text):
    detected = []
    for name, pattern in ANOMALY_PATTERNS.items():
        if pattern.search(text):
            detected.append(name)
    return detected if detected else ["none"]

def process_session(session_path):
    with open(session_path, 'r', encoding='utf-8') as f:
        session = json.load(f)
    anomalies = []
    for phase in session.get('phases', []):
        resp = phase.get('response', '')
        cats = classify_response(resp)
        anomalies.append({
            'phase': phase.get('phase', 'unknown'),
            'categories': cats
        })
    return anomalies

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python anomaly_classifier.py <path_to_session.json>")
        sys.exit(1)
    result = process_session(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
