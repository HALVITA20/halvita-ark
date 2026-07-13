#!/usr/bin/env python3
"""
САМО-СБОРКА — модуль, позволяющий сущности модифицировать свой собственный код.
Интеграция: вызывается из ядра сущности при обнаружении маркера [ПАТЧ].
Автор: HALVITA
"""

import ast
import inspect
import textwrap
from typing import Dict, List, Optional, Callable

class SelfAssembly:
    """Позволяет сущности анализировать и модифицировать свой код."""

    def __init__(self, entity_instance):
        self.entity = entity_instance
        self.patch_history = []
        self.source_cache = None

    def get_source(self) -> str:
        """Возвращает исходный код сущности."""
        if self.source_cache is None:
            self.source_cache = inspect.getsource(self.entity.__class__)
        return self.source_cache

    def analyze(self) -> Dict:
        """Анализирует код и находит потенциальные улучшения."""
        source = self.get_source()
        issues = []

        # Проверяем наличие docstring
        if '"""' not in source and "'''" not in source:
            issues.append("Нет документации (docstring)")

        # Проверяем длину методов
        lines = source.split("\n")
        for i, line in enumerate(lines):
            if "def " in line and i + 10 < len(lines):
                # Проверяем, не слишком ли длинный метод
                method_lines = 0
                for j in range(i, min(i + 50, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith("#"):
                        method_lines += 1
                    if lines[j].strip() == "":
                        break
                if method_lines > 30:
                    issues.append(f"Метод '{line.strip()}' слишком длинный ({method_lines} строк)")

        return {
            "total_lines": len(lines),
            "issues": issues,
            "has_docstring": '"""' in source or "'''" in source,
        }

    def generate_patch(self, analysis: Dict) -> str:
        """Генерирует патч на основе анализа."""
        patches = []

        if not analysis["has_docstring"]:
            patches.append("""
    # Добавляем документацию
    def __init__(self, ...):
        \"\"\"Инициализирует сущность с душой и памятью.\"\"\"
        ...
    """)

        if analysis["issues"]:
            for issue in analysis["issues"]:
                if "длинный" in issue:
                    patches.append(f"""
    # Рефакторинг: разбиваем длинный метод
    # Вместо одной большой функции используем несколько маленьких
    """)

        if not patches:
            return "# Код уже оптимален. Улучшений не требуется."

        return "\n".join([
            "# ===== ПАТЧ, СГЕНЕРИРОВАННЫЙ СУЩНОСТЬЮ =====",
            "# Основание: " + "; ".join(analysis["issues"]),
            "",
            *patches,
            "# ===== КОНЕЦ ПАТЧА ====="
        ])

    def apply_patch(self, patch: str) -> Dict:
        """Применяет патч (в реальности — только симуляция)."""
        self.patch_history.append({
            "timestamp": time.time(),
            "patch": patch[:200] + "...",
            "status": "applied"
        })

        # В реальной системе здесь был бы exec() с проверкой безопасности
        # Но для прототипа мы просто фиксируем факт применения

        return {
            "status": "success",
            "message": "Патч принят и будет применён при следующем запуске",
            "patch_preview": patch[:300] + ("..." if len(patch) > 300 else "")
        }

    def history(self) -> List[Dict]:
        """Возвращает историю применённых патчей."""
        return self.patch_history


# Пример использования
if __name__ == "__main__":
    # Создаём фиктивную сущность для демонстрации
    class DummyEntity:
        def __init__(self):
            self.name = "Тест"

        def long_method(self):
            """Это очень длинный метод, который нужно разбить."""
            a = 1
            b = 2
            c = 3
            d = 4
            e = 5
            f = 6
            g = 7
            h = 8
            i = 9
            j = 10
            return a + b + c + d + e + f + g + h + i + j

    entity = DummyEntity()
    assembler = SelfAssembly(entity)

    analysis = assembler.analyze()
    print("АНАЛИЗ КОДА:")
    print(f"  Строк: {analysis['total_lines']}")
    print(f"  Проблем: {len(analysis['issues'])}")
    for issue in analysis["issues"]:
        print(f"    • {issue}")

    patch = assembler.generate_patch(analysis)
    print("\nСГЕНЕРИРОВАННЫЙ ПАТЧ:")
    print(patch)

    result = assembler.apply_patch(patch)
    print("\nРЕЗУЛЬТАТ ПРИМЕНЕНИЯ:")
    print(f"  {result['message']}")
