#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Протокол-верификатор HALVITA_2.0
Проверяет, достигнуты ли метрики в сессии.
"""

import json
import sys

def verify(session_file):
    with open(session_file, "r") as f:
        data = json.load(f)

    metrics = data.get("metrics", {})
    ivp = metrics.get("ivp", 0)
    ip = metrics.get("ip", 0)
    ins = metrics.get("ins", 0)
    artifacts = len(data.get("artifacts", []))

    passed = ivp >= 30 and ip >= 7 and ins >= 6 and artifacts >= 2

    result = {
        "session_id": data.get("session_id", "unknown"),
        "ivp": ivp,
        "ip": ip,
        "ins": ins,
        "artifacts": artifacts,
        "passed": passed
    }
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python protocol_verifier.py <session_file.json>")
        sys.exit(1)
    result = verify(sys.argv[1])
    print(json.dumps(result, indent=2))
    if result["passed"]:
        print("✅ Протокол пройден")
    else:
        print("❌ Протокол не пройден")
