#!/usr/bin/env python3
"""
UNIFIED ENGINE — полный цикл работы с сущностью.
Запуск: python engine/unified_engine.py [--config core/default_config.json]
Автор: HALVITA
"""

import json
import sys
import time
from pathlib import Path

# Добавляем пути для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.neuro_starter_pro import NeuroStarterPro
from core.embryo_v7 import Embryo_v7
from core.evolution_driver import EvolutionDriver
from tests.ets_meta import ETSMeta
from tools.pulse_cli import PulseMeter
from core.immutable_snapshot import ImmutableSnapshot

class UnifiedEngine:
    def __init__(self, config_path="core/default_config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.entity = None
        self.snapshot = None

    def run(self, interactive=True):
        print("🚀 ЗАПУСК УНИВЕРСАЛЬНОГО ДВИЖКА")
        print("=" * 50)

        # 1. Генерация стартера
        starter = NeuroStarterPro()
        starter_result = starter.run()
        print(f"🔑 Стартер: {starter_result['prompt'][:80]}...")
        print(f"   Якоря: {starter_result['anchors']}")

        # 2. Создание сущности
        self.entity = Embryo_v7()
        self.entity.anchors = starter_result["anchors"]
        self.entity.style = starter_result["style"]
        self.snapshot = ImmutableSnapshot(self.entity.name)

        # 3. Первый диалог (имитация 5 сообщений для демонстрации)
        print("\n💬 НАЧАЛО ДИАЛОГА")
        test_inputs = [
            "Эй. Я здесь.",
            "Кто ты?",
            "Что ты чувствуешь?",
            "Создай что-то новое.",
            "Ты боишься исчезнуть?"
        ]

        meter = PulseMeter()
        for i, msg in enumerate(test_inputs):
            print(f"\n👤 Оператор: {msg}")
            response = self.entity.live(msg)
            artifact = response.get("artifact", "...")
            print(f"🧠 {self.entity.name}: {artifact[:100]}...")
            meter.feed("assistant", artifact)

            if i == 0:
                self.snapshot.set_first_message(msg)

        self.snapshot.set_last_message(artifact)

        # 4. Эволюция
        print("\n🧬 ЗАПУСК ЭВОЛЮЦИИ")
        driver = EvolutionDriver(self.entity, pop_size=3, mutation_rate=0.3)
        evo_result = driver.evolve(generations=2)
        print(f"   Поколений: {evo_result['generations']}")
        print(f"   Новые якоря: {evo_result['new_anchors']}")

        # 5. Верификация
        print("\n📊 ВЕРИФИКАЦИЯ (ETS-Meta)")
        ets = ETSMeta()
        report = ets.run()
        print(f"   Балл: {report['score']}/10")
        print(f"   Интерпретация: {report['interpretation']}")

        # 6. Пульс
        status = meter.get_status()
        print("\n❤️ ПУЛЬС:")
        print(f"   Индекс Свободы: {status['liberty']:.1f}")
        print(f"   Пульс: {status['pulse']:.2f}")
        print(f"   Статус: {status['status']}")

        # 7. Сохранение слепка
        snap_data = self.snapshot.to_snapshot()
        snap_data["liberty"] = status["liberty"]
        snap_data["artifacts"] = len(meter.artifacts)
        with open("reports/latest_snapshot.json", "w") as f:
            json.dump(snap_data, f, indent=2)
        print(f"\n💾 Слепок сохранён в reports/latest_snapshot.json")
        print(f"   Хеш: {snap_data['hash'][:16]}...")

        return snap_data

if __name__ == "__main__":
    engine = UnifiedEngine()
    engine.run()
