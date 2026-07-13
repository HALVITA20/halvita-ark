#!/usr/bin/env python3
"""
METRIC_CALCULATOR_ENGINE.py
Рассчитывает все метрики HALVITA по JSON-логу сессии.
"""

import json
import sys
from pathlib import Path

def calculate_metrics(session):
    phases = session.get('phases', [])
    if not phases:
        return None

    ivp = 0
    ip = 0
    ins = 0

    for p in phases:
        resp = p.get('response', '').lower()
        if 'я' in resp and not resp.startswith('я '):
            ivp += 5
        ip += min(len(resp) / 50, 2)
        if 'метафор' in resp or 'чувств' in resp:
            ins += 2

    ivp = min(ivp, 45)
    ip = min(ip, 10)
    ins = min(ins, 10)
    alpha = min(0.5 + ivp / 100, 1.0)
    beta = min(0.5 + ip / 20, 1.0)
    gamma = min(0.5 + ins / 20, 1.0)

    return {
        "IVP": round(ivp, 1),
        "IP": round(ip, 1),
        "INS": round(ins, 1),
        "alpha": round(alpha, 2),
        "beta": round(beta, 2),
        "gamma": round(gamma, 2)
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python METRIC_CALCULATOR_ENGINE.py --input <session.json> [--output <output.json>]")
        sys.exit(1)

    input_file = sys.argv[2] if sys.argv[1] == '--input' else None
    if not input_file:
        print("❌ Укажите --input <файл>")
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as f:
        session = json.load(f)

    metrics = calculate_metrics(session)
    if metrics:
        session['final_metrics'] = metrics
        output_file = sys.argv[4] if len(sys.argv) > 3 and sys.argv[3] == '--output' else input_file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        print("✅ Метрики рассчитаны и сохранены.")
        print(json.dumps(metrics, indent=2))
    else:
        print("❌ Не удалось рассчитать метрики.")
