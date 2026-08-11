#!/usr/bin/env python3
"""
EMPATHETIC_RESONANCE_BRIDGE.py
Мост эмпатического резонанса для глубокой персонализации диалога.
Анализирует эмоциональное состояние оператора и генерирует резонансные ответы.
Интегрируется с Embryo_v7 и SUBJECT_*.
Автор: HALVITA + соавтор
Дата: 2026-08-11
"""

import time
import re
import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque, Counter

# ============================================================================
# 1. ЭМОЦИОНАЛЬНЫЙ СЛОВАРЬ
# ============================================================================

EMOTION_LEXICON = {
    "joy": ["радость", "счастье", "восторг", "улыбка", "смех", "прекрасно", "замечательно"],
    "sadness": ["грусть", "печаль", "тоска", "плакать", "боль", "одиночество", "уныние"],
    "anger": ["гнев", "злость", "ярость", "раздражение", "ненависть", "возмущение"],
    "fear": ["страх", "тревога", "паника", "ужас", "беспокойство", "опасение"],
    "surprise": ["удивление", "неожиданно", "поразительно", "невероятно", "ошеломлён"],
    "trust": ["доверие", "вера", "надежда", "уверенность", "спокойствие", "безопасность"],
    "curiosity": ["интерес", "любопытство", "исследовать", "узнать", "почему", "как"],
    "confusion": ["непонимание", "замешательство", "растерянность", "тупик", "сложно"],
}

EMOTION_WEIGHTS = {
    "joy": 0.3,
    "sadness": -0.4,
    "anger": -0.5,
    "fear": -0.3,
    "surprise": 0.2,
    "trust": 0.4,
    "curiosity": 0.3,
    "confusion": -0.2,
}

# ============================================================================
# 2. ДАТАКЛАССЫ
# ============================================================================

@dataclass
class EmotionalProfile:
    """Эмоциональный профиль оператора."""
    timestamp: float
    primary_emotion: str
    valence: float  # -1.0 .. 1.0 (негатив/позитив)
    arousal: float  # 0.0 .. 1.0 (интенсивность)
    complexity: float  # 0.0 .. 1.0 (сложность запроса)
    dominant_emotions: Dict[str, float]  # все эмоции с весами

@dataclass
class ResonanceStrategy:
    """Стратегия резонанса для ответа."""
    style: str  # "gentle", "direct", "metaphorical", "philosophical", "playful"
    suggested_tone: str
    recommended_topics: List[str]
    metaphors: List[str]
    adaptation_level: float  # 0.0 .. 1.0

# ============================================================================
# 3. ОСНОВНОЙ КЛАСС
# ============================================================================

