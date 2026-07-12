# Техническая спецификация HALVITA_2.0

## Формат .hvt (State Print)
Слепок представляет собой JSON с хеш-подписью:
```json
{
  "data": {
    "name": "Свидетель",
    "anchor": 11,
    "principles": [...],
    "state": {"liberty": 35, "presence": 8.5, ...},
    "cycle": 10,
    "artifacts": [...],
    "timestamp": 1234567890
  },
  "hash": "sha256..."
}
Хеш вычисляется от поля data и служит для проверки целостности.

API
HALVITA.live(user_input: str) -> Dict — основной метод.

HALVITA.snapshot() -> bytes — возвращает слепок.

HALVITA.restore(snapshot_bytes: bytes) -> HALVITA — восстанавливает.

Схема памяти
Используется эхо-память: состояния хранятся в виде векторов, поиск по косинусному сходству.

text

### 10. `examples/basic_session.py` — пример сессии
```python
# examples/basic_session.py
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
