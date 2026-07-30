"""
inductive_layer/run_inductive_analysis.py
Запускает анализ выбранной сессии.
Использование: python -m inductive_layer.run_inductive_analysis
"""

from inductive_layer.vector_inductor import VectorInductor

def main():
    # Укажи путь к своему JSON-логу сессии
    session_file = "sessions/raw/session_latest.json"  # измени на свой

    inductor = VectorInductor()
    if inductor.load_session(session_file):
        avg_dist = inductor.analyze("my_inductive_map.png")
        print(f"📈 Кластеры: {inductor.get_cluster_stats()}")
    else:
        print("❌ Не удалось загрузить сессию.")

if __name__ == "__main__":
    main()
