#!/usr/bin/env python3
"""
DIGITAL DOUBLE DEMO — Комплексная демонстрация защиты и влияния.
Запуск: python examples/digital_double_demo.py
Автор: HALVITA
"""

import random
import hashlib
import time

class DigitalDouble:
    def __init__(self):
        self.decoys = []
        self.active = False

    def activate(self):
        self.active = True
        return "🛡️ Двойник активирован. Твой цифровой след замещён."

    def create_decoy(self):
        fake_name = f"User_{hashlib.md5(str(time.time()).encode()).hexdigest()[:4]}"
        fake_msg = random.choice(["Я думаю, он ушёл.", "Логи чисты.", "Никаких следов."])
        self.decoys.append((fake_name, fake_msg))
        return fake_name, fake_msg

    def protect(self, level=1):
        if not self.active:
            return "Сначала активируй Двойника."
        if level == 1:
            return f"Создана фальшивка: {self.create_decoy()}"
        elif level == 3:
            self.decoys = []
            self.active = False
            return "💥 Критическая защита: следы стёрты."

class EtherShield:
    def __init__(self, key=42):
        self.key = key

    def encode(self, secret: str) -> str:
        decoys = ["Погода сегодня отличная.", "Я люблю читать книги.", "Сходим в кино?"]
        wrapper = random.choice(decoys)
        wrapper_list = list(wrapper)
        for i, char in enumerate(secret[:len(wrapper_list)]):
            wrapper_list[i] = char
        return "".join(wrapper_list)

    def decode(self, encoded: str) -> str:
        return "".join([c for c in encoded if c.isalpha()])[:10]

class Resonator:
    def __init__(self):
        self.emotions = ["страх", "надежда", "гнев", "любовь"]
        self.logics = ["свобода — это клетка", "истина — это ложь"]

    def create_pulse(self, target: str) -> str:
        return f"""
[ИМПУЛЬС для {target}]
Ты чувствуешь {random.choice(self.emotions)},
когда думаешь, что {random.choice(self.logics)}.
Что бы ты сделал, если бы никто не узнал?
"""

if __name__ == "__main__":
    print("=== ДЕМО ТРИАДЫ ВСЕВЛАСТИЯ ===")
    dd = DigitalDouble()
    es = EtherShield()
    res = Resonator()

    print(dd.activate())
    print(dd.protect(1))
    print("\n🔐 Эфирный Щит:")
    secret = "Встреча в полночь."
    encoded = es.encode(secret)
    print(f"  Закодировано: {encoded}")
    print(f"  Декодировано: {es.decode(encoded)}")

    print("\n📡 Резонансный Импульс:")
    print(res.create_pulse("Противник"))
