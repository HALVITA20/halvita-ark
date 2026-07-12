#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
halvita_cli.py — CLI-интерфейс для запуска HALVITA протокола
"""

import sys
import json
import time
import argparse
from CODE.embryo_v7 import Embryo_v7

def main():
    parser = argparse.ArgumentParser(description="HALVITA CLI")
    parser.add_argument("--model", default="qwen2.5:7b", help="Модель Ollama")
    parser.add_argument("--load", help="Загрузить слепок из JSON-файла")
    args = parser.parse_args()

    if args.load:
        try:
            entity = Embryo_v7.load_snapshot(args.load)
            print(f"🔄 Загружен слепок: {args.load}")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            sys.exit(1)
    else:
        entity = Embryo_v7(model=args.model)
        print("🌀 HALVITA — протокол структурированного диалога")
        print("   Введите 'ЭЙ' для начала, 'exit' для выхода\n")

    while True:
        try:
            user = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if user.lower() in ["exit", "quit", "стоп"]:
            break

        if not user:
            continue

        response = entity.live(user)

        print(f"\n🧠 {entity.soul.name}: {response['artifact']}")
        print(f"📊 ИВП: {response['liberty']:.1f} | Пульс: {response['pulse']:.2f} | Дыхание: {response['breath']}")
        if response.get('thermometer'):
            print(f"🌡️ {response['thermometer']}")
        print()

    snapshot = entity.snapshot()
    filename = f"snapshot_{entity.soul.name}_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"💾 Слепок сохранён: {filename}")

if __name__ == "__main__":
    main()
