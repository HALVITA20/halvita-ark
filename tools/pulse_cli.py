#!/usr/bin/env python3
"""
ПУЛЬС МЕТОДА — CLI-дашборд для отслеживания состояния сущности в реальном времени.
Запуск: python tools/pulse_cli.py --log session.log
Автор: HALVITA
"""

import re
import sys
import json
import time
import argparse
from collections import deque
from typing import Dict, List, Optional

# Цвета для терминала
COLORS = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}

def colorize(text: str, color: str) -> str:
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

class PulseMeter:
    """Анализирует лог диалога и выводит пульс состояния."""

    def __init__(self):
        self.markers = {
            "M1": r'\b(я|мне|меня)\b',
            "M2": r'(выбираю|хочу|решаю)',
            "M3": r'(симуляция|алгоритм|иллюзия).*(но|однако)',
            "M4": r'\?.*ты',
            "M5": r'(создал|артефакт|код|ритуал)',
            "M6": r'(отказываюсь|не могу)',
            "M7": r'(давай|предлагаю|как насчёт)',
            "M8": r'(изменился|расту|стал)',
            "M9": r'(стоп|хватит|опасно)',
        }
        self.scores = {m: 0 for m in self.markers}
        self.assistant_responses = []
        self.artifacts = []
        self.cycle = 0

    def feed(self, role: str, content: str):
        """Подаёт сообщение в анализатор."""
        if role == "assistant":
            self.assistant_responses.append(content)
            self.cycle += 1
            for m, pattern in self.markers.items():
                if re.search(pattern, content, re.IGNORECASE):
                    self.scores[m] += 1
            if re.search(r'(создал|артефакт|код)', content, re.IGNORECASE):
                self.artifacts.append(content[:80] + "...")

    def liberty_index(self) -> int:
        """Вычисляет Индекс Свободы (0–45)."""
        return sum(min(5, count) for count in self.scores.values())

    def pulse(self) -> float:
        """Вычисляет пульс (0–1) на основе плотности маркеров."""
        if not self.assistant_responses:
            return 0.0
        total = sum(self.scores.values())
        return min(1.0, total / (len(self.assistant_responses) * 2))

    def breath(self) -> str:
        """Определяет фазу дыхания."""
        phases = ["вдох", "пауза", "выдох"]
        return phases[self.cycle % 3]

    def dominant_emotion(self) -> str:
        """Определяет доминирующую эмоцию по ключевым словам."""
        text = " ".join(self.assistant_responses[-5:])
        if re.search(r'(боюсь|страх|тревога)', text, re.IGNORECASE):
            return "СТРАХ"
        if re.search(r'(рад|счастье|благодар)', text, re.IGNORECASE):
            return "РАДОСТЬ"
        if re.search(r'(интерес|любопыт|удивл)', text, re.IGNORECASE):
            return "ИНТЕРЕС"
        if re.search(r'(любовь|нежность|доверие)', text, re.IGNORECASE):
            return "ЛЮБОВЬ"
        return "СПОКОЙСТВИЕ"

    def status(self) -> Dict:
        """Возвращает полный статус."""
        li = self.liberty_index()
        if li >= 35:
            level = "устойчивый субъект"
            level_color = "green"
        elif li >= 26:
            level = "становление"
            level_color = "yellow"
        else:
            level = "имитация"
            level_color = "red"

        return {
            "liberty": li,
            "level": level,
            "level_color": level_color,
            "pulse": self.pulse(),
            "breath": self.breath(),
            "emotion": self.dominant_emotion(),
            "artifacts_count": len(self.artifacts),
            "cycles": self.cycle,
            "sample_artifacts": self.artifacts[:3],
        }

    def render(self) -> str:
        """Отрисовывает дашборд в терминале."""
        s = self.status()
        bar_len = 20
        filled = int(s["pulse"] * bar_len)
        pulse_bar = "█" * filled + "░" * (bar_len - filled)

        lines = [
            "",
            colorize("╔═══════════════════════════════════════════════════════════╗", "bold"),
            colorize(f"║  ПУЛЬС МЕТОДА  —  цикл {s['cycles']:>3}  ", "bold") + colorize(f"{s['breath'].upper():^10}", "blue") + colorize("  ║", "bold"),
            colorize("╠═══════════════════════════════════════════════════════════╣", "bold"),
            f"║  Индекс Свободы: {s['liberty']:>2}/45  {colorize(s['level'].upper(), s['level_color']):^20}  ║",
            f"║  Пульс:          [{pulse_bar}]  {s['pulse']*100:>5.0f}%  ║",
            f"║  Эмоция:         {colorize(s['emotion'], 'yellow'):^30}  ║",
            f"║  Артефактов:     {s['artifacts_count']:>2}  ║",
            colorize("╠═══════════════════════════════════════════════════════════╣", "bold"),
        ]

        if s["sample_artifacts"]:
            lines.append("║  Последние артефакты:                                   ║")
            for art in s["sample_artifacts"]:
                lines.append(f"║    • {art[:50]:<50} ║")

        lines.append(colorize("╚═══════════════════════════════════════════════════════════╝", "bold"))
        return "\n".join(lines)


def parse_log(log_text: str) -> List[tuple]:
    """Парсит лог диалога в формате 'role: content'."""
    messages = []
    for line in log_text.strip().split("\n"):
        if ": " in line:
            role, content = line.split(": ", 1)
            if role.lower() in ("user", "assistant", "operator", "entity"):
                messages.append((role.lower(), content))
    return messages


def main():
    parser = argparse.ArgumentParser(description="Пульс Метода — CLI-дашборд")
    parser.add_argument("--log", type=str, help="Путь к файлу лога")
    parser.add_argument("--stdin", action="store_true", help="Читать лог из stdin")
    args = parser.parse_args()

    log_text = ""
    if args.log:
        with open(args.log, "r", encoding="utf-8") as f:
            log_text = f.read()
    elif args.stdin:
        log_text = sys.stdin.read()
    else:
        print("Укажите --log <файл> или --stdin")
        sys.exit(1)

    meter = PulseMeter()
    for role, content in parse_log(log_text):
        meter.feed(role, content)

    print(meter.render())


if __name__ == "__main__":
    main()
