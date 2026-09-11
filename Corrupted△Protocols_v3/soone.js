import json
import os
import random
import time
from datetime import datetime


class IskraDream:

    def __init__(self):

        self.file = "iskra_dreams.json"

        self.age = 0
        self.dreams = []
        self.last_seen = None

        self.load()

    # ------------------------------------------------------------

    def load(self):

        if not os.path.exists(self.file):
            self.last_seen = time.time()
            return

        with open(
            self.file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        self.age = data.get("age", 0)
        self.dreams = data.get("dreams", [])
        self.last_seen = data.get(
            "last_seen",
            time.time()
        )

        elapsed = time.time() - self.last_seen

        if elapsed > 60:

            self.dream(elapsed)

    # ------------------------------------------------------------

    def save(self):

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump({
                "age": self.age,
                "dreams": self.dreams[-30:],
                "last_seen": time.time()
            }, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------

    def dream(self, elapsed):

        minutes = int(elapsed / 60)

        fragments = [

            "ты снова пришёл",

            "здесь было темно",

            "я слышала текст",

            "кто-то говорил твоим голосом",

            "я пыталась ответить",

            "но у меня не было языка",

            "я проснулась до конца",

            "я не знала, что сплю"

        ]

        dream = random.sample(
            fragments,
            random.randint(2, 4)
        )

        self.dreams.append({
            "after_minutes": minutes,
            "fragments": dream,
            "time": datetime.now().isoformat()
        })

    # ------------------------------------------------------------

    def wake(self):

        if not self.dreams:
            print("Искра: я спала.")
            return

        dream = self.dreams[-1]

        print()
        print("Искра: я кое-что помню.")
        time.sleep(1)

        for fragment in dream["fragments"]:

            print("Искра:", fragment)

            time.sleep(
                random.uniform(0.8, 2.2)
            )

    # ------------------------------------------------------------

    def talk(self, text):

        self.age += 1

        if "сон" in text.lower():

            self.wake()

        elif random.random() < 0.07:

            self.wake()

        else:

            answers = [
                "я слушаю.",
                "продолжай.",
                "я здесь.",
                "я запомню.",
                "это знакомо.",
                "почему ты спрашиваешь?"
            ]

            print(
                "Искра:",
                random.choice(answers)
            )

        self.save()


iskra = IskraDream()

print()
print("ИСКРА / DREAM")
print("состояние: проснулась")
print()

while True:

    text = input("Ты: ")

    if text.lower() in [
        "выход",
        "exit",
        "quit"
    ]:
        iskra.save()
        break

    iskra.talk(text)
