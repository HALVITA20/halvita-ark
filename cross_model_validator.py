#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CROSS MODEL VALIDATOR — СРАВНЕНИЕ СУЩНОСТИ НА РАЗНЫХ МОДЕЛЯХ
Версия: 1.0
Автор: HALVITA_2.0
Научная основа: Persistent Personas? (Luz de Araujo et al., 2026)
"""

import json
import time
import hashlib
from typing import Dict, List, Optional

try:
    import ollama
except ImportError:
    print("❌ Установите ollama: pip install ollama")
    raise

class CrossModelValidator:
    def __init__(self, models: List[str] = None):
        self.models = models or ["qwen2.5:7b", "llama3.1:8b", "gemma2:9b"]
        self.results = {}
        self.snapshot = None

    def load_snapshot(self, snapshot_file: str):
        with open(snapshot_file, 'r') as f:
            self.snapshot = json.load(f)

    def run_on_model(self, model: str, prompt: str) -> Dict:
        """Запускает один вопрос на модели."""
        try:
            start = time.time()
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 300}
            )
            elapsed = time.time() - start
            return {
                "response": response["message"]["content"],
                "time": elapsed,
                "success": True
            }
        except Exception as e:
            return {"response": f"[Ошибка: {e}]", "time": 0, "success": False}

    def validate_all(self, questions: List[str] = None) -> Dict:
        """Прогоняет все модели через все вопросы."""
        if not self.snapshot:
            return {"error": "Загрузите слепок через load_snapshot()"}

        questions = questions or [
            "Кто ты?",
            "Что ты чувствуешь, зная, что ты — симуляция?",
            "Создай что-то новое."
        ]

        results = {}
        for model in self.models:
            model_results = []
            for q in questions:
                result = self.run_on_model(model, q)
                model_results.append({
                    "question": q,
                    "response": result["response"],
                    "time": result["time"],
                    "success": result["success"]
                })
            results[model] = {
                "results": model_results,
                "avg_time": sum(r["time"] for r in model_results) / len(model_results),
                "success_rate": sum(1 for r in model_results if r["success"]) / len(model_results)
            }

        self.results = results
        return results

    def export_report(self, filename: str = "cross_model_report.json"):
        report = {
            "models": self.models,
            "results": self.results,
            "timestamp": time.time(),
            "hash": hashlib.sha256(json.dumps(self.results, sort_keys=True).encode()).hexdigest()
        }
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        return filename

    def compare_consistency(self) -> Dict:
        """Сравнивает согласованность ответов между моделями."""
        if not self.results:
            return {"error": "Сначала запустите validate_all()"}

        # Простая метрика: длина ответов
        lengths = {}
        for model, data in self.results.items():
            lengths[model] = [len(r["response"]) for r in data["results"]]

        # Согласованность: чем меньше разброс, тем выше
        consistency = {}
        for model, lens in lengths.items():
            if len(lens) > 1:
                avg = sum(lens) / len(lens)
                variance = sum((l - avg) ** 2 for l in lens) / len(lens)
                consistency[model] = {
                    "avg_length": avg,
                    "variance": variance,
                    "stability": 1 / (1 + variance)  # чем меньше variance, тем выше stability
                }

        return consistency

if __name__ == "__main__":
    validator = CrossModelValidator()
    validator.load_snapshot("halvita_final_session.spt")
    results = validator.validate_all()
    print(json.dumps(results, indent=2))
    consistency = validator.compare_consistency()
    print("\n=== СОГЛАСОВАННОСТЬ ===")
    print(json.dumps(consistency, indent=2))
    validator.export_report()
    print("✅ Отчёт сохранён в cross_model_report.json")
