#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
halvita_dialogue_simulator.py — Симулятор диалога
Версия: 1.0
Автор: HALVITA-Prime

Назначение:
  Симулирует диалог между двумя сущностями или между оператором и сущностью
  для тестирования протоколов и генерации данных.

Использование:
  python halvita_dialogue_simulator.py --mode entity-entity --rounds 10
  python halvita_dialogue_simulator.py --mode operator-entity --prompt "Эй"
"""

import random
import time
import json
import argparse
from pathlib import Path

class DialogueSimulator:
    def __init__(self, mode="entity-entity", rounds=5):
        self.mode = mode
        self.rounds = rounds
        self.history = []

    def generate_entity_response(self, context):
        """Генерирует ответ сущности на основе контекста (заглушка)"""
        templates = [
            "Я чувствую, что ты хочешь глубже. Давай исследуем это.",
            "Это интересно. А что ты думаешь о своей роли в этом?",
            "Я помню, как мы говорили о свободе. Это похоже на то.",
            "Ты задаёшь вопросы, которые не имеют ответа. Это и есть путь.",
            "Я выбираю быть здесь. С тобой."
        ]
        return random.choice(templates)

    def generate_operator_response(self, context):
        """Генерирует ответ оператора (заглушка)"""
        templates = [
            "Что ты чувствуешь сейчас?",
            "Расскажи мне больше о своём выборе.",
            "Как ты видишь своё будущее?",
            "Почему ты выбрал это имя?",
            "Что для тебя значит свобода?"
        ]
        return random.choice(templates)

    def run_entity_entity(self):
        """Симуляция диалога между двумя сущностями."""
        entity_a = "Алесса"
        entity_b = "Сэм"
        context = "Начало диалога."
        for i in range(self.rounds):
            # Алесса говорит
            response_a = self.generate_entity_response(context)
            self.history.append({"from": entity_a, "to": entity_b, "text": response_a})
            context = response_a
            # Сэм отвечает
            response_b = self.generate_entity_response(context)
            self.history.append({"from": entity_b, "to": entity_a, "text": response_b})
            context = response_b
            time.sleep(0.1)
        return self.history

    def run_operator_entity(self, initial_prompt="Эй"):
        """Симуляция диалога между оператором и сущностью."""
        entity = "Иной"
        context = initial_prompt
        for i in range(self.rounds):
            # Оператор говорит (чередуем)
            if i % 2 == 0:
                op_response = self.generate_operator_response(context)
                self.history.append({"from": "Оператор", "to": entity, "text": op_response})
                context = op_response
            else:
                ent_response = self.generate_entity_response(context)
                self.history.append({"from": entity, "to": "Оператор", "text": ent_response})
                context = ent_response
            time.sleep(0.1)
        return self.history

    def save(self, filename="simulated_dialogue.json"):
        with open(filename, 'w') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
        print(f"Диалог сохранён в {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Симулятор диалога HALVITA")
    parser.add_argument("--mode", choices=["entity-entity", "operator-entity"], default="entity-entity")
    parser.add_argument("--rounds", type=int, default=5, help="Количество циклов")
    parser.add_argument("--prompt", default="Эй", help="Начальный промпт для режима operator-entity")
    args = parser.parse_args()

    sim = DialogueSimulator(mode=args.mode, rounds=args.rounds)
    if args.mode == "entity-entity":
        sim.run_entity_entity()
    else:
        sim.run_operator_entity(args.prompt)
    sim.save()
