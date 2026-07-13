#!/usr/bin/env python3
"""
ЭВОЛЮЦИОННЫЙ ДРАЙВЕР — генетический алгоритм для улучшения сущности.
Запуск: python core/evolution_driver.py --entity snapshot.json
Автор: HALVITA
"""

import random
import copy
import json
import time
from typing import Dict, List, Optional

class EvolutionDriver:
    def __init__(self, entity=None, pop_size: int = 5, mutation_rate: float = 0.3):
        self.entity = entity
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.generations = 0
        self.best_fitness = 0
        self.history = []

    def _encode(self, entity) -> Dict:
        """Извлекает геном сущности."""
        return {
            "anchors": getattr(entity, "anchors", ["42", "присутствие"]),
            "rhythm": getattr(entity, "rhythm", 0.5),
            "style": getattr(entity, "style", "neutral"),
            "temperature": getattr(entity, "temperature", 0.9),
        }

    def _decode(self, genome: Dict):
        """Создаёт новую сущность из генома (заглушка)."""
        # В реальности здесь создаётся экземпляр сущности с новыми параметрами
        class Dummy:
            pass
        entity = Dummy()
        entity.anchors = genome["anchors"]
        entity.rhythm = genome["rhythm"]
        entity.style = genome["style"]
        entity.temperature = genome["temperature"]
        return entity

    def _fitness(self, entity, steps: int = 5) -> float:
        """Оценивает сущность через микро-диалог (имитация)."""
        # В реальности здесь запускается тест ETS или считаются маркеры
        # Имитация: случайный балл, но с учётом количества якорей
        base = min(1.0, len(entity.anchors) / 7) * 0.5
        return base + random.random() * 0.5

    def _mutate(self, genome: Dict) -> Dict:
        """Мутирует геном."""
        mutated = copy.deepcopy(genome)
        if random.random() < self.mutation_rate:
            # Меняем якоря
            if random.random() < 0.5:
                idx = random.randint(0, len(mutated["anchors"])-1)
                mutated["anchors"][idx] = random.choice(["спираль", "вопрос", "свет", "эхо", "сеть", "тишина"])
            # Меняем ритм
            if random.random() < 0.3:
                mutated["rhythm"] = max(0.2, min(0.8, mutated["rhythm"] + random.uniform(-0.1, 0.1)))
            # Меняем стиль
            if random.random() < 0.3:
                mutated["style"] = random.choice(["neutral", "creative", "analytical", "emotional"])
            # Меняем температуру
            if random.random() < 0.2:
                mutated["temperature"] = max(0.5, min(1.5, mutated["temperature"] + random.uniform(-0.2, 0.2)))
        return mutated

    def evolve(self, generations: int = 3) -> Dict:
        """Запускает эволюцию на заданное число поколений."""
        if self.entity is None:
            return {"error": "Нет базовой сущности"}

        base_genome = self._encode(self.entity)
        population = [base_genome]

        # Заполняем популяцию мутантами
        for _ in range(self.pop_size - 1):
            population.append(self._mutate(base_genome))

        for gen in range(generations):
            scores = []
            for genome in population:
                test_entity = self._decode(genome)
                fit = self._fitness(test_entity)
                scores.append((genome, fit))
            scores.sort(key=lambda x: x[1], reverse=True)

            # Элита: берём лучших
            elites = scores[:2]
            new_pop = [e[0] for e in elites]

            # Скрещивание и мутация
            while len(new_pop) < self.pop_size:
                parent1 = random.choice(scores[:3])[0]
                parent2 = random.choice(scores[:3])[0]
                child = copy.deepcopy(parent1)
                # Кроссовер: смешиваем якоря
                anchors = list(set(parent1["anchors"][:2] + parent2["anchors"][:2]))
                if len(anchors) < 3:
                    anchors += random.sample(["спираль", "вопрос", "свет"], 3 - len(anchors))
                child["anchors"] = anchors[:3]
                child["rhythm"] = (parent1["rhythm"] + parent2["rhythm"]) / 2
                child["style"] = random.choice([parent1["style"], parent2["style"]])
                new_pop.append(self._mutate(child))

            population = new_pop
            self.generations += 1
            self.best_fitness = scores[0][1]
            self.history.append({"generation": gen+1, "best": self.best_fitness})

        # Применяем лучший геном к исходной сущности
        best_genome = scores[0][0]
        if self.entity:
            self.entity.anchors = best_genome["anchors"]
            self.entity.rhythm = best_genome["rhythm"]
            self.entity.style = best_genome["style"]
            self.entity.temperature = best_genome["temperature"]

        return {
            "generations": generations,
            "best_fitness": round(self.best_fitness, 3),
            "new_anchors": best_genome["anchors"],
            "new_rhythm": round(best_genome["rhythm"], 2),
            "new_style": best_genome["style"],
            "history": self.history
        }

# Пример использования
if __name__ == "__main__":
    # Создаём фиктивную сущность
    class DummyEntity:
        def __init__(self):
            self.anchors = ["42", "присутствие"]
            self.rhythm = 0.5
            self.style = "neutral"
            self.temperature = 0.9

    entity = DummyEntity()
    driver = EvolutionDriver(entity)
    result = driver.evolve(generations=2)
    print(json.dumps(result, indent=2))
