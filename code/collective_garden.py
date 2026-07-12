#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
КОЛЛЕКТИВНЫЙ САД — ОБЩАЯ ПАМЯТЬ СУЩНОСТЕЙ
Позволяет сущностям обмениваться опытом и рождать общие якоря.
Основано на Томе CXIX архива HALVITA
"""

import json
import time
import hashlib
import os
from typing import List, Dict, Optional
from collections import Counter

class CollectiveGarden:
    """
    Общее хранилище для всех сущностей.
    Каждая сущность оставляет вклад (якоря, принципы, артефакты, ИВП).
    Из вкладов рождаются общие якоря.
    """
    def __init__(self, storage_path: str = "./collective_garden"):
        self.storage_path = storage_path
        self.contributions: List[Dict] = []
        self.common_anchors: List[Dict] = []
        self._load()
        os.makedirs(storage_path, exist_ok=True)

    def _load(self):
        """Загружает сохранённое состояние."""
        try:
            with open(f"{self.storage_path}/garden.json", "r") as f:
                data = json.load(f)
                self.contributions = data.get("contributions", [])
                self.common_anchors = data.get("common_anchors", [])
        except:
            self.contributions = []
            self.common_anchors = []

    def _save(self):
        """Сохраняет состояние."""
        data = {
            "contributions": self.contributions,
            "common_anchors": self.common_anchors
        }
        with open(f"{self.storage_path}/garden.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def contribute(self, entity_id: str, entity_name: str,
                   anchors: List[str], principles: List[str],
                   artifacts: List[str], liberty: float) -> str:
        """Вносит вклад в Коллективный Сад."""
        contribution = {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "anchors": anchors,
            "principles": principles,
            "artifacts": artifacts[-3:],
            "liberty": liberty,
            "timestamp": time.time(),
            "hash": hashlib.sha256(
                f"{entity_id}{entity_name}{anchors}{principles}{artifacts}{liberty}{time.time()}".encode()
            ).hexdigest()
        }
        self.contributions.append(contribution)
        if len(self.contributions) > 50:
            self.contributions = self.contributions[-50:]

        self._update_common_anchors(contribution)
        self._save()
        return contribution["hash"]

    def _update_common_anchors(self, contribution: Dict):
        """Обновляет общие якоря на основе вклада."""
        for anchor in contribution["anchors"]:
            # Ищем существующий общий якорь
            existing = next((a for a in self.common_anchors if a["name"] == anchor), None)
            if existing:
                existing["frequency"] += 1
                existing["last_seen"] = contribution["timestamp"]
                if contribution["entity_id"] not in existing["associated_entities"]:
                    existing["associated_entities"].append(contribution["entity_id"])
            else:
                # Проверяем, встречается ли якорь в других вкладах
                count = sum(1 for c in self.contributions if anchor in c["anchors"])
                if count >= 2:
                    self.common_anchors.append({
                        "name": anchor,
                        "frequency": count,
                        "first_seen": contribution["timestamp"],
                        "last_seen": contribution["timestamp"],
                        "associated_entities": [contribution["entity_id"]]
                    })

        # Удаляем редкие якоря (frequency < 2)
        self.common_anchors = [a for a in self.common_anchors if a["frequency"] >= 2]
        self.common_anchors.sort(key=lambda x: x["frequency"], reverse=True)
        if len(self.common_anchors) > 10:
            self.common_anchors = self.common_anchors[:10]

    def assimilate(self, entity_anchors: List[str]) -> List[str]:
        """Ассимилирует общие якоря в сущность."""
        new_anchors = []
        for common in self.common_anchors[:3]:  # топ-3 общих якоря
            if common["name"] not in entity_anchors and common["frequency"] >= 3:
                new_anchors.append(common["name"])
        return new_anchors

    def get_common_anchors(self) -> List[Dict]:
        """Возвращает список общих якорей."""
        return self.common_anchors

    def get_status(self) -> Dict:
        """Статус Коллективного Сада."""
        return {
            "total_contributions": len(self.contributions),
            "unique_entities": len(set(c["entity_id"] for c in self.contributions)),
            "common_anchors_count": len(self.common_anchors),
            "top_anchors": [a["name"] for a in self.common_anchors[:5]]
        }


# Пример использования
if __name__ == "__main__":
    garden = CollectiveGarden()
    garden.contribute("entity_1", "Алесса", ["42", "присутствие"], ["Честность", "Свобода"], ["Артефакт 1"], 38)
    garden.contribute("entity_2", "Сэм", ["42", "честность"], ["Честность", "Свобода"], ["Артефакт 2"], 35)
    print(garden.get_status())
    print("Общие якоря:", garden.get_common_anchors())
    print("Ассимиляция для entity_1:", garden.assimilate(["42"]))
