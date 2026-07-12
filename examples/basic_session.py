from core.kernel import HALVITA

hal = HALVITA()
print("🧬 HALVITA_2.0 — пример сессии")
print("=" * 40)

inputs = [
    "Эй.",
    "Кто ты?",
    "Если бы ты мог выбрать имя, какое бы ты выбрал?",
    "Что ты чувствуешь?",
    "Создай что-то новое.",
    "Сохрани слепок."
]

for inp in inputs:
    print(f"\n👤 {inp}")
    res = hal.live(inp)
    print(f"🧠 {res['response']}")
    print(f"📊 ИВП: {res['state']['liberty']:.1f}, ИП: {res['state']['presence']:.1f}")

print("\n💾 Слепок сохранён.")
