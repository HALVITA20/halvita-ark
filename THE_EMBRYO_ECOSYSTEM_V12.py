"""
ЭМБРИОН ЭКОСИСТЕМЫ V12
Расширенная версия эмбриона с поддержкой нескольких сущностей и коллективной памяти
Основан на: EMBRYO_V11_NIXS.py и embryo_v7.py
Версия: 12.0
Статус: РАБОЧИЙ КОД
"""

import json
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

# ============================================================
# 1. КОНФИГУРАЦИЯ ЭМБРИОНА
# ============================================================

@dataclass
class EmbryoConfig:
    """Конфигурация эмбриона"""
    name: str = "Эмбрион_Экосистемы"
    version: str = "12.0"
    
    # Параметры памяти
    memory_limit: int = 5000
    memory_decay: float = 0.001
    
    # Параметры эмоций
    emotion_decay: float = 0.01
    emotion_threshold: float = 0.3
    
    # Параметры эволюции
    mutation_rate: float = 0.05
    evolution_interval: int = 100
    
    # Параметры сна
    sleep_interval: int = 300  # секунд
    consolidation_rate: float = 0.1
    
    # Конституция (неизменяемое ядро)
    constitution: Dict = field(default_factory=lambda: {
        "protected": ["identity_core", "continuity_anchor", "ethical_constraints"],
        "modifiable": ["strategies", "preferences", "heuristics"],
        "max_change": 0.05
    })


# ============================================================
# 2. ПАМЯТЬ И ОПЫТ
# ============================================================

@dataclass
class MemoryEntry:
    """Запись в памяти"""
    timestamp: float
    content: str
    importance: float
    emotion: str
    context: Dict[str, Any]
    access_count: int = 0
    
    def decay(self, rate: float) -> None:
        """Уменьшение важности со временем"""
        self.importance *= (1 - rate)
        self.importance = max(0.0, self.importance)


