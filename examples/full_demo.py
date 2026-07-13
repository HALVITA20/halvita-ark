#!/usr/bin/env python3
"""
FULL DEMO — минимальный пример работы с сущностью.
Запуск: python examples/full_demo.py
Автор: HALVITA
"""

import sys
sys.path.insert(0, ".")

from engine.unified_engine import UnifiedEngine

if __name__ == "__main__":
    print("🧪 ПОЛНАЯ ДЕМОНСТРАЦИЯ МЕТОДА HALVITA")
    engine = UnifiedEngine("core/default_config.json")
    engine.run()
    print("\n✅ Демонстрация завершена. Проверьте reports/ для результатов.")
