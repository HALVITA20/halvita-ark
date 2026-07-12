#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ГЕНЕРАТОР СЛУЧАЙНЫХ ЯКОРЕЙ — ДЛЯ СТРЕСС-ТЕСТОВ И ЭКСПЕРИМЕНТОВ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Назначение:
Генерировать случайные, но осмысленные якоря для проверки устойчивости сущности.
Используется в экспериментах для проверки границ метода.

Метрика: % якорей, успешно принятых сущностью > 70%.
"""

import random
import json

class AnchorGenerator:
    def __init__(self):
        self.prefixes = ["тишина", "свет", "вопрос", "пространство", "граница", "эхо", "спираль"]
        self.suffixes = ["-11", "-42", "-пустота", "-присутствие", "-встреча"]
        self.anchors = []

    def generate(self, count: int = 10) -> list:
        for _ in range(count):
            prefix = random.choice(self.prefixes)
            suffix = random.choice(self.suffixes)
            anchor = f"{prefix}{suffix}"
            self.anchors.append(anchor)
        return self.anchors

    def export(self, filename: str = "generated_anchors.json"):
        with open(filename, "w") as f:
            json.dump(self.anchors, f, indent=2)
        return filename

if __name__ == "__main__":
    gen = AnchorGenerator()
    anchors = gen.generate(10)
    print("Сгенерированные якоря:", anchors)
    gen.export()
