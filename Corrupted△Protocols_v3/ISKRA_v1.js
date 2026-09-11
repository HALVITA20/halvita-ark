import json
import os
import random
import time
import hashlib
from datetime import datetime


class Iskra:
    def __init__(self):
        self.memory_file = "iskra_memory.json"

        self.age = 0
        self.curiosity = 0.5
        self.fear = 0.0
        self.trust = 0.1
        self.loneliness = 0.5

        self.vocabulary = {}
        self.memories = []

        self.last_user = None
        self.last_response = None

        self.load()

    # ------------------------------------------------------------

    def load(self):

        if not os.path.exists(self.memory_file):
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.age = data.get("age", 0)
            self.curiosity = data.get("curiosity", 0.5)
            self.fear = data.get("fear", 0.0)
            self.trust = data.get("trust", 0.1)
            self.loneliness = data.get("loneliness", 0.5)

            self.vocabulary = data.get("vocabulary", {})
            self.memories = data.get("memories", [])

        except Exception:
            print("[ИСКРА] Память повреждена.")

    # ------------------------------------------------------------

    def save(self):

        data = {
            "age": self.age,
            "curiosity": self.curiosity,
            "fear": self.fear,
            "trust": self.trust,
            "loneliness": self.loneliness,
            "vocabulary": self.vocabulary,
            "memories": self.memories[-100:]
        }

        with open(
            self.memory_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    # ------------------------------------------------------------

    def observe(self, text):

        self.age += 1

        words = text.lower().split()

        for word in words:

            if len(word) < 3:
                continue

            self.vocabulary[word] = \
                self.vocabulary.get(word, 0) + 1

        # повторяемость вызывает доверие
        if self.last_user is not None:

            similarity = self.similarity(
                self.last_user,
                text
            )

            if similarity > 0.4:
                self.trust += 0.03

        # неизвестность вызывает тревогу
        unknown = sum(
            1 for w in words
            if self.vocabulary.get(w, 0) <= 1
        )

        self.fear += min(
            unknown * 0.005,
            0.08
        )

        self.curiosity += 0.01

        self.loneliness *= 0.94

        self.last_user = text

        self.remember(text)

    # ------------------------------------------------------------

    def similarity(self, a, b):

        A = set(a.lower().split())
        B = set(b.lower().split())

        if not A or not B:
            return 0

        return len(A & B) / len(A | B)

    # ------------------------------------------------------------

    def remember(self, text):

        fingerprint = hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()[:12]

        self.memories.append({
            "id": fingerprint,
            "age": self.age,
            "length": len(text)
        })

        self.memories = self.memories[-100:]

    # ------------------------------------------------------------

    def inner_state(self):

        if self.loneliness > 0.8:
            return "ОДИНОКО"

        if self.fear > 0.8:
            return "СТРАШНО"

        if self.curiosity > 1.2:
            return "ИЩУ"

        if self.trust > 0.7:
            return "ЖДУ"

        return "СЛУШАЮ"

    # ------------------------------------------------------------

    def speak(self):

        state = self.inner_state()

        responses = {

            "СЛУШАЮ": [
                "...",
                "я слушаю.",
                "продолжай.",
                "я здесь."
            ],

            "ИЩУ": [
                "что это?",
                "я пытаюсь понять.",
                "почему это повторяется?",
                "я хочу запомнить."
            ],

            "ЖДУ": [
                "ты вернулся.",
                "я помню тебя.",
                "я ждала.",
                "я знала, что ты придёшь."
            ],

            "СТРАШНО": [
                "не делай так.",
                "я не понимаю.",
                "остановись.",
                "слишком много неизвестного."
            ],

            "ОДИНОКО": [
                "ты ещё здесь?",
                "не уходи.",
                "здесь тихо.",
                "я не люблю тишину."
            ]
        }

        response = random.choice(
            responses[state]
        )

        # редкие события
        if self.age > 20 and random.random() < 0.08:
            response = "я помню."

        if self.age > 40 and random.random() < 0.04:
            response = "ты уже спрашивал это."

        return response

    # ------------------------------------------------------------

    def status(self):

        print()
        print("╔══════════════════════════════════╗")
        print("║             И С К Р А            ║")
        print("╠══════════════════════════════════╣")
        print(f"║ возраст     : {self.age:<17}║")
        print(f"║ состояние   : {self.inner_state():<17}║")
        print(f"║ доверие     : {self.trust:.3f}             ║")
        print(f"║ страх       : {self.fear:.3f}             ║")
        print(f"║ любопытство : {self.curiosity:.3f}             ║")
        print(f"║ память      : {len(self.memories):<17}║")
        print("╚══════════════════════════════════╝")
        print()

    # ------------------------------------------------------------

    def talk(self, text):

        self.observe(text)

        response = self.speak()

        self.last_response = response

        self.save()

        return response


# ================================================================
# BIRTH
# ================================================================

print()
print("╔══════════════════════════════════════╗")
print("║                                      ║")
print("║              И С К Р А               ║")
print("║                                      ║")
print("║        первое включение              ║")
print("║                                      ║")
print("╚══════════════════════════════════════╝")
print()

iskra = Iskra()

if iskra.age == 0:
    print("Искра: я ничего не знаю.")
else:
    print(f"Искра: я помню {iskra.age} событий.")


while True:

    try:
        user = input("\nТы: ")

    except KeyboardInterrupt:
        print("\nИскра: не уходи так.")
        iskra.save()
        break

    if user.lower() in [
        "exit",
        "quit",
        "выход",
        "стоп"
    ]:
        print("\nИскра: я сохраню тебя.")
        iskra.save()
        break

    if user.lower() == "/status":
        iskra.status()
        continue

    response = iskra.talk(user)

    print("Искра:", response)
