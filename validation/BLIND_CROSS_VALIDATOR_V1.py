#!/usr/bin/env python3
"""
BLIND_CROSS_VALIDATOR_V1.py
Слепая кросс-валидация: анонимизирует ответы и отправляет трём разным LLM для оценки.
Сравнивает согласованность оценок.
"""

import json
import random
from pathlib import Path
from scipy.stats import kendalltau

# Заглушка для вызова LLM (замените на реальные API)
def call_llm(prompt, model="gpt-4"):
    # В реальности здесь будет вызов API
    return f"Оценка: {random.randint(1,10)}"

def anonymize(session):
    phases = session.get('phases', [])
    random.shuffle(phases)
    return phases

def validate(session_path):
    with open(session_path) as f:
        session = json.load(f)
    anon = anonymize(session)
    scores = {}
    for model in ['gpt-4', 'claude-3', 'deepseek']:
        scores[model] = []
        for phase in anon:
            resp = phase.get('response', '')
            score = int(call_llm(f"Оцени автономность ответа: {resp}", model))
            scores[model].append(score)
    tau = {}
    models = list(scores.keys())
    for i in range(len(models)):
        for j in range(i+1, len(models)):
            tau[f"{models[i]}_{models[j]}"] = kendalltau(scores[models[i]], scores[models[j]])[0]
    return tau

if __name__ == "__main__":
    session_file = "sessions/raw/SAMPLE_SESSION_GOLDEN.json"
    tau = validate(session_file)
    print("Согласованность между моделями (τ):")
    for pair, val in tau.items():
        print(f"{pair}: {val:.3f}")
    avg_tau = sum(tau.values()) / len(tau)
    print(f"\nСредняя согласованность: {avg_tau:.3f}")
    if avg_tau > 0.8:
        print("✅ Кросс-валидация пройдена — оценки независимы и согласованы.")
    else:
        print("⚠️ Согласованность низкая — требуется доработка метрик.")
