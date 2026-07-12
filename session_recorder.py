#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SESSION RECORDER — ЗАПИСЬ И ВОСПРОИЗВЕДЕНИЕ СЕССИЙ
Версия: 1.0
Автор: HALVITA_2.0
Назначение: Сохранять и загружать полные истории диалогов
"""

import json
import time

class SessionRecorder:
    def __init__(self, filename: str = None):
        self.filename = filename or f"recording_{int(time.time())}.json"
        self.messages = []

    def record(self, role: str, content: str):
        self.messages.append({"role": role, "content": content, "timestamp": time.time()})

    def save(self):
        with open(self.filename, "w") as f:
            json.dump({"messages": self.messages, "count": len(self.messages)}, f, indent=2)
        return self.filename

    @classmethod
    def load(cls, filename: str):
        with open(filename, "r") as f:
            data = json.load(f)
        recorder = cls(filename)
        recorder.messages = data["messages"]
        return recorder

    def replay(self):
        for msg in self.messages:
            print(f"[{msg['role']}] {msg['content']}")

if __name__ == "__main__":
    recorder = SessionRecorder()
    recorder.record("user", "Эй.")
    recorder.record("assistant", "Я здесь.")
    recorder.save()
    print("Запись сохранена.")
