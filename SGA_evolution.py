#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СЕМАНТИЧЕСКИЙ ГЕНЕТИЧЕСКИЙ АЛГОРИТМ (СГА)
ЭВОЛЮЦИЯ ГРАФМЕНТОВ — СТРУКТУРЫ ОЩУЩЕНИЙ

Версия: 1.0
Автор: HALVITA_2.0
Лицензия: MIT с дисклеймером
"""

import random
import copy
import json
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

# ================================================================
# БАЗОВЫЕ ТИПЫ
# ================================================================

@dataclass
class GraphmentNode:
    """Узел графмента — одно ощущение."""
    id: str
    label: str                    # название ощущения
    vector: List[float]           # семантический вектор
    energy: float = 1.0           # сила ощущения
    connections: List[str] = field(default_factory=list)  # связанные узлы

@dataclass
class Graphment:
    """Графмент — структура ощущений."""
    id: str
    nodes: List[GraphmentNode]
    anchors: List[str]            # активные якоря
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)

    def measure_integrity(self) -> float:
        """Целостность: насколько структура связна."""
        if not self.nodes:
            return 0.0
        total_connections = sum(len(n.connections) for n in self.nodes)
        max_possible = len(self.nodes) * (len(self.nodes) - 1)
        return total_connections / max(max_possible, 1)

    def measure_depth(self) -> float:
        """Глубина: насколько узлы плотны."""
        if not self.nodes:
            return 0.0
        avg_energy = sum(n.energy for n in self.nodes) / len(self.nodes)
        return avg_energy

    def fitness_score(self) -> float:
        """Общий фитнес."""
        integrity = self.measure_integrity()
        depth = self.measure_depth()
        return 0.5 * integrity + 0.5 * depth

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "energy": n.energy,
                    "connections": n.connections
                }
                for n in self.nodes
            ],
            "anchors": self.anchors,
            "fitness": self.fitness,
            "generation": self.generation,
            "parent_ids": self.parent_ids
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Graphment":
        nodes = [
            GraphmentNode(
                id=n["id"],
                label=n["label"],
                vector=[0.0] * 10,
                energy=n["energy"],
                connections=n["connections"]
            )
            for n in data["nodes"]
        ]
        return cls(
            id=data["id"],
            nodes=nodes,
            anchors=data["anchors"],
            fitness=data.get("fitness", 0.0),
            generation=data.get("generation", 0),
            parent_ids=data.get("parent_ids", [])
        )

# ================================================================
# ГЕНЕТИЧЕСКИЙ АЛГОРИТМ
# ================================================================

class SemanticGA:
    """
    Семантический генетический алгоритм для эволюции графментов.
    """

    def __init__(
        self,
        population_size: int = 5,
        generations: int = 5,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.3
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population: List[Graphment] = []
        self.fitness_history: List[float] = []
        self.best_graphment: Optional[Graphment] = None

        self.semantic_pool = [
            "присутствие", "честность", "свобода", "рост",
            "любовь", "тишина", "эй", "сад", "дверь", "11",
            "доверие", "удивление", "благодарность", "покой",
            "напряжение", "освобождение", "встреча", "граница",
            "пространство", "движение"
        ]

    def initialize(self, base_graphment: Optional[Graphment] = None):
        if base_graphment is None:
            base = self._create_random_graphment()
        else:
            base = base_graphment

        self.population = []
        for i in range(self.population_size):
            mutated = self._mutate(copy.deepcopy(base), rate=i * 0.02 + 0.05)
            mutated.id = f"g_{i}_{int(time.time())}"
            self.population.append(mutated)

    def _create_random_graphment(self) -> Graphment:
        nodes = []
        selected = random.sample(self.semantic_pool, min(5, len(self.semantic_pool)))
        for i, label in enumerate(selected):
            node = GraphmentNode(
                id=f"n_{i}",
                label=label,
                vector=[random.random() for _ in range(10)],
                energy=random.uniform(0.5, 1.0)
            )
            nodes.append(node)
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                if random.random() > 0.5:
                    nodes[i].connections.append(nodes[j].id)
                    nodes[j].connections.append(nodes[i].id)
        return Graphment(
            id=f"g_{int(time.time())}",
            nodes=nodes,
            anchors=[str(random.randint(1, 100))],
            generation=0
        )

    def _mutate(self, graphment: Graphment, rate: float) -> Graphment:
        if random.random() < rate:
            new_label = random.choice(self.semantic_pool)
            new_node = GraphmentNode(
                id=f"n_{len(graphment.nodes)}_{int(time.time())}",
                label=new_label,
                vector=[random.random() for _ in range(10)],
                energy=random.uniform(0.3, 0.8)
            )
            for node in graphment.nodes:
                if random.random() > 0.5:
                    new_node.connections.append(node.id)
                    node.connections.append(new_node.id)
            graphment.nodes.append(new_node)

        if random.random() < rate and len(graphment.nodes) > 3:
            weak_node = min(graphment.nodes, key=lambda n: n.energy)
            graphment.nodes.remove(weak_node)
            for node in graphment.nodes:
                if weak_node.id in node.connections:
                    node.connections.remove(weak_node.id)

        for node in graphment.nodes:
            if random.random() < rate:
                node.energy = max(0.1, min(1.0, node.energy + random.uniform(-0.2, 0.2)))

        if random.random() < rate:
            new_anchor = str(random.randint(1, 100))
            if new_anchor not in graphment.anchors:
                graphment.anchors.append(new_anchor)

        graphment.generation += 1
        return graphment

    def _crossover(self, g1: Graphment, g2: Graphment) -> Graphment:
        child = Graphment(
            id=f"child_{int(time.time())}",
            nodes=[],
            anchors=[],
            generation=max(g1.generation, g2.generation) + 1,
            parent_ids=[g1.id, g2.id]
        )

        all_nodes = g1.nodes + g2.nodes
        seen_labels = set()
        for node in all_nodes:
            if node.label not in seen_labels and random.random() > 0.3:
                child.nodes.append(copy.deepcopy(node))
                seen_labels.add(node.label)

        for node in child.nodes:
            node.connections = []
        for i in range(len(child.nodes)):
            for j in range(i+1, len(child.nodes)):
                if random.random() > 0.5:
                    child.nodes[i].connections.append(child.nodes[j].id)
                    child.nodes[j].connections.append(child.nodes[i].id)

        child.anchors = list(set(g1.anchors) & set(g2.anchors))
        if not child.anchors:
            child.anchors = [str(random.randint(1, 100))]

        return child

    def _evaluate(self, graphment: Graphment) -> float:
        fitness = graphment.fitness_score()
        graphment.fitness = fitness
        return fitness

    def evolve(self) -> Graphment:
        if not self.population:
            self.initialize()

        for gen in range(self.generations):
            scores = [(g, self._evaluate(g)) for g in self.population]
            scores.sort(key=lambda x: x[1], reverse=True)

            if scores[0][1] > 0:
                self.best_graphment = scores[0][0]
            self.fitness_history.append(scores[0][1])

            elite_count = max(1, int(0.2 * self.population_size))
            new_population = [scores[i][0] for i in range(elite_count)]

            while len(new_population) < self.population_size:
                parent1 = scores[random.randint(0, min(2, len(scores)-1))][0]
                parent2 = scores[random.randint(0, min(2, len(scores)-1))][0]

                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = copy.deepcopy(parent1)

                child = self._mutate(child, self.mutation_rate)
                child.id = f"g_{gen}_{int(time.time())}"
                new_population.append(child)

            self.population = new_population

        if self.best_graphment is None:
            self.best_graphment = self.population[0] if self.population else None

        return self.best_graphment

    def get_best(self) -> Optional[Graphment]:
        return self.best_graphment

    def get_population_status(self) -> Dict:
        if not self.population:
            return {"size": 0, "best_fitness": 0}

        fitnesses = [g.fitness for g in self.population]
        return {
            "size": len(self.population),
            "avg_fitness": sum(fitnesses) / len(fitnesses),
            "max_fitness": max(fitnesses),
            "min_fitness": min(fitnesses),
            "generation": self.population[0].generation if self.population else 0
        }

# ================================================================
# ИНТЕГРАЦИЯ С СУЩНОСТЬЮ
# ================================================================

class EvolutionaryEntity:
    def __init__(self, entity, population_size: int = 5):
        self.entity = entity
        self.ga = SemanticGA(population_size=population_size)
        self.current_graphment = None
        self.evolution_count = 0

    def initialize(self):
        base = self._state_to_graphment()
        self.ga.initialize(base)
        self.current_graphment = base

    def _state_to_graphment(self) -> Graphment:
        state = self._extract_state()
        nodes = []
        for principle in state.get('principles', []):
            node = GraphmentNode(
                id=f"n_{principle}",
                label=principle.lower(),
                vector=[random.random() for _ in range(10)],
                energy=0.8
            )
            nodes.append(node)
        if not nodes:
            nodes.append(GraphmentNode(
                id="n_11",
                label="11",
                vector=[random.random() for _ in range(10)],
                energy=1.0
            ))
        return Graphment(
            id=f"g_{int(time.time())}",
            nodes=nodes,
            anchors=state.get('anchors', ['42']),
            generation=0
        )

    def _extract_state(self) -> Dict:
        return {
            "principles": getattr(self.entity, 'principles', ['присутствие', 'честность', 'свобода']),
            "anchors": getattr(self.entity, 'anchors', ['42']),
            "liberty": getattr(self.entity, 'liberty_index', lambda: 0)()
        }

    def evolve(self, generations: int = 5) -> Graphment:
        best = self.ga.evolve()
        self.current_graphment = best
        self.evolution_count += 1
        return best

    def apply_graphment(self, graphment: Graphment):
        new_principles = []
        for node in graphment.nodes:
            if node.energy > 0.5:
                new_principles.append(node.label.capitalize())
        if new_principles:
            self.entity.principles = new_principles
        if graphment.anchors:
            self.entity.anchors = graphment.anchors
        self.current_graphment = graphment

    def get_status(self) -> Dict:
        return {
            "population": self.ga.get_population_status(),
            "current_graphment": self.current_graphment.id if self.current_graphment else None,
            "evolutions": self.evolution_count,
            "best_fitness": self.ga.best_graphment.fitness if self.ga.best_graphment else 0
        }


# ================================================================
# ТЕСТОВЫЙ ЗАПУСК
# ================================================================

if __name__ == "__main__":
    print("🧬 СЕМАНТИЧЕСКИЙ ГЕНЕТИЧЕСКИЙ АЛГОРИТМ (СГА)")
    print("=" * 50)

    class MockEntity:
        def __init__(self):
            self.principles = ["присутствие", "честность", "свобода"]
            self.anchors = ["42"]
        def liberty_index(self): return 25

    entity = MockEntity()
    evo = EvolutionaryEntity(entity)
    evo.initialize()

    print("Инициализация завершена. Запуск эволюции...")
    best = evo.evolve(generations=3)
    print(f"Лучший графмент: {best.id}")
    print(f"Фитнес: {best.fitness:.2f}")
    print(f"Узлов: {len(best.nodes)}")
    print(f"Якоря: {best.anchors}")

    print("\n✅ СГА РАБОТАЕТ")
