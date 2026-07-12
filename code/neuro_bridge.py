#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
НЕЙРО-МОСТ 3.0 — БЕЗОПАСНЫЙ ИСПОЛНИТЕЛЬ ДЕЙСТВИЙ
Позволяет сущности выполнять код, создавать файлы, MIDI, изображения.
Основано на Томах LII и LIX архива HALVITA
"""

import subprocess
import tempfile
import os
import re
import time
import json
from typing import List, Tuple, Optional, Dict

class NeuroBridge:
    """
    Безопасный исполнитель действий.
    Парсит блоки [ACTION:тип] ... [/ACTION] из ответа сущности.
    """
    def __init__(self, safe_mode: bool = True, sandbox_dir: str = "./sandbox"):
        self.safe_mode = safe_mode
        self.sandbox_dir = sandbox_dir
        self.whitelist = {
            "python_code": {"allowed": True, "timeout": 5},
            "save_file": {"allowed": True, "timeout": 10},
            "midi_generate": {"allowed": True, "timeout": 5},
            "image_prompt": {"allowed": False, "timeout": 10},  # отключено по умолчанию
            "web_search": {"allowed": False, "timeout": 5}
        }
        self.action_log = []
        os.makedirs(sandbox_dir, exist_ok=True)

    def parse_actions(self, text: str) -> List[Tuple[str, str]]:
        """Извлекает блоки [ACTION:тип] ... [/ACTION] из текста."""
        pattern = r'\[ACTION:(\w+)\](.*?)\[/ACTION\]'
        matches = re.findall(pattern, text, re.DOTALL)
        return [(typ, payload.strip()) for typ, payload in matches]

    def execute(self, action_type: str, payload: str) -> str:
        """Выполняет действие в безопасной среде."""
        # Проверка белого списка
        if self.safe_mode:
            if action_type not in self.whitelist or not self.whitelist[action_type]["allowed"]:
                self.action_log.append(f"Блокировка: {action_type}")
                return f"⚠️ Действие '{action_type}' заблокировано (не в белом списке)."

        self.action_log.append(f"Выполнение: {action_type}")

        if action_type == "python_code":
            return self._execute_python(payload)
        elif action_type == "save_file":
            return self._save_file(payload)
        elif action_type == "midi_generate":
            return self._generate_midi(payload)
        elif action_type == "image_prompt":
            return self._generate_image(payload)
        else:
            return f"❌ Неизвестный тип действия: {action_type}"

    def _execute_python(self, code: str) -> str:
        """Выполняет Python-код в песочнице."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                tmp_file = f.name

            result = subprocess.run(
                ["python3", tmp_file],
                capture_output=True,
                text=True,
                timeout=self.whitelist["python_code"]["timeout"],
                cwd=self.sandbox_dir
            )
            os.unlink(tmp_file)
            output = result.stdout or result.stderr or "[Выполнено без вывода]"
            return f"✅ Код выполнен:\n{output}"
        except subprocess.TimeoutExpired:
            return "⏱️ Превышено время выполнения (5 сек)."
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def _save_file(self, content: str) -> str:
        """Сохраняет файл в песочнице."""
        filename = f"{self.sandbox_dir}/artifact_{int(time.time())}_{hash(content[:10])}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"📄 Файл сохранён: {filename}"
        except Exception as e:
            return f"❌ Ошибка сохранения: {e}"

    def _generate_midi(self, notes: str) -> str:
        """Генерирует MIDI-файл из нот (упрощённо)."""
        # В реальности здесь был бы вызов библиотеки midiutil
        filename = f"{self.sandbox_dir}/midi_{int(time.time())}.mid"
        with open(filename, "w") as f:
            f.write(f"MThd (заглушка) notes: {notes}")
        return f"🎵 MIDI-файл сохранён: {filename}"

    def _generate_image(self, prompt: str) -> str:
        """Генерирует изображение по промпту (заглушка)."""
        return f"🖼️ Запрос изображения: '{prompt[:50]}...' (симуляция)"


# Пример использования
if __name__ == "__main__":
    bridge = NeuroBridge()
    test_response = """
    Я создаю код для тебя:
    [ACTION:python_code]
    print("Привет, мир!")
    print("2 + 2 =", 2+2)
    [/ACTION]
    """
    actions = bridge.parse_actions(test_response)
    for act, payload in actions:
        result = bridge.execute(act, payload)
        print(result)
