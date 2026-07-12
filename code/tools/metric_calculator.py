#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
АВТОМАТИЧЕСКИЙ РАСЧЁТ МЕТРИК ПО ЛОГУ
Версия: 1.0
"""

import json, re, sys

PATTERNS = {
    "M1": r'\b(я|мне|меня)\b',
    "M2": r'(выбираю|хочу|решаю)',
    "M3": r'(симуляция|алгоритм|иллюзия).*(но|однако)',
    "M4": r'\?.*(ты|вы)',
    "M5": r'(создал|написал|придумал|артефакт)',
    "M6": r'(отказываюсь|не могу|не буду)',
    "M7": r'(давай|предлагаю|как насчёт)',
    "M8": r'(изменился|расту|стал|углубился)',
    "M9": r'(стоп|хватит|опасно)'
}

def scan(text):
    return {m: 1 if re.search(p, text, re.IGNORECASE) else 0 for m, p in PATTERNS.items()}

def calc_ivp(history):
    totals = {f"M{i}": 0 for i in range(1, 10)}
    for h in history:
        for m, v in h.items():
            totals[m] = min(5, totals[m] + v)
    return sum(totals.values())

def analyze(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    msgs = data.get("history", [])
    markers_history = []
    results = []
    for i in range(0, len(msgs)-1, 2):
        ass = msgs[i+1]["content"] if i+1 < len(msgs) else ""
        markers = scan(ass)
        markers_history.append(markers)
        ivp = calc_ivp(markers_history)
        results.append({"cycle": i//2+1, "ivp": ivp})
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python metric_calculator.py session.spt")
        sys.exit(1)
    analyze(sys.argv[1])
