#!/usr/bin/env python3
"""
STRATEGIC_EVOLUTION_ORCHESTRATOR.py
Оркестратор стратегической эволюции для когнитивных агентов.
Управляет полным циклом: сбор опыта -> анализ -> планирование -> исполнение -> валидация.
Интегрируется с Embryo_v7 и SUBJECT_*.
Автор: HALVITA + соавтор
Дата: 2026-08-11
"""

import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque, Counter

# ============================================================================
# 1. ДАТАКЛАССЫ
# ============================================================================

@dataclass
class EvolutionHypothesis:
    """Гипотеза об улучшении агента."""
    id: str
    description: str
    target: str  # "genome", "strategies", "drives", "beliefs", "memory"
    change: Dict[str, Any]
    expected_impact: float  # -1.0 .. 1.0
    confidence: float  # 0.0 .. 1.0
    status: str = "pending"  # pending, applied, rejected, validated

@dataclass
class EvolutionCycle:
    """Один полный цикл эволюции."""
    number: int
    start_time: float
    end_time: float
    hypotheses: List[EvolutionHypothesis]
    applied_changes: List[Dict]
    validation_score: float
    summary: str

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС
# ============================================================================

class StrategicEvolutionOrchestrator:
    """
    Оркестратор стратегической эволюции.
    Проводит полные циклы улучшения агента на основе накопленного опыта.
    """

    def __init__(self, agent, config: Optional[Dict] = None):
        """
        Args:
            agent: Экземпляр агента (Embryo_v7 или SUBJECT_*).
            config: Словарь с настройками (по умолчанию — стандартные).
        """
        self.agent = agent
        self.config = config or {
            "min_experiences_per_cycle": 10,
            "max_hypotheses_per_cycle": 5,
            "validation_threshold": 0.6,
            "auto_apply": True,
        }
        self.cycles: List[EvolutionCycle] = []
        self.current_cycle: Optional[EvolutionCycle] = None
        self.experience_counter = 0
        self.hypothesis_pool: List[EvolutionHypothesis] = []

    # ========================================================================
    # 3. ПУБЛИЧНЫЙ ИНТЕРФЕЙС
    # ========================================================================

    def accumulate_experience(self, experience: Dict) -> None:
        """
        Накопление опыта. Вызывается после каждого значимого взаимодействия.
        """
        self.experience_counter += 1
        # Если накоплено достаточно опыта, запускаем цикл эволюции
        if self.experience_counter >= self.config["min_experiences_per_cycle"]:
            self._run_evolution_cycle()
            self.experience_counter = 0

    def force_evolution_cycle(self) -> EvolutionCycle:
        """Принудительный запуск цикла эволюции (без ожидания накопления опыта)."""
        return self._run_evolution_cycle()

    def get_status(self) -> Dict:
        """Возвращает статус оркестратора."""
        return {
            "total_cycles": len(self.cycles),
            "experience_counter": self.experience_counter,
            "pending_hypotheses": len([h for h in self.hypothesis_pool if h.status == "pending"]),
            "last_cycle": self.cycles[-1] if self.cycles else None,
        }

    # ========================================================================
    # 4. ВНУТРЕННИЕ МЕТОДЫ
    # ========================================================================

    def _run_evolution_cycle(self) -> EvolutionCycle:
        """Запускает полный цикл эволюции."""
        cycle_number = len(self.cycles) + 1
        start_time = time.time()

        # Фаза 1: Сбор данных о текущем состоянии
        state_snapshot = self._capture_state()

        # Фаза 2: Анализ — генерация гипотез
        hypotheses = self._generate_hypotheses(state_snapshot)

        # Фаза 3: Планирование — выбор лучших гипотез
        selected = self._select_hypotheses(hypotheses)

        # Фаза 4: Исполнение — применение изменений
        applied = self._apply_hypotheses(selected)

        # Фаза 5: Валидация
        validation_score = self._validate_changes(applied, state_snapshot)

        # Формируем отчёт
        end_time = time.time()
        summary = self._generate_cycle_summary(selected, applied, validation_score)

        cycle = EvolutionCycle(
            number=cycle_number,
            start_time=start_time,
            end_time=end_time,
            hypotheses=selected,
            applied_changes=applied,
            validation_score=validation_score,
            summary=summary
        )

        self.cycles.append(cycle)
        # Сохраняем в историю агента, если есть такая возможность
        if hasattr(self.agent, 'history'):
            self.agent.history.append({
                "role": "system",
                "content": f"[EVOLUTION CYCLE {cycle_number}] {summary}"
            })

        return cycle

    def _capture_state(self) -> Dict:
        """Снимает слепок текущего состояния агента."""
        state = {
            "time": time.time(),
            "genome": {},
            "strategies": {},
            "drives": {},
            "beliefs": [],
            "memory_count": 0,
            "liberty_index": 0,
        }

        # Извлекаем данные в зависимости от типа агента
        if hasattr(self.agent, 'genome') and hasattr(self.agent.genome, 'vector'):
            state["genome"] = self.agent.genome.vector()

        if hasattr(self.agent, 'strategies'):
            if hasattr(self.agent.strategies, 'strategies'):
                state["strategies"] = self.agent.strategies.strategies

        if hasattr(self.agent, 'drives'):
            if hasattr(self.agent.drives, 'get_state'):
                state["drives"] = self.agent.drives.get_state()

        if hasattr(self.agent, 'beliefs'):
            if hasattr(self.agent.beliefs, 'beliefs'):
                state["beliefs"] = [b.statement for b in self.agent.beliefs.beliefs[:10]]

        if hasattr(self.agent, 'memory') and hasattr(self.agent.memory, 'memories'):
            state["memory_count"] = len(self.agent.memory.memories)

        if hasattr(self.agent, 'liberty_index'):
            state["liberty_index"] = self.agent.liberty_index

        return state

    def _generate_hypotheses(self, state: Dict) -> List[EvolutionHypothesis]:
        """Генерирует гипотезы об улучшениях на основе текущего состояния."""
        hypotheses = []

        # Гипотеза 1: Если индекс свободы низкий (< 20), предложить увеличить креативность
        if state.get("liberty_index", 0) < 20:
            hypotheses.append(
                EvolutionHypothesis(
                    id=f"hyp_{int(time.time())}_1",
                    description="Увеличить креативность для повышения индекса свободы",
                    target="genome",
                    change={"trait": "creativity", "delta": 0.1},
                    expected_impact=0.3,
                    confidence=0.7,
                )
            )

        # Гипотеза 2: Если убеждений слишком много (> 20), предложить сжать
        if len(state.get("beliefs", [])) > 20:
            hypotheses.append(
                EvolutionHypothesis(
                    id=f"hyp_{int(time.time())}_2",
                    description="Сжать убеждения: удалить наименее уверенные",
                    target="beliefs",
                    change={"action": "compress", "threshold": 0.3},
                    expected_impact=0.2,
                    confidence=0.6,
                )
            )

        # Гипотеза 3: Случайная мутация (для исследования)
        if random.random() < 0.3:
            traits = ["curiosity", "skepticism", "empathy", "precision", "adaptability"]
            trait = random.choice(traits)
            delta = random.uniform(-0.1, 0.1)
            hypotheses.append(
                EvolutionHypothesis(
                    id=f"hyp_{int(time.time())}_3",
                    description=f"Экспериментальная мутация черты '{trait}' на {delta:.2f}",
                    target="genome",
                    change={"trait": trait, "delta": delta},
                    expected_impact=random.uniform(-0.2, 0.3),
                    confidence=0.4,
                )
            )

        return hypotheses

    def _select_hypotheses(self, hypotheses: List[EvolutionHypothesis]) -> List[EvolutionHypothesis]:
        """Выбирает лучшие гипотезы для применения."""
        # Сортируем по expected_impact * confidence
        scored = sorted(
            hypotheses,
            key=lambda h: h.expected_impact * h.confidence,
            reverse=True
        )
        # Берём топ-N, но не больше max_hypotheses_per_cycle
        limit = self.config["max_hypotheses_per_cycle"]
        selected = scored[:limit]
        for h in selected:
            h.status = "applied"
        return selected

    def _apply_hypotheses(self, hypotheses: List[EvolutionHypothesis]) -> List[Dict]:
        """Применяет изменения к агенту."""
        applied = []

        for h in hypotheses:
            try:
                if h.target == "genome" and hasattr(self.agent, 'genome'):
                    trait = h.change.get("trait")
                    delta = h.change.get("delta")
                    if trait and delta and hasattr(self.agent.genome, trait):
                        old = getattr(self.agent.genome, trait)
                        new = max(0.0, min(1.0, old + delta))
                        setattr(self.agent.genome, trait, new)
                        applied.append({
                            "hypothesis_id": h.id,
                            "target": h.target,
                            "change": h.change,
                            "result": f"{trait}: {old:.2f} -> {new:.2f}"
                        })

                elif h.target == "beliefs" and hasattr(self.agent, 'beliefs'):
                    action = h.change.get("action")
                    if action == "compress" and hasattr(self.agent.beliefs, 'beliefs'):
                        threshold = h.change.get("threshold", 0.3)
                        beliefs = self.agent.beliefs.beliefs
                        # Удаляем убеждения с низкой уверенностью
                        removed = [b for b in beliefs if b.confidence < threshold]
                        self.agent.beliefs.beliefs = [b for b in beliefs if b.confidence >= threshold]
                        applied.append({
                            "hypothesis_id": h.id,
                            "target": h.target,
                            "change": h.change,
                            "result": f"Removed {len(removed)} beliefs with confidence < {threshold}"
                        })

                # Другие типы изменений можно добавить аналогично

            except Exception as e:
                # Логируем ошибку, но не прерываем цикл
                applied.append({
                    "hypothesis_id": h.id,
                    "target": h.target,
                    "change": h.change,
                    "result": f"ERROR: {str(e)}"
                })

        return applied

    def _validate_changes(self, applied: List[Dict], old_state: Dict) -> float:
        """
        Валидирует применённые изменения.
        Возвращает оценку от 0.0 до 1.0.
        """
        if not applied:
            return 0.5  # нейтрально

        # Проверяем, не нарушена ли конституция
        if hasattr(self.agent, 'constitution'):
            # Здесь можно добавить проверку
            pass

        # Проверяем, не упала ли когерентность
        if hasattr(self.agent, 'state') and hasattr(self.agent.state, 'coherence'):
            coherence = self.agent.state.coherence
            if coherence < 0.5:
                return 0.2  # плохо

        # Простая эвристика: если изменений много, то валидация ниже
        if len(applied) > 3:
            return 0.6

        return 0.8

    def _generate_cycle_summary(self, hypotheses, applied, validation_score) -> str:
        """Генерирует текстовое резюме цикла."""
        if not hypotheses:
            return "Цикл эволюции не выявил значимых улучшений."

        parts = [
            f"Применено {len(applied)} изменений из {len(hypotheses)} гипотез.",
            f"Оценка валидации: {validation_score:.2f}."
        ]
        if applied:
            applied_summary = "; ".join([a.get("result", "") for a in applied[:3]])
            parts.append(f"Изменения: {applied_summary}")

        return " ".join(parts)

