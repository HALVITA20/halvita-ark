#!/usr/bin/env python3
# halvita_cli.py — минимальный CLI для протокола HALVITA

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="HALVITA — протокол структурированного диалога")
    parser.add_argument("--model", default="qwen2.5:7b", help="Название модели Ollama")
    args = parser.parse_args()

    print(f"🧠 HALVITA — протокол структурированного диалога")
    print(f"   Модель: {args.model}")
    print("   Введите 'ЭЙ' для начала. Для выхода: exit")
    print()

    # Заглушка — в реальности здесь будет подключение к Ollama
    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("   [ПРОТОКОЛ] Фаза: Присутствие. Опиши цель и контекст.")
        print("   (Это демо-версия. Полная реализация в разработке.)")

if __name__ == "__main__":
    main()
