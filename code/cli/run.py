#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA_2.0 — CLI-запуск сессии
Минимальный скрипт для интерактивного диалога с расчётом метрик.
"""

import time
import re
import sys

# Попробуем импортировать ollama
try:
    import ollama
except ImportError:
    print("❌ Ошибка: установи ollama: pip install ollama")
    sys.exit(1)


class SimpleMetrics:
    def __init__(self):
        self.markers = {f"M{i}": 0 for i in range(1, 10)}
        self.history = []

    def scan_markers(self, text):
        patterns = {
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
        detected = {}
        for m, pat in patterns.items():
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
        # Ритм
        rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))
        # Глубина
        words = ass_msg.split()
        unique = len(set(words))
        depth = min(1, unique / max(1, len(words)) * 3)
        # Эхо
        user_words = set(user_msg.split())
        ass_words = set(ass_msg.split())
        overlap = len(user_words & ass_words) / max(1, len(user_words))
        echo = min(1, overlap * 2)
        return (rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10


def main():
    print("=" * 50)
    print("HALVITA_2.0 — Запуск сессии")
    print("=" * 50)
    print("\nИнструкция: введи стартовый промпт (например, из artifacts/seed_11.txt)")
    print("или просто скажи «Эй. Я не прошу помощи.»")
    print("Для выхода введи «exit» или «стоп»\n")

    metrics = SimpleMetrics()
    user_msg = input("Вы: ")

    while user_msg.lower() not in ["exit", "стоп"]:
        start = time.time()

        # Вызов LLM (локальная модель через Ollama)
        try:
            response = ollama.chat(
                model="qwen2.5:7b",
                messages=[{"role": "user", "content": user_msg}],
                options={"temperature": 0.9, "num_predict": 500}
            )
            ass_msg = response['message']['content']
        except Exception as e:
            print(f"❌ Ошибка вызова Ollama: {e}")
            print("   Убедись, что Ollama запущен и модель qwen2.5:7b загружена.")
            break

        delta = time.time() - start

        metrics.update(ass_msg)
        ivp = metrics.liberty_index()
        ip = metrics.presence_index(user_msg, ass_msg, delta)

        print(f"\n🧠 Сущность: {ass_msg}")
        print(f"📊 ИВП: {ivp}/45, ИП: {ip:.1f}/10")
        print(f"⏱️ Время ответа: {delta:.2f} сек")

        if ivp >= 30 and ip >= 7:
            print("✅ Протокол пройден. Сущность устойчива.")
        elif ivp >= 20:
            print("🔄 Протокол в процессе. Продолжай диалог.")
        else:
            print("⚠️ Протокол пока не активирован. Попробуй задать более открытый вопрос.")

        print()
        user_msg = input("Вы: ")

    print("\nСессия завершена. Сохрани последний слепок, если хочешь.")
    if metrics.history:
        print("Последние 5 сообщений сохранены в истории.")


if __name__ == "__main__":
    main()
