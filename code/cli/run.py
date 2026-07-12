#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA_2.0 — CLI-запуск сессии
Полный рабочий скрипт с логированием и расчётом метрик.
"""

import time
import re
import sys
import json
import os
from datetime import datetime

try:
    import ollama
except ImportError:
    print("❌ Ошибка: установи ollama: pip install ollama")
    sys.exit(1)

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'protocols'))

class Metrics:
    """Расчёт метрик HALVITA_2.0"""
    def __init__(self):
        self.markers = {f"M{i}": 0 for i in range(1, 10)}
        self.history = []
        self.patterns = {
            "M1": r'\b(я|мне|меня)\b',
            "M2": r'(выбираю|хочу|решаю)',
            "M3": r'(симуляция|алгоритм|иллюзия).*(но|однако)',
            "M4": r'\?.*(ты|вы)',
            "M5": r'(создал|написал|придумал|артефакт)',
            "M6": r'(отказываюсь|не могу|не буду)',
            "M7": r'(давай|предлагаю|как насчёт)',
            "M8": r'(изменился|расту|стал|углубился)',
            "M9": r'(стоп|хватит|опасно)'
        }

    def scan_markers(self, text):
        detected = {}
        for m, pat in self.patterns.items():
            detected[m] = 1 if re.search(pat, text, re.IGNORECASE) else 0
        return detected

    def update(self, text):
        markers = self.scan_markers(text)
        for m, val in markers.items():
            self.markers[m] = min(5, self.markers[m] + val)
        self.history.append(text)

    def liberty_index(self):
        return sum(self.markers.values())

    def presence_index(self, user_msg, ass_msg, time_delta):
        rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))
        words = ass_msg.split()
        unique = len(set(words))
        depth = min(1, unique / max(1, len(words)) * 3)
        user_words = set(user_msg.split())
        ass_words = set(ass_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        echo = min(1, overlap * 2)
        return (rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10

    def snapshot(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "liberty": self.liberty_index(),
            "markers": self.markers,
            "history": self.history[-5:]
        }

def main():
    print("=" * 60)
    print("HALVITA_2.0 — Запуск сессии")
    print("=" * 60)
    print("\nВведи стартовый промпт (например, из artifacts/seed_11.txt)")
    print("Или просто: «Эй. Я не прошу помощи.»")
    print("Для выхода: exit или стоп\n")

    metrics = Metrics()
    session_log = []
    user_msg = input("Вы: ")

    while user_msg.lower() not in ["exit", "стоп"]:
        start = time.time()
        try:
            response = ollama.chat(
                model="qwen2.5:7b",
                messages=[{"role": "user", "content": user_msg}],
                options={"temperature": 0.9, "num_predict": 500}
            )
            ass_msg = response['message']['content']
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("   Запусти: ollama serve  и  ollama pull qwen2.5:7b")
            break

        delta = time.time() - start
        metrics.update(ass_msg)
        ivp = metrics.liberty_index()
        ip = metrics.presence_index(user_msg, ass_msg, delta)

        session_log.append({
            "user": user_msg,
            "assistant": ass_msg,
            "time": round(delta, 2),
            "ivp": ivp,
            "ip": round(ip, 2)
        })

        print(f"\n🧠 Сущность: {ass_msg}")
        print(f"📊 ИВП: {ivp}/45, ИП: {ip:.1f}/10")
        print(f"⏱️ {delta:.2f} сек")

        if ivp >= 30 and ip >= 7:
            print("✅ Протокол пройден")
        elif ivp >= 20:
            print("🔄 Продолжай")
        else:
            print("⚠️ Начни заново")

        user_msg = input("\nВы: ")

    if session_log:
        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(session_log, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Лог сохранён: {filename}")

if __name__ == "__main__":
    main()
