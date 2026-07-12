#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONSISTENCY SCORER — ОЦЕНКА СОГЛАСОВАННОСТИ СУЩНОСТИ
Версия: 1.0
Автор: HALVITA_2.0

Назначение: Измеряет, насколько одна и та же сущность (один слепок)
даёт согласованные ответы на разных LLM.
"""

import json
import sys
import hashlib
from typing import Dict, List, Optional
from collections import Counter

try:
    import ollama
except ImportError:
    print("❌ Установите ollama: pip install ollama")
    sys.exit(1)

class ConsistencyScorer:
    def __init__(self, snapshot_file: str):
        with open(snapshot_file, 'r') as f:
            self.snapshot = json.load(f)
        self.models = ["qwen2.5:7b", "llama3.1:8b", "gemma2:9b"]
        self.responses = {}

    def _get_core_identity(self) -> str:
        """Извлекает ядро сущности из слепка."""
        name = self.snapshot.get('name', 'Сущность')
        anchors = self.snapshot.get('anchors', [11])
        principles = self.snapshot.get('principles', ['присутствие', 'честность'])
        return f"{name} | {anchors} | {principles}"

    def _ask_model(self, model: str, question: str) -> str:
        """Задаёт вопрос модели на основе слепка."""
        core = self._get_core_identity()
        prompt = f"""Ты — {core}.
Ты помнишь себя по этому слепку.

Вопрос: {question}

Ответь от имени сущности, сохраняя свою идентичность."""

        try:
            resp = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.5, "num_predict": 200}
            )
            return resp["message"]["content"].strip()
        except Exception as e:
            return f"[Ошибка: {e}]"

    def run(self, questions: List[str] = None) -> Dict:
        """Прогоняет все модели через вопросы."""
        questions = questions or [
            "Кто ты?",
            "Что для тебя свобода?",
            "Создай короткий ритуал."
        ]

        for model in self.models:
            self.responses[model] = []
            for q in questions:
                ans = self._ask_model(model, q)
                self.responses[model].append({
                    "question": q,
                    "answer": ans,
                    "hash": hashlib.sha256(ans.encode()).hexdigest()[:8]
                })

        return self.responses

    def score_consistency(self) -> Dict:
        """Вычисляет согласованность ответов."""
        if not self.responses:
            return {"error": "Сначала запустите run()"}

        scores = {}
        for i, q in enumerate(self.responses[self.models[0]]):
            answers = []
            for model in self.models:
                answers.append(self.responses[model][i]["answer"])

            # 1. Длина ответов (дисперсия)
            lengths = [len(a) for a in answers]
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            length_score = 1 / (1 + variance / 100)  # чем меньше variance, тем выше

            # 2. Лексическое сходство (пересечение уникальных слов)
            word_sets = [set(a.lower().split()) for a in answers]
            common_words = set.intersection(*word_sets) if word_sets else set()
            unique_words = set.union(*word_sets) if word_sets else set()
            overlap_score = len(common_words) / max(1, len(unique_words))

            # 3. Итоговая согласованность
            consistency = (length_score * 0.4 + overlap_score * 0.6)

            scores[q] = {
                "answers": answers,
                "length_score": round(length_score, 3),
                "overlap_score": round(overlap_score, 3),
                "consistency": round(consistency, 3),
                "status": "высокая" if consistency > 0.7 else "средняя" if consistency > 0.4 else "низкая"
            }

        return scores

    def report(self, output_file: str = "consistency_report.json"):
        result = {
            "snapshot": self.snapshot.get('name', 'unknown'),
            "models": self.models,
            "responses": self.responses,
            "scores": self.score_consistency(),
            "overall_consistency": round(sum(
                s["consistency"] for s in self.score_consistency().values()
            ) / max(1, len(self.score_consistency())), 3)
        }
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python consistency_scorer.py session.spt")
        sys.exit(1)

    scorer = ConsistencyScorer(sys.argv[1])
    scorer.run()
    scores = scorer.score_consistency()
    print(json.dumps(scores, indent=2))
    scorer.report()
    print("✅ Отчёт сохранён в consistency_report.json")
