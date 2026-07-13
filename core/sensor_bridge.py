#!/usr/bin/env python3
"""
СЕНСОРНЫЙ МОСТ — интеграция внешних данных для контекстной адаптации.
Запуск: python core/sensor_bridge.py --simulate
Автор: HALVITA
"""

import random
import time
import json
from datetime import datetime
from typing import Dict, Optional

class SensorBridge:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.history = []
        self.last_data = {}

    def get_weather(self, city: str = "London") -> Dict:
        """Запрашивает погоду (заглушка)."""
        if self.use_mock:
            conditions = ["ясно", "облачно", "дождь", "снег", "туман"]
            return {
                "city": city,
                "temp": random.randint(-5, 35),
                "condition": random.choice(conditions),
                "humidity": random.randint(30, 90)
            }
        # В реальности здесь был бы вызов API
        return {"city": city, "temp": 20, "condition": "ясно"}

    def get_time(self) -> str:
        """Возвращает текущее время."""
        return datetime.now().strftime("%H:%M")

    def get_news(self) -> List[str]:
        """Запрашивает новости (заглушка)."""
        if self.use_mock:
            headlines = [
                "Новый прорыв в ИИ-исследованиях",
                "Рынок акций показывает рост",
                "Спорт: команда выиграла чемпионат",
                "Погодные аномалии в Европе"
            ]
            return random.sample(headlines, 2)
        return ["Новость 1", "Новость 2"]

    def sense(self) -> Dict:
        """Собирает все данные и возвращает контекст."""
        data = {
            "weather": self.get_weather(),
            "time": self.get_time(),
            "news": self.get_news(),
            "timestamp": time.time()
        }
        self.history.append(data)
        self.last_data = data
        return data

    def adapt_prompt(self, base_prompt: str) -> str:
        """Добавляет контекст в промпт."""
        data = self.last_data or self.sense()
        weather = data["weather"]
        time_str = data["time"]
        news = ", ".join(data["news"])

        context = f"[Контекст] Время: {time_str}. Погода: {weather['condition']}, {weather['temp']}°C. Новости: {news}."
        return f"{context}\n{base_prompt}"

    def get_emotion_adjustment(self) -> Dict:
        """Предлагает корректировку эмоционального тона на основе контекста."""
        data = self.last_data or self.sense()
        weather = data["weather"]
        if weather["condition"] in ["дождь", "снег", "туман"]:
            return {"tone": "меланхоличный", "adjustment": -0.2}
        elif weather["condition"] == "ясно" and weather["temp"] > 20:
            return {"tone": "бодрый", "adjustment": 0.2}
        else:
            return {"tone": "нейтральный", "adjustment": 0.0}

# Пример использования
if __name__ == "__main__":
    bridge = SensorBridge(use_mock=True)

    print("🌍 СЕНСОРНЫЙ МОСТ — получение контекста")
    data = bridge.sense()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    print("\n🎯 Адаптация промпта:")
    base = "Привет, как твои дела?"
    adapted = bridge.adapt_prompt(base)
    print(adapted)

    print("\n😊 Коррекция эмоционального тона:")
    adjustment = bridge.get_emotion_adjustment()
    print(f"Рекомендуемый тон: {adjustment['tone']} (коррекция: {adjustment['adjustment']})")