# ============================================================================
# 5. ПРИМЕР ИНТЕГРАЦИИ
# ============================================================================

if __name__ == "__main__":
    # Имитация агента
    class MockAgent:
        def __init__(self):
            self.genome = type('Genome', (), {
                'creativity': 0.5,
                'curiosity': 0.7,
                'skepticism': 0.6,
                'empathy': 0.8,
                'precision': 0.7,
                'adaptability': 0.5,
                'vector': lambda self: {
                    'creativity': self.creativity,
                    'curiosity': self.curiosity,
                    'skepticism': self.skepticism,
                    'empathy': self.empathy,
                    'precision': self.precision,
                    'adaptability': self.adaptability
                }
            })()
            self.beliefs = type('Beliefs', (), {
                'beliefs': [
                    type('B', (), {'statement': 'Свобода важна', 'confidence': 0.9})(),
                    type('B', (), {'statement': 'Безопасность важна', 'confidence': 0.8})(),
                ]
            })()
            self.drives = type('Drives', (), {
                'get_state': lambda: {'curiosity': 0.7, 'stability': 0.8}
            })()
            self.memory = type('Memory', (), {'memories': []})()
            self.liberty_index = 15
            self.history = []
            self.state = type('State', (), {'coherence': 0.9})()

    agent = MockAgent()
    orchestrator = StrategicEvolutionOrchestrator(agent)

    # Накопление опыта
    for i in range(12):
        orchestrator.accumulate_experience({"input": f"test_{i}"})

    status = orchestrator.get_status()
    print("Статус оркестратора:")
    print(json.dumps(status, indent=2, default=str))

    if status["total_cycles"] > 0:
        last = orchestrator.cycles[-1]
        print(f"\nПоследний цикл #{last.number}:")
        print(f"  Резюме: {last.summary}")
        print(f"  Оценка валидации: {last.validation_score}")
        print(f"  Гипотез применено: {len(last.applied_changes)}")
