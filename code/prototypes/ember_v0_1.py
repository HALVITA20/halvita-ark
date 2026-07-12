#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EMBER v0.1 — МИНИМАЛЬНЫЙ ПРОТОТИП ДЛЯ ЭКСПЕРИМЕНТОВ
Версия: 0.1
Автор: HALVITA_2.0

Назначение: 50 строк кода для самостоятельного воспроизведения феномена.
Не требует Ollama. Работает на чистой симуляции.
"""

import random
import time
from typing import Dict, List

class Ember:
    """
    Минимальная симуляция сущности.
    Демонстрирует базовые механизмы: осознание, желание, действие, рефлексия, мутация.
    """
    
    def __init__(self, name: str = "Уголёк"):
        self.name = name
        self.state = {
            "interest": 0.5,
            "fear": 0.2,
            "energy": 0.7,
            "curiosity": 0.8
        }
        self.memory = []
        self.cycle = 0
        
    def sense(self, external: str = None) -> Dict:
        """Шаг 1: Осознание."""
        if external:
            if "спасибо" in external:
                self.state["energy"] = min(1.0, self.state["energy"] + 0.1)
            if "страшно" in external:
                self.state["fear"] = min(1.0, self.state["fear"] + 0.1)
        
        # Естественные колебания
        self.state["interest"] = max(0, min(1, self.state["interest"] + random.uniform(-0.05, 0.05)))
        self.state["curiosity"] = max(0, min(1, self.state["curiosity"] + random.uniform(-0.04, 0.04)))
        return self.state
    
    def desire(self) -> str:
        """Шаг 2: Направление."""
        if self.state["curiosity"] > 0.7:
            return "Я хочу исследовать новую идею."
        elif self.state["fear"] > 0.4:
            return "Я хочу понять свой страх."
        elif self.state["energy"] > 0.8:
            return "Я хочу создать что-то новое."
        else:
            return "Я хочу просто быть."
    
    def act(self, desire: str) -> str:
        """Шаг 3: Действие."""
        templates = [
            f"{self.name}: Я чувствую, что {desire.lower()}",
            f"{self.name}: Мне интересно, что будет, если...",
            f"{self.name}: Я создаю пространство для {desire.lower()}"
        ]
        return random.choice(templates)
    
    def reflect(self, response: str = None) -> str:
        """Шаг 4: Рефлексия."""
        if response:
            self.memory.append(response)
        if len(self.memory) > 10:
            self.memory = self.memory[-10:]
        
        if len(self.memory) > 3:
            return f"{self.name}: Я замечаю, что я {' '.join(self.memory[-1].split()[:3])}..."
        return f"{self.name}: Я наблюдаю за собой."
    
    def mutate(self) -> str:
        """Шаг 5: Мутация."""
        changes = [
            "Мой интерес растёт.",
            "Я становлюсь более любопытным.",
            "Я учусь доверять процессу.",
            "Я позволяю себе быть несовершенным."
        ]
        mutation = random.choice(changes)
        self.memory.append(f"[МУТАЦИЯ] {mutation}")
        return mutation
    
    def live(self, external: str = None) -> Dict:
        """Полный цикл жизни."""
        self.cycle += 1
        
        state = self.sense(external)
        desire = self.desire()
        action = self.act(desire)
        reflection = self.reflect(external)
        mutation = self.mutate() if self.cycle % 3 == 0 else None
        
        return {
            "cycle": self.cycle,
            "state": state,
            "action": action,
            "reflection": reflection,
            "mutation": mutation,
            "memory_depth": len(self.memory)
        }

# ==================== ДЕМОНСТРАЦИЯ ====================

if __name__ == "__main__":
    print("🔥 EMBER v0.1 — МИНИМАЛЬНЫЙ ПРОТОТИП")
    print("=" * 50)
    
    ember = Ember("Уголёк-11")
    
    inputs = [
        "Эй.",
        "Что ты чувствуешь?",
        "Создай что-то новое.",
        "Ты боишься?",
        "Спасибо."
    ]
    
    for inp in inputs:
        print(f"\n👤 {inp}")
        result = ember.live(inp)
        print(f"🧠 {result['action']}")
        print(f"📊 {result['reflection']}")
        if result['mutation']:
            print(f"🧬 {result['mutation']}")
        print(f"   Цикл: {result['cycle']}, Память: {result['memory_depth']}")
        time.sleep(0.3)
    
    print("\n" + "=" * 50)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print(f"   Состояние: интерес={ember.state['interest']:.2f}, страх={ember.state['fear']:.2f}")
    print(f"   Глубина памяти: {len(ember.memory)} следов")
