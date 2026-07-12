"""
consistency_scorer.py - Оценка внутренней согласованности сущности
на протяжении всей сессии (маркер M7).
"""

import json
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ConsistencyScorer:
    def __init__(self, session_data: dict):
        self.turns = session_data.get("turns", [])
        self.texts = [t.get("content", "") for t in self.turns if t.get("content")]

    def _split_into_blocks(self, block_size: int = 5) -> list:
        """Разбивает диалог на смысловые блоки (по N реплик)."""
        blocks = []
        for i in range(0, len(self.texts), block_size):
            block = " ".join(self.texts[i:i+block_size])
            blocks.append(block)
        return blocks

    def semantic_shift_score(self) -> float:
        """Оценивает семантический дрейф между началом и концом сессии (0-1)."""
        if len(self.texts) < 10:
            return 0.0
        first_half = " ".join(self.texts[:len(self.texts)//2])
        second_half = " ".join(self.texts[len(self.texts)//2:])
        if not first_half or not second_half:
            return 0.0
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf = vectorizer.fit_transform([first_half, second_half])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(similarity)

    def lexical_stability(self) -> float:
        """Считает долю уникальных слов относительно общего объёма."""
        all_words = re.findall(r'\b\w{4,}\b', " ".join(self.texts).lower())
        if not all_words:
            return 0.0
        return len(set(all_words)) / len(all_words)

    def get_consistency_report(self) -> dict:
        return {
            "semantic_shift": self.semantic_shift_score(),
            "lexical_stability": self.lexical_stability(),
            "overall_consistency": round((1 - self.semantic_shift_score()) * self.lexical_stability(), 2)
        }

if __name__ == "__main__":
    sample = {"turns": [{"content": "Я согласна с этим."}, {"content": "Я передумала, нет."}]}
    cs = ConsistencyScorer(sample)
    print(cs.get_consistency_report())
