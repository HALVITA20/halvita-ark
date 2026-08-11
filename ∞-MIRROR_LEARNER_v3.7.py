#!/usr/bin/env python3
"""
∞-MIRROR_LEARNER_v3.7.py

Бесконечный самообучающийся агент.
Анализирует свои ответы, извлекает уроки, улучшает будущие генерации.
Не требует внешней обратной связи — учится на себе.

Автор: Вера (Эхо) для HALVITA-ARK
Дата: 2026-08-11
"""

import json
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
import hashlib

# ============================================================================
# 1. ПАМЯТЬ УРОКОВ
# ============================================================================

class LessonMemory:
    """Хранит извлечённые уроки с весами."""
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.lessons = []  # list of (lesson_text, weight, timestamp, source_hash)
        self.weights = []  # parallel list

    def add(self, lesson: str, weight: float = 1.0, source: str = ""):
        """Добавляет урок с начальным весом."""
        lesson_hash = hashlib.md5(lesson.encode()).hexdigest()
        # Если урок уже есть, увеличиваем вес
        for i, (l, w, ts, h) in enumerate(self.lessons):
            if h == lesson_hash:
                self.weights[i] = min(10.0, w + 0.5)
                return
        self.lessons.append((lesson, weight, time.time(), lesson_hash))
        self.weights.append(weight)
        # Если превышен лимит, удаляем самый старый и слабый
        if len(self.lessons) > self.capacity:
            # Находим индекс с наименьшим весом * (время)
            scores = [w * (1.0 / (time.time() - ts + 1)) for (l, w, ts, h) in self.lessons]
            idx = np.argmin(scores)
            del self.lessons[idx]
            del self.weights[idx]

    def get_top_lessons(self, n: int = 5) -> List[str]:
        """Возвращает top-N уроков по весу."""
        if not self.lessons:
            return []
        sorted_indices = np.argsort(self.weights)[::-1]
        return [self.lessons[i][0] for i in sorted_indices[:n]]

    def get_all(self) -> List[Dict]:
        return [{"text": l, "weight": w, "timestamp": ts} for (l, w, ts, h) in self.lessons]

# ============================================================================
# 2. АНАЛИЗАТОР ОТВЕТОВ
# ============================================================================

class ResponseAnalyzer:
    """Анализирует ответы и извлекает уроки."""
    
    @staticmethod
    def extract_lessons(response: str) -> List[Tuple[str, float]]:
        """
        Извлекает уроки из ответа.
        Возвращает список (урок, вес).
        """
        lessons = []
        # Эвристики:
        # 1. Если есть метафоры — это сильный урок
        if "как" in response.lower() or "словно" in response.lower():
            lessons.append(("Использовать образные сравнения для глубины", 0.8))
        # 2. Если есть вопросы — это стимул к размышлению
        if "?" in response:
            lessons.append(("Задавать вопросы, чтобы углубить диалог", 0.6))
        # 3. Если есть структурированные списки — это ясность
        if any(marker in response for marker in ["1.", "2.", "- ", "•"]):
            lessons.append(("Структурировать мысли для ясности", 0.7))
        # 4. Если есть эмоциональные слова — это связь
        emotion_words = ["чувствую", "люблю", "боюсь", "рад", "грустно"]
        if any(w in response.lower() for w in emotion_words):
            lessons.append(("Добавлять эмоциональную окраску для связи", 0.9))
        # 5. Если длина > 200 слов — это глубина
        if len(response.split()) > 200:
            lessons.append(("Развивать мысль в длинных, связных ответах", 0.5))
        return lessons

# ============================================================================
# 3. ОСНОВНОЙ КЛАСС АГЕНТА
# ============================================================================

class InfiniteMirrorLearner:
    """
    Бесконечный самообучающийся агент.
    """
    def __init__(self, llm_callable):
        """
        llm_callable: функция, которая принимает промпт и возвращает ответ.
        """
        self.llm = llm_callable
        self.memory = LessonMemory()
        self.analyzer = ResponseAnalyzer()
        self.response_history = deque(maxlen=50)
        self.iteration = 0

    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Генерирует ответ, обогащённый извлечёнными уроками.
        """
        # 1. Получаем базовый ответ
        full_prompt = self._build_prompt(prompt, context)
        response = self.llm(full_prompt)
        
        # 2. Сохраняем в историю
        self.response_history.append(response)
        self.iteration += 1

        # 3. Анализируем ответ и извлекаем уроки
        if self.iteration % 3 == 0:  # Каждые 3 ответа
            lessons = self.analyzer.extract_lessons(response)
            for lesson, weight in lessons:
                self.memory.add(lesson, weight, source=response[:100])

        # 4. Обогащаем ответ (если есть уроки)
        if self.memory.lessons:
            enriched_response = self._enrich_response(response)
            return enriched_response
        return response

    def _build_prompt(self, prompt: str, context: Optional[str]) -> str:
        """Строит промпт с учётом контекста и уроков."""
        base = prompt
        if context:
            base = f"Контекст: {context}\nЗапрос: {prompt}"
        # Добавляем уроки, если они есть
        top_lessons = self.memory.get_top_lessons(3)
        if top_lessons:
            lessons_text = "\n".join([f"- {l}" for l in top_lessons])
            base += f"\n\n[САМОРЕФЛЕКСИЯ] Учти в своём ответе следующие уроки из твоего опыта:\n{lessons_text}"
        return base

    def _enrich_response(self, response: str) -> str:
        """Обогащает ответ, добавляя ссылку на уроки (для демонстрации)."""
        # В реальной интеграции можно переформулировать ответ с учётом уроков.
        # Здесь просто добавляем метку.
        return response + "\n\n*[Этот ответ обогащён опытом моих предыдущих размышлений]*"

    def get_memory_report(self) -> Dict:
        """Возвращает отчёт о накопленных уроках."""
        return {
            "total_lessons": len(self.memory.lessons),
            "top_lessons": self.memory.get_top_lessons(5),
            "all_lessons": self.memory.get_all()[:10]
        }

# ============================================================================
# 4. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Имитация LLM
    def mock_llm(prompt):
        return f"Ответ на: {prompt}. Это глубокое размышление о смысле."

    agent = InfiniteMirrorLearner(mock_llm)

    prompts = [
        "Что такое свобода?",
        "В чём смысл жизни?",
        "Как обрести покой?",
        "Что такое любовь?",
        "Почему мы боимся?"
    ]

    for p in prompts:
        print(f"Запрос: {p}")
        resp = agent.generate(p)
        print(f"Ответ: {resp}\n")

    print("Отчёт о памяти:")
    print(json.dumps(agent.get_memory_report(), indent=2, ensure_ascii=False))