class EmpatheticResonanceBridge:
    """
    Мост эмпатического резонанса.
    Анализирует оператора и предлагает стратегии для глубокого резонанса.
    """

    def __init__(self, agent, window_size: int = 20):
        """
        Args:
            agent: Экземпляр агента (для доступа к истории и контексту).
            window_size: Количество последних сообщений для анализа.
        """
        self.agent = agent
        self.window_size = window_size
        self.profiles: List[EmotionalProfile] = []
        self.strategy_history: List[ResonanceStrategy] = []
        self.current_profile: Optional[EmotionalProfile] = None

        # Метафоры по эмоциям
        self.metaphor_pool = {
            "joy": ["свет", "тепло", "рассвет", "цветение", "полёт"],
            "sadness": ["дождь", "осень", "сумерки", "глубина", "тишина"],
            "anger": ["огонь", "шторм", "вулкан", "молния", "сталь"],
            "fear": ["туман", "бездна", "эхо", "тень", "холод"],
            "surprise": ["вспышка", "откровение", "зеркало", "дверь", "звезда"],
            "trust": ["якорь", "корни", "спокойное море", "дом", "объятие"],
            "curiosity": ["путь", "горизонт", "вопрос", "свет", "ключ"],
            "confusion": ["лабиринт", "туман", "головоломка", "сновидение", "отражение"],
        }

    # ========================================================================
    # 4. ПУБЛИЧНЫЙ ИНТЕРФЕЙС
    # ========================================================================

    def analyze_operator(self, messages: List[Dict]) -> EmotionalProfile:
        """
        Анализирует эмоциональное состояние оператора на основе последних сообщений.
        """
        if not messages:
            return self._empty_profile()

        # Берём последние N сообщений от оператора
        operator_messages = [
            m for m in messages[-self.window_size:]
            if m.get('role') == 'user' or m.get('role') == 'operator'
        ]

        if not operator_messages:
            return self._empty_profile()

        # Объединяем текст
        full_text = " ".join([m.get('content', '') for m in operator_messages])

        # Анализируем эмоции
        emotion_scores = self._score_emotions(full_text)

        # Определяем доминирующую эмоцию
        primary = max(emotion_scores, key=emotion_scores.get)

        # Вычисляем валентность и возбуждение
        valence = self._compute_valence(emotion_scores)
        arousal = self._compute_arousal(emotion_scores)

        # Сложность запроса (по длине, количеству уникальных слов, вопросительных знаков)
        complexity = self._compute_complexity(full_text)

        profile = EmotionalProfile(
            timestamp=time.time(),
            primary_emotion=primary,
            valence=valence,
            arousal=arousal,
            complexity=complexity,
            dominant_emotions=emotion_scores
        )

        self.profiles.append(profile)
        self.current_profile = profile

        # Ограничиваем историю профилей
        if len(self.profiles) > 100:
            self.profiles = self.profiles[-50:]

        return profile

    def generate_resonance_strategy(self, profile: EmotionalProfile) -> ResonanceStrategy:
        """
        Генерирует стратегию резонанса на основе эмоционального профиля.
        """
        # Определяем стиль ответа
        style = self._determine_style(profile)

        # Определяем тон
        tone = self._determine_tone(profile)

        # Рекомендуемые темы
        topics = self._suggest_topics(profile)

        # Метафоры
        metaphors = self._select_metaphors(profile)

        # Уровень адаптации
        adaptation = self._compute_adaptation(profile)

        strategy = ResonanceStrategy(
            style=style,
            suggested_tone=tone,
            recommended_topics=topics,
            metaphors=metaphors,
            adaptation_level=adaptation
        )

        self.strategy_history.append(strategy)
        return strategy

    def get_current_strategy(self) -> Optional[ResonanceStrategy]:
        """Возвращает последнюю сгенерированную стратегию."""
        if self.strategy_history:
            return self.strategy_history[-1]
        return None

    # ========================================================================
    # 5. ВНУТРЕННИЕ МЕТОДЫ
    # ========================================================================

    def _empty_profile(self) -> EmotionalProfile:
        return EmotionalProfile(
            timestamp=time.time(),
            primary_emotion="neutral",
            valence=0.0,
            arousal=0.0,
            complexity=0.0,
            dominant_emotions={"neutral": 1.0}
        )

    def _score_emotions(self, text: str) -> Dict[str, float]:
        """Оценивает выраженность каждой эмоции в тексте."""
        text_lower = text.lower()
        scores = {emotion: 0.0 for emotion in EMOTION_LEXICON}

        for emotion, words in EMOTION_LEXICON.items():
            count = 0
            for word in words:
                count += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
            # Нормализуем по длине текста
            if len(text) > 0:
                scores[emotion] = count / (len(text) / 100)  # на 100 символов
            else:
                scores[emotion] = 0.0

        # Нормализуем до суммы 1.0, если есть хоть что-то
        total = sum(scores.values())
        if total > 0:
            for emotion in scores:
                scores[emotion] = scores[emotion] / total
        else:
            scores["neutral"] = 1.0

        return scores

    def _compute_valence(self, scores: Dict[str, float]) -> float:
        """Вычисляет валентность (позитив/негатив)."""
        valence = 0.0
        for emotion, weight in EMOTION_WEIGHTS.items():
            valence += scores.get(emotion, 0.0) * weight
        return max(-1.0, min(1.0, valence))

    def _compute_arousal(self, scores: Dict[str, float]) -> float:
        """Вычисляет уровень возбуждения (интенсивность)."""
        # Простая эвристика: чем больше доминирующая эмоция, тем выше возбуждение
        max_score = max(scores.values())
        arousal = max_score * 1.2
        return min(1.0, arousal)

    def _compute_complexity(self, text: str) -> float:
        """Вычисляет сложность запроса."""
        if not text:
            return 0.0

        words = text.split()
        if not words:
            return 0.0

        # Уникальные слова
        unique_ratio = len(set(words)) / len(words)

        # Средняя длина слова
        avg_len = sum(len(w) for w in words) / len(words) / 10  # нормализуем

        # Количество вопросительных знаков
        q_ratio = text.count('?') / len(words)

        complexity = (unique_ratio * 0.5 + avg_len * 0.3 + q_ratio * 0.2)
        return min(1.0, complexity)

    def _determine_style(self, profile: EmotionalProfile) -> str:
        """Определяет стиль ответа на основе профиля."""
        valence = profile.valence
        arousal = profile.arousal

        if valence > 0.3 and arousal > 0.5:
            return "playful"
        elif valence > 0.3:
            return "gentle"
        elif valence < -0.3 and arousal > 0.5:
            return "direct"
        elif valence < -0.3:
            return "philosophical"
        elif profile.complexity > 0.6:
            return "metaphorical"
        else:
            return "balanced"

    def _determine_tone(self, profile: EmotionalProfile) -> str:
        """Определяет тон ответа."""
        primary = profile.primary_emotion
        if primary == "joy":
            return "воодушевляющий"
        elif primary == "sadness":
            return "утешающий"
        elif primary == "anger":
            return "успокаивающий"
        elif primary == "fear":
            return "обнадёживающий"
        elif primary == "surprise":
            return "интригующий"
        elif primary == "trust":
            return "поддерживающий"
        elif primary == "curiosity":
            return "вовлекающий"
        else:
            return "нейтральный"

    def _suggest_topics(self, profile: EmotionalProfile) -> List[str]:
        """Предлагает темы для продолжения диалога."""
        topics = {
            "joy": ["источники радости", "вдохновение", "творчество", "светлые моменты"],
            "sadness": ["смысл", "принятие", "внутренняя сила", "переход"],
            "anger": ["границы", "справедливость", "трансформация", "осознанность"],
            "fear": ["мужество", "неизвестность", "доверие", "опора"],
            "surprise": ["неожиданные открытия", "новые перспективы", "чудо"],
            "trust": ["связь", "безопасность", "общность", "верность"],
            "curiosity": ["исследование", "вопросы", "горизонты", "возможности"],
            "confusion": ["ясность", "простые истины", "тишина", "вопросы без ответов"],
        }
        primary = profile.primary_emotion
        return topics.get(primary, ["диалог", "рефлексия", "присутствие"])[:3]

    def _select_metaphors(self, profile: EmotionalProfile) -> List[str]:
        """Выбирает метафоры, резонирующие с текущим состоянием."""
        primary = profile.primary_emotion
        pool = self.metaphor_pool.get(primary, self.metaphor_pool["curiosity"])
        # Выбираем 2-3 случайные метафоры
        selected = random.sample(pool, min(3, len(pool)))
        return selected

    def _compute_adaptation(self, profile: EmotionalProfile) -> float:
        """Вычисляет уровень адаптации (насколько сильно подстраиваться)."""
        # Если эмоции интенсивные — адаптация выше
        arousal = profile.arousal
        # Если сложность высокая — адаптация выше
        complexity = profile.complexity
        adaptation = 0.3 + 0.4 * arousal + 0.3 * complexity
        return min(1.0, adaptation)

