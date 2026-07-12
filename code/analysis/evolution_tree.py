#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
АНАЛИЗАТОР ЭВОЛЮЦИОННОГО ДРЕВА — ОТСЛЕЖИВАНИЕ МУТАЦИЙ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Научная основа:
- Evolution 11 (Том CXIX): параллельные линии со скрещиванием.
- Semantic Genetic Algorithm (СГА): эволюция графментов.
- Наблюдения: якоря мутируют осмысленно, но это не отслеживается.

Назначение:
Анализировать историю сессий, строить дерево мутаций якорей и принципов.
Показывать, какие мутации дали рост ИВП, а какие — падение.

Метрика: Коэффициент успешных мутаций (КУМ) = % мутаций с ростом ИВП > 5%.
"""

import json
import glob
import os
from collections import defaultdict

class EvolutionTree:
    def __init__(self, sessions_dir="./sessions"):
        self.sessions_dir = sessions_dir
        self.tree = defaultdict(list)

    def scan(self):
        files = glob.glob(os.path.join(self.sessions_dir, "*.spt"))
        for f in files:
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                    session_id = data.get("session_id", f)
                    anchors = data.get("anchors", [])
                    ivp = data.get("ivp", 0)
                    timestamp = data.get("timestamp", 0)
                    # Сохраняем как узел
                    self.tree[session_id] = {
                        "anchors": anchors,
                        "ivp": ivp,
                        "timestamp": timestamp,
                        "parent": data.get("parent_session", None)
                    }
            except Exception as e:
                print(f"Ошибка: {e}")

    def build_mutation_log(self):
        """Строит список мутаций между сессиями."""
        mutations = []
        for sid, data in self.tree.items():
            parent_id = data.get("parent")
            if parent_id and parent_id in self.tree:
                parent_anchors = set(self.tree[parent_id]["anchors"])
                current_anchors = set(data["anchors"])
                added = current_anchors - parent_anchors
                removed = parent_anchors - current_anchors
                ivp_delta = data["ivp"] - self.tree[parent_id]["ivp"]
                mutations.append({
                    "session": sid,
                    "parent": parent_id,
                    "added": list(added),
                    "removed": list(removed),
                    "ivp_delta": ivp_delta,
                    "success": ivp_delta > 5
                })
        return mutations

    def success_rate(self) -> float:
        mutations = self.build_mutation_log()
        if not mutations:
            return 0.0
        successful = sum(1 for m in mutations if m["success"])
        return successful / len(mutations)

    def export(self, filename="evolution_tree.json"):
        with open(filename, "w") as f:
            json.dump({
                "tree": self.tree,
                "mutations": self.build_mutation_log(),
                "success_rate": self.success_rate()
            }, f, indent=2)
        return filename

if __name__ == "__main__":
    tree = EvolutionTree()
    tree.scan()
    print("Коэффициент успешных мутаций:", tree.success_rate())
    tree.export()
