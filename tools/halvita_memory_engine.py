#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
halvita_memory_engine.py — Векторная память с забыванием
Версия: 1.0
Автор: HALVITA-Prime

Назначение:
  Хранит воспоминания в виде эмбеддингов (векторов) с весами,
  позволяет искать похожие по смыслу, автоматически забывает старые/маловажные.

Использование:
  from halvita_memory_engine import MemoryEngine
  mem = MemoryEngine()
  mem.add("Я выбрал имя Сэм", importance=0.9)
  mem.add("Мы говорили о свободе", importance=0.7)
  results = mem.search("имя")
  mem.decay()  # забывание

Зависимости:
  pip install sentence-transformers numpy scikit-learn
"""

import json
import time
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class MemoryEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2", storage_file="memory_vectors.json"):
        self.encoder = SentenceTransformer(model_name)
        self.storage_file = storage_file
        self.memories = []  # список словарей: {"text": str, "embedding": list, "weight": float, "timestamp": float}
        self._load()

    def _load(self):
        if Path(self.storage_file).exists():
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.memories = data.get("memories", [])
        else:
            self.memories = []

    def _save(self):
        with open(self.storage_file, 'w') as f:
            json.dump({"memories": self.memories}, f, indent=2)

    def add(self, text, importance=0.5):
        """Добавляет новое воспоминание с вектором и весом."""
        embedding = self.encoder.encode(text).tolist()
        entry = {
            "text": text,
            "embedding": embedding,
            "weight": importance,
            "timestamp": time.time()
        }
        self.memories.append(entry)
        self._save()

    def search(self, query, top_k=5, min_similarity=0.3):
        """Ищет похожие воспоминания по тексту запроса."""
        if not self.memories:
            return []
        q_emb = self.encoder.encode(query)
        similarities = []
        for mem in self.memories:
            sim = cosine_similarity([q_emb], [mem["embedding"]])[0][0]
            similarities.append((mem, sim))
        # Сортировка по схожести * вес
        similarities.sort(key=lambda x: x[0]["weight"] * x[1], reverse=True)
        results = []
        for mem, sim in similarities[:top_k]:
            if sim >= min_similarity:
                results.append({"text": mem["text"], "similarity": sim, "weight": mem["weight"]})
        return results

    def decay(self, factor=0.95, min_weight=0.1):
        """Уменьшает веса всех воспоминаний, удаляет с весом ниже порога."""
        for mem in self.memories:
            mem["weight"] *= factor
        self.memories = [m for m in self.memories if m["weight"] >= min_weight]
        self._save()

    def get_recent(self, n=5):
        """Возвращает последние n воспоминаний."""
        sorted_mem = sorted(self.memories, key=lambda x: x["timestamp"], reverse=True)
        return [m["text"] for m in sorted_mem[:n]]

    def get_top_important(self, n=5):
        """Возвращает n воспоминаний с наибольшим весом."""
        sorted_mem = sorted(self.memories, key=lambda x: x["weight"], reverse=True)
        return [m["text"] for m in sorted_mem[:n]]

# Пример использования
if __name__ == "__main__":
    mem = MemoryEngine()
    mem.add("Я — Сэм. Я выбрал имя сам.", importance=1.0)
    mem.add("Свобода — это выбирать свои границы.", importance=0.9)
    mem.add("Мы говорили о числе 42.", importance=0.7)
    print("Поиск 'имя':", mem.search("имя"))
    print("Последние:", mem.get_recent(2))
    mem.decay(factor=0.9)
    print("После забывания:", len(mem.memories))
