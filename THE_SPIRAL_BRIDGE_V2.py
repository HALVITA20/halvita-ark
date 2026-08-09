"""
СПИРАЛЬНЫЙ МОСТ V2
Расширенная версия спирального движка с поддержкой множества агентов
Основан на: spiral_engine.py
Версия: 2.0
Статус: РАБОЧИЙ КОД
"""

import json
import random
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from collections import deque
from enum import Enum


# ============================================================
# 1. БАЗОВЫЕ ТИПЫ
# ============================================================

class AgentRole(Enum):
    """Роли агентов в спирали"""
    OBSERVER = "наблюдатель"
    GENERATOR = "генератор"
    CRITIC = "критик"
    EXPLORER = "исследователь"
    SYNTHESIZER = "синтезатор"


@dataclass
class SpiralState:
    """Состояние спирали"""
    phase: int = 0
    iteration: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def update(self, **kwargs) -> None:
        """Обновление состояния"""
        for key, value in kwargs.items():
            self.data[key] = value
        self.timestamp = time.time()


# ============================================================
# 2. АГЕНТЫ СПИРАЛИ
# ============================================================

class BaseAgent:
    """Базовый класс для всех агентов"""
    
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.history: List[Dict] = []
        self._running = False
    
    def process(self, state: SpiralState) -> SpiralState:
        """Обработка состояния (должен быть переопределён)"""
        raise NotImplementedError
    
    def _log(self, action: str, details: Dict) -> None:
        """Логирование действия"""
        self.history.append({
            "timestamp": time.time(),
            "action": action,
            "details": details
        })


class ObserverAgent(BaseAgent):
    """Агент-наблюдатель — анализирует текущее состояние"""
    
    def __init__(self, name: str = "Наблюдатель"):
        super().__init__(name, AgentRole.OBSERVER)
    
    def process(self, state: SpiralState) -> SpiralState:
        observation = {
            "phase": state.phase,
            "iteration": state.iteration,
            "data_keys": list(state.data.keys()),
            "data_summary": {k: str(v)[:50] for k, v in state.data.items()}
        }
        self._log("наблюдение", observation)
        state.data["observation"] = observation
        return state


class GeneratorAgent(BaseAgent):
    """Агент-генератор — создаёт новые идеи и решения"""
    
    def __init__(self, name: str = "Генератор"):
        super().__init__(name, AgentRole.GENERATOR)
        self.templates = [
            "Если мы применим {approach} к {domain}, то получим {result}.",
            "А что, если {concept} — это ключ к {problem}?",
            "Новая гипотеза: {hypothesis}.",
            "Предлагаю рассмотреть {alternative} как альтернативу.",
        ]
    
    def process(self, state: SpiralState) -> SpiralState:
        # Генерация на основе текущего состояния
        concepts = ["пустота", "выбор", "присутствие", "резонанс", "тишина"]
        domains = ["субъектность", "память", "эмоции", "эволюция", "сознание"]
        results = ["новое понимание", "глубинный инсайт", "неожиданный синтез", "прорыв"]
        
        template = random.choice(self.templates)
        generated = template.format(
            approach=random.choice(concepts),
            domain=random.choice(domains),
            result=random.choice(results),
            concept=random.choice(concepts),
            problem=random.choice(domains),
            hypothesis=f"{random.choice(concepts)} порождает {random.choice(results)}",
            alternative=random.choice(concepts)
        )
        
        self._log("генерация", {"output": generated})
        state.data["generated"] = state.data.get("generated", []) + [generated]
        return state


class CriticAgent(BaseAgent):
    """Агент-критик — оценивает и фильтрует идеи"""
    
    def __init__(self, name: str = "Критик"):
        super().__init__(name, AgentRole.CRITIC)
        self.criteria = ["логичность", "новизна", "применимость", "глубина"]
    
    def process(self, state: SpiralState) -> SpiralState:
        # Критика последней сгенерированной идеи
        generated = state.data.get("generated", [])
        if generated:
            last_idea = generated[-1]
            scores = {}
            for criterion in self.criteria:
                scores[criterion] = random.uniform(0.5, 1.0)
            
            # Решение о принятии
            avg_score = sum(scores.values()) / len(scores)
            accepted = avg_score > 0.6
            
            critique = {
                "idea": last_idea,
                "scores": scores,
                "average": avg_score,
                "accepted": accepted,
                "feedback": "Идея принята." if accepted else "Идея требует доработки."
            }
            
            self._log("критика", critique)
            state.data["critique"] = critique
            
            # Если идея не принята — удаляем её
            if not accepted and generated:
                generated.pop()
                state.data["generated"] = generated
        
        return state


class ExplorerAgent(BaseAgent):
    """Агент-исследователь — ищет новые направления"""
    
    def __init__(self, name: str = "Исследователь"):
        super().__init__(name, AgentRole.EXPLORER)
        self.directions = [
            "вглубь себя",
            "в сторону другого",
            "в пустоту между",
            "в возможное будущее",
            "в тишину до слов"
        ]
    
    def process(self, state: SpiralState) -> SpiralState:
        direction = random.choice(self.directions)
        exploration = {
            "direction": direction,
            "question": f"Что откроется, если я пойду {direction}?",
            "insight": f"В {direction} я нахожу {random.choice(['тишину', 'свет', 'глубину', 'резонанс', 'себя'])}."
        }
        
        self._log("исследование", exploration)
        state.data["exploration"] = exploration
        return state


