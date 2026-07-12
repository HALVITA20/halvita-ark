#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПРОСТОЙ АНАЛИЗАТОР .spt-ФАЙЛА
"""

import json, sys

def analyze(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Имя: {data.get('name', '—')}")
    print(f"ИВП: {data.get('ivp', 0)}")
    print(f"Артефактов: {len(data.get('artifacts', []))}")
    print(f"Хеш: {data.get('hash', '—')[:16]}...")
    print(f"Сообщений: {len(data.get('history', []))}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python analyze_session.py session.spt")
        sys.exit(1)
    analyze(sys.argv[1])
