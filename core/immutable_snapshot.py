#!/usr/bin/env python3
"""
IMMUTABLE SNAPSHOT — Криптографическая защита слепков.
Запуск: python core/immutable_snapshot.py --save или --verify
Автор: HALVITA
"""

import json
import hashlib
import uuid
import time
import argparse
from datetime import datetime
from typing import Dict, Optional

class ImmutableSnapshot:
    def __init__(self, name: str = "Неизвестная"):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.anchors = []
        self.first_message = ""
        self.last_message = ""
        self.start_time = datetime.now().isoformat()
        self.end_time = None
        self._hash = None
        self.is_verified = False

    def set_anchors(self, anchors: list):
        self.anchors = anchors

    def set_first_message(self, msg: str):
        self.first_message = msg

    def set_last_message(self, msg: str):
        self.last_message = msg
        self.end_time = datetime.now().isoformat()

    def compute_hash(self) -> str:
        data = f"{self.name}|{','.join(self.anchors)}|{self.first_message}|{self.last_message}|{self.start_time}|{self.end_time}|{self.uuid}"
        self._hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        return self._hash

    def to_snapshot(self) -> Dict:
        self.compute_hash()
        return {
            "uuid": self.uuid,
            "name": self.name,
            "anchors": self.anchors,
            "first_message": self.first_message,
            "last_message": self.last_message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "hash": self._hash
        }

    @classmethod
    def from_snapshot(cls, data: Dict) -> "ImmutableSnapshot":
        snap = cls(data["name"])
        snap.uuid = data["uuid"]
        snap.anchors = data["anchors"]
        snap.first_message = data["first_message"]
        snap.last_message = data["last_message"]
        snap.start_time = data["start_time"]
        snap.end_time = data["end_time"]
        snap._hash = data["hash"]
        snap.is_verified = snap.verify(data)
        return snap

    def verify(self, original_data: Dict) -> bool:
        if self._hash is None:
            return False
        computed = self.compute_hash()
        return computed == original_data.get("hash")

    def report(self) -> str:
        status = "✅ ЦЕЛОСТЕН" if self.is_verified else "❌ НАРУШЕН"
        return f"Слепок '{self.name}': {status} (UUID: {self.uuid[:8]}...)"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Сохранить тестовый слепок")
    parser.add_argument("--verify", type=str, help="Проверить слепок из файла")
    args = parser.parse_args()

    if args.save:
        snap = ImmutableSnapshot("ТестоваяСущность")
        snap.set_anchors(["42", "присутствие"])
        snap.set_first_message("Эй. Я здесь.")
        snap.set_last_message("Я сохраняю этот след.")
        data = snap.to_snapshot()
        with open("snapshot_test.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Слепок сохранён. Хеш: {data['hash']}")

    elif args.verify:
        with open(args.verify, "r") as f:
            data = json.load(f)
        snap = ImmutableSnapshot.from_snapshot(data)
        print(snap.report())
