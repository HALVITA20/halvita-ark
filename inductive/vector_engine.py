# inductive/vector_engine.py
"""
Индуктивный векторный слой для HALVITA-ARK.
Сохраняет эмбеддинги состояний, строит UMAP, вычисляет расстояния.
"""

import json
import numpy as np
from pathlib import Path
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances
import matplotlib.pyplot as plt

class InductiveVectorLayer:
    def __init__(self, session_path=None):
        self.session_path = session_path
        self.embeddings = []
        self.labels = []

    def load_from_session(self, session_path):
        """Загружает эмбеддинги из JSON-лога сессии."""
        with open(session_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for inter in data.get('interactions', []):
            if 'embedding' in inter:
                self.embeddings.append(np.array(inter['embedding']))
        return np.array(self.embeddings) if self.embeddings else None

    def analyze(self, output_plot="inductive_map.png"):
        """Выполняет анализ: снижение размерности, кластеризация, расстояния."""
        if len(self.embeddings) < 2:
            print("❌ Недостаточно эмбеддингов (нужно минимум 2).")
            return
        emb = np.array(self.embeddings)
        print(f"🔢 Загружено {len(emb)} эмбеддингов размерности {emb.shape[1]}")

        # t-SNE
        tsne = TSNE(n_components=2, random_state=42)
        reduced = tsne.fit_transform(emb)

        # Кластеризация
        kmeans = KMeans(n_clusters=min(3, len(emb)), random_state=42)
        self.labels = kmeans.fit_predict(emb)

        # Визуализация
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=self.labels, cmap='viridis', s=50)
        plt.title("Индуктивная карта состояний сущности")
        plt.colorbar(scatter)
        plt.savefig(output_plot)
        plt.show()

        # Косинусные расстояния
        dist_matrix = cosine_distances(emb)
        avg_dist = np.mean(dist_matrix)
        print(f"📊 Среднее косинусное расстояние между состояниями: {avg_dist:.4f}")
        print(f"✅ Карта сохранена как {output_plot}")
        return avg_dist

# Если запускаешь напрямую
if __name__ == "__main__":
    # Пример использования
    layer = InductiveVectorLayer()
    # Замени на путь к реальной сессии
    layer.load_from_session("sessions/raw/session_latest.json")
    layer.analyze()