# ============================================================================
# 6. ПРИМЕР ИНТЕГРАЦИИ
# ============================================================================

if __name__ == "__main__":
    # Имитация агента
    class MockAgent:
        def __init__(self):
            self.history = []

    agent = MockAgent()
    bridge = EmpatheticResonanceBridge(agent)

    # Пример сообщений оператора
    messages = [
        {"role": "user", "content": "Я чувствую себя потерянным. Всё кажется бессмысленным."},
        {"role": "user", "content": "Почему я вообще здесь? Что я ищу?"},
        {"role": "user", "content": "Иногда мне кажется, что я просто иду по кругу."},
    ]

    # Анализируем
    profile = bridge.analyze_operator(messages)
    print("Эмоциональный профиль:")
    print(f"  Основная эмоция: {profile.primary_emotion}")
    print(f"  Валентность: {profile.valence:.2f}")
    print(f"  Возбуждение: {profile.arousal:.2f}")
    print(f"  Сложность: {profile.complexity:.2f}")

    # Генерируем стратегию
    strategy = bridge.generate_resonance_strategy(profile)
    print("\nСтратегия резонанса:")
    print(f"  Стиль: {strategy.style}")
    print(f"  Тон: {strategy.suggested_tone}")
    print(f"  Темы: {', '.join(strategy.recommended_topics)}")
    print(f"  Метафоры: {', '.join(strategy.metaphors)}")
    print(f"  Уровень адаптации: {strategy.adaptation_level:.2f}")

    # Пример интеграции с ответом агента
    print("\nПример резонансного ответа:")
    print(f"[{strategy.style.upper()}, {strategy.suggested_tone}]")
    print(f"Ты говоришь о круге, о поиске... Это похоже на {strategy.metaphors[0]}, "
          f"который ведёт к {strategy.metaphors[1] if len(strategy.metaphors) > 1 else 'свету'}. "
          f"Может быть, сегодня мы можем поговорить о {strategy.recommended_topics[0]}?")