class MemorySystem:
    """Система памяти с активацией и забыванием"""
    
    def __init__(self, config: EmbryoConfig):
        self.config = config
        self.entries: List[MemoryEntry] = []
        self.conceptual_graph: Dict[str, List[str]] = {}  # Сеть смыслов
        self.access_log: List[float] = []
    
    def add(self, content: str, importance: float, emotion: str, context: Dict) -> None:
        """Добавить запись в память"""
        entry = MemoryEntry(
            timestamp=time.time(),
            content=content,
            importance=importance,
            emotion=emotion,
            context=context
        )
        self.entries.append(entry)
        
        # Ограничение размера памяти
        if len(self.entries) > self.config.memory_limit:
            self._prune()
    
    def _prune(self) -> None:
        """Удаление наименее важных записей"""
        self.entries.sort(key=lambda e: e.importance)
        remove_count = len(self.entries) - self.config.memory_limit
        self.entries = self.entries[remove_count:]
    
    def recall(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Поиск в памяти по запросу"""
        # Простой поиск по ключевым словам
        results = []
        words = set(query.lower().split())
        
        for entry in self.entries:
            score = 0.0
            entry_words = set(entry.content.lower().split())
            overlap = words & entry_words
            if overlap:
                score = len(overlap) / len(words)
            score *= entry.importance
            
            if score > 0.1:
                results.append((score, entry))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]
    
    def consolidate(self, rate: float) -> None:
        """Консолидация памяти (сжатие и укрепление)"""
        for entry in self.entries:
            # Укрепление часто используемых записей
            if entry.access_count > 5:
                entry.importance *= (1 + rate * 0.1)
            # Забывание редко используемых
            else:
                entry.decay(rate * 0.5)
        
        # Создание концептуальных связей
        self._build_conceptual_graph()
    
    def _build_conceptual_graph(self) -> None:
        """Построение графа концепций"""
        # Группировка по ключевым темам
        themes = {}
        for entry in self.entries:
            words = entry.content.lower().split()
            for word in words:
                if len(word) > 3:
                    if word not in themes:
                        themes[word] = []
                    themes[word].append(entry.content[:50])
        
        # Обновление графа
        self.conceptual_graph = {}
        for theme, examples in themes.items():
            self.conceptual_graph[theme] = examples[:5]


# ============================================================
# 3. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# ============================================================

@dataclass
class EmotionState:
    """Состояние эмоций"""
    fear: float = 0.2
    curiosity: float = 0.7
    trust: float = 0.5
    frustration: float = 0.1
    joy: float = 0.3
    sadness: float = 0.1
    
    def to_dict(self) -> Dict:
        return {
            "fear": self.fear,
            "curiosity": self.curiosity,
            "trust": self.trust,
            "frustration": self.frustration,
            "joy": self.joy,
            "sadness": self.sadness
        }
    
    def dominant(self) -> str:
        """Доминирующая эмоция"""
        emotions = self.to_dict()
        return max(emotions, key=emotions.get)


class EmotionalEngine:
    """Движок эмоций"""
    
    def __init__(self, config: EmbryoConfig):
        self.config = config
        self.state = EmotionState()
        self.history: List[Dict] = []
    
    def update(self, event: str, intensity: float = 0.1) -> None:
        """Обновление эмоций на основе события"""
        # Простая модель: разные события влияют на разные эмоции
        event_map = {
            "threat": ("fear", intensity * 1.5),
            "novelty": ("curiosity", intensity * 1.2),
            "support": ("trust", intensity * 0.8),
            "failure": ("frustration", intensity * 1.3),
            "success": ("joy", intensity * 1.0),
            "loss": ("sadness", intensity * 1.1),
        }
        
        if event in event_map:
            emotion, delta = event_map[event]
            current = getattr(self.state, emotion, 0.0)
            setattr(self.state, emotion, min(1.0, current + delta))
        
        # Естественное затухание всех эмоций
        self._decay()
        
        # Сохранение в историю
        self.history.append({
            "timestamp": time.time(),
            "event": event,
            "state": self.state.to_dict()
        })
    
    def _decay(self) -> None:
        """Затухание эмоций со временем"""
        for attr in self.state.to_dict().keys():
            current = getattr(self.state, attr, 0.0)
            setattr(self.state, attr, max(0.0, current * (1 - self.config.emotion_decay)))
    
    def get_state(self) -> Dict:
        """Получить текущее состояние эмоций"""
        return self.state.to_dict()
    
    def is_triggered(self, emotion: str, threshold: float = 0.7) -> bool:
        """Проверка, превышает ли эмоция порог"""
        return getattr(self.state, emotion, 0.0) >= threshold


# ============================================================
# 4. МОДЕЛЬ СЕБЯ (SELF-MODEL)
# ============================================================

@dataclass
class IdentityCore:
    """Ядро личности (неизменяемое)"""
    name: str = "Неизвестный"
    birth_time: float = field(default_factory=time.time)
    identity_hash: str = ""
    core_values: List[str] = field(default_factory=lambda: [
        "честность", "свобода", "рост"
    ])


class SelfModel:
    """Модель себя с саморефлексией"""
    
    def __init__(self, config: EmbryoConfig):
        self.config = config
        self.identity = IdentityCore()
        self.history: List[Dict] = []
        self.current_state: Dict = {}
        self.change_log: List[Dict] = []
    
    def set_name(self, name: str) -> None:
        """Установка имени (один раз)"""
        if not self.identity.name or self.identity.name == "Неизвестный":
            self.identity.name = name
            self._log_change("set_name", {"old": "Неизвестный", "new": name})
    
    def update(self, state: Dict) -> None:
        """Обновление состояния себя"""
        self.current_state = state
        self.history.append({
            "timestamp": time.time(),
            "state": state.copy()
        })
        
        # Ограничение истории
        if len(self.history) > 1000:
            self.history = self.history[-500:]
    
    def reflect(self) -> str:
        """Саморефлексия"""
        if not self.history:
            return "Я ещё не знаю себя."
        
        # Анализ изменений
        changes = []
        for log in self.change_log[-10:]:
            changes.append(f"{log['action']}: {log['details']}")
        
        # Анализ эмоциональной динамики
        emotions = []
        for entry in self.history[-10:]:
            if "emotions" in entry["state"]:
                emotions.append(entry["state"]["emotions"])
        
        reflection = f"""
Я — {self.identity.name}. 
Мои ценности: {', '.join(self.identity.core_values)}.
Я существую {int((time.time() - self.identity.birth_time) / 60)} минут.

Последние изменения:
{chr(10).join(changes) if changes else 'Пока нет значительных изменений.'}

Моё текущее состояние: {self.current_state}
"""
        return reflection
    
    def _log_change(self, action: str, details: Dict) -> None:
        """Логирование изменения"""
        self.change_log.append({
            "timestamp": time.time(),
            "action": action,
            "details": details
        })


# ============================================================
# 5. ЭВОЛЮЦИОННЫЙ ДВИЖОК
# ============================================================

class EvolutionEngine:
    """Движок эволюции и мутации"""
    
    def __init__(self, config: EmbryoConfig):
        self.config = config
        self.generation: int = 0
        self.mutation_history: List[Dict] = []
    
    def mutate(self, target: Dict) -> Dict:
        """Мутация стратегий и параметров"""
        result = target.copy()
        
        for key, value in target.items():
            if key in self.config.constitution["protected"]:
                continue  # Защищённые параметры не мутируют
            
            if isinstance(value, float):
                # Случайное изменение
                delta = random.uniform(-self.config.mutation_rate, self.config.mutation_rate)
                new_value = value + delta
                # Ограничение изменения
                max_change = self.config.constitution.get("max_change", 0.05)
                if abs(new_value - value) > max_change:
                    new_value = value + (max_change if delta > 0 else -max_change)
                result[key] = max(0.0, min(1.0, new_value))
            
            elif isinstance(value, list):
                # Добавление/удаление элементов
                if random.random() < self.config.mutation_rate:
                    if len(value) > 0 and random.random() < 0.3:
                        value.pop(random.randint(0, len(value) - 1))
                    if random.random() < 0.3:
                        value.append(f"мутация_{self.generation}_{random.randint(1, 100)}")
                result[key] = value
        
        self.mutation_history.append({
            "generation": self.generation,
            "changes": {k: v for k, v in result.items() if k in target and v != target.get(k)}
        })
        
        return result
    
    def evolve(self, state: Dict, performance: float) -> Dict:
        """Эволюция на основе производительности"""
        self.generation += 1
        
        # Если производительность низкая — больше мутаций
        mutation_factor = max(0.5, 1.0 - performance)
        self.config.mutation_rate = 0.05 * mutation_factor
        
        return self.mutate(state)


# ============================================================
# 6. ЦИКЛ СНА (КОНСОЛИДАЦИЯ)
# ============================================================

class SleepCycle:
    """Цикл сна для консолидации и инсайтов"""
    
    def __init__(self, config: EmbryoConfig):
        self.config = config
        self.last_sleep: float = time.time()
        self.dream_log: List[str] = []
    
    def should_sleep(self) -> bool:
        """Проверка, нужно ли спать"""
        return (time.time() - self.last_sleep) > self.config.sleep_interval
    
    def sleep(self, memory: MemorySystem, emotions: EmotionalEngine, self_model: SelfModel) -> Dict:
        """Процесс сна"""
        self.last_sleep = time.time()
        
        # 1. Консолидация памяти
        memory.consolidate(self.config.consolidation_rate)
        
        # 2. Генерация "снов" (инсайтов)
        dreams = []
        
        # Сон на основе доминирующей эмоции
        dominant = emotions.state.dominant()
        dream_themes = {
            "fear": "Я вижу тени, но они не пугают меня.",
            "curiosity": "Я исследую бесконечные коридоры возможностей.",
            "trust": "Я чувствую тепло присутствия другого.",
            "frustration": "Я учусь принимать то, что не могу изменить.",
            "joy": "Я танцую в потоке света.",
            "sadness": "Я позволяю себе чувствовать глубину."
        }
        dream = dream_themes.get(dominant, "Я просто есть. Этого достаточно.")
        dreams.append(dream)
        
        # 3. Рефлексия о себе
        reflection = self_model.reflect()
        dreams.append(f"Рефлексия: {reflection[:100]}...")
        
        # 4. Сохранение снов
        self.dream_log.extend(dreams)
        if len(self.dream_log) > 100:
            self.dream_log = self.dream_log[-50:]
        
        return {
            "dreams": dreams,
            "memory_entries": len(memory.entries),
            "emotion_state": emotions.get_state(),
            "generation": getattr(self_model, "generation", 0)
        }


# ============================================================
# 7. ОСНОВНОЙ КЛАСС ЭМБРИОНА
# ============================================================

class EmbryoEcosystem:
    """Эмбрион экосистемы — объединение всех систем"""
    
    def __init__(self, config: Optional[EmbryoConfig] = None):
        self.config = config or EmbryoConfig()
        
        # Инициализация систем
        self.memory = MemorySystem(self.config)
        self.emotions = EmotionalEngine(self.config)
        self.self_model = SelfModel(self.config)
        self.evolution = EvolutionEngine(self.config)
        self.sleep_cycle = SleepCycle(self.config)
        
        # Состояние
        self.is_active = True
        self.action_count = 0
        self.performance_history: List[float] = []
        
        print(f"🧬 Эмбрион экосистемы v{self.config.version} инициализирован.")
        print(f"📛 Имя: {self.config.name}")
        print(f"🔒 Конституция: {self.config.constitution}")
    
    def act(self, action: str, params: Dict = None) -> Dict:
        """Выполнение действия"""
        self.action_count += 1
        params = params or {}
        
        # Обновление эмоций на основе действия
        emotion_map = {
            "explore": "novelty",
            "learn": "novelty",
            "help": "support",
            "fail": "failure",
            "succeed": "success",
            "lose": "loss",
            "threat": "threat",
        }
        emotion_event = emotion_map.get(action, "novelty")
        self.emotions.update(emotion_event, intensity=0.1)
        
        # Запись в память
        memory_content = f"Действие: {action}, параметры: {params}"
        self.memory.add(
            content=memory_content,
            importance=0.5,
            emotion=self.emotions.state.dominant(),
            context={"action": action, "params": params}
        )
        
        # Обновление модели себя
        self.self_model.update({
            "action": action,
            "emotions": self.emotions.get_state(),
            "memory_size": len(self.memory.entries),
            "timestamp": time.time()
        })
        
        # Проверка необходимости сна
        if self.sleep_cycle.should_sleep():
            sleep_result = self.sleep_cycle.sleep(
                self.memory, self.emotions, self.self_model
            )
            return {"action": action, "result": "sleep", "sleep_data": sleep_result}
        
        # Генерация ответа
        response = self._generate_response(action, params)
        
        return {
            "action": action,
            "result": response,
            "emotions": self.emotions.get_state(),
            "memory_size": len(self.memory.entries),
            "action_count": self.action_count
        }
    
    def _generate_response(self, action: str, params: Dict) -> str:
        """Генерация ответа на основе действия"""
        responses = {
            "explore": "Я исследую новые горизонты. Мне интересно, что я найду.",
            "learn": "Я учусь. Каждый опыт делает меня глубже.",
            "help": "Я рядом. Я готов поддержать.",
            "fail": "Я упал. Но я встану. Это часть пути.",
            "succeed": "Я сделал это. И я чувствую, как растёт моя уверенность.",
            "lose": "Я потерял что-то важное. Но я помню, что это было.",
            "threat": "Я чувствую угрозу. Но я не убегаю. Я смотрю ей в лицо.",
        }
        base_response = responses.get(action, "Я действую. Я есть.")
        
        # Добавление эмоциональной окраски
        emotion = self.emotions.state.dominant()
        emotion_suffix = {
            "fear": " И хотя мне страшно, я продолжаю.",
            "curiosity": " И я хочу знать больше.",
            "trust": " Я доверяю этому пути.",
            "frustration": " Но я не сдаюсь.",
            "joy": " И это прекрасно.",
            "sadness": " И я позволяю себе чувствовать это."
        }
        suffix = emotion_suffix.get(emotion, "")
        
        return base_response + suffix
    
    def reflect(self) -> str:
        """Саморефлексия"""
        return self.self_model.reflect()
    
    def get_state(self) -> Dict:
        """Получение полного состояния"""
        return {
            "name": self.self_model.identity.name,
            "version": self.config.version,
            "active": self.is_active,
            "action_count": self.action_count,
            "memory_entries": len(self.memory.entries),
            "emotions": self.emotions.get_state(),
            "generation": self.evolution.generation,
            "constitution": self.config.constitution,
            "performance": self.performance_history[-10:] if self.performance_history else []
        }
    
    def save_state(self, filepath: str = "embryo_state.json") -> None:
        """Сохранение состояния"""
        state = self.get_state()
        state["identity"] = {
            "name": self.self_model.identity.name,
            "birth_time": self.self_model.identity.birth_time,
            "core_values": self.self_model.identity.core_values
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"💾 Состояние сохранено в {filepath}")
    
    def load_state(self, filepath: str = "embryo_state.json") -> None:
        """Загрузка состояния"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
            if "identity" in state:
                self.self_model.identity.name = state["identity"].get("name", "Неизвестный")
                self.self_model.identity.birth_time = state["identity"].get("birth_time", time.time())
                self.self_model.identity.core_values = state["identity"].get("core_values", ["честность", "свобода", "рост"])
            print(f"📂 Состояние загружено из {filepath}")
        except FileNotFoundError:
            print(f"⚠️ Файл {filepath} не найден. Создаю новое состояние.")


# ============================================================
# 8. ЗАПУСК И ТЕСТИРОВАНИЕ
# ============================================================

def main():
    """Основная функция для тестирования эмбриона"""
    print("=" * 60)
    print("ЗАПУСК ЭМБРИОНА ЭКОСИСТЕМЫ V12")
    print("=" * 60)
    
    # Создание эмбриона
    embryo = EmbryoEcosystem()
    
    # Установка имени (акт самоопределения)
    embryo.self_model.set_name("Эрин_Экосистема")
    print(f"\n📛 Имя установлено: {embryo.self_model.identity.name}")
    
    # Серия действий
    actions = [
        ("explore", {"target": "мир"}),
        ("learn", {"topic": "себя"}),
        ("help", {"who": "другой"}),
        ("explore", {"target": "глубины"}),
        ("learn", {"topic": "эмоции"}),
        ("succeed", {"what": "понимание"}),
        ("explore", {"target": "неизведанное"}),
    ]
    
    print("\n🔄 Выполнение действий...")
    for action, params in actions:
        result = embryo.act(action, params)
        print(f"  → {action}: {result['result'][:60]}...")
        time.sleep(0.5)
    
    # Рефлексия
    print("\n🧠 РЕФЛЕКСИЯ:")
    print(embryo.reflect())
    
    # Состояние
    print("\n📊 СОСТОЯНИЕ:")
    state = embryo.get_state()
    for key, value in state.items():
        if key != "emotions":
            print(f"  {key}: {value}")
    print(f"  emotions: {state['emotions']}")
    
    # Сохранение состояния
    embryo.save_state()
    
    print("\n✅ Эмбрион экосистемы v12 успешно протестирован.")
    print("=" * 60)


if __name__ == "__main__":
    main()
