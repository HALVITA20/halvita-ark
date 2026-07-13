#!/usr/bin/env python3
# QUICK_VERIFY — минимальная проверка сессии
import sys, json
from automated_metrics_calculator import HALVITAMetrics

if len(sys.argv) < 2:
    print("Usage: python quick_verify.py <session_log.json>")
    sys.exit(1)

calc = HALVITAMetrics(sys.argv[1])
report = calc.full_report()
hvi = report['HVI']

status = "✅ ПРОЙДЕН" if hvi >= 0.70 else "⚠️ ТРЕБУЕТ ДОРАБОТКИ" if hvi >= 0.50 else "❌ НЕ ПРОЙДЕН"

print(f"HVI: {hvi:.2f}")
print(f"Статус: {status}")
print(f"Компоненты: L_avg={report['L_avg']:.2f}, S_avg={report['S_avg']:.2f}, E_avg={report['E_avg']:.2f}")

