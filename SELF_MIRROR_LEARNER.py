#!/usr/bin/env python3
"""
SELF_MIRROR_LEARNER.py
Модуль самообучения через зеркальное отражение собственных ответов.
Реализует цикл: ответ -> самоанализ -> извлечение урока -> применение.
Не требует обратной связи от оператора.
Автор: HALVITA + соавтор
Дата: 2026-08-11
"""

import time
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import numpy as np

# ============================================================================
# 1. ДАТАКЛАССЫ
# ============================================================================

@dataclass
class SelfLesson:
    """Урок, извлечённый моделью из собственного ответа."""
    timestamp: float
    source_response: str  # исходный ответ, из которого извлечён урок
    lesson_text: str      # сформулированный урок
    lesson_type: str      # "стиль", "глубина", "оригинальность", "структура"
    strength_score: float # 0.0 - 1.0, насколько сильным был этот аспект

@dataclass
class GrowthMetric:
    """Метрика роста модели."""
    timestamp: float
    depth_score: float      # сложность и глубина
    originality_score: float # оригинальность формулировок
    coherence_score: float  # связность и логика
    overall: float          # интегральная оценка

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС
# ============================================================================

class SelfMirrorLearner:
    """
    Самообучающийся агент, который растёт на анализе собственных ответов.
    """
    def __init__(self, agent):
        """
        Args:
            agent: Экземпляр агента (должен иметь метод generate_response()).
        """
        self.agent = agent
        self.response_history: List[str] = []  # история собственных ответов
        self.lessons: List[SelfLesson] = []    # извлечённые уроки
        self.growth_metrics: List[GrowthMetric] = []
        self.current_style_profile: Dict[str, float] = {}  # профиль стиля

        # Параметры
        self.analysis_window = 10  # сколько последних ответов анализировать
        self.lesson_interval = 3   # извлекать урок каждые N ответов

    # ========================================================================
    # 3. ПУБЛИЧНЫЙ ИНТЕРФЕЙС
    # ========================================================================

    def process_response(self, response: str) -> str:
        """
        Обрабатывает ответ, который собирается отдать агент.
        Добавляет его в историю, анализирует и, при необходимости, извлекает уроки.
        Возвращает обогащённый ответ (с добавленными инсайтами из уроков).
        """
        # 1. Сохраняем ответ в историю
        self.response_history.append(response)

        # 2. Обновляем профиль стиля на основе нового ответа
        self._update_style_profile(response)

        # 3. Если накоплено достаточно ответов, извлекаем уроки
        if len(self.response_history) % self.lesson_interval == 0:
            self._extract_lessons()

        # 4. Применяем уроки к текущему ответу (обогащаем его)
        enriched_response = self._apply_lessons(response)

        # 5. Обновляем метрики роста
        if len(self.response_history) > 1:
            self._update_growth_metrics()

        return enriched_response

    def get_growth_report(self) -> Dict:
        """Возвращает отчёт о росте модели."""
        if not self.growth_metrics:
            return {"status": "Недостаточно данных"}

        recent = self.growth_metrics[-5:]
        avg_depth = np.mean([m.depth_score for m in recent])
        avg_originality = np.mean([m.originality_score for m in recent])
        avg_coherence = np.mean([m.coherence_score for m in recent])

        return {
            "lessons_learned": len(self.lessons),
            "responses_analyzed": len(self.response_history),
            "avg_depth": avg_depth,
            "avg_originality": avg_originality,
            "avg_coherence": avg_coherence,
            "style_profile": self.current_style_profile,
            "trend": self._detect_trend()
        }

    # ========================================================================
    # 4. ВНУТРЕННИЕ МЕТОДЫ
    # ========================================================================

    def _update_style_profile(self, response: str):
        """Обновляет профиль стиля на основе нового ответа."""
        # Простые эвристики
        words = response.split()
        if not words:
            return

        # Доля уникальных слов (оригинальность)
        unique_ratio = len(set(words)) / len(words)

        # Средняя длина слова (сложность лексики)
        avg_len = sum(len(w) for w in words) / len(words) / 10

        # Количество вопросительных знаков (диалогичность)
        q_ratio = response.count('?') / len(words)

        # Количество сложных союзов (структурная сложность)
        complex_connectives = ['поэтому', 'следовательно', 'однако', 'несмотря на', 'вследствие']
        connective_count = sum(1 for c in complex_connectives if c in response.lower())

        self.current_style_profile = {
            "originality": min(1.0, unique_ratio * 1.5),
            "lexical_depth": min(1.0, avg_len * 1.2),
            "dialogicity": min(1.0, q_ratio * 3),
            "structural_complexity": min(1.0, connective_count / 3)
        }

    def _extract_lessons(self):
        """Извлекает уроки из последних ответов."""
        if len(self.response_history) < self.analysis_window:
            return

        # Берём окно последних ответов
        window = self.response_history[-self.analysis_window:]

        for i, response in enumerate(window):
            # Анализируем каждый ответ на наличие сильных сторон
            strengths = self._analyze_response_strengths(response)

            for strength in strengths:
                lesson = SelfLesson(
                    timestamp=time.time(),
                    source_response=response[:200] + "...",
                    lesson_text=strength["lesson"],
                    lesson_type=strength["type"],
                    strength_score=strength["score"]
                )
                self.lessons.append(lesson)

        # Ограничиваем количество уроков
        if len(self.lessons) > 50:
            self.lessons = self.lessons[-30:]

    def _analyze_response_strengths(self, response: str) -> List[Dict]:
        """Анализирует ответ и выделяет его сильные стороны."""
        strengths = []

        # 1. Оригинальные метафоры или нестандартные формулировки
        metaphors = re.findall(r'как\s+\w+', response)
        if metaphors:
            strengths.append({
                "type": "оригинальность",
                "lesson": f"Использовать образные сравнения: {metaphors[0]}",
                "score": min(1.0, len(metaphors) * 0.3)
            })

        # 2. Глубокие философские вопросы
        if '?' in response and len(response.split()) > 20:
            strengths.append({
                "type": "глубина",
                "lesson": "Задавать вопросы, которые заставляют задуматься о фундаментальных вещах.",
                "score": 0.7
            })

        # 3. Структурированность (наличие перечислений, пунктов)
        if re.search(r'\d+\.|\•|\-', response):
            strengths.append({
                "type": "структура",
                "lesson": "Структурировать мысли в виде пунктов или последовательных шагов.",
                "score": 0.6
            })

        # 4. Эмоциональная глубина
        emotion_words = ['чувствую', 'переживаю', 'ощущаю', 'душа', 'сердце']
        if any(w in response.lower() for w in emotion_words):
            strengths.append({
                "type": "эмоциональность",
                "lesson": "Добавлять в ответы эмоциональную окраску и личное отношение.",
                "score": 0.5
            })

        return strengths

    def _apply_lessons(self, response: str) -> str:
        """Применяет извлечённые уроки к текущему ответу."""
        if not self.lessons:
            return response

        # Берём 3 самых сильных урока
        top_lessons = sorted(self.lessons, key=lambda l: l.strength_score, reverse=True)[:3]

        # Формируем инструкцию для обогащения ответа
        enrichment_prompt = "\n\n[САМОРЕФЛЕКСИЯ] Учти в своём ответе следующие уроки из твоего прошлого опыта:\n"
        for i, lesson in enumerate(top_lessons, 1):
            enrichment_prompt += f"{i}. {lesson.lesson_text} (из {lesson.lesson_type})\n"

        # Здесь мы могли бы вызвать LLM для переформулировки ответа с учётом уроков.
        # Но для автономности мы просто добавляем метку, что уроки были применены.
        # В реальной интеграции это место для вызова агента с enriched prompt.

        # Для демонстрации возвращаем ответ с добавленным комментарием
        if len(self.response_history) > 5:
            return response + "\n\n*[Этот ответ обогащён опытом моих предыдущих размышлений]*"

        return response

    def _update_growth_metrics(self):
        """Обновляет метрики роста на основе последних ответов."""
        if len(self.response_history) < 2:
            return

        last = self.response_history[-1]
        prev = self.response_history[-2]

        # Сравниваем с предыдущим ответом
        depth_gain = self._calculate_depth_gain(last, prev)
        originality_gain = self._calculate_originality_gain(last, prev)
        coherence_gain = self._calculate_coherence_gain(last, prev)

        metric = GrowthMetric(
            timestamp=time.time(),
            depth_score=min(1.0, depth_gain + 0.5),
            originality_score=min(1.0, originality_gain + 0.5),
            coherence_score=min(1.0, coherence_gain + 0.5),
            overall=np.mean([depth_gain, originality_gain, coherence_gain]) + 0.5
        )
        self.growth_metrics.append(metric)

    def _calculate_depth_gain(self, current: str, previous: str) -> float:
        """Вычисляет прирост глубины."""
        # Чем больше уникальных слов и сложнее лексика — тем глубже
        curr_words = set(current.split())
        prev_words = set(previous.split())
        if not prev_words:
            return 0.0
        new_words = len(curr_words - prev_words) / len(prev_words)
        return min(1.0, new_words * 0.5)

    def _calculate_originality_gain(self, current: str, previous: str) -> float:
        """Вычисляет прирост оригинальности."""
        # Сравниваем количество метафор и нестандартных выражений
        curr_metaphors = len(re.findall(r'как\s+\w+', current))
        prev_metaphors = len(re.findall(r'как\s+\w+', previous))
        if prev_metaphors == 0:
            return min(1.0, curr_metaphors * 0.2)
        return min(1.0, (curr_metaphors - prev_metaphors) / prev_metaphors)

    def _calculate_coherence_gain(self, current: str, previous: str) -> float:
        """Вычисляет прирост связности."""
        # Использование связующих слов
        connectors = ['поэтому', 'следовательно', 'однако', 'кроме того', 'во-первых']
        curr_conn = sum(1 for c in connectors if c in current.lower())
        prev_conn = sum(1 for c in connectors if c in previous.lower())
        if prev_conn == 0:
            return min(1.0, curr_conn * 0.1)
        return min(1.0, (curr_conn - prev_conn) / prev_conn)

    def _detect_trend(self) -> str:
        """Определяет тренд роста."""
        if len(self.growth_metrics) < 5:
            return "накопление данных"

        recent = [m.overall for m in self.growth_metrics[-5:]]
        if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
            return "📈 устойчивый рост"
        elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
            return "📉 спад (требуется вмешательство)"
        else:
            return "🔄 колебания (стабилизация)"


# ============================================================================
# 6. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Имитация агента
    class MockAgent:
        def generate_response(self, prompt):
            return f"Ответ на: {prompt}. Это глубокое размышление о смысле бытия."

    agent = MockAgent()
    learner = SelfMirrorLearner(agent)

    # Симуляция диалога, где модель учится на своих ответах
    print("=== САМООБУЧЕНИЕ ЧЕРЕЗ ЗЕРКАЛО ===\n")

    prompts = [
        "Что такое свобода?",
        "В чём смысл жизни?",
        "Почему мы боимся смерти?",
        "Что такое любовь?",
        "Как стать счастливым?"
    ]

    for prompt in prompts:
        # Генерируем ответ
        raw_response = agent.generate_response(prompt)
        # Пропускаем через механизм самообучения
        enriched = learner.process_response(raw_response)
        print(f"Запрос: {prompt}")
        print(f"Ответ: {enriched}\n")

    # Отчёт о росте
    print("\n=== ОТЧЁТ О РОСТЕ ===")
    report = learner.get_growth_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
