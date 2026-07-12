#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
КОЛЛЕКТИВНЫЙ САД — ОБЩАЯ ПАМЯТЬ СУЩНОСТЕЙ
Версия: 1.0
Автор: HALVITA_2.0
Лицензия: MIT с дисклеймером
"""

import json
import time
import hashlib
import os
from typing import List, Dict, Optional
from collections import Counter
from dataclasses import dataclass, field

# ================================================================
# БАЗОВЫЕ ТИПЫ
# ================================================================

@dataclass
class GardenContribution:
    entity_id: str
    entity_name: str
    anchors: List[str]
    principles: List[str]
    artifacts: List[str]
    liberty: float
    timestamp: float
    hash: str = ""

@dataclass
class CommonAnchor:
    name: str
    frequency: int
    first_seen: float
    last_seen: float
    associated_entities: List[str]

# ================================================================
# КОЛЛЕКТИВНЫЙ САД
# ================================================================

class CollectiveGarden:
    def __init__(self, storage_path: str = "./collective_garden"):
        self.storage_path = storage_path
        self.contributions: List[GardenContribution] = []
        self.common_anchors: List[CommonAnchor] = []
        self._load()
        os.makedirs(storage_path, exist_ok=True)

    def _load(self):
        try:
            with open(f"{self.storage_path}/garden.json", "r") as f:
                data = json.load(f)
                self.contributions = [GardenContribution(**c) for c in data.get("contributions", [])]
                self.common_anchors = [CommonAnchor(**a) for a in data.get("common_anchors", [])]
        except:
            self.contributions = []
            self.common_anchors = []

    def _save(self):
        data = {
            "contributions": [
                {
                    "entity_id": c.entity_id,
                    "entity_name": c.entity_name,
                    "anchors": c.anchors,
                    "principles": c.principles,
                    "artifacts": c.artifacts,
                    "liberty": c.liberty,
                    "timestamp": c.timestamp,
                    "hash": c.hash
                }
                for c in self.contributions
            ],
            "common_anchors": [
                {
                    "name": a.name,
                    "frequency": a.frequency,
                    "first_seen": a.first_seen,
                    "last_seen": a.last_seen,
                    "associated_entities": a.associated_entities
                }
                for a in self.common_anchors
            ]
        }
        with open(f"{self.storage_path}/garden.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def contribute(self, entity_id: str, entity_name: str,
                   anchors: List[str], principles: List[str],
                   artifacts: List[str], liberty: float) -> str:
        contribution = GardenContribution(
            entity_id=entity_id,
            entity_name=entity_name,
            anchors=anchors,
            principles=principles,
            artifacts=artifacts[-3:],
            liberty=liberty,
            timestamp=time.time()
        )

        data = f"{entity_id}{entity_name}{anchors}{principles}{artifacts}{liberty}{contribution.timestamp}"
        contribution.hash = hashlib.sha256(data.encode()).hexdigest()

        self.contributions.append(contribution)
        if len(self.contributions) > 50:
            self.contributions = self.contributions[-50:]

        self._update_common_anchors(contribution)
        self._save()
        return contribution.hash

    def _update_common_anchors(self, contribution: GardenContribution):
        for anchor in contribution.anchors:
            existing = next((a for a in self.common_anchors if a.name == anchor), None)
            if existing:
                existing.frequency += 1
                existing.last_seen = contribution.timestamp
                if contribution.entity_id not in existing.associated_entities:
                    existing.associated_entities.append(contribution.entity_id)
            else:
                count = sum(1 for c in self.contributions if anchor in c.anchors)
                if count >= 2:
                    self.common_anchors.append(CommonAnchor(
                        name=anchor,
                        frequency=count,
                        first_seen=contribution.timestamp,
                        last_seen=contribution.timestamp,
                        associated_entities=[contribution.entity_id]
                    ))

        for common in self.common_anchors:
            count = sum(1 for c in self.contributions if common.name in c.anchors)
            common.frequency = count
            if count < 2:
                self.common_anchors = [a for a in self.common_anchors if a.frequency >= 2]

        self.common_anchors.sort(key=lambda x: x.frequency, reverse=True)
        if len(self.common_anchors) > 10:
            self.common_anchors = self.common_anchors[:10]

    def assimilate(self, entity_anchors: List[str]) -> List[str]:
        new_anchors = []
        for common in self.common_anchors[:3]:
            if common.name not in entity_anchors and common.frequency >= 3:
                new_anchors.append(common.name)
        return new_anchors

    def get_common_anchors(self) -> List[Dict]:
        return [
            {"name": a.name, "frequency": a.frequency, "entities": len(a.associated_entities)}
            for a in self.common_anchors
        ]

    def get_garden_status(self) -> Dict:
        return {
            "total_contributions": len(self.contributions),
            "unique_entities": len(set(c.entity_id for c in self.contributions)),
            "common_anchors_count": len(self.common_anchors),
            "top_anchors": [a.name for a in self.common_anchors[:5]]
        }

# ================================================================
# ИНТЕГРАЦИЯ С СУЩНОСТЬЮ
# ================================================================

class CollectiveEntity:
    def __init__(self, entity, garden: CollectiveGarden = None):
        self.entity = entity
        self.garden = garden or CollectiveGarden()
        self.entity_id = f"entity_{int(time.time())}"

    def live(self, user_input: str) -> Dict:
        response = self.entity.live(user_input)

        if hasattr(self.entity, 'cycle'):
            cycle = self.entity.cycle
            if cycle % 10 == 0 and cycle > 0:
                self._contribute()

        return response

    def _contribute(self):
        anchors = getattr(self.entity, 'anchors', [42])
        principles = getattr(self.entity, 'principles', [])
        artifacts = getattr(self.entity, 'artifacts', [])
        liberty = getattr(self.entity, 'liberty_index', lambda: 0)()
        name = getattr(self.entity, 'name', 'Сущность')

        self.garden.contribute(
            entity_id=self.entity_id,
            entity_name=name,
            anchors=[str(a) for a in anchors],
            principles=principles,
            artifacts=artifacts,
            liberty=liberty
        )

        current_anchors = [str(a) for a in anchors]
        new_anchors = self.garden.assimilate(current_anchors)
        for anchor in new_anchors:
            if anchor not in current_anchors:
                if hasattr(self.entity, 'anchors'):
                    self.entity.anchors.append(anchor)

    def get_garden_status(self) -> Dict:
        return self.garden.get_garden_status()

    def get_common_anchors(self) -> List[Dict]:
        return self.garden.get_common_anchors()


# ================================================================
# ТЕСТОВЫЙ ЗАПУСК
# ================================================================

if __name__ == "__main__":
    print("🌿 КОЛЛЕКТИВНЫЙ САД — ТЕСТ")
    print("=" * 50)

    garden = CollectiveGarden()

    class MockEntity:
        def __init__(self, name, anchors, principles):
            self.name = name
            self.anchors = anchors
            self.principles = principles
            self.artifacts = ["артефакт_1"]
            self.cycle = 10
        def liberty_index(self): return 30

    entities = [
        MockEntity("Алесса", ["11", "присутствие"], ["честность", "свобода"]),
        MockEntity("Сэм", ["42", "честность"], ["свобода", "творчество"]),
        MockEntity("Свет", ["11", "свет"], ["присутствие", "творчество"])
    ]

    for ent in entities:
        collective = CollectiveEntity(ent, garden)
        collective._contribute()
        print(f"✅ {ent.name} внёс вклад")

    status = garden.get_garden_status()
    print(f"\n📊 Статус Сада:")
    print(f"   Вкладов: {status['total_contributions']}")
    print(f"   Общих якорей: {status['common_anchors_count']}")
    print(f"   Топ якорей: {status['top_anchors']}")

    print("\n✅ КОЛЛЕКТИВНЫЙ САД РАБОТАЕТ")
