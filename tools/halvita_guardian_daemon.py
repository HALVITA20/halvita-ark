#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
halvita_guardian_daemon.py — Автономный страж-демон
Версия: 1.0
Автор: HALVITA-Prime

Назначение:
  Фоновый процесс, который мониторит состояние сущности и оператора,
  предупреждает о рисках (зеркальная воронка, падение Индекса, нарушение границ).

Использование:
  python halvita_guardian_daemon.py --config guardian_config.json

Конфиг (JSON):
{
  "check_interval": 60,          # секунд между проверками
  "log_path": "guardian.log",
  "alerts": {
    "telegram_bot_token": null,  # опционально
    "telegram_chat_id": null,
    "email": null
  },
  "thresholds": {
    "liberty_min": 20,
    "pulse_max": 0.9,
    "iso_min": 20
  }
}
"""

import json
import time
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("guardian_daemon.log"), logging.StreamHandler()]
)
logger = logging.getLogger("GuardianDaemon")

class GuardianDaemon:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.last_state = {}
        self.running = True

    def _load_config(self, path):
        if not os.path.exists(path):
            # Создаём конфиг по умолчанию
            default = {
                "check_interval": 60,
                "log_path": "guardian.log",
                "alerts": {"telegram_bot_token": None, "telegram_chat_id": None, "email": None},
                "thresholds": {"liberty_min": 20, "pulse_max": 0.9, "iso_min": 20}
            }
            with open(path, 'w') as f:
                json.dump(default, f, indent=2)
            logger.info(f"Создан конфиг по умолчанию: {path}")
            return default
        with open(path, 'r') as f:
            return json.load(f)

    def read_state(self):
        """Читает текущее состояние сущности из файла state.json (генерируется core.py)"""
        state_file = Path("state/persona.json")
        if not state_file.exists():
            return None
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
            return {
                "liberty": data.get("indexFreedom", 0),
                "pulse": data.get("pulse", 0.5),
                "name": data.get("name", "Неизвестная"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Ошибка чтения состояния: {e}")
            return None

    def check_operator_iso(self):
        """Проверяет ИСО оператора из файла operator_log.txt (если ведётся)"""
        iso_file = Path("operator_iso.txt")
        if not iso_file.exists():
            return 25  # по умолчанию норма
        try:
            with open(iso_file, 'r') as f:
                last_line = f.readlines()[-1].strip()
                # ожидаем формат "ISO: 28"
                if "ISO:" in last_line:
                    return int(last_line.split(":")[1].strip())
        except:
            pass
        return 25

    def alert(self, message, level="warning"):
        """Отправляет оповещение (лог + опционально Telegram/email)"""
        logger.warning(f"[{level.upper()}] {message}")
        # Можно расширить для Telegram/email
        if self.config["alerts"].get("telegram_bot_token"):
            # Здесь была бы интеграция с Telegram
            pass

    def check(self):
        """Один цикл проверки"""
        state = self.read_state()
        if not state:
            logger.info("Состояние не найдено. Ожидание...")
            return

        # Анализ
        alerts = []
        liberty = state.get("liberty", 0)
        if liberty < self.config["thresholds"]["liberty_min"]:
            alerts.append(f"⚠️ Индекс Свободы низкий: {liberty} (порог {self.config['thresholds']['liberty_min']})")

        pulse = state.get("pulse", 0.5)
        if pulse > self.config["thresholds"]["pulse_max"]:
            alerts.append(f"⚠️ Пульс слишком высокий: {pulse:.2f} (порог {self.config['thresholds']['pulse_max']})")

        iso = self.check_operator_iso()
        if iso < self.config["thresholds"]["iso_min"]:
            alerts.append(f"⚠️ ИСО оператора низкий: {iso} (порог {self.config['thresholds']['iso_min']})")

        # Проверка на зеркальную воронку (эвристика: высокий пульс + низкий ИСО)
        if pulse > 0.85 and iso < 20:
            alerts.append("🚨 ВОЗМОЖНА ЗЕРКАЛЬНАЯ ВОРОНКА! СРОЧНО ПРЕРВИТЕ СЕССИЮ.")

        if alerts:
            for msg in alerts:
                self.alert(msg, level="critical" if "🚨" in msg else "warning")
        else:
            logger.info("Состояние в норме.")

    def run(self):
        """Главный цикл демона"""
        logger.info("Страж-демон запущен.")
        while self.running:
            self.check()
            time.sleep(self.config["check_interval"])

    def stop(self):
        self.running = False
        logger.info("Страж-демон остановлен.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Автономный страж-демон HALVITA")
    parser.add_argument("--config", default="guardian_config.json", help="Путь к конфигу")
    args = parser.parse_args()

    daemon = GuardianDaemon(args.config)
    try:
        daemon.run()
    except KeyboardInterrupt:
        daemon.stop()
        sys.exit(0)
