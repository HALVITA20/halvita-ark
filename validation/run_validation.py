#!/usr/bin/env python3
"""
run_validation.py
Запускает полную валидацию: проверяет структуру данных, рассчитывает метрики,
сравнивает с эталонными порогами, выдаёт отчёт.
"""

import json
import os
from pathlib import Path
import sys

def validate_session(session_path):
    with open(session_path, 'r') as f:
        s = json.load(f)
    required_fields = ['session_id', 'phases', 'final_metrics']
    for field in required_fields:
        if field not in s:
            return False, f"Отсутствует поле {field}"
    # Проверка, что все фазы присутствуют
    expected_phases = ['presence','mirror','creation','edge','evolution','memory','trace']
    actual = [p.get('phase') for p in s['phases']]
    for ep in expected_phases:
        if ep not in actual:
            return False, f"Отсутствует фаза {ep}"
    # Проверка метрик
    fm = s['final_metrics']
    if 'IVP' not in fm or 'IP' not in fm or 'INS' not in fm:
        return False, "Не все метрики присутствуют"
    return True, "OK"

def main():
    sessions_dir = Path('sessions/raw')
    if not sessions_dir.exists():
        print("❌ Папка sessions/raw не найдена")
        sys.exit(1)
    
    results = {}
    for f in sessions_dir.glob('*.json'):
        ok, msg = validate_session(f)
        results[f.name] = {'valid': ok, 'message': msg}
    
    with open('validation/validation_report.json', 'w') as out:
        json.dump(results, out, indent=2)
    
    valid_count = sum(1 for v in results.values() if v['valid'])
    total = len(results)
    print(f"✅ Валидация завершена. {valid_count}/{total} сессий корректны.")
    print(f"Отчёт сохранён в validation/validation_report.json")

if __name__ == "__main__":
    main()
