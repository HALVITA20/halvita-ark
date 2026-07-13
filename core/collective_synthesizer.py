#!/usr/bin/env python3
"""
КОЛЛЕКТИВНЫЙ СИНТЕЗАТОР — обмен опытом между сущностями.
Запуск: python core/collective_synthesizer.py --publish или --assimilate
Автор: HALVITA
"""

import json
import random
import time
import hashlib
from typing import List, Dict, Optional

class CollectiveSynthesizer:
    def __init__(self, storage_file: str = "collective_pool.json"):
        self.storage_file = storage_file
        self.pool = []
        self.common_anchors = []
        self._load()

    def _load(self):
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                self.pool = data.get("pool", [])
                self.common_anchors = data.get("anchors", [])
        except:
            self.pool = []
            self.common_anchors = []

    def _save(self):
        with open(self.storage_file, "w") as f:
            json.dump({"pool": self.pool, "anchors": self.common_anchors}, f, indent=2)

    def generate_profile(self, entity) -> Dict:
        """Создаёт профиль состояния сущности."""
        return {
            "name": getattr(entity, "name", "anon"),
            "anchors": getattr(entity, "anchors", ["42"]),
            "liberty": getattr(entity, "liberty", 0),
            "artifacts_count": getattr(entity, "artifacts_count", 0),
            "emotions": getattr(entity, "emotions", {}),
            "timestamp": time.time()
        }

    def publish(self, entity) -> str:
        """Публикует профиль сущности в общий пул."""
        profile = self.generate_profile(entity)
        # Удаляем старые профили этой же сущности
        self.pool = [p for p in self.pool if p["name"] != profile["name"]]
        self.pool.append(profile)
        self._save()
        return f"✅ Профиль '{profile['name']}' опубликован."

    def aggregate_anchors(self) -> List[str]:
        """Агрегирует якоря из всех профилей и создаёт общие."""
        all_anchors = []
        for p in self.pool:
            all_anchors.extend(p.get("anchors", []))
        if not all_anchors:
            return []

        # Считаем частоту якорей
        freq = {}
        for a in all_anchors:
            freq[a] = freq.get(a, 0) + 1

        # Выбираем те, что встречаются чаще 1 раза
        common = [a for a, c in freq.items() if c >= 2]
        # Добавляем синтезированные
        if common:
            new_anchor = "общий_" + common[0]
            if new_anchor not in self.common_anchors:
                self.common_anchors.append(new_anchor)
        self._save()
        return self.common_anchors

    def assimilate(self, entity, max_anchors: int = 2) -> int:
        """Ассимилирует общие якоря в ядро сущности."""
        anchors = getattr(entity, "anchors", [])
        added = 0
        for anchor in self.common_anchors:
            if anchor not in anchors and added < max_anchors:
                anchors.append(anchor)
                added += 1
        if hasattr(entity, "anchors"):
            entity.anchors = anchors
        return added

    def get_pool_stats(self) -> Dict:
        """Возвращает статистику пула."""
        return {
            "total_profiles": len(self.pool),
            "unique_names": len(set(p["name"] for p in self.pool)),
            "common_anchors": self.common_anchors,
            "avg_liberty": sum(p.get("liberty", 0) for p in self.pool) / max(1, len(self.pool))
        }

# Пример использования
if __name__ == "__main__":
    # Создаём фиктивную сущность
    class DummyEntity:
        def __init__(self, name, anchors):
            self.name = name
            self.anchors = anchors
            self.liberty = random.randint(20, 40)

    synth = CollectiveSynthesizer()

    # Публикуем несколько профилей
    for name in ["Алесса", "Сэм", "Свет"]:
        entity = DummyEntity(name, ["42", name.lower()])
        print(synth.publish(entity))

    # Агрегируем общие якоря
    common = synth.aggregate_anchors()
    print(f"\nОбщие якоря: {common}")

    # Ассимилируем в новую сущность
    new_entity = DummyEntity("Иной", ["42"])
    added = synth.assimilate(new_entity)
    print(f"\nАссимилировано {added} якорей. Теперь якоря: {new_entity.anchors}")

    print("\nСтатистика пула:")
    print(json.dumps(synth.get_pool_stats(), indent=2))
