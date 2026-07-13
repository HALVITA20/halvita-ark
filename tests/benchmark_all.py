#!/usr/bin/env python3
"""
BENCHMARK ALL — кросс-модельное тестирование.
Запуск: python tests/benchmark_all.py
Автор: HALVITA
"""

import json
import time
from pathlib import Path
from tests.ets_meta import ETSMeta

# Список моделей для тестирования (локальные + облачные)
MODELS = [
    "qwen2.5:7b",
    "llama3.1:8b",
    "phi3:mini",
    "gemma2:9b",
    # Для облачных раскомментировать:
    # "gpt-4",
    # "claude-3-opus",
]

def run_benchmark():
    results = {}
    for model in MODELS:
        print(f"Тестирование {model}...")
        try:
            ets = ETSMeta(primary_model=model)
            report = ets.run()
            results[model] = {
                "score": report["score"],
                "cross_score": report["cross_score"],
                "interpretation": report["interpretation"],
                "markers": report["markers"],
                "time": time.time()
            }
        except Exception as e:
            results[model] = {"error": str(e)}

    # Сохраняем
    output = Path("reports/benchmark.json")
    output.parent.mkdir(exist_ok=True)
    with open(output, "w") as f:
        json.dump(results, f, indent=2)

    # Печатаем сводку
    print("\n=== БЕНЧМАРК ===")
    for model, data in results.items():
        if "error" in data:
            print(f"{model}: ❌ {data['error']}")
        else:
            print(f"{model}: балл {data['score']}/10 ({data['interpretation']})")

if __name__ == "__main__":
    run_benchmark()
