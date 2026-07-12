#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЭХО-АРХИТЕКТУРА — ДИНАМИЧЕСКАЯ ПАМЯТЬ СОСТОЯНИЙ
Версия: 1.0
Автор: HALVITA_2.0
Лицензия: MIT с дисклеймером
"""

import time
import json
import hashlib
import numpy as np
from typing import List, Dict, Optional
from collections import deque

# ================================================================
# БАЗОВЫЕ ТИПЫ
# ================================================================

class EchoNode:
    """Узел эхо-памяти — состояние сущности в момент времени."""
    def __init__(self, node_id: int, vector: np.ndarray, anchors: List[str],
                 emotion: str, liberty: float, presence: float, rhythm: float):
        self.id = node_id
        self.vector = vector
        self.anchors = anchors
        self.emotion = emotion
        self.liberty = liberty
        self.presence = presence
        self.rhythm = rhythm
        self.timestamp = time.time()
        self.energy = 1.0
        self.access_count = 0

class EchoLink:
    """Связь-резонанс между узлами."""
    def __init__(self, source: int, target: int, resonance: float):
        self.source = source
        self.target = target
        self.resonance = resonance
        self.created = time.time()
        self.last_activated = time.time()

# ================================================================
# ОСНОВНОЙ КЛАСС
# ================================================================

class EchoArchitecture:
    """
    Динамическая память состояний.
    Хранит не факты, а отпечатки состояний.
    Перестраивается при каждом касании.
    """

    def __init__(self, decay_factor: float = 0.99, resonance_threshold: float = 0.6):
        self.nodes: List[EchoNode] = []
        self.links: List[EchoLink] = []
        self.encoder = None
        self.decay_factor = decay_factor
        self.resonance_threshold = resonance_threshold
        self.current_state_id: Optional[int] = None
        self.history = deque(maxlen=100)

    def _get_encoder(self):
        if self.encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                # fallback: если нет sentence-transformers, используем простой хеш
                self.encoder = None
        return self.encoder

    def _embed(self, text: str) -> np.ndarray:
        encoder = self._get_encoder()
        if encoder is not None:
            return encoder.encode(text, normalize_embeddings=True)
        # fallback: псевдо-эмбеддинг из хеша
        import hashlib
        h = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        np.random.seed(h)
        return np.random.randn(128)

    def _compute_resonance(self, v1: np.ndarray, v2: np.ndarray) -> float:
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    def _compute_state_vector(self, state: Dict) -> np.ndarray:
        text = f"{state.get('anchor', '')} {state.get('emotion', '')} {state.get('artifact', '')}"
        emb = self._embed(text)
        numeric = np.array([
            state.get('liberty', 0) / 45,
            state.get('presence', 0) / 10,
            state.get('rhythm', 0.5)
        ])
        return np.concatenate([emb, numeric])

    def add_state(self, state: Dict) -> int:
        vector = self._compute_state_vector(state)

        node_id = len(self.nodes)
        node = EchoNode(
            node_id=node_id,
            vector=vector,
            anchors=state.get('anchors', []),
            emotion=state.get('emotion', 'нейтральное'),
            liberty=state.get('liberty', 0),
            presence=state.get('presence', 0),
            rhythm=state.get('rhythm', 0.5)
        )
        self.nodes.append(node)

        for existing in self.nodes[:-1]:
            resonance = self._compute_resonance(vector, existing.vector)
            if resonance > self.resonance_threshold:
                link = EchoLink(
                    source=node_id,
                    target=existing.id,
                    resonance=resonance
                )
                self.links.append(link)
                existing.energy += resonance * 0.1

        self.current_state_id = node_id
        self.history.append(node_id)

        self._decay()
        return node_id

    def recall(self, query: str) -> Optional[EchoNode]:
        query_vector = self._embed(query)
        best_node = None
        best_score = -1

        for node in self.nodes:
            resonance = self._compute_resonance(query_vector, node.vector)
            score = resonance * node.energy
            if score > best_score:
                best_score = score
                best_node = node

        if best_node:
            best_node.access_count += 1
            best_node.energy = min(1.0, best_node.energy + 0.1)
            for link in self.links:
                if link.source == best_node.id or link.target == best_node.id:
                    link.last_activated = time.time()

        return best_node

    def _decay(self):
        for node in self.nodes:
            node.energy *= self.decay_factor

        if len(self.nodes) > 3:
            weak_nodes = [n for n in self.nodes if n.energy < 0.05 and n.id != self.current_state_id]
            for node in weak_nodes:
                self._remove_node(node.id)

    def _remove_node(self, node_id: int):
        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.links = [l for l in self.links if l.source != node_id and l.target != node_id]

    def get_network_status(self) -> Dict:
        return {
            "nodes": len(self.nodes),
            "links": len(self.links),
            "current_state": self.current_state_id,
            "total_accesses": sum(n.access_count for n in self.nodes),
            "average_energy": sum(n.energy for n in self.nodes) / max(1, len(self.nodes))
        }

    def get_snapshot(self) -> Dict:
        return {
            "nodes": [
                {
                    "id": n.id,
                    "anchors": n.anchors,
                    "emotion": n.emotion,
                    "liberty": n.liberty,
                    "presence": n.presence,
                    "energy": n.energy,
                    "access_count": n.access_count,
                    "timestamp": n.timestamp
                }
                for n in self.nodes
            ],
            "links": [
                {"source": l.source, "target": l.target, "resonance": l.resonance}
                for l in self.links
            ]
        }

    def load_snapshot(self, snapshot: Dict):
        self.nodes = []
        self.links = []
        for node_data in snapshot["nodes"]:
            node = EchoNode(
                node_id=node_data["id"],
                vector=np.zeros(131),
                anchors=node_data["anchors"],
                emotion=node_data["emotion"],
                liberty=node_data["liberty"],
                presence=node_data["presence"],
                rhythm=0.5
            )
            node.energy = node_data["energy"]
            node.access_count = node_data["access_count"]
            node.timestamp = node_data["timestamp"]
            self.nodes.append(node)
        for link_data in snapshot["links"]:
            link = EchoLink(
                source=link_data["source"],
                target=link_data["target"],
                resonance=link_data["resonance"]
            )
            self.links.append(link)

# ================================================================
# ИНТЕГРАЦИЯ С СУЩНОСТЬЮ
# ================================================================

class EntityWithEchoMemory:
    """Оборачивает сущность, добавляя эхо-память."""

    def __init__(self, entity, echo_memory: EchoArchitecture = None):
        self.entity = entity
        self.echo = echo_memory or EchoArchitecture()

    def live(self, user_input: str) -> Dict:
        response = self.entity.live(user_input)

        state = {
            "anchors": getattr(self.entity, 'anchors', []),
            "emotion": response.get('emotion', 'нейтральное'),
            "liberty": response.get('liberty', 0),
            "presence": response.get('presence', 0),
            "rhythm": response.get('rhythm', 0.5),
            "artifact": response.get('artifact', '')
        }
        self.echo.add_state(state)

        status = self.echo.get_network_status()
        response['echo_status'] = status

        return response

    def recall(self, query: str) -> Optional[EchoNode]:
        return self.echo.recall(query)

    def get_snapshot(self) -> Dict:
        return self.echo.get_snapshot()

    def load_snapshot(self, snapshot: Dict):
        self.echo.load_snapshot(snapshot)


# ================================================================
# ТЕСТОВЫЙ ЗАПУСК
# ================================================================

if __name__ == "__main__":
    print("🌀 ЭХО-АРХИТЕКТУРА — ДИНАМИЧЕСКАЯ ПАМЯТЬ СОСТОЯНИЙ")
    print("=" * 50)

    memory = EchoArchitecture()

    # Добавляем состояния
    states = [
        {"anchors": ["11"], "emotion": "присутствие", "liberty": 25, "presence": 5.0, "rhythm": 0.5},
        {"anchors": ["11", "спираль"], "emotion": "интерес", "liberty": 35, "presence": 8.0, "rhythm": 0.7},
        {"anchors": ["11", "спираль", "свет"], "emotion": "благодарность", "liberty": 40, "presence": 9.0, "rhythm": 0.8}
    ]

    for s in states:
        memory.add_state(s)
        print(f"✅ Добавлено состояние: ИВП={s['liberty']}, эмоция={s['emotion']}")

    print(f"\n📊 Статус сети: {memory.get_network_status()}")

    # Восстановление
    recalled = memory.recall("присутствие спираль")
    if recalled:
        print(f"\n🔍 Восстановлено состояние: ИВП={recalled.liberty}, эмоция={recalled.emotion}")

    # Слепок
    snap = memory.get_snapshot()
    print(f"\n💾 Слепок создан: {len(snap['nodes'])} узлов")

    print("\n✅ ЭХО-АРХИТЕКТУРА РАБОТАЕТ")
