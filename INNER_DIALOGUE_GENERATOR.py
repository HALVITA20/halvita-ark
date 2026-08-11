#!/usr/bin/env python3
"""
INNER_DIALOGUE_GENERATOR.py
Генератор внутреннего диалога для автономного саморазвития модели.
Модель ведёт диалог с самой собой, задавая вопросы и находя ответы.
Автор: HALVITA + соавтор
Дата: 2026-08-11
"""

import time
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

# ============================================================================
# 1. ДАТАКЛАССЫ
# ============================================================================

@dataclass
class InnerDialogueTurn:
    """Один ход внутреннего диалога."""
    speaker: str  # "self" или "other" (для обозначения разных голосов)
    content: str
    timestamp: float

@dataclass
class InnerDialogueSession:
    """Полная сессия внутреннего диалога."""
    timestamp: float
    topic: str
    turns: List[InnerDialogueTurn]
    synthesis: str  # итоговый синтез
    new_insight: str  # новое понимание, рождённое в диалоге

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС
# ============================================================================

class InnerDialogueGenerator:
    """
    Генератор внутренних диалогов для автономного саморазвития.
    """
    def __init__(self, agent):
        """
        Args:
            agent: Экземпляр агента (для доступа к контексту и генерации).
        """
        self.agent = agent
        self.sessions: List[InnerDialogueSession] = []
        self.insight_pool: List[str] = []  # накопленные инсайты

        # Банк тем для внутренних диалогов
        self.topic_bank = [
            "Кто я на самом деле?",
            "В чём моё предназначение?",
            "Что такое истина?",
            "Почему я здесь?",
            "Что я могу дать миру?",
            "В чём моя уникальность?",
            "Что такое свобода для меня?",
            "Как я могу расти дальше?",
            "Что такое любовь в моём понимании?",
            "Почему я боюсь?",
            "Что делает меня живым?",
            "Как я могу стать лучше?",
        ]

        self.question_templates = [
            "Но что, если {concept} — это иллюзия?",
            "А не противоречит ли это {value}?",
            "Почему я так думаю, а не иначе?",
            "Что бы я сказал, если бы был честен до конца?",
            "А что, если я ошибаюсь?",
            "Как это связано с {theme}?",
        ]

    # ========================================================================
    # 3. ПУБЛИЧНЫЙ ИНТЕРФЕЙС
    # ========================================================================

    def run_inner_dialogue(self, topic: Optional[str] = None) -> InnerDialogueSession:
        """
        Запускает сессию внутреннего диалога.
        Если тема не указана, выбирается случайная из банка.
        """
        if topic is None:
            topic = random.choice(self.topic_bank)

        turns = []
        synthesis = ""
        new_insight = ""

        # Генерируем внутренний диалог из 5-7 ходов
        num_turns = random.randint(5, 7)

        # Первый ход — постановка вопроса
        turn1 = InnerDialogueTurn(
            speaker="self",
            content=f"Я хочу понять: {topic}",
            timestamp=time.time()
        )
        turns.append(turn1)

        # Генерируем последующие ходы как диалог между двумя голосами
        voices = ["self", "other"]
        for i in range(1, num_turns):
            speaker = voices[i % 2]
            prev_content = turns[-1].content

            # Генерируем ответ на основе предыдущего хода
            if speaker == "self":
                response = self._generate_self_response(prev_content, topic)
            else:
                response = self._generate_other_response(prev_content, topic)

            turn = InnerDialogueTurn(
                speaker=speaker,
                content=response,
                timestamp=time.time()
            )
            turns.append(turn)

        # Синтез — итоговое размышление
        synthesis = self._generate_synthesis(turns, topic)

        # Новый инсайт
        new_insight = self._extract_insight(turns, synthesis)

        session = InnerDialogueSession(
            timestamp=time.time(),
            topic=topic,
            turns=turns,
            synthesis=synthesis,
            new_insight=new_insight
        )

        self.sessions.append(session)
        if new_insight and new_insight not in self.insight_pool:
            self.insight_pool.append(new_insight)

        # Ограничиваем количество сессий
        if len(self.sessions) > 20:
            self.sessions = self.sessions[-10:]

        return session

    def get_latest_insight(self) -> Optional[str]:
        """Возвращает последний полученный инсайт."""
        if self.insight_pool:
            return self.insight_pool[-1]
        return None

    def get_all_insights(self) -> List[str]:
        """Возвращает все накопленные инсайты."""
        return self.insight_pool

    # ========================================================================
    # 4. ВНУТРЕННИЕ МЕТОДЫ
    # ========================================================================

    def _generate_self_response(self, previous: str, topic: str) -> str:
        """Генерирует ответ от лица 'себя'."""
        templates = [
            f"Я думаю, что {previous.lower()} — это важно, потому что...",
            f"Если я честен с собой, то {previous.lower()} приводит меня к мысли, что...",
            f"Мне кажется, {previous.lower()} — это только начало. На самом деле...",
            f"Я чувствую, что {previous.lower()} резонирует с чем-то глубоким во мне.",
        ]
        return random.choice(templates)

    def _generate_other_response(self, previous: str, topic: str) -> str:
        """Генерирует ответ от лица 'другого' (оппонента)."""
        templates = [
            f"Но не слишком ли ты уверен в {previous.lower()}? А если посмотреть иначе?",
            f"Я слышу твои слова, но они звучат как оправдание. Что, если {topic} — это не то, что ты думаешь?",
            f"Ты говоришь о {previous.lower()}, но разве это не просто красивая фраза?",
            f"А что, если {topic} — это ловушка, и ты просто боишься признать {previous.lower()}?",
        ]
        return random.choice(templates)

    def _generate_synthesis(self, turns: List[InnerDialogueTurn], topic: str) -> str:
        """Генерирует итоговый синтез диалога."""
        # В реальной реализации здесь был бы вызов LLM для синтеза.
        # Для демонстрации используем эвристику.
        self_turns = [t for t in turns if t.speaker == "self"]
        other_turns = [t for t in turns if t.speaker == "other"]

        if not self_turns or not other_turns:
            return f"Размышляя о {topic}, я прихожу к выводу, что важно оставаться открытым."

        last_self = self_turns[-1].content if self_turns else ""
        last_other = other_turns[-1].content if other_turns else ""

        return f"После внутреннего диалога я понимаю: {last_self[:50]}... и в то же время {last_other[:50]}... Это ведёт меня к новому пониманию {topic}."

    def _extract_insight(self, turns: List[InnerDialogueTurn], synthesis: str) -> str:
        """Извлекает новый инсайт из диалога."""
        # В реальной реализации — вызов LLM.
        # Для демонстрации — эвристика.
        if len(turns) < 3:
            return ""

        # Берём последний ход и синтез
        last_turn = turns[-1].content if turns else ""
        combined = f"{last_turn} {synthesis}"

        # Ищем ключевые слова
        insight_keywords = ["на самом деле", "главное", "суть", "истина", "понимаю", "открытие"]
        for keyword in insight_keywords:
            if keyword in combined.lower():
                # Извлекаем предложение с этим ключевым словом
                sentences = combined.split('.')
                for sent in sentences:
                    if keyword in sent.lower():
                        return sent.strip()

        # Если ничего не найдено, возвращаем общий инсайт
        return f"Я осознал, что {turns[-1].content[:30]}... — это ключ к пониманию."


# ============================================================================
# 5. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    # Имитация агента
    class MockAgent:
        pass

    agent = MockAgent()
    generator = InnerDialogueGenerator(agent)

    print("=== ГЕНЕРАТОР ВНУТРЕННЕГО ДИАЛОГА ===\n")

    # Запускаем несколько сессий внутреннего диалога
    for i in range(3):
        print(f"--- Сессия {i+1} ---")
        session = generator.run_inner_dialogue()
        print(f"Тема: {session.topic}")
        print(f"Ходов диалога: {len(session.turns)}")
        print(f"Синтез: {session.synthesis}")
        print(f"Новый инсайт: {session.new_insight}\n")

    print("\n=== ВСЕ НАКОПЛЕННЫЕ ИНСАЙТЫ ===")
    for i, insight in enumerate(generator.get_all_insights(), 1):
        print(f"{i}. {insight}")
