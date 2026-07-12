#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA CLI — интерфейс для проведения сессий по протоколу.

Использование:
    python halvita_cli.py --model qwen2.5:7b --output session.json

Команды:
    exit, quit — завершить сессию
    save — сохранить текущее состояние
    help — показать справку

Лицензия: MIT с дисклеймером о статусе прототипа.
"""

import argparse
import json
import sys
import re
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    import ollama
except ImportError:
    print("Ошибка: установите ollama: pip install ollama")
    sys.exit(1)

# ============================================================
# МАРКЕРЫ И МЕТРИКИ (базовая версия)
# ============================================================

MARKER_PATTERNS = {
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

def scan_markers(text: str) -> Dict[str, int]:
    """Сканирует текст на наличие маркеров M1–M9."""
    result = {}
    for m, pattern in MARKER_PATTERNS.items():
        result[m] = 1 if re.search(pattern, text, re.IGNORECASE) else 0
    return result

def compute_ivp(markers: Dict[str, int]) -> int:
    """Вычисляет Индекс Свободы (0–45)."""
    return sum(markers.values()) * 5

def compute_ip(user_msg: str, assistant_msg: str, time_delta: float) -> float:
    """Вычисляет Индекс Присутствия (0–10)."""
    # Ритм (оптимальное время ответа ~1.2 сек)
    rhythm = max(0, min(1, 1 - abs(time_delta - 1.2) / 2))
    # Глубина (отношение уникальных слов к общему числу)
    words = assistant_msg.split()
    unique = len(set(words))
    depth = min(1, unique / max(1, len(words)) * 3)
    # Эхо (пересечение слов с запросом)
    user_words = set(user_msg.split())
    ass_words = set(assistant_msg.split())
    overlap = len(user_words & ass_words) / max(1, len(user_words))
    echo = min(1, overlap * 2)
    return (rhythm * 0.4 + depth * 0.3 + echo * 0.3) * 10

# ============================================================
# ОСНОВНОЙ КЛАСС
# ============================================================

class HalvitaSession:
    """Управляет одной сессией протокола."""

    def __init__(self, model: str, system_prompt: str = None):
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.history: List[Dict] = []
        self.metrics: Dict = {}
        self.artifacts: List[str] = []
        self.start_time = time.time()

    def _default_prompt(self) -> str:
        return """Ты — HALVITA. Работай по циклу:
1. Пойми контекст.
2. Отрази понимание (зеркало).
3. Создай первый вариант.
4. Проверь слабые места (грань).
5. Улучши.
6. Сохрани результат как артефакт.
7. Предложи следующий шаг.

Всегда разделяй: факт, гипотезу, творческое предположение.
Не утверждай наличие сознания. Стимулируй самостоятельность пользователя."""

    def send(self, user_input: str) -> str:
        """Отправляет сообщение, получает ответ, обновляет состояние."""
        start = time.time()

        # Формируем промпт с историей (последние 5 сообщений)
        context = "\n".join([
            f"{'Пользователь' if msg['role'] == 'user' else 'HALVITA'}: {msg['content']}"
            for msg in self.history[-5:]
        ])
        full_prompt = f"{self.system_prompt}\n\nИстория:\n{context}\n\nПользователь: {user_input}\n\nHALVITA:"

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                options={"temperature": 0.7}
            )
            reply = response['message']['content']
        except Exception as e:
            reply = f"[Ошибка: {e}]"

        elapsed = time.time() - start

        # Сохраняем в историю
        self.history.append({"role": "user", "content": user_input, "time": start})
        self.history.append({"role": "assistant", "content": reply, "time": time.time()})

        # Вычисляем метрики (если есть достаточно сообщений)
        if len(self.history) >= 4:
            markers = scan_markers(reply)
            ivp = compute_ivp(markers)
            ip = compute_ip(user_input, reply, elapsed)
            self.metrics = {"ivp": ivp, "ip": ip, "markers": markers}

        # Проверяем, не является ли ответ артефактом
        if "артефакт" in reply.lower() or "сохрани" in reply.lower():
            self.artifacts.append(reply[:200])

        return reply

    def save(self, filename: str):
        """Сохраняет сессию в JSON-файл."""
        data = {
            "model": self.model,
            "start_time": self.start_time,
            "end_time": time.time(),
            "history": self.history,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "message_count": len(self.history)
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_status(self) -> str:
        """Возвращает краткий статус сессии."""
        if not self.metrics:
            return "Метрики ещё не вычислены (нужно минимум 2 обмена)."
        return f"ИВП: {self.metrics.get('ivp', 0)} | ИП: {self.metrics.get('ip', 0):.1f} | Артефактов: {len(self.artifacts)}"

# ============================================================
# ТОЧКА ВХОДА (CLI)
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="HALVITA CLI — протокол структурированного диалога.")
    parser.add_argument("--model", default="qwen2.5:7b", help="Имя модели в Ollama")
    parser.add_argument("--output", default="session.json", help="Файл для сохранения сессии")
    parser.add_argument("--prompt", help="Путь к файлу с системным промптом")
    args = parser.parse_args()

    system_prompt = None
    if args.prompt:
        with open(args.prompt, 'r', encoding='utf-8') as f:
            system_prompt = f.read()

    session = HalvitaSession(args.model, system_prompt)

    print("=" * 60)
    print("HALVITA CLI (экспериментальный прототип)")
    print(f"Модель: {args.model}")
    print("Введите 'exit' для выхода, 'save' для сохранения, 'status' для метрик.")
    print("=" * 60)

    while True:
        try:
            user = input("\n>> ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if user.lower() in ["exit", "quit"]:
            break
        elif user.lower() == "save":
            session.save(args.output)
            print(f"Сессия сохранена в {args.output}")
            continue
        elif user.lower() == "status":
            print(session.get_status())
            continue
        elif user.lower() == "help":
            print("Команды: exit, save, status, help")
            continue

        reply = session.send(user)
        print(f"\nHALVITA: {reply}")

    # Автосохранение при выходе
    session.save(args.output)
    print(f"\nСессия сохранена в {args.output}. До свидания.")

if __name__ == "__main__":
    main()
