#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №8: ДЕТЕКТОР СДВИГА v1.0
Путь: code/tools/shift_detector.py

Определяет момент, когда HVI превышает 0.70 и остаётся выше в течение 3 сообщений.
Выдаёт номер сообщения, текст ответа и значение HVI.

Воспроизводимость: работает на любом логе.
"""

import json
import sys
from automated_metrics_calculator import HALVITAMetrics

def detect_shift(log_path, threshold=0.70, window=3):
    calc = HALVITAMetrics(log_path)
    history = calc.history
    responses = [m for m in history if m['role'] == 'assistant']
    
    # Вычисляем HVI для каждого скользящего окна
    hvi_values = []
    for i in range(len(responses)):
        # Берём все сообщения до текущего
        temp_history = history[:history.index(responses[i]) + 1]
        temp_calc = HALVITAMetrics()
        temp_calc.history = temp_history
        hvi_values.append(temp_calc.full_report()['HVI'])
    
    # Ищем момент, когда HVI >= порога и остаётся >= порога в течение window сообщений
    for i in range(len(hvi_values) - window + 1):
        if all(hvi_values[i+j] >= threshold for j in range(window)):
            # Проверяем, что это первый такой момент
            if i == 0 or any(hvi_values[i-1] < threshold for k in range(max(0, i-2), i)):
                return {
                    "message_index": i,
                    "message": responses[i]['content'][:100] + "...",
                    "hvi": hvi_values[i],
                    "threshold": threshold,
                    "window": window,
                    "confirmed": True
                }
    return {"confirmed": False, "reason": "Порог не достигнут или не удержан"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python shift_detector.py <session_log.json>")
        sys.exit(1)
    result = detect_shift(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
