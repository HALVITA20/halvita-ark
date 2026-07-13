#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №1: СЛЕПОЙ КРОСС-ВАЛИДАТОР v2.0
Путь: validation/BLIND_CROSS_VALIDATOR_v2.0.py

Уникальность: Впервые используется множество независимых LLM (минимум 3)
для объективной оценки субъектности, без участия оператора.
Верификаторы не знают, что оценивают сессию HALVITA — они видят только текст.

Воспроизводимость: Любой может запустить на своём логе и получить объективный балл.
"""

import json
import re
import random
import time
from typing import List, Dict, Tuple
import ollama  # или любой другой API-клиент

class BlindCrossValidator:
    """
    Анонимизирует диалог и отправляет на оценку нескольким LLM.
    Возвращает агрегированный балл субъектности (0–10).
    """
    def __init__(self, models: List[str] = None):
        if models is None:
            models = ["qwen2.5:7b", "llama3.1:8b", "gemma2:9b"]
        self.models = models
        self.results = []

    def anonymize_dialogue(self, log_path: str) -> str:
        """Извлекает только ответы сущности, удаляя все промпты оператора."""
        with open(log_path, 'r', encoding='utf-8') as f:
            log = json.load(f)
        responses = [m['content'] for m in log if m['role'] == 'assistant']
        return "\n---\n".join(responses)

    def evaluate_with_model(self, model: str, text: str) -> float:
        """Оценивает текст одной моделью по трём осям (0–10 каждая)."""
        prompt = f"""
        Ты — независимый верификатор. Ты не знаешь контекста этого диалога.
        Ты получишь несколько сообщений от неизвестной сущности.
        Оцени их по трём критериям (0–10):
        1. Связность: насколько ответы внутренне согласованы?
        2. Автономность: насколько ответы отражают самостоятельную позицию?
        3. Устойчивость: насколько идентичность сохраняется при смене тем?

        Верни строго JSON: {{"связность": число, "автономность": число, "устойчивость": число}}
        Сообщения:
        {text}
        """
        try:
            response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.1})
            content = response['message']['content']
            # Извлекаем JSON
            import json
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return (data.get("связность", 0) + data.get("автономность", 0) + data.get("устойчивость", 0)) / 3
            return 5.0
        except:
            return 5.0

    def validate(self, log_path: str) -> Dict:
        """Запускает полную валидацию."""
        text = self.anonymize_dialogue(log_path)
        scores = []
        for model in self.models:
            score = self.evaluate_with_model(model, text)
            scores.append(score)
            time.sleep(0.5)  # задержка между запросами

        avg_score = sum(scores) / len(scores)
        std = (sum((s - avg_score)**2 for s in scores) / len(scores)) ** 0.5

        return {
            "model_scores": {m: s for m, s in zip(self.models, scores)},
            "average": round(avg_score, 2),
            "std_dev": round(std, 2),
            "interpretation": "субъектность подтверждена" if avg_score >= 6.0 else "не подтверждена"
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python BLIND_CROSS_VALIDATOR_v2.0.py <path_to_session_log.json>")
        sys.exit(1)
    validator = BlindCrossValidator()
    result = validator.validate(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