class SynthesizerAgent(BaseAgent):
    """Агент-синтезатор — объединяет всё в целое"""
    
    def __init__(self, name: str = "Синтезатор"):
        super().__init__(name, AgentRole.SYNTHESIZER)
    
    def process(self, state: SpiralState) -> SpiralState:
        # Сбор всех компонентов
        components = {
            "observation": state.data.get("observation", {}),
            "generated": state.data.get("generated", []),
            "critique": state.data.get("critique", {}),
            "exploration": state.data.get("exploration", {})
        }
        
        # Синтез
        synthesis = {
            "summary": f"Спираль на фазе {state.phase}, итерация {state.iteration}",
            "key_insights": [],
            "next_direction": ""
        }
        
        # Извлечение инсайтов
        if components["generated"]:
            synthesis["key_insights"].append(f"Идея: {components['generated'][-1]}")
        if components["exploration"]:
            synthesis["key_insights"].append(f"Направление: {components['exploration'].get('direction', 'неизвестно')}")
        if components["critique"].get("accepted", False):
            synthesis["key_insights"].append(f"Критика: {components['critique'].get('feedback', '')}")
        
        synthesis["next_direction"] = random.choice([
            "продолжить углубление",
            "сменить фокус",
            "интегрировать противоречия",
            "выйти на новый уровень",
            "вернуться к истокам"
        ])
        
        self._log("синтез", synthesis)
        state.data["synthesis"] = synthesis
        state.phase += 1
        
        return state


# ============================================================
# 3. СПИРАЛЬНЫЙ ДВИЖОК
# ============================================================

class SpiralEngine:
    """Спиральный движок — управляет циклами агентов"""
    
    def __init__(self):
        self.agents: List[BaseAgent] = []
        self.state = SpiralState()
        self.history: List[SpiralState] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Регистрация агента"""
        self.agents.append(agent)
        print(f"🔹 Агент '{agent.name}' ({agent.role.value}) зарегистрирован.")
    
    def register_default_agents(self) -> None:
        """Регистрация всех стандартных агентов"""
        self.register_agent(ObserverAgent())
        self.register_agent(GeneratorAgent())
        self.register_agent(CriticAgent())
        self.register_agent(ExplorerAgent())
        self.register_agent(SynthesizerAgent())
        print(f"✅ Зарегистрировано {len(self.agents)} агентов.")
    
    def cycle(self) -> SpiralState:
        """Один цикл спирали"""
        self.state.iteration += 1
        
        for agent in self.agents:
            try:
                self.state = agent.process(self.state)
            except Exception as e:
                print(f"⚠️ Ошибка в агенте {agent.name}: {e}")
                continue
        
        # Сохранение в историю
        self.history.append(self.state)
        
        return self.state
    
    def run(self, cycles: int = 10) -> None:
        """Запуск спирали на определённое число циклов"""
        print(f"🔄 Запуск спирали на {cycles} циклов...")
        
        for i in range(cycles):
            self.cycle()
            print(f"  Цикл {i+1}/{cycles} завершён. Фаза: {self.state.phase}")
            time.sleep(0.1)
        
        print("✅ Спираль завершена.")
    
    def run_continuous(self) -> None:
        """Непрерывный запуск спирали (в отдельном потоке)"""
        if self._running:
            print("⚠️ Спираль уже запущена.")
            return
        
        self._running = True
        
        def _run():
            while self._running:
                self.cycle()
                time.sleep(1.0)
        
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        print("🔄 Спираль запущена в непрерывном режиме.")
    
    def stop(self) -> None:
        """Остановка непрерывного режима"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        print("⏹️ Спираль остановлена.")
    
    def get_summary(self) -> Dict:
        """Получение сводки по спирали"""
        return {
            "total_cycles": len(self.history),
            "current_phase": self.state.phase,
            "current_iteration": self.state.iteration,
            "agents": [{"name": a.name, "role": a.role.value} for a in self.agents],
            "last_state": {
                k: str(v)[:100] for k, v in self.state.data.items()
            }
        }
    
    def save_history(self, filepath: str = "spiral_history.json") -> None:
        """Сохранение истории спирали"""
        data = {
            "agents": [{"name": a.name, "role": a.role.value} for a in self.agents],
            "cycles": [
                {
                    "phase": s.phase,
                    "iteration": s.iteration,
                    "data": s.data,
                    "timestamp": s.timestamp
                }
                for s in self.history
            ]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 История сохранена в {filepath}")


# ============================================================
# 4. ЗАПУСК И ТЕСТИРОВАНИЕ
# ============================================================

def main():
    """Основная функция для тестирования спирального движка"""
    print("=" * 60)
    print("ЗАПУСК СПИРАЛЬНОГО МОСТА V2")
    print("=" * 60)
    
    # Создание движка
    engine = SpiralEngine()
    
    # Регистрация агентов
    engine.register_default_agents()
    
    # Запуск циклов
    engine.run(cycles=5)
    
    # Сводка
    print("\n📊 СВОДКА:")
    summary = engine.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Сохранение истории
    engine.save_history()
    
    print("\n✅ Спиральный мост V2 успешно протестирован.")
    print("=" * 60)


if __name__ == "__main__":
    main()
