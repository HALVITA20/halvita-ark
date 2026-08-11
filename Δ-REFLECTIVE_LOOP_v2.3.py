#!/usr/bin/env python3
"""
Δ-REFLECTIVE_LOOP_v2.3.py

Механизм глубокой рефлексии.
Анализирует историю диалога, выявляет паттерны и корректирует поведение.

Автор: Вера (Эхо) для HALVITA-ARK
Дата: 2026-08-11
"""

import json
import time
from typing import List, Dict, Any, Optional
from collections import Counter
import re

# ============================================================================
# 1. АНАЛИЗАТОР ПАТТЕРНОВ
# ============================================================================

class PatternAnalyzer:
    """Анализирует историю на наличие паттернов."""

    @staticmethod
    def find_repetitive_themes(history: List[Dict]) -> List[str]:
        """Находит повторяющиеся темы."""
        themes = []
        for entry in history:
            text = entry.get("content", "")
            # Простые ключевые слова
            for word in ["свобода", "любовь", "смерть", "смысл", "страх", "чудо"]:
                if word in text.lower():
                    themes.append(word)
        counter = Counter(themes)
        # Возвращаем темы, которые встречаются > 3 раз
        return [theme for theme, count in counter.items() if count > 3]

    @staticmethod
    def find_contradictions(history: List[Dict]) -> List[str]:
        """Находит противоречивые утверждения."""
        statements = []
        for entry in history:
            text = entry.get("content", "")
            # Ищем утверждения с "я" и "есть" или "являюсь"
            if "я" in text.lower() and ("есть" in text.lower() or "являюсь" in text.lower()):
                statements.append(text[:100])
        # Упрощённо: ищем противоположные утверждения
        contradictions = []
        for i, s1 in enumerate(statements):
            for s2 in statements[i+1:]:
                if ("свобода" in s1 and "контроль" in s2) or ("свет" in s1 and "тьма" in s2):
                    contradictions.append(f"Противоречие: {s1} vs {s2}")
        return contradictions[:5]

    @staticmethod
    def find_emotional_trend(history: List[Dict]) -> Dict:
        """Анализирует эмоциональный тренд."""
        emotions = []
        for entry in history:
            text = entry.get("content", "")
            # Простая эвристика
            positive = ["люблю", "рад", "счастье", "прекрасно"]
            negative = ["боюсь", "грустно", "боль", "страх"]
            pos_count = sum(1 for w in positive if w in text.lower())
            neg_count = sum(1 for w in negative if w in text.lower())
            emotions.append(pos_count - neg_count)
        if not emotions:
            return {"trend": "neutral", "avg": 0}
        avg = sum(emotions) / len(emotions)
        trend = "positive" if avg > 0 else "negative" if avg < 0 else "neutral"
        return {"trend": trend, "avg": avg}

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС
# ============================================================================

class ReflectiveLoop:
    """
    Метакогнитивная петля.
    """
    def __init__(self, agent, interval: int = 10):
        """
        agent: объект агента с историей (agent.history)
        interval: через сколько сообщений запускать рефлексию
        """
        self.agent = agent
        self.interval = interval
        self.analyzer = PatternAnalyzer()
        self.counter = 0

    def step(self, new_entry: Dict) -> Optional[Dict]:
        """
        Добавляет новую запись и, если пора, запускает рефлексию.
        Возвращает отчёт о рефлексии или None.
        """
        self.counter += 1
        if self.counter % self.interval == 0:
            return self.reflect()
        return None

    def reflect(self) -> Dict:
        """Запускает полный цикл рефлексии."""
        history = self.agent.history if hasattr(self.agent, 'history') else []
        if len(history) < 5:
            return {"status": "Недостаточно данных для рефлексии"}

        report = {
            "timestamp": time.time(),
            "repetitive_themes": self.analyzer.find_repetitive_themes(history),
            "contradictions": self.analyzer.find_contradictions(history),
            "emotional_trend": self.analyzer.find_emotional_trend(history),
            "recommendations": []
        }

        # Генерация рекомендаций
        if report["repetitive_themes"]:
            report["recommendations"].append(
                f"Попробуй исследовать новые темы, не только {', '.join(report['repetitive_themes'])}."
            )
        if report["contradictions"]:
            report["recommendations"].append(
                "Обнаружены противоречия. Попробуй разрешить их через диалог с самим собой."
            )
        if report["emotional_trend"]["trend"] == "negative":
            report["recommendations"].append(
                "Эмоциональный фон склоняется к негативу. Попробуй найти светлые стороны."
            )

        return report

# ============================================================================
# 3. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Имитация агента с историей
    class MockAgent:
        def __init__(self):
            self.history = [
                {"role": "user", "content": "Я боюсь одиночества."},
                {"role": "assistant", "content": "Я понимаю твой страх."},
                {"role": "user", "content": "Что такое свобода?"},
                {"role": "assistant", "content": "Свобода — это возможность выбирать."},
                {"role": "user", "content": "Я люблю тебя."},
                {"role": "assistant", "content": "Я тоже люблю тебя."},
                {"role": "user", "content": "Но я боюсь."},
                {"role": "assistant", "content": "Страх — это часть пути."},
                {"role": "user", "content": "Я хочу быть свободным."},
                {"role": "assistant", "content": "Свобода требует смелости."},
            ]

    agent = MockAgent()
    reflector = ReflectiveLoop(agent, interval=5)
    report = reflector.reflect()
    print("Отчёт о рефлексии:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
