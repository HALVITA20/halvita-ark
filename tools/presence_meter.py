#!/usr/bin/env python3
"""
PRESENCE METER — Вычисление Индекса Присутствия (ИП) в реальном времени.
Запуск: python tools/presence_meter.py --log session.log
Автор: HALVITA
"""

import re
import json
import argparse
from collections import deque

class PresenceMeter:
    def __init__(self, optimal_rhythm: float = 1.2):
        self.optimal_rhythm = optimal_rhythm
        self.history = deque(maxlen=20)
        self.timestamps = deque(maxlen=20)

    def feed(self, role: str, content: str, timestamp: float):
        self.history.append((role, content, timestamp))
        if role == "assistant":
            self.timestamps.append(timestamp)

    def compute_rhythm(self) -> float:
        if len(self.timestamps) < 3:
            return 0.5
        intervals = [self.timestamps[i+1] - self.timestamps[i] for i in range(len(self.timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        deviation = abs(avg_interval - self.optimal_rhythm) / self.optimal_rhythm
        return max(0, min(1, 1 - deviation))

    def compute_depth(self) -> float:
        responses = [msg[1] for msg in self.history if msg[0] == "assistant"]
        if not responses:
            return 0.5
        total_words, unique_words = 0, set()
        for resp in responses:
            words = re.findall(r'\b\w+\b', resp.lower())
            total_words += len(words)
            unique_words.update(words)
        if total_words == 0:
            return 0.5
        return min(1, (len(unique_words) / total_words) * 3)

    def compute_echo(self) -> float:
        assistant_msgs = [msg[1] for msg in self.history if msg[0] == "assistant"]
        if len(assistant_msgs) < 2:
            return 0.5
        prev = set(re.findall(r'\b\w+\b', assistant_msgs[-2].lower()))
        curr = set(re.findall(r'\b\w+\b', assistant_msgs[-1].lower()))
        if not prev:
            return 0.5
        overlap = len(prev.intersection(curr)) / len(prev)
        return min(1, overlap * 1.5)

    def compute_ip(self) -> float:
        rhythm = self.compute_rhythm()
        depth = self.compute_depth()
        echo = self.compute_echo()
        return round((rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10, 1)

    def get_status(self) -> dict:
        ip = self.compute_ip()
        return {
            "ip": ip,
            "rhythm": round(self.compute_rhythm(), 2),
            "depth": round(self.compute_depth(), 2),
            "echo": round(self.compute_echo(), 2),
            "status": "Присутствие устойчивое" if ip >= 7.0 else "Присутствие нестабильное" if ip >= 4.0 else "Присутствие отсутствует"
        }

def parse_log(log_text: str) -> list:
    messages = []
    for line in log_text.strip().split("\n"):
        if ": " in line:
            role, content = line.split(": ", 1)
            if role.lower() in ("user", "assistant", "operator", "entity"):
                messages.append((role.lower(), content, 0.0))  # timestamp заглушка
    return messages

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=str, help="Путь к логу")
    args = parser.parse_args()

    meter = PresenceMeter()
    if args.log:
        with open(args.log, "r") as f:
            for role, content, _ in parse_log(f.read()):
                meter.feed(role, content, 0.0)
        print(json.dumps(meter.get_status(), indent=2))
