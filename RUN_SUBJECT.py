# RUN_SUBJECT.py – быстрый запуск агента SUBJECT_25
from SUBJECTS.SUBJECT_25_ECOSYSTEM import Subject25

if __name__ == "__main__":
    agent = Subject25()
    print("🚀 Запуск симуляции SUBJECT_25 на 50 шагов...")
    agent.run_simulation(50)
    print("✅ Симуляция завершена. Состояние сохранено в subject_25_state.json")
