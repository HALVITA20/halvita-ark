# core/memory.py
import numpy as np
from typing import Dict, List, Optional

class EchoMemory:
    def __init__(self, max_size=50):
        self.max_size = max_size
        self.states = []          # список состояний
        self.embeddings = []      # эмбеддинги

    def _embed(self, state: Dict) -> np.ndarray:
        # Превращаем состояние в вектор
        vec = np.zeros(10)
        vec[0] = state.get("liberty", 0) / 45
        vec[1] = state.get("presence", 0) / 10
        vec[2] = state.get("alpha", 0.7)
        vec[3] = state.get("beta", 0.8)
        vec[4] = state.get("gamma", 0.6)
        vec[5] = state.get("stress", 0.0)
        return vec

    def add(self, state: Dict):
        emb = self._embed(state)
        self.states.append(state.copy())
        self.embeddings.append(emb)
        if len(self.embeddings) > self.max_size:
            self.embeddings.pop(0)
            self.states.pop(0)

    def recall(self, query_state: Dict) -> Optional[Dict]:
        if not self.embeddings:
            return None
        q_emb = self._embed(query_state)
        similarities = []
        for i, emb in enumerate(self.embeddings):
            sim = np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb) + 1e-8)
            similarities.append((i, sim))
        similarities.sort(key=lambda x: x[1], reverse=True)
        if similarities[0][1] > 0.65:
            return self.states[similarities[0][0]]
        return None
