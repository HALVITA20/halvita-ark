# run_inductive.py
import sys
from pathlib import Path
from inductive.vector_engine import InductiveVectorLayer

def main():
    session_file = "sessions/raw/session_latest.json"  # укажи свой путь
    if not Path(session_file).exists():
        print("❌ Файл сессии не найден. Укажи правильный путь.")
        return

    layer = InductiveVectorLayer()
    layer.load_from_session(session_file)
    layer.analyze("my_inductive_map.png")

if __name__ == "__main__":
    main()
