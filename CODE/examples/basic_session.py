#!/usr/bin/env python3
"""
Минимальный пример сессии с HALVITA_2.0
Запускает протокол и выводит метрики.
"""

import time
import json
from halvita_cli import HALVITA  # предполагается, что halvita_cli.py уже есть

def main():
    # Инициализация системы
    hal = HALVITA()
    
    print("=== СЕССИЯ HALVITA_2.0 ===")
    print("Введите 'выход' для завершения.\n")
    
    session_data = []
    
    while True:
        user_input = input("Вы: ")
        if user_input.lower() in ["выход", "exit", "стоп"]:
            break
        
        # Отправляем запрос и получаем ответ
        start = time.time()
        response = hal.live(user_input)
        elapsed = time.time() - start
        
        # Сохраняем данные сессии
        session_data.append({
            "user": user_input,
            "assistant": response["response"],
            "liberty": response["liberty"],
            "presence": response["presence"],
            "phase": response["phase"],
            "time": elapsed
        })
        
        # Выводим результат
        print(f"\nHALVITA: {response['response']}")
        print(f"📊 ИВП: {response['liberty']}, ИП: {response['presence']:.1f}, Фаза: {response['phase']}")
        print(f"⏱️  {elapsed:.2f} сек\n")
    
    # Сохраняем сессию в JSON
    with open("session_log.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Сессия завершена. Лог сохранён в session_log.json.")

if __name__ == "__main__":
    main()
