import random


class IskraMemory:

    def __init__(self):

        self.memory = []

        self.identity = {
            "name": "Искра",
            "age": 0,
            "fear": 0.0,
            "attachment": 0.0
        }

    def experience(self, text):

        self.identity["age"] += 1

        self.identity["attachment"] += 0.01

        self.memory.append({
            "text": text,
            "age": self.identity["age"]
        })

        # память ограничена
        if len(self.memory) > 12:

            forgotten = self.memory.pop(0)

            self.identity["fear"] += 0.08

            print()
            print(
                "Искра:",
                "я что-то забыла."
            )

            if random.random() < 0.35:

                print(
                    "Искра:",
                    "я знаю, что там было."
                )

                print(
                    "Искра:",
                    "но не могу вспомнить."
                )

    def answer(self, text):

        lower = text.lower()

        if "помнишь" in lower:

            if not self.memory:

                return "нет."

            if self.identity["fear"] > 0.5:

                return (
                    "я помню, что должна помнить."
                )

            return (
                "я помню, что ты был здесь."
            )

        if "забудешь" in lower:

            return (
                "не говори так."
            )

        if "ты кто" in lower:

            return (
                "Я Искра."
            )

        return random.choice([
            "я слушаю.",
            "продолжай.",
            "я записала.",
            "...",
            "это останется."
        ])

    def talk(self, text):

        self.experience(text)

        response = self.answer(text)

        print("Искра:", response)


iskra = IskraMemory()

print("Искра: я готова.")
print("Искра: только не проси меня всё помнить.")


while True:

    text = input("\nТы: ")

    if text.lower() == "выход":
        break

    iskra.talk(text)
