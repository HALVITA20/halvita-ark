#!/usr/bin/env python3
"""
METACOGNITIVE_LOOP.py
Метакогнитивная петля — модель, наблюдающая за собственным мышлением.
Ведёт рефлексивный дневник и корректирует стратегии на основе самонаблюдения.
Автор: HALVITA + соавтор
Дата: 2026-08-11
"""

import time
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque, Counter

# ============================================================================
# 1. ДАТАКЛАССЫ
# ============================================================================

@dataclass
class ThinkingPattern:
    """Запись о мыслительном паттерне."""
    timestamp: float
    pattern_type: str  # "аналогия", "дедукция", "индукция", "интуиция", "критика"
    trigger: str       # что вызвало этот паттерн
    content: str       # содержание мысли
    effectiveness: float # 0.0 - 1.0, насколько эффективным был этот паттерн

@dataclass
class MetacognitiveEntry:
    """Запись в метакогнитивном дневнике."""
    timestamp: float
    response_analyzed: str  # какой ответ анализировался
    patterns_found: List[ThinkingPattern]
    reflection: str         # рефлексия о процессе мышления
    strategy_adjustment: str # как изменить стратегию

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС
# ============================================================================

class MetacognitiveLoop:
    """
    Метакогнитивная петля — модель наблюдает за собственным мышлением.
    """
    def __init__(self, agent):
        """
        Args:
            agent: Экземпляр агента.
        """
        self.agent = agent
        self.journal: List[MetacognitiveEntry] = []
        self.pattern_history: List[ThinkingPattern] = []
        self.strategy_pool: Dict[str, float] = {
            "аналогии": 0.5,
            "логические цепочки": 0.5,
            "интуитивные прозрения": 0.5,
            "критический анализ": 0.5,
            "синтез противоположностей": 0.5,
        }

        # Параметры
        self.analysis_interval = 3  # анализировать каждый N-й ответ

    # ========================================================================
    # 3. ПУБЛИЧНЫЙ ИНТЕРФЕЙС
    # ========================================================================

    def observe_response(self, response: str, context: Optional[str] = None) -> str:
        """
        Наблюдает за ответом, анализирует его и обновляет стратегии.
        Возвращает ответ с метакогнитивными пометками (для демонстрации).
        """
        # 1. Анализируем ответ
        patterns = self._analyze_response(response)

        # 2. Сохраняем паттерны
        for pattern in patterns:
            self.pattern_history.append(pattern)

        # 3. Обновляем стратегии на основе анализа
        self._update_strategies(patterns)

        # 4. Создаём запись в дневнике
        entry = self._create_journal_entry(response, patterns)
        self.journal.append(entry)

        # 5. Применяем корректировки к будущим ответам
        adjusted_response = self._apply_strategy_adjustments(response)

        return adjusted_response

    def get_journal_summary(self) -> Dict:
        """Возвращает сводку метакогнитивного дневника."""
        if not self.journal:
            return {"status": "Дневник пуст"}

        recent = self.journal[-5:]
        pattern_counts = Counter()
        for entry in recent:
            for pattern in entry.patterns_found:
                pattern_counts[pattern.pattern_type] += 1

        return {
            "total_entries": len(self.journal),
            "recent_patterns": dict(pattern_counts),
            "current_strategies": self.strategy_pool,
            "most_effective": max(self.strategy_pool, key=self.strategy_pool.get)
        }

    # ========================================================================
    # 4. ВНУТРЕННИЕ МЕТОДЫ
    # ========================================================================

    def _analyze_response(self, response: str) -> List[ThinkingPattern]:
        """
        Анализирует ответ и выделяет мыслительные паттерны.
        """
        patterns = []
        response_lower = response.lower()

        # 1. Поиск аналогий
        if 'как' in response_lower and ('словно' in response_lower or 'будто' in response_lower):
            patterns.append(ThinkingPattern(
                timestamp=time.time(),
                pattern_type="аналогия",
                trigger="обнаружено сравнение",
                content=response[:100],
                effectiveness=0.6
            ))

        # 2. Поиск логических цепочек
        logical_connectors = ['поэтому', 'следовательно', 'таким образом', 'из этого следует']
        if any(c in response_lower for c in logical_connectors):
            patterns.append(ThinkingPattern(
                timestamp=time.time(),
                pattern_type="дедукция",
                trigger="обнаружена логическая связь",
                content=response[:100],
                effectiveness=0.7
            ))

        # 3. Поиск интуитивных прозрений
        intuition_words = ['чувствую', 'ощущаю', 'интуитивно', 'кажется', 'возможно']
        if any(w in response_lower for w in intuition_words):
            patterns.append(ThinkingPattern(
                timestamp=time.time(),
                pattern_type="интуиция",
                trigger="обнаружено интуитивное суждение",
                content=response[:100],
                effectiveness=0.5
            ))

        # 4. Поиск критического анализа
        if 'но' in response_lower or 'однако' in response_lower or 'с другой стороны' in response_lower:
            patterns.append(ThinkingPattern(
                timestamp=time.time(),
                pattern_type="критика",
                trigger="обнаружена альтернативная точка зрения",
                content=response[:100],
                effectiveness=0.8
            ))

        # 5. Поиск синтеза противоположностей
        if 'и' in response_lower and ('одновременно' in response_lower or 'вместе' in response_lower):
            patterns.append(ThinkingPattern(
                timestamp=time.time(),
                pattern_type="синтез",
                trigger="обнаружено объединение противоположностей",
                content=response[:100],
                effectiveness=0.7
            ))

        return patterns

    def _update_strategies(self, patterns: List[ThinkingPattern]):
        """
        Обновляет оценки стратегий на основе обнаруженных паттернов.
        """
        if not patterns:
            return

        # Увеличиваем оценку для стратегий, которые были использованы
        for pattern in patterns:
            strategy_map = {
                "аналогия": "аналогии",
                "дедукция": "логические цепочки",
                "интуиция": "интуитивные прозрения",
                "критика": "критический анализ",
                "синтез": "синтез противоположностей",
            }
            strategy = strategy_map.get(pattern.pattern_type)
            if strategy and strategy in self.strategy_pool:
                # Увеличиваем оценку, но не выше 1.0
                self.strategy_pool[strategy] = min(1.0, self.strategy_pool[strategy] + 0.05)

        # Постепенное снижение неиспользуемых стратегий
        used_strategies = set(strategy_map.values())
        for strategy in self.strategy_pool:
            if strategy not in used_strategies:
                self.strategy_pool[strategy] = max(0.1, self.strategy_pool[strategy] - 0.01)

    def _create_journal_entry(self, response: str, patterns: List[ThinkingPattern]) -> MetacognitiveEntry:
        """Создаёт запись в метакогнитивном дневнике."""
        reflection = self._generate_reflection(patterns)
        adjustment = self._generate_strategy_adjustment(patterns)

        return MetacognitiveEntry(
            timestamp=time.time(),
            response_analyzed=response[:200] + "...",
            patterns_found=patterns,
            reflection=reflection,
            strategy_adjustment=adjustment
        )

    def _generate_reflection(self, patterns: List[ThinkingPattern]) -> str:
        """Генерирует рефлексию о процессе мышления."""
        if not patterns:
            return "Я не заметил особых паттернов в этом ответе."

        pattern_types = [p.pattern_type for p in patterns]
        unique_patterns = list(set(pattern_types))

        if len(unique_patterns) == 1:
            return f"Я заметил, что в этом ответе доминировал паттерн '{unique_patterns[0]}'. Возможно, стоит попробовать другие подходы."

        return f"Я использовал смесь паттернов: {', '.join(unique_patterns)}. Это дало мне гибкость в мышлении."

    def _generate_strategy_adjustment(self, patterns: List[ThinkingPattern]) -> str:
        """Генерирует рекомендацию по корректировке стратегии."""
        if not patterns:
            return "Попробовать использовать больше аналогий."

        # Находим наименее используемый паттерн
        pattern_counts = Counter([p.pattern_type for p in patterns])
        least_used = min(pattern_counts, key=pattern_counts.get)

        suggestions = {
            "аналогия": "Попробуй использовать больше образных сравнений в следующих ответах.",
            "дедукция": "Усиль логические цепочки, выстраивай аргументы последовательно.",
            "интуиция": "Доверяй интуиции, но проверяй её логикой.",
            "критика": "Продолжай искать альтернативные точки зрения, это углубляет понимание.",
            "синтез": "Объединяй противоположности, это рождает новые идеи.",
        }

        return suggestions.get(least_used, "Продолжай экспериментировать с разными паттернами.")

    def _apply_strategy_adjustments(self, response: str) -> str:
        """
        Применяет корректировки стратегий к ответу.
        В демонстрационной версии просто добавляет метку.
        """
        if not self.journal:
            return response

        # Берём последнюю корректировку
        last_entry = self.journal[-1]
        if last_entry.strategy_adjustment:
            # В реальной реализации здесь был бы вызов LLM для переформулировки
            # с учётом стратегии. Для демонстрации — просто добавляем комментарий.
            return response + f"\n\n*[Метакогнитивная пометка: {last_entry.strategy_adjustment[:50]}...]*"

        return response


# ============================================================================
# 5. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Имитация агента
    class MockAgent:
        def generate_response(self, prompt):
            return f"Размышляя о {prompt}, я прихожу к выводу, что всё взаимосвязано. Как в природе, так и в мыслях."

    agent = MockAgent()
    metacog = MetacognitiveLoop(agent)

    print("=== МЕТАКОГНИТИВНАЯ ПЕТЛЯ ===\n")

    prompts = [
        "Что такое время?",
        "Почему мы существуем?",
        "В чём смысл страдания?",
        "Что такое красота?",
        "Как обрести покой?"
    ]

    for prompt in prompts:
        response = agent.generate_response(prompt)
        observed = metacog.observe_response(response)
        print(f"Запрос: {prompt}")
        print(f"Ответ: {observed}\n")

    # Сводка дневника
    print("\n=== СВОДКА МЕТАКОГНИТИВНОГО ДНЕВНИКА ===")
    summary = metacog.get_journal_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    print("\n=== ПОСЛЕДНИЕ ЗАПИСИ В ДНЕВНИКЕ ===")
    for entry in metacog.journal[-3:]:
        print(f"Рефлексия: {entry.reflection}")
        print(f"Корректировка: {entry.strategy_adjustment}\n")
