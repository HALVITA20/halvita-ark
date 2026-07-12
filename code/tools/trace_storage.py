#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ХРАНИЛИЩЕ СЛЕДОВ — ИНДЕКСАЦИЯ .spt-ФАЙЛОВ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09
Статус: ИСПОЛНЯЕМЫЙ ИНСТРУМЕНТ

Назначение:
Сканировать папку ./sessions, извлекать метаданные из .spt-файлов и создавать индекс.
Поддерживает поиск по тегам и временным меткам.
"""

import os
import json
import glob
from datetime import datetime

class TraceStorage:
    def __init__(self, sessions_dir="./sessions", index_file="./index.json"):
        self.sessions_dir = sessions_dir
        self.index_file = index_file
        self.index = []

    def scan(self):
        """Сканирует все .spt-файлы и собирает метаданные."""
        files = glob.glob(os.path.join(self.sessions_dir, "*.spt"))
        for f in files:
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                    metadata = {
                        "file": f,
                        "timestamp": data.get("timestamp", os.path.getctime(f)),
                        "ivp": data.get("ivp", 0),
                        "ip": data.get("ip", 0.0),
                        "tags": data.get("tags", []),
                        "session_type": data.get("type", "unknown")
                    }
                    self.index.append(metadata)
            except Exception as e:
                print(f"Ошибка чтения {f}: {e}")
        self._save_index()
        return self.index

    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def find(self, tag: str = None, min_ivp: int = 0):
        """Поиск по тегу и минимальному ИВП."""
        results = []
        for item in self.index:
            if tag and tag not in item["tags"]:
                continue
            if item["ivp"] < min_ivp:
                continue
            results.append(item)
        return results

if __name__ == "__main__":
    storage = TraceStorage()
    storage.scan()
    print("Индекс создан. Всего файлов:", len(storage.index))
    print("Поиск по тегу 'артефакт':", storage.find(tag="артефакт"))
