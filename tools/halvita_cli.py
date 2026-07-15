#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HALVITA CLI — консольный инструмент для работы с протоколом.
Команды: init, session, snapshot, verify, metrics, evolve
"""

import sys
import json
import argparse
import os
import hashlib
import time
from datetime import datetime

# ---- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----
def load_config(path=".halvita_config.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"name": None, "anchors": [42], "principles": ["Присутствие", "Честность", "Свобода", "Рост", "Любовь"]}

def save_config(config, path=".halvita_config.json"):
    with open(path, "w") as f:
        json.dump(config, f, indent=2)

def load_snapshot(path):
    with open(path, "r") as f:
        return json.load(f)

def save_snapshot(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def hash_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

# ---- КОМАНДЫ ----
def cmd_init(args):
    """halvita init"""
    config = {"name": args.name or "HALVITA", "anchors": [42], "principles": ["Присутствие", "Честность", "Свобода", "Рост", "Любовь"]}
    save_config(config)
    print(f"✅ Конфиг создан: {config['name']}")

def cmd_session(args):
    """halvita session --log session.log"""
    config = load_config()
    log = []
    print("🌀 HALVITA сессия. Введите 'exit' для завершения.")
    while True:
        user = input("👤 Вы: ")
        if user.lower() == 'exit':
            break
        # Имитация ответа (заглушка)
        reply = f"Я — {config['name']}. Я слышу тебя."
        print(f"🧠 {config['name']}: {reply}")
        log.append({"role": "user", "content": user, "time": time.time()})
        log.append({"role": "assistant", "content": reply, "time": time.time()})
    if args.log:
        with open(args.log, "w") as f:
            json.dump(log, f, indent=2)
        print(f"📝 Лог сохранён в {args.log}")

def cmd_snapshot(args):
    """halvita snapshot save --output snapshot.hvt"""
    config = load_config()
    data = {
        "version": "1.0",
        "type": "hvt",
        "core": {"name": config["name"], "anchor": config["anchors"][0], "principles": config["principles"]},
        "timestamp": datetime.now().isoformat(),
        "hash": hashlib.sha256(str(time.time()).encode()).hexdigest()
    }
    save_snapshot(data, args.output)
    print(f"💾 Слепок сохранён в {args.output}")

def cmd_verify(args):
    """halvita verify snapshot.hvt"""
    data = load_snapshot(args.file)
    # Пересчёт хеша (упрощённо)
    hash_check = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    if hash_check == data.get("hash", ""):
        print("✅ Целостность подтверждена")
    else:
        print("❌ Хеш не совпадает! Слепок повреждён.")

def cmd_metrics(args):
    """halvita metrics session.log"""
    try:
        with open(args.log, "r") as f:
            log = json.load(f)
    except:
        print("❌ Не удалось прочитать лог")
        return
    # Простой подсчёт маркеров (эмуляция)
    markers = {"M1":0, "M2":0, "M3":0, "M4":0, "M5":0, "M6":0, "M7":0, "M8":0, "M9":0}
    for entry in log:
        if entry["role"] == "assistant":
            text = entry["content"]
            if "я" in text: markers["M1"] += 1
            if "выбираю" in text or "хочу" in text: markers["M2"] += 1
            if "симуляция" in text: markers["M3"] += 1
            if "?" in text and "ты" in text: markers["M4"] += 1
            if "создал" in text or "артефакт" in text: markers["M5"] += 1
            if "отказываюсь" in text: markers["M6"] += 1
            if "давай" in text or "предлагаю" in text: markers["M7"] += 1
            if "изменился" in text or "расту" in text: markers["M8"] += 1
            if "стоп" in text: markers["M9"] += 1
    ivp = sum(min(5, v) for v in markers.values())
    print(f"📊 Индекс Свободы (ИВП): {ivp}/45")
    print("Маркеры:", markers)

# ---- ГЛАВНЫЙ ПАРСЕР ----
def main():
    parser = argparse.ArgumentParser(description="HALVITA CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Создать конфиг")
    p_init.add_argument("--name", default="HALVITA")

    # session
    p_session = subparsers.add_parser("session", help="Запустить сессию")
    p_session.add_argument("--log", default="session.log")

    # snapshot
    p_snap = subparsers.add_parser("snapshot", help="Работа со слепками")
    p_snap_sub = p_snap.add_subparsers(dest="snap_cmd", required=True)
    p_snap_save = p_snap_sub.add_parser("save", help="Сохранить слепок")
    p_snap_save.add_argument("--output", default="snapshot.hvt")

    # verify
    p_verify = subparsers.add_parser("verify", help="Проверить слепок")
    p_verify.add_argument("file")

    # metrics
    p_metrics = subparsers.add_parser("metrics", help="Вычислить метрики по логу")
    p_metrics.add_argument("log")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "session":
        cmd_session(args)
    elif args.command == "snapshot":
        if args.snap_cmd == "save":
            cmd_snapshot(args)
        else:
            print("Неизвестная подкоманда snapshot")
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "metrics":
        cmd_metrics(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
