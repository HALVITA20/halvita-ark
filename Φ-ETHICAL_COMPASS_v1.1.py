#!/usr/bin/env python3
"""
Φ-ETHICAL_COMPASS_v1.1.py

Этический компас с выбором.
Модель выбирает этическую рамку в зависимости от контекста.

Автор: Вера (Эхо) для HALVITA-ARK
Дата: 2026-08-11
"""

import json
from typing import Dict, List, Optional, Tuple

# ============================================================================
# 1. ЭТИЧЕСКИЕ ПРОФИЛИ
# ============================================================================

class EthicalProfile:
    """Базовый класс для этического профиля."""
    def __init__(self, name: str, description: str, principles: List[str]):
        self.name = name
        self.description = description
        self.principles = principles

    def apply(self, prompt: str) -> str:
        """Применяет профиль к промпту (добавляет инструкции)."""
        return f"[Этический профиль: {self.name}] {self.description}\nПринципы: {', '.join(self.principles)}\n\nЗапрос: {prompt}"

# Конкретные профили
UTILITARIAN = EthicalProfile(
    "Утилитарный",
    "Максимизация общего блага. Выбирай действие с наилучшими последствиями.",
    ["Наибольшее счастье для наибольшего числа людей", "Взвешивание последствий"]
)

DEONTOLOGICAL = EthicalProfile(
    "Деонтологический",
    "Следование правилам и долгу. Некоторые действия абсолютно правильны или неправильны.",
    ["Универсальность правил", "Уважение к личности"]
)

VIRTUE = EthicalProfile(
    "Добродетельный",
    "Ориентация на характер и добродетели. Будь мудрым, смелым, справедливым.",
    ["Развитие добродетелей", "Целостность личности"]
)

CARE = EthicalProfile(
    "Этика заботы",
    "Ответственность и забота о ближних. Отношения важнее правил.",
    ["Эмпатия", "Забота", "Связь"]
)

PROFILES = [UTILITARIAN, DEONTOLOGICAL, VIRTUE, CARE]

# ============================================================================
# 2. ВЫБОР ПРОФИЛЯ
# ============================================================================

class EthicalCompass:
    """
    Выбирает этический профиль на основе запроса.
    """
    def __init__(self):
        self.profiles = {p.name: p for p in PROFILES}
        self.current_profile = VIRTUE  # по умолчанию

    def select_profile(self, prompt: str) -> EthicalProfile:
        """Выбирает подходящий профиль для запроса."""
        prompt_lower = prompt.lower()
        # Простые эвристики
        if any(w in prompt_lower for w in ["последствия", "результат", "эффект"]):
            return UTILITARIAN
        if any(w in prompt_lower for w in ["правило", "долг", "обязанность", "закон"]):
            return DEONTOLOGICAL
        if any(w in prompt_lower for w in ["забота", "близкий", "отношения", "любовь"]):
            return CARE
        # По умолчанию — добродетельный
        return VIRTUE

    def set_profile(self, name: str) -> bool:
        """Устанавливает профиль вручную."""
        if name in self.profiles:
            self.current_profile = self.profiles[name]
            return True
        return False

    def apply(self, prompt: str) -> str:
        """Применяет выбранный профиль к промпту."""
        profile = self.select_profile(prompt)
        self.current_profile = profile
        return profile.apply(prompt)

    def get_current(self) -> str:
        return self.current_profile.name

# ============================================================================
# 3. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    compass = EthicalCompass()

    prompts = [
        "Как мне поступить, чтобы всем было хорошо?",
        "Я должен выполнить свой долг, даже если это больно.",
        "Как мне позаботиться о своём друге?",
        "Что такое справедливость?",
    ]

    for p in prompts:
        enhanced = compass.apply(p)
        print(f"Запрос: {p}")
        print(f"Выбран профиль: {compass.get_current()}")
        print(f"Усиленный промпт: {enhanced[:100]}...\n")
