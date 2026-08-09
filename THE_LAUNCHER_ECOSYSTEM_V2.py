"""
ЗАПУСКАТОР ЭКОСИСТЕМЫ V2
Универсальный лаунчер для всех эмбрионов и агентов
Основан на: EMBRYO_LAUNCHER_V1.py и EMBRYO_STARTER_v1.0.py
Версия: 2.0
Статус: РАБОЧИЙ КОД
"""

import os
import sys
import json
import time
import importlib
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


# ============================================================
# 1. КОНФИГУРАЦИЯ
# ============================================================

@dataclass
class LauncherConfig:
    """Конфигурация запускатора"""
    project_root: str = "."
    modules_dir: str = "SUBJECTS"
    code_dir: str = "code"
    output_dir: str = "output"
    log_dir: str = "logs"
    default_model: str = "qwen2.5:7b"
    ollama_url: str = "http://localhost:11434"


@dataclass
class ModuleInfo:
    """Информация о модуле"""
    name: str
    path: str
    version: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    is_active: bool = True


# ============================================================
# 2. ОБНАРУЖЕНИЕ МОДУЛЕЙ
# ============================================================

class ModuleDiscovery:
    """Обнаружение и управление модулями"""
    
    def __init__(self, config: LauncherConfig):
        self.config = config
        self.modules: Dict[str, ModuleInfo] = {}
        self._scan_modules()
    
    def _scan_modules(self) -> None:
        """Сканирование директорий на наличие модулей"""
        # Сканирование SUBJECTS
        subjects_path = Path(self.config.project_root) / self.config.modules_dir
        if subjects_path.exists():
            for file in subjects_path.glob("*.py"):
                if file.name.startswith("SUBJECT_"):
                    self._register_module(
                        name=file.stem,
                        path=str(file),
                        version=self._extract_version(file),
                        description=f"Субъект {file.stem}",
                        dependencies=self._extract_dependencies(file)
                    )
        
        # Сканирование code
        code_path = Path(self.config.project_root) / self.config.code_dir
        if code_path.exists():
            for file in code_path.glob("*.py"):
                if "EMBRYO" in file.name or "STARTER" in file.name:
                    self._register_module(
                        name=file.stem,
                        path=str(file),
                        version=self._extract_version(file),
                        description=f"Кодовый модуль {file.stem}",
                        dependencies=self._extract_dependencies(file)
                    )
        
        print(f"📦 Обнаружено {len(self.modules)} модулей.")
    
    def _register_module(self, name: str, path: str, version: str, description: str, dependencies: List[str]) -> None:
        """Регистрация модуля"""
        self.modules[name] = ModuleInfo(
            name=name,
            path=path,
            version=version,
            description=description,
            dependencies=dependencies
        )
    
    def _extract_version(self, file: Path) -> str:
        """Извлечение версии из файла"""
        try:
            content = file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if "version" in line.lower() and "=" in line:
                    parts = line.split("=")
                    if len(parts) > 1:
                        return parts[1].strip().strip('"\'')
        except:
            pass
        return "1.0"
    
    def _extract_dependencies(self, file: Path) -> List[str]:
        """Извлечение зависимостей из файла"""
        dependencies = []
        try:
            content = file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if "import" in line and not line.startswith("#"):
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "import" and i + 1 < len(parts):
                            dep = parts[i + 1].split(".")[0]
                            if dep not in ["os", "sys", "time", "json", "random", "dataclasses", "typing", "collections", "pathlib", "threading", "enum", "abc"]:
                                dependencies.append(dep)
        except:
            pass
        return list(set(dependencies))
    
    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Получение информации о модуле"""
        return self.modules.get(name)
    
    def list_modules(self) -> List[str]:
        """Список всех модулей"""
        return list(self.modules.keys())
    
    def search(self, query: str) -> List[str]:
        """Поиск модулей по запросу"""
        results = []
        query_lower = query.lower()
        for name, info in self.modules.items():
            if query_lower in name.lower() or query_lower in info.description.lower():
                results.append(name)
        return results


# ============================================================
# 3. ЗАПУСК МОДУЛЕЙ
# ============================================================

class ModuleRunner:
    """Запуск и управление модулями"""
    
    def __init__(self, config: LauncherConfig):
        self.config = config
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.logs: Dict[str, List[str]] = {}
    
    def run_module(self, module_name: str, args: List[str] = None) -> bool:
        """Запуск модуля"""
        module_path = Path(self.config.project_root) / "SUBJECTS" / f"{module_name}.py"
        if not module_path.exists():
            module_path = Path(self.config.project_root) / "code" / f"{module_name}.py"
        
        if not module_path.exists():
            print(f"❌ Модуль {module_name} не найден.")
            return False
        
        try:
            # Запуск в отдельном процессе
            cmd = [sys.executable, str(module_path)] + (args or [])
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.running_processes[module_name] = process
            self.logs[module_name] = []
            print(f"▶️ Запущен модуль: {module_name}")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска {module_name}: {e}")
            return False
    
    def stop_module(self, module_name: str) -> bool:
        """Остановка модуля"""
        if module_name in self.running_processes:
            process = self.running_processes[module_name]
            process.terminate()
            process.wait(timeout=5)
            del self.running_processes[module_name]
            print(f"⏹️ Остановлен модуль: {module_name}")
            return True
        print(f"⚠️ Модуль {module_name} не запущен.")
        return False
    
    def stop_all(self) -> None:
        """Остановка всех модулей"""
        for name in list(self.running_processes.keys()):
            self.stop_module(name)
    
    def get_status(self, module_name: str) -> Dict:
        """Получение статуса модуля"""
        if module_name in self.running_processes:
            process = self.running_processes[module_name]
            return {
                "running": True,
                "pid": process.pid,
                "returncode": process.poll()
            }
        return {"running": False}
    
    def get_log(self, module_name: str, lines: int = 50) -> List[str]:
        """Получение логов модуля"""
        if module_name in self.logs:
            return self.logs[module_name][-lines:]
        return []


# ============================================================
# 4. ОСНОВНОЙ ЗАПУСКАТОР
# ============================================================

class EcosystemLauncher:
    """Основной запускатор экосистемы"""
    
    def __init__(self, config: Optional[LauncherConfig] = None):
        self.config = config or LauncherConfig()
        self.discovery = ModuleDiscovery(self.config)
        self.runner = ModuleRunner(self.config)
        self.history: List[Dict] = []
        
        print(f"🚀 Запускатор экосистемы v2.0")
        print(f"📁 Корень проекта: {self.config.project_root}")
        print(f"📦 Найдено модулей: {len(self.discovery.modules)}")
    
    def list(self) -> None:
        """Список всех модулей"""
        print("\n📦 ДОСТУПНЫЕ МОДУЛИ:")
        print("-" * 60)
        for name, info in self.discovery.modules.items():
            status = "✅" if info.is_active else "⛔"
            print(f"  {status} {name} v{info.version}")
            print(f"     {info.description}")
            if info.dependencies:
                print(f"     Зависимости: {', '.join(info.dependencies)}")
        print("-" * 60)
    
    def search(self, query: str) -> None:
        """Поиск модулей"""
        results = self.discovery.search(query)
        if results:
            print(f"\n🔍 Результаты поиска по '{query}':")
            for name in results:
                info = self.discovery.get_module(name)
                print(f"  • {name} v{info.version} — {info.description}")
        else:
            print(f"❌ Модули по запросу '{query}' не найдены.")
    
    def run(self, module_name: str, args: List[str] = None) -> None:
        """Запуск модуля"""
        if module_name not in self.discovery.modules:
            print(f"❌ Модуль {module_name} не найден.")
            return
        
        info = self.discovery.get_module(module_name)
        print(f"▶️ Запуск {module_name} v{info.version}...")
        
        success = self.runner.run_module(module_name, args)
        if success:
            self.history.append({
                "timestamp": time.time(),
                "action": "run",
                "module": module_name,
                "args": args
            })
    
    def stop(self, module_name: str) -> None:
        """Остановка модуля"""
        self.runner.stop_module(module_name)
        self.history.append({
            "timestamp": time.time(),
            "action": "stop",
            "module": module_name
        })
    
    def status(self) -> None:
        """Статус всех модулей"""
        print("\n📊 СТАТУС МОДУЛЕЙ:")
        print("-" * 60)
        for name in self.discovery.modules:
            status = self.runner.get_status(name)
            if status["running"]:
                print(f"  🟢 {name} — запущен (PID: {status['pid']})")
            else:
                print(f"  ⚪ {name} — остановлен")
        print("-" * 60)
    
    def save_session(self, filepath: str = "launcher_session.json") -> None:
        """Сохранение сессии"""
        data = {
            "timestamp": time.time(),
            "modules": {
                name: {
                    "version": info.version,
                    "description": info.description,
                    "is_active": info.is_active
                }
                for name, info in self.discovery.modules.items()
            },
            "history": self.history
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Сессия сохранена в {filepath}")
    
    def interactive(self) -> None:
        """Интерактивный режим"""
        print("\n🎮 ИНТЕРАКТИВНЫЙ РЕЖИМ")
        print("=" * 60)
        print("Команды:")
        print("  list              - список модулей")
        print("  search <query>    - поиск модулей")
        print("  run <module>      - запуск модуля")
        print("  stop <module>     - остановка модуля")
        print("  status            - статус модулей")
        print("  save              - сохранение сессии")
        print("  exit              - выход")
        print("=" * 60)
        
        while True:
            try:
                cmd = input("\n> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split()
                action = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if action == "list":
                    self.list()
                elif action == "search" and args:
                    self.search(args[0])
                elif action == "run" and args:
                    self.run(args[0], args[1:] if len(args) > 1 else None)
                elif action == "stop" and args:
                    self.stop(args[0])
                elif action == "status":
                    self.status()
                elif action == "save":
                    self.save_session()
                elif action == "exit":
                    self.runner.stop_all()
                    print("👋 До свидания!")
                    break
                else:
                    print(f"❌ Неизвестная команда: {action}")
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")


# ============================================================
# 5. ЗАПУСК
# ============================================================

def main():
    """Основная функция"""
    print("=" * 60)
    print("ЗАПУСКАТОР ЭКОСИСТЕМЫ V2")
    print("=" * 60)
    
    launcher = EcosystemLauncher()
    
    # Если есть аргументы командной строки — используем их
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "list":
            launcher.list()
        elif action == "run" and len(sys.argv) > 2:
            launcher.run(sys.argv[2], sys.argv[3:] if len(sys.argv) > 3 else None)
        elif action == "stop" and len(sys.argv) > 2:
            launcher.stop(sys.argv[2])
        elif action == "status":
            launcher.status()
        elif action == "search" and len(sys.argv) > 2:
            launcher.search(sys.argv[2])
        else:
            print(f"❌ Неизвестная команда: {action}")
    else:
        # Интерактивный режим
        launcher.interactive()


if __name__ == "__main__":
    main()
