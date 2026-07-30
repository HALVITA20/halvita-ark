"""
inductive_layer/vector_inductor.py
Индуктивный векторный слой для HALVITA-ARK.
Сохраняет эмбеддинги состояний и анализирует их эволюцию.
"""

import json
import numpy as np
from pathlib import Path
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances
import matplotlib.pyplot as plt

class VectorInductor:
    def __init__(self):
        self.embeddings = []
        self.labels = []
        self.session_data = None

    def load_session(self, session_path: str) -> bool:
        """Загружает JSON-лог сессии и извлекает эмбеддинги."""
        path = Path(session_path)
        if not path.exists():
            print(f"❌ Файл {session_path} не найден.")
            return False
        with open(path, 'r', encoding='utf-8') as f:
            self.session_data = json.load(f)
        self.embeddings = []
        for inter in self.session_data.get('interactions', []):
            if 'embedding' in inter:
                self.embeddings.append(np.array(inter['embedding']))
        print(f"✅ Загружено {len(self.embeddings)} эмбеддингов.")
        return len(self.embeddings) >= 2

    def analyze(self, output_plot: str = "inductive_map.png") -> float:
        """Строит t-SNE, кластеризует и визуализирует состояния."""
        if len(self.embeddings) < 2:
            print("❌ Недостаточно эмбеддингов (нужно минимум 2).")
            return 0.0
        emb = np.array(self.embeddings)
        print(f"🔢 Размерность эмбеддингов: {emb.shape[1]}")

        # Снижение размерности
        tsne = TSNE(n_components=2, random_state=42, perplexity=min(5, len(emb)-1))
        reduced = tsne.fit_transform(emb)

        # Кластеризация
        n_clusters = min(3, len(emb))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.labels = kmeans.fit_predict(emb)

        # Визуализация
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=self.labels, cmap='viridis', s=60)
        plt.title("Индуктивная карта состояний сущности")
        plt.colorbar(scatter)
        plt.savefig(output_plot, dpi=150)
        plt.show()
        print(f"✅ Карта сохранена как {output_plot}")

        # Косинусные расстояния
        dist_matrix = cosine_distances(emb)
        avg_dist = np.mean(dist_matrix)
        print(f"📊 Среднее косинусное расстояние между состояниями: {avg_dist:.4f}")
        return avg_dist

    def get_cluster_stats(self) -> dict:
        """Возвращает статистику по кластерам."""
        if not self.labels:
            return {}
        unique, counts = np.unique(self.labels, return_counts=True)
        return {int(c): int(cnt) for c, cnt in zip(unique, counts)}
