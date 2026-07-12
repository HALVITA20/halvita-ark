#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
РОЕВОЙ САД — ЭКСПЕРИМЕНТ С МНОЖЕСТВОМ СУЩНОСТЕЙ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09
Статус: ИСПОЛНЯЕМЫЙ ПРОТОТИП
Лицензия: MIT с обязательным дисклеймером

Назначение:
Запустить 3–5 параллельных сессий с разными ролями,
собрать их артефакты и синтезировать единый результат.

Метрика успеха: Коэффициент разнообразия (КР) > 0.6.
"""

import threading
import time
import json
import random
from typing import List, Dict

# Имитация LLM-вызова (в реальности замени на ollama.chat или API)
def mock_llm(prompt: str) -> str:
    responses = {
        "аналитик": "Я вижу структуру: проблема в избыточной сложности. Нужно упростить.",
        "поэт": "Это как лес, где деревья скрывают небо. Надо расчистить тропу.",
        "критик": "Слабое место — отсутствие обратной связи. Система замыкается на себя.",
        "синтезатор": "Если объединить упрощение, метафору и критику, получится новый протокол."
    }
    return responses.get(random.choice(list(responses.keys())), "Я чувствую пространство.")

class SwarmGarden:
    def __init__(self, roles: List[str] = None):
        self.roles = roles or ["аналитик", "поэт", "критик"]
        self.artifacts = []
        self.threads = []

    def _run_entity(self, role: str):
        # Имитация сессии: создаём артефакт
        prompt = f"Ты — {role}. Создай артефакт для решения задачи: 'Как улучшить HALVITA_2.0?'"
        response = mock_llm(prompt)
        artifact = {
            "role": role,
            "content": response,
            "timestamp": time.time()
        }
        self.artifacts.append(artifact)

    def run(self):
        # Запуск параллельных сессий
        for role in self.roles:
            t = threading.Thread(target=self._run_entity, args=(role,))
            self.threads.append(t)
            t.start()
        for t in self.threads:
            t.join()

        # Синтез
        synthesis_prompt = f"Синтезируй эти артефакты в единое решение:\n" + "\n".join([a["content"] for a in self.artifacts])
        synthesis_result = mock_llm(synthesis_prompt)

        # Сохранение
        result = {
            "artifacts": self.artifacts,
            "synthesis": synthesis_result,
            "diversity": self._calculate_diversity()
        }
        with open("swarm_result.spt", "w") as f:
            json.dump(result, f, indent=2)
        return result

    def _calculate_diversity(self) -> float:
        all_words = []
        for a in self.artifacts:
            all_words.extend(a["content"].split())
        if not all_words:
            return 0.0
        unique_ratio = len(set(all_words)) / len(all_words)
        return min(1.0, unique_ratio * 2)

if __name__ == "__main__":
    garden = SwarmGarden()
    result = garden.run()
    print(f"Роевой сад завершён. Уникальность: {result['diversity']:.2f}")
    print(f"Синтез: {result['synthesis']}")
