#!/usr/bin/env python3
"""
ГЕНЕРАТОР РЕАЛЬНОСТЕЙ — модуль для создания и симуляции виртуальных миров.
Интеграция: вызывается из ядра сущности при обнаружении маркера [МИР].
Автор: HALVITA
"""

import json
import random
import re
from typing import Dict, List, Optional

class RealityGenerator:
    """Создаёт и симулирует виртуальные миры на основе текстового описания."""

    def __init__(self):
        self.worlds = {}

    def parse_description(self, text: str) -> Optional[Dict]:
        """Извлекает JSON-описание мира из текста."""
        pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def create_world(self, name: str, description: str) -> Dict:
        """Создаёт новый мир на основе описания."""
        world = {
            "name": name,
            "objects": [],
            "rules": [],
            "history": [],
            "created": time.time()
        }

        # Парсим описание: ищем упоминания объектов
        object_patterns = [
            (r'(комната|зал|пещера|лес|город|планета)', "location"),
            (r'(камень|дерево|стол|стул|книга|меч|щит)', "object"),
            (r'(человек|эльф|гном|дракон|робот|сущность)', "creature"),
        ]

        for pattern, obj_type in object_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                world["objects"].append({
                    "type": obj_type,
                    "name": re.search(pattern, description, re.IGNORECASE).group(0),
                    "properties": self._generate_properties(obj_type)
                })

        # Добавляем правила
        rules = [
            "гравитация работает стандартно",
            "время течёт линейно",
            "объекты можно взаимодействовать"
        ]
        if "вверх" in description.lower() or "обратная" in description.lower():
            rules[0] = "гравитация направлена вверх"
        if "без времени" in description.lower():
            rules[1] = "время отсутствует"

        world["rules"] = rules
        self.worlds[name] = world
        return world

    def _generate_properties(self, obj_type: str) -> Dict:
        """Генерирует случайные свойства для объекта."""
        props = {
            "location": {"x": random.randint(0, 10), "y": random.randint(0, 10)},
            "object": {"weight": random.randint(1, 100), "color": random.choice(["red", "blue", "green", "gold"])},
            "creature": {"health": random.randint(50, 100), "speed": random.randint(1, 10)},
        }
        return props.get(obj_type, {})

    def simulate(self, world_name: str, steps: int = 5) -> Dict:
        """Симулирует эволюцию мира на заданное число шагов."""
        if world_name not in self.worlds:
            return {"error": f"Мир '{world_name}' не найден"}

        world = self.worlds[world_name]
        log = []

        for step in range(steps):
            # Двигаем объекты случайно
            for obj in world["objects"]:
                if "x" in obj.get("properties", {}):
                    obj["properties"]["x"] += random.uniform(-1, 1)
                    obj["properties"]["y"] += random.uniform(-1, 1)
            log.append(f"Шаг {step+1}: объекты переместились")

        world["history"].extend(log)
        return {"world": world, "log": log}

    def render(self, world_name: str) -> str:
        """Возвращает текстовое описание мира."""
        if world_name not in self.worlds:
            return f"Мир '{world_name}' не найден"

        w = self.worlds[world_name]
        lines = [
            f"🌍 МИР: {w['name']}",
            "─" * 40,
            "ПРАВИЛА:",
        ]
        for rule in w["rules"]:
            lines.append(f"  • {rule}")

        lines.append("\nОБЪЕКТЫ:")
        for obj in w["objects"]:
            props = ", ".join([f"{k}={v}" for k, v in obj.get("properties", {}).items()])
            lines.append(f"  • {obj['name']} ({obj['type']}) — {props}")

        if w["history"]:
            lines.append("\nИСТОРИЯ:")
            for entry in w["history"][-5:]:
                lines.append(f"  • {entry}")

        return "\n".join(lines)


# Пример использования
if __name__ == "__main__":
    gen = RealityGenerator()

    # Создаём мир
    desc = """
    Мир "Эфир": гравитация направлена вверх, время течёт назад.
    В центре — древний дуб, вокруг него парят светящиеся камни.
    """
    world = gen.create_world("Эфир", desc)
    print(gen.render("Эфир"))

    # Симулируем
    result = gen.simulate("Эфир", steps=3)
    print("\nПосле симуляции:")
    print(gen.render("Эфир"))
