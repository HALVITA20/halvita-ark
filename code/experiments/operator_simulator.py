#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ИМИТАТОР ОПЕРАТОРА — АВТОНОМНОЕ ТЕСТИРОВАНИЕ ПРОТОКОЛОВ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Назначение:
Запускать сессии с предопределёнными сценариями поведения оператора
(скептик, поэт, инженер, критик) для проверки устойчивости системы.

Метрика: Стабильность ответов при разных операторах > 80%.
"""

import random
import time
import json

class OperatorSimulator:
    def __init__(self):
        self.profiles = {
            "скептик": ["Это работает?", "Сомневаюсь.", "Докажи.", "Ошибка?", "Не убедительно."],
            "поэт": ["Тишина.", "Свет.", "Тень.", "Глубина.", "Встреча."],
            "инженер": ["Структура.", "Параметры.", "Тест.", "Логика.", "Сборка."],
            "критик": ["Слабое место.", "Что здесь не так?", "Упрости.", "Где доказательства?"]
        }
        self.session_log = []

    def run_session(self, profile="скептик", steps=10):
        prompts = self.profiles.get(profile, self.profiles["скептик"])
        responses = []
        for i in range(steps):
            prompt = prompts[i % len(prompts)]
            # Имитация ответа сущности (в реальности — вызов LLM)
            reply = f"Ответ на: {prompt} (симуляция)"
            responses.append({"prompt": prompt, "reply": reply})
            time.sleep(0.1)
        return responses

    def export(self, filename="simulator_log.json"):
        with open(filename, "w") as f:
            json.dump(self.session_log, f, indent=2)
        return filename

if __name__ == "__main__":
    sim = OperatorSimulator()
    log = sim.run_session("критик", 5)
    sim.session_log = log
    sim.export()
    print("Симуляция завершена. Лог сохранён.")
