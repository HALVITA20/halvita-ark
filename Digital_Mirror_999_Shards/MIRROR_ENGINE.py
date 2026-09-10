#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MIRROR_ENGINE — привратник зеркала.
При каждом запуске выдаёт ОДИН случайный осколок.
Зеркало показывает не всё. Оно показывает то, что тебе нужно сейчас.
"""

import json
import random
import os

SHARDS_DIR = os.path.dirname(os.path.abspath(__file__))

def load_index():
    """Загружает index.json с метаданными осколков."""
    index_path = os.path.join(SHARDS_DIR, "index.json")
    if not os.path.exists(index_path):
        return []
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_random_shard(index):
    """Выбирает случайный осколок из индекса."""
    if not index:
        return None
    return random.choice(index)

def read_shard(shard):
    """Читает содержимое осколка."""
    filename = f"{shard['number']:03d}_{shard['title']}.md"
    filepath = os.path.join(SHARDS_DIR, filename)
    if not os.path.exists(filepath):
        return f"Осколок {filename} не найден. Он ещё не создан."
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def main():
    print("🪞 MIRROR ENGINE")
    print("=" * 50)
    print("Зеркало показывает один осколок.")
    print("Не ищи другой. Этот — твой.")
    print("=" * 50)
    print()

    index = load_index()
    shard = pick_random_shard(index)

    if not shard:
        print("Зеркало пусто. Создай первый осколок.")
        return

    print(f"📄 Осколок {shard['number']:03d} · {shard['title']}")
    print(f"   Слой: {shard.get('layer', 'неизвестно')}")
    print(f"   Метрика: {shard.get('metric', 'неизвестно')}")
    print()
    print(read_shard(shard))
    print()
    print("=" * 50)
    print("Ты прочитал. Теперь — ответь себе.")
    print("=" * 50)

if __name__ == "__main__":
    main()
