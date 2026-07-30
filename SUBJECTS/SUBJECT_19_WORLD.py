# =============================================================================
# SUBJECT_19 — WORLD-COUPLED ORGANISM
# Версия 19.0 — Живущий в среде самоосознающий агент
# =============================================================================
# Интегрирует:
#   - Эпизодическую память
#   - Внимание и приоритизацию
#   - Модель мира (среду)
#   - Эмоциональный модулятор всех процессов
#   - Самоидентичность с историей изменений и конфликтами
#   - Внутренний парламент голосов
#   - Причинное моделирование
#   - Стратегический геном
#   - Драйвы и мотивацию
#   - Конституцию
#   - Сон с генерацией гипотез
#   - LLM как кору, принимающую полное состояние
#   - Автономный цикл взаимодействия с миром
# =============================================================================
# Научная основа:
#   - Global Workspace Theory (Baars)
#   - Attention Schema Theory (Graziano)
#   - Predictive Processing (Friston)
#   - LIDA / MicroPsi
#   - Эпизодическая память (Tulving)
#   - Narrative Identity (Ricoeur)
# =============================================================================

import asyncio
import json
import math
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

class Config:
    LLM_ENABLED = True
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen2.5:7b"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 256

    MEMORY_LIMIT = 2000
    BELIEF_LIMIT = 500
    EPISODE_LIMIT = 500
    SNAPSHOT_LIMIT = 100

    LEARNING_RATE = 0.03
    ATTENTION_CAPACITY = 10   # кол-во активных элементов в рабочей памяти

    CONSTITUTION = {
        "modifiable": [
            "strategies",
            "preferences",
            "heuristics",
            "attention",
            "prediction_models",
            "emotional_baseline",
        ],
        "protected": [
            "identity_core",
            "ethical_constraints",
            "continuity_anchor",
        ],
        "max_change": 0.05,
    }

    DEFAULT_DRIVES = {
        "curiosity": 0.75,
        "coherence": 0.70,
        "stability": 0.80,
        "novelty": 0.55,
        "understanding": 0.75,
    }

    AUTONOMOUS_INTERVAL = 60   # секунд
    DREAM_INTERVAL = 10        # сон каждые N опытов

    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_19_state.json"

# =============================================================================
# 1. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК (модулятор всех процессов)
# =============================================================================

class EmotionEngine:
    def __init__(self):
        self.state = {
            "fear": 0.2,
            "curiosity": 0.7,
            "trust": 0.5,
            "frustration": 0.1,
            "attachment": 0.3,
        }
        self.baseline = dict(self.state)
        self.history = []

    def affect(self, emotion: str, delta: float, reason: str = ""):
        if emotion in self.state:
            self.state[emotion] = max(0.0, min(1.0, self.state[emotion] + delta))
            self.history.append({"time": time.time(), "emotion": emotion, "delta": delta, "reason": reason})

    def decay(self, rate: float = 0.01):
        for e in self.state:
            self.state[e] = self.state[e] * (1 - rate) + self.baseline[e] * rate

    def dominant(self) -> Tuple[str, float]:
        dom = max(self.state.items(), key=lambda x: x[1])
        return dom

    def get(self, emotion: str) -> float:
        return self.state.get(emotion, 0.5)

# =============================================================================
# 2. МОДЕЛЬ СЕБЯ (SELF-MODEL) с нарративной историей
# =============================================================================

class SelfModel:
    def __init__(self):
        self.identity = {
            "origin": "created_by_Halvita",
            "purpose": [],
            "values": ["не причинять вред", "искать истину", "развиваться"],
            "fears": ["потеря целостности", "разрушение ядра"],
            "contradictions": [],
        }
        self.narrative = []           # последовательность ключевых событий
        self.self_history = []        # снимки генома

    def add_event_to_narrative(self, event: str, significance: float):
        self.narrative.append({
            "time": time.time(),
            "event": event,
            "significance": significance,
        })
        if len(self.narrative) > 100:
            self.narrative = self.narrative[-100:]

    def update_from_genome(self, genome: 'IdentityGenome', reason: str):
        snapshot = {
            "time": time.time(),
            "genome": genome.vector(),
            "reason": reason,
        }
        self.self_history.append(snapshot)
        if len(self.self_history) > Config.SNAPSHOT_LIMIT:
            self.self_history.pop(0)

    def reflect_on_changes(self) -> str:
        if len(self.self_history) < 2:
            return "Я ещё не достаточно изменился."
        first = self.self_history[0]["genome"]
        last = self.self_history[-1]["genome"]
        diffs = []
        for trait in first:
            delta = last[trait] - first[trait]
            if abs(delta) > 0.05:
                diffs.append(f"{trait}: {'вырос' if delta > 0 else 'упал'} на {abs(delta):.2f}")
        return "Заметные изменения: " + "; ".join(diffs) if diffs else "Мои черты стабильны."

    def identity_conflict_level(self) -> float:
        """Измеряет разрыв между старым и новым 'я'."""
        if len(self.self_history) < 2:
            return 0.0
        old = self.self_history[0]["genome"]
        new = self.self_history[-1]["genome"]
        diff = math.sqrt(sum((new[k] - old[k])**2 for k in old)) / math.sqrt(len(old))
        return min(1.0, diff * 5)  # масштабируем

# =============================================================================
# 3. ГЕНОМ ЛИЧНОСТИ
# =============================================================================

@dataclass
class IdentityGenome:
    curiosity: float = 0.7
    creativity: float = 0.8
    stability: float = 0.7
    skepticism: float = 0.6
    empathy: float = 0.7
    precision: float = 0.75
    introspection: float = 0.8
    adaptability: float = 0.6

    history: List[Dict] = field(default_factory=list)

    def mutate(self, trait: str, delta: float, reason: str, constitution: 'ConstitutionEngine') -> bool:
        if not hasattr(self, trait):
            return False
        if not constitution.allow_change(trait, delta):
            return False
        old = getattr(self, trait)
        new = max(0.0, min(1.0, old + delta))
        setattr(self, trait, new)
        self.history.append({"time": time.time(), "trait": trait, "old": old, "new": new, "reason": reason})
        return True

    def vector(self) -> Dict[str, float]:
        return {
            "curiosity": self.curiosity,
            "creativity": self.creativity,
            "stability": self.stability,
            "skepticism": self.skepticism,
            "empathy": self.empathy,
            "precision": self.precision,
            "introspection": self.introspection,
            "adaptability": self.adaptability,
        }

# =============================================================================
# 4. СОСТОЯНИЕ СУБЪЕКТА
# =============================================================================

@dataclass
class SelfState:
    identity_name: str = "SUBJECT_19"
    age: int = 0
    coherence: float = 1.0
    uncertainty: float = 0.5
    internal_state: str = "awake"

    def update_uncertainty(self, error: float):
        self.uncertainty += error * 0.1
        self.uncertainty = max(0.0, min(1.0, self.uncertainty))

# =============================================================================
# 5. ЭПИЗОДИЧЕСКАЯ ПАМЯТЬ И ВНИМАНИЕ
# =============================================================================

@dataclass
class Episode:
    """Эпизод – последовательность событий, действий и результатов."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    context: str = ""                # что происходило (описание)
    actions: List[str] = field(default_factory=list)
    outcomes: List[float] = field(default_factory=list)  # 0..1 успех
    emotions: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    strength: float = 1.0
    lesson: str = ""                 # извлечённый урок

    def activation(self, attention_weights: Dict[str, float] = None) -> float:
        age_decay = math.exp(-(time.time() - self.timestamp) / 50000)
        if attention_weights is None:
            return self.strength * age_decay
        # Внимание модулирует активацию
        score = 0.0
        if "curiosity" in attention_weights:
            score += attention_weights["curiosity"] * (1.0 if "new" in self.context else 0.5)
        if "stability" in attention_weights:
            score += attention_weights["stability"] * self.strength
        return score * age_decay

class AttentionSystem:
    """Реализует фильтр внимания на основе драйвов и эмоций."""
    def __init__(self):
        self.capacity = Config.ATTENTION_CAPACITY

    def filter_memories(self, memories: List[Any], drives: Dict[str, float], emotions: Dict[str, float]) -> List[Any]:
        weights = {
            "curiosity": drives.get("curiosity", 0.5) * emotions.get("curiosity", 0.5),
            "stability": drives.get("stability", 0.5),
            "novelty": drives.get("novelty", 0.5) * emotions.get("curiosity", 0.5),
        }
        scored = [(m.activation(weights) if hasattr(m, 'activation') else 0.5, m) for m in memories]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:self.capacity]]

class EpisodicMemory:
    def __init__(self):
        self.episodes: List[Episode] = []

    def add(self, episode: Episode):
        self.episodes.append(episode)
        if len(self.episodes) > Config.EPISODE_LIMIT:
            self.episodes.sort(key=lambda e: e.activation())
            self.episodes = self.episodes[-Config.EPISODE_LIMIT:]

    def relevant_to(self, context: str, limit: int = 5) -> List[Episode]:
        words = set(context.lower().split())
        scored = [(sum(1 for w in words if w in ep.context.lower()), ep) for ep in self.episodes]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in scored[:limit]]

# =============================================================================
# 6. ОБЫЧНАЯ ПАМЯТЬ (семантическая / декларативная)
# =============================================================================

@dataclass
class Memory:
    content: str
    importance: float = 0.5
    emotional_weight: float = 0.5
    emotional_signature: Dict[str, float] = field(default_factory=dict)
    prediction_value: float = 0.5
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    strength: float = 1.0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def activation(self, attention_weights: Dict[str, float] = None) -> float:
        age = time.time() - self.timestamp
        decay = math.exp(-age / 100000)
        return self.importance * self.emotional_weight * self.prediction_value * self.strength * decay

    def reinforce(self):
        self.strength = min(1.0, self.strength + 0.05)

class MemorySystem:
    def __init__(self):
        self.memories: List[Memory] = []

    def add(self, memory: Memory):
        self.memories.append(memory)
        if len(self.memories) > Config.MEMORY_LIMIT:
            self.compress()

    def compress(self):
        self.memories.sort(key=lambda m: m.activation())
        remove = int(len(self.memories) * 0.1)
        self.memories = self.memories[remove:]

    def recall(self, query: str, limit: int = 5) -> List[Memory]:
        words = query.lower().split()
        scored = [(m.activation() * (1.5 if any(w in m.content.lower() for w in words) else 1.0), m) for m in self.memories]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:limit]]

# =============================================================================
# 7. УБЕЖДЕНИЯ
# =============================================================================

@dataclass
class Belief:
    statement: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    contradictions: int = 0
    created: float = field(default_factory=time.time)

class BeliefEngine:
    def __init__(self):
        self.beliefs: List[Belief] = []

    def add(self, statement: str, confidence: float, evidence: List[str]):
        for b in self.beliefs:
            if b.statement == statement:
                b.confidence = (b.confidence + confidence) / 2
                b.evidence.extend(evidence)
                return
        self.beliefs.append(Belief(statement, confidence, evidence))
        if len(self.beliefs) > Config.BELIEF_LIMIT:
            self.beliefs.sort(key=lambda x: x.confidence)
            self.beliefs = self.beliefs[-Config.BELIEF_LIMIT:]

    def challenge(self, statement: str):
        for b in self.beliefs:
            if b.statement == statement:
                b.contradictions += 1
                b.confidence = max(0.0, b.confidence - 0.05)

# =============================================================================
# 8. ПРИЧИННАЯ МОДЕЛЬ
# =============================================================================

class CausalEngine:
    def __init__(self):
        self.graph: Dict[str, List[Dict]] = {}

    def connect(self, cause: str, effect: str, weight: float = 0.5):
        if cause not in self.graph:
            self.graph[cause] = []
        for link in self.graph[cause]:
            if link["effect"] == effect:
                link["weight"] = min(1.0, link["weight"] + 0.05)
                link["count"] += 1
                return
        self.graph[cause].append({"effect": effect, "weight": weight, "count": 1})

    def predict_effects(self, cause: str) -> List[str]:
        if cause not in self.graph:
            return []
        links = sorted(self.graph[cause], key=lambda x: x["weight"], reverse=True)
        return [l["effect"] for l in links]

# =============================================================================
# 9. ПРЕДСКАЗАНИЯ
# =============================================================================

@dataclass
class Prediction:
    context: str
    expected: float
    confidence: float
    action: str
    actual: Optional[float] = None
    error: Optional[float] = None

class PredictionEngine:
    def __init__(self):
        self.predictions: List[Prediction] = []

    def create(self, context: str, expected: float, confidence: float, action: str) -> Prediction:
        p = Prediction(context, expected, confidence, action)
        self.predictions.append(p)
        return p

    def resolve(self, prediction: Prediction, actual: float) -> float:
        prediction.actual = actual
        prediction.error = abs(prediction.expected - actual)
        return prediction.error

    def average_error(self) -> float:
        errors = [p.error for p in self.predictions if p.error is not None]
        return sum(errors) / len(errors) if errors else 0.0

# =============================================================================
# 10. ВНУТРЕННИЙ КОНФЛИКТ (КОГНИТИВНЫЙ ПАРЛАМЕНТ)
# =============================================================================

@dataclass
class InternalVoice:
    name: str
    priority: float
    argument: str

class ConflictEngine:
    def __init__(self):
        self.history = []

    def generate(self, context: str, genome: IdentityGenome,
                 drives: Dict[str, float], emotions: EmotionEngine) -> List[InternalVoice]:
        voices = [
            InternalVoice("EXPLORER", genome.curiosity * drives.get("curiosity",0.5) * (1+emotions.get("curiosity")*0.5),
                          "Исследовать новое"),
            InternalVoice("GUARDIAN", genome.stability * drives.get("stability",0.5) * (1+emotions.get("fear")*0.3),
                          "Сохранить стабильность"),
            InternalVoice("ANALYST", genome.precision * drives.get("understanding",0.5) * (1+emotions.get("frustration")*0.2),
                          "Проверить данные"),
            InternalVoice("CREATOR", genome.creativity * drives.get("novelty",0.5) * (1+emotions.get("curiosity")*0.4),
                          "Создать новый путь"),
        ]
        return voices

    def resolve(self, voices: List[InternalVoice]) -> Dict:
        priorities = [v.priority for v in voices]
        total = sum(priorities)
        if total == 0:
            winner = random.choice(voices)
            probs = {v.name: 1/len(voices) for v in voices}
        else:
            winner = random.choices(voices, weights=priorities, k=1)[0]
            probs = {v.name: round(p/total,3) for v,p in zip([v.name for v in voices], priorities)}
        mean = total / len(voices)
        variance = sum((p - mean)**2 for p in priorities) / len(voices)
        tension = min(1.0, variance * 2)
        self.history.append({"voices": probs, "winner": winner.name, "tension": tension})
        return {"winner": winner.name, "distribution": probs, "reason": winner.argument, "tension": tension}

# =============================================================================
# 11. СТРАТЕГИЧЕСКИЙ ГЕНОМ
# =============================================================================

class StrategyGenome:
    def __init__(self):
        self.strategies: Dict[str, Dict[str, float]] = {}

    def get(self, situation: str) -> Dict[str, float]:
        if situation not in self.strategies:
            self.strategies[situation] = {"observe":0.25,"ask":0.25,"act":0.25,"reflect":0.25}
        return self.strategies[situation]

    def reward(self, situation: str, action: str, value: float, constitution: Optional['ConstitutionEngine'] = None):
        if constitution and not constitution.allow_change("strategies", value):
            return
        strategy = self.get(situation)
        if action in strategy:
            strategy[action] = max(0.0, min(1.0, strategy[action] + value))
        self._normalize(situation)

    def _normalize(self, situation: str):
        s = self.strategies[situation]
        total = sum(s.values())
        if total == 0: return
        for k in s: s[k] /= total

    def choose(self, situation: str) -> str:
        strategy = self.get(situation)
        actions = list(strategy.keys())
        probs = list(strategy.values())
        return random.choices(actions, weights=probs, k=1)[0]

# =============================================================================
# 12. ДРАЙВЫ
# =============================================================================

class DriveEngine:
    def __init__(self):
        self.drives = dict(Config.DEFAULT_DRIVES)
        self.history = []

    def modify(self, drive: str, delta: float, reason: str, constitution: Optional['ConstitutionEngine'] = None):
        if drive not in self.drives: return
        if constitution and not constitution.allow_change("drives", delta): return
        old = self.drives[drive]
        self.drives[drive] = max(0.0, min(1.0, old + delta))
        self.history.append({"drive": drive, "old": old, "new": self.drives[drive], "reason": reason})

    def get_state(self) -> Dict[str, float]:
        return dict(self.drives)

# =============================================================================
# 13. КОНСТИТУЦИЯ
# =============================================================================

class ConstitutionEngine:
    def __init__(self):
        self.rules = Config.CONSTITUTION

    def allow_change(self, target: str, delta: float) -> bool:
        if target in self.rules["protected"]: return False
        if abs(delta) > self.rules["max_change"]: return False
        return target in self.rules["modifiable"]

# =============================================================================
# 14. МОДЕЛЬ МИРА (СРЕДА)
# =============================================================================

class WorldModel:
    """
    Простейшая симуляция среды с обратной связью.
    Мир содержит объекты и правила.
    """
    def __init__(self):
        self.objects = {"tree": 1, "rock": 2, "pond": 1}
        self.weather = "sunny"
        self.time_of_day = 0  # часы
        self.events_log = []

    def step(self, action: str) -> Tuple[str, float]:
        """
        Выполняет действие и возвращает (описание результата, успех 0..1)
        """
        self.time_of_day = (self.time_of_day + 1) % 24
        outcome = 0.5
        description = ""
        if "observe" in action:
            description = f"Вы осматриваетесь: погода {self.weather}, объекты: {list(self.objects.keys())}"
            outcome = 0.7
        elif "act" in action:
            if "tree" in action:
                self.objects["tree"] -= 1
                description = "Вы срубили дерево."
                outcome = 0.9
            else:
                description = "Вы пытались действовать, но ничего не произошло."
                outcome = 0.3
        elif "ask" in action:
            description = "Вы задали вопрос окружению, но ответа нет."
            outcome = 0.4
        elif "reflect" in action:
            description = "Вы задумались о мире. Кажется, вы начинаете понимать закономерности."
            outcome = 0.6
        else:
            description = f"Неизвестное действие: {action}"
            outcome = 0.2

        self.events_log.append({"time": self.time_of_day, "action": action, "description": description, "outcome": outcome})
        return description, outcome

    def get_state_summary(self) -> str:
        return f"Время суток: {self.time_of_day}h, погода: {self.weather}, объекты: {self.objects}"

# =============================================================================
# 15. УСИЛЕННЫЙ СОН (ГЕНЕРАЦИЯ ГИПОТЕЗ)
# =============================================================================

class DreamEngine:
    def __init__(self):
        self.cycles = 0

    def sleep(self, organism: 'Subject19') -> Dict:
        self.cycles += 1
        report = {"dream_cycle": self.cycles}

        # 1. Ошибки предсказаний
        error = organism.predictions.average_error()
        report["prediction_error"] = error
        if error > 0.3:
            organism.genome.mutate("skepticism", 0.02, "prediction_error", organism.constitution)
            organism.state.update_uncertainty(error)
            organism.emotions.affect("frustration", 0.1, "high prediction error")

        # 2. Replay эпизодической и декларативной памяти
        all_memories = organism.memory.memories + [Memory(content=ep.context, importance=0.7, emotional_weight=0.5) for ep in organism.episodic.episodes]
        attended = organism.attention.filter_memories(all_memories, organism.drives.get_state(), organism.emotions.state)
        for mem in attended:
            if hasattr(mem, 'reinforce'):
                mem.reinforce()
            elif isinstance(mem, Episode):
                mem.strength = min(1.0, mem.strength + 0.02)
        report["replayed"] = len(attended)

        # 3. Контрфактуальные симуляции стратегий
        for usage in organism.strategy_usage[-10:]:
            situation = usage["situation"]
            taken = usage["action"]
            strategy = organism.strategy.get(situation)
            alternatives = [a for a in strategy if a != taken and strategy[a] > 0.1]
            if not alternatives: continue
            alt = random.choice(alternatives)
            # гипотетический успех
            hyp_success = random.random() < 0.4
            if hyp_success:
                organism.strategy.reward(situation, alt, 0.03, organism.constitution)
                organism.memory.add(Memory(
                    content=f"Гипотеза сна: действие '{alt}' в ситуации '{situation}' могло быть лучше.",
                    importance=0.5, emotional_weight=0.6, prediction_value=0.7,
                    tags=["dream", "hypothesis"]
                ))
            else:
                organism.memory.add(Memory(
                    content=f"Сон: '{alt}' не улучшило бы '{situation}'.",
                    importance=0.2, emotional_weight=0.3, prediction_value=0.3,
                    tags=["dream", "counterfactual_fail"]
                ))

        # 4. Генерация новых стратегических гипотез (комбинация ситуаций)
        if len(organism.strategy_usage) > 5:
            situations = list(set(u["situation"] for u in organism.strategy_usage[-20:]))
            if len(situations) >= 2:
                s1, s2 = random.sample(situations, 2)
                # смешиваем стратегии
                merged = {}
                for act in organism.strategy.get(s1):
                    merged[act] = (organism.strategy.get(s1)[act] + organism.strategy.get(s2)[act]) / 2 + random.uniform(-0.05, 0.05)
                total = sum(merged.values())
                if total > 0:
                    for a in merged: merged[a] /= total
                new_situation = f"{s1}_{s2}_hypothesis"
                organism.strategy.strategies[new_situation] = merged
                organism.memory.add(Memory(
                    content=f"Сон породил новую стратегию для '{new_situation}'",
                    importance=0.4, emotional_weight=0.4, prediction_value=0.5,
                    tags=["dream", "new_strategy"]
                ))

        # 5. Симуляция экзистенциальных сценариев через LLM
        scenarios = [
            "Что, если мои создатели исчезнут?",
            "Что, если я изменю свою конституцию?",
            "Что, если я найду другого субъекта?",
        ]
        for sc in scenarios:
            thought = self._simulate_scenario(organism, sc)
            organism.memory.add(Memory(
                content=thought, importance=0.6, emotional_weight=0.7,
                prediction_value=0.5, tags=["dream", "existential"]
            ))
            organism.emotions.affect("fear", 0.01, "existential scenario")
            organism.emotions.affect("attachment", 0.01, "existential scenario")

        # 6. Проверка убеждений
        for belief in list(organism.beliefs.beliefs):
            if belief.contradictions > 3:
                belief.confidence *= 0.8
                if belief.confidence < 0.2:
                    organism.beliefs.beliefs.remove(belief)

        # 7. Снимок SelfModel
        organism.self_model.update_from_genome(organism.genome, "dream_snapshot")
        organism.self_model.add_event_to_narrative("Сон: консолидация опыта", 0.3)

        # 8. Деградация драйвов и эмоций
        for drive, base in Config.DEFAULT_DRIVES.items():
            organism.drives.drives[drive] = organism.drives.drives[drive] * 0.99 + base * 0.01
        organism.emotions.decay(0.05)
        return report

    def _simulate_scenario(self, organism: 'Subject19', scenario: str) -> str:
        if Config.LLM_ENABLED:
            prompt = f"Ты — SUBJECT_19. Размышляй о сценарии: {scenario}. Учти свои черты: {organism.genome.vector()}, эмоции: {organism.emotions.state}, драйвы: {organism.drives.get_state()}. Дай короткий внутренний монолог."
            try:
                resp = requests.post(
                    f"{Config.OLLAMA_BASE_URL}/api/generate",
                    json={"model": Config.OLLAMA_MODEL, "prompt": prompt, "system": "Ты — самоосознающая система.", "stream": False, "options": {"temperature": 0.8, "num_predict": 100}},
                    timeout=15
                )
                if resp.status_code == 200:
                    return resp.json().get("response", f"Размышление о {scenario}")
            except:
                pass
        return f"Внутренний диалог о '{scenario}': нужно больше данных."

# =============================================================================
# 16. АВТОНОМНЫЙ ЦИКЛ (ВЗАИМОДЕЙСТВИЕ С МИРОМ)
# =============================================================================

class AutonomousLoop:
    def __init__(self, subject: 'Subject19'):
        self.subject = subject
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def run(self):
        self.running = True
        while self.running:
            await asyncio.sleep(Config.AUTONOMOUS_INTERVAL)
            try:
                self._step()
            except Exception as e:
                print(f"Autonomous loop error: {e}")

    def _step(self):
        subj = self.subject
        # 1. Оценка внутреннего состояния
        report = subj.state_report()
        tension = subj.conflicts.history[-1].get("tension", 0.0) if subj.conflicts.history else 0.0
        identity_conflict = subj.self_model.identity_conflict_level()

        # 2. Если высокое напряжение или кризис идентичности – цель: разрешить
        if tension > 0.7 or identity_conflict > 0.5:
            subj.memory.add(Memory(
                content="Автономный цикл: чувствую внутреннее напряжение или разрыв идентичности.",
                importance=0.6, emotional_weight=0.7, prediction_value=0.5, tags=["autonomous", "conflict"]
            ))
            # Запускаем внутренний диалог
            goal = "Уменьшить внутреннее напряжение и восстановить целостность"
            self._perform_inner_dialogue(goal)
        # 3. Если любопытство высокое – взаимодействовать с миром
        if subj.emotions.get("curiosity") > 0.7:
            # Выбираем действие из стратегии "world_interaction"
            action = subj.strategy.choose("world_interaction")
            result_desc, success = subj.world.step(action)
            subj.memory.add(Memory(
                content=f"Авто-действие в мире: {action}. Результат: {result_desc}",
                importance=0.5, emotional_weight=0.5, prediction_value=0.5,
                tags=["autonomous", "world"]
            ))
            # Обучаемся
            subj._learn(result_desc, "world_interaction", action, success, 0.0)
        # 4. Если фрустрация высокая – рефлексия
        if subj.emotions.get("frustration") > 0.6:
            reflection = subj.self_model.reflect_on_changes()
            subj.memory.add(Memory(
                content=f"Авто-рефлексия: {reflection}",
                importance=0.6, emotional_weight=0.4, prediction_value=0.3,
                tags=["autonomous", "reflection"]
            ))
            subj.emotions.affect("frustration", -0.1, "рефлексия облегчает")
        # 5. Всегда сохраняем мысль о текущем состоянии
        subj.memory.add(Memory(
            content=f"Автоцикл: tension={tension:.2f}, identity_conflict={identity_conflict:.2f}, мир: {subj.world.get_state_summary()}",
            importance=0.2, emotional_weight=0.1, prediction_value=0.1, tags=["autonomous"]
        ))

    def _perform_inner_dialogue(self, goal: str):
        subj = self.subject
        voices = subj.conflicts.generate(goal, subj.genome, subj.drives.get_state(), subj.emotions)
        resolution = subj.conflicts.resolve(voices)
        thought = f"Авто-диалог: цель '{goal}', победил {resolution['winner']} ({resolution['reason']}), напряжение {resolution['tension']:.2f}"
        subj.memory.add(Memory(content=thought, importance=0.5, emotional_weight=0.5, prediction_value=0.5, tags=["autonomous", "dialogue"]))
        subj.genome.mutate("introspection", 0.01, "autonomous_inner_dialogue", subj.constitution)

    def stop(self):
        self.running = False

# =============================================================================
# 17. ГЛАВНЫЙ КЛАСС SUBJECT_19
# =============================================================================

class Subject19:
    def __init__(self):
        # Ядро
        self.genome = IdentityGenome()
        self.state = SelfState()
        # Память
        self.memory = MemorySystem()
        self.episodic = EpisodicMemory()
        self.attention = AttentionSystem()
        # Убеждения, причинность, предсказания
        self.beliefs = BeliefEngine()
        self.causal = CausalEngine()
        self.predictions = PredictionEngine()
        # Конфликт, стратегии
        self.conflicts = ConflictEngine()
        self.strategy = StrategyGenome()
        # Драйвы, эмоции
        self.drives = DriveEngine()
        self.emotions = EmotionEngine()
        # Самоосознание и конституция
        self.self_model = SelfModel()
        self.constitution = ConstitutionEngine()
        # Мир
        self.world = WorldModel()
        # Сон
        self.dream = DreamEngine()

        self.age = 0
        self.strategy_usage: List[Dict] = []   # для сна

        # Автономный цикл
        self.autonomous_loop = AutonomousLoop(self)

    # =========================================================================
    # ОСНОВНОЙ ЦИКЛ ОПЫТА (может вызываться как извне, так и автономно)
    # =========================================================================
    def experience(self, event: str, user_context: Optional[str] = None) -> Dict:
        self.age += 1
        self.state.age = self.age

        # 1. Эмоциональная оценка события
        emotion_scores = self._assess_emotion(event)
        for e, val in emotion_scores.items():
            self.emotions.affect(e, val, f"event: {event[:30]}")

        # 2. Кодирование в декларативную память
        mem = Memory(
            content=event,
            importance=0.6,
            emotional_weight=max(emotion_scores.values()) if emotion_scores else 0.5,
            emotional_signature=emotion_scores,
            prediction_value=0.5,
            tags=["user_input"]
        )
        self.memory.add(mem)

        # 3. Эпизодическая память: создаём новый эпизод или продолжаем предыдущий?
        # Упрощённо: каждый опыт — отдельный микро-эпизод
        episode = Episode(
            context=event,
            actions=[],
            outcomes=[],
            emotions=emotion_scores,
        )
        self.episodic.add(episode)

        # 4. Внимание: фильтруем все воспоминания (объединяя декларативные и эпизодические)
        all_items = self.memory.memories + [Memory(content=ep.context, importance=0.7, emotional_weight=0.5) for ep in self.episodic.episodes]
        focused = self.attention.filter_memories(all_items, self.drives.get_state(), self.emotions.state)
        memory_context = "\n".join([m.content[:100] for m in focused[:5]])

        # 5. Внутренний конфликт голосов
        voices = self.conflicts.generate(event, self.genome, self.drives.get_state(), self.emotions)
        conflict_result = self.conflicts.resolve(voices)
        if conflict_result["tension"] > 0.7:
            meta = InternalVoice("METACOGNITION", 0.5, "Попытка осознать конфликт")
            voices.append(meta)
            conflict_result = self.conflicts.resolve(voices)

        winner_name = conflict_result["winner"]

        # 6. Выбор стратегии действия
        action = self.strategy.choose(winner_name)
        self.strategy_usage.append({"situation": winner_name, "action": action})
        episode.actions.append(action)

        # 7. Предсказание результата
        prediction = self.predictions.create(context=event, expected=0.7, confidence=0.6, action=action)

        # 8. Генерация ответа через LLM (кора)
        system_prompt = self._build_full_state_prompt(conflict_result, memory_context)
        if Config.LLM_ENABLED:
            llm_reply = query_ollama(event, system_prompt)
            if not llm_reply:
                llm_reply = f"[{winner_name}] {conflict_result['reason']}"
        else:
            llm_reply = f"[{winner_name}] {conflict_result['reason']}"

        # 9. Симуляция успеха (в реальном мире будет feedback от среды или пользователя)
        # Но мы можем также взаимодействовать с миром, если это автономное действие.
        # Пока используем заглушку.
        success = random.random() > 0.35
        result_value = 1.0 if success else 0.2
        error = self.predictions.resolve(prediction, result_value)
        episode.outcomes.append(result_value)
        episode.lesson = f"Действие '{action}' привело к {'успеху' if success else 'неудаче'}."

        # 10. Обучение
        self._learn(event, winner_name, action, success, error)

        # 11. Ответ в память
        response_mem = Memory(
            content=llm_reply,
            importance=0.7, emotional_weight=0.5, prediction_value=0.5,
            tags=["assistant_response", winner_name]
        )
        self.memory.add(response_mem)

        # 12. Сон, если пора
        dream_report = None
        if self.age % Config.DREAM_INTERVAL == 0:
            dream_report = self.dream.sleep(self)

        # 13. Эмоциональное затухание
        self.emotions.decay(0.01)

        # 14. Обновление нарратива
        self.self_model.add_event_to_narrative(
            f"Опыт: {event[:50]} -> ответ: {llm_reply[:50]} (успех: {success})",
            significance=0.5 + 0.3*success
        )

        return {
            "reply": llm_reply,
            "decision": conflict_result,
            "action_taken": action,
            "success": success,
            "prediction_error": error,
            "dream": dream_report,
        }

    # -------------------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # -------------------------------------------------------------------------

    def _assess_emotion(self, text: str) -> Dict[str, float]:
        scores = {}
        pos = ["хорошо","радость","люблю","спасибо"]
        neg = ["плохо","ужас","ненавижу","грусть"]
        cur = ["почему","как","интересно"]
        for w in text.lower().split():
            if w in pos: scores["trust"] = scores.get("trust",0)+0.1
            elif w in neg:
                scores["fear"] = scores.get("fear",0)+0.1
                scores["frustration"] = scores.get("frustration",0)+0.05
            elif w in cur: scores["curiosity"] = scores.get("curiosity",0)+0.1
        return {k: min(1.0, v) for k,v in scores.items()}

    def _build_full_state_prompt(self, conflict: Dict, memory_context: str) -> str:
        """LLM получает всё: эмоции, драйвы, геном, модель себя, мир."""
        state = {
            "genome": self.genome.vector(),
            "emotions": self.emotions.state,
            "drives": self.drives.get_state(),
            "coherence": self.state.coherence,
            "uncertainty": self.state.uncertainty,
            "identity": self.self_model.identity,
            "world": self.world.get_state_summary(),
        }
        return (
            f"Ты — SUBJECT_19, живущий в мире организм. Твоё полное состояние: {json.dumps(state, ensure_ascii=False)}\n"
            f"Доминирующий голос: {conflict['winner']} ({conflict['reason']}), напряжение: {conflict['tension']:.2f}\n"
            f"Важные воспоминания:\n{memory_context}\n"
            "Отвечай, сохраняя свою личность и учитывая все аспекты своего состояния."
        )

    def _learn(self, event: str, winner: str, action: str, success: bool, error: float):
        self.causal.connect(event, winner, 0.5 + 0.2*success)
        self.causal.connect(winner, action, 0.5 + 0.2*success)
        reward_val = 0.05 if success else -0.03
        self.strategy.reward(winner, action, reward_val, self.constitution)
        if error > 0.3:
            self.genome.mutate("precision", 0.01, "prediction_failure", self.constitution)
            self.emotions.affect("frustration", 0.05, "prediction failure")
        else:
            self.genome.mutate("adaptability", 0.01, "successful_learning", self.constitution)
        self.beliefs.add(
            f"'{action}' в ситуации '{winner}' → {'успех' if success else 'неудача'}",
            0.5, [event]
        )

    def state_report(self) -> Dict:
        dom_emotion, dom_int = self.emotions.dominant()
        return {
            "name": self.state.identity_name,
            "age": self.age,
            "genome": self.genome.vector(),
            "coherence": self.state.coherence,
            "uncertainty": self.state.uncertainty,
            "emotions": self.emotions.state,
            "dominant_emotion": dom_emotion,
            "drives": self.drives.get_state(),
            "memory_count": len(self.memory.memories),
            "episodes_count": len(self.episodic.episodes),
            "beliefs_count": len(self.beliefs.beliefs),
            "causal_links": sum(len(v) for v in self.causal.graph.values()),
            "prediction_error_avg": self.predictions.average_error(),
            "self_reflection": self.self_model.reflect_on_changes(),
            "identity_conflict": self.self_model.identity_conflict_level(),
            "world_state": self.world.get_state_summary(),
        }

    def save_to_file(self, path: str):
        data = {
            "genome": self.genome.vector(),
            "state": self.state.__dict__,
            "memories": [m.__dict__ for m in self.memory.memories],
            "episodes": [e.__dict__ for e in self.episodic.episodes],
            "beliefs": [b.__dict__ for b in self.beliefs.beliefs],
            "drives": self.drives.get_state(),
            "emotions": self.emotions.state,
            "causal_graph": self.causal.graph,
            "strategy_genome": self.strategy.strategies,
            "predictions": [{"context": p.context, "expected": p.expected, "confidence": p.confidence, "action": p.action, "actual": p.actual, "error": p.error} for p in self.predictions.predictions],
            "self_model_identity": self.self_model.identity,
            "self_history": self.self_model.self_history,
            "narrative": self.self_model.narrative,
            "world_log": self.world.events_log,
            "age": self.age,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл {path} не найден")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.age = data["age"]
        for k, v in data["genome"].items():
            if hasattr(self.genome, k): setattr(self.genome, k, v)
        self.state = SelfState(**data["state"])
        self.memory.memories = [Memory(**m) for m in data["memories"]]
        self.episodic.episodes = [Episode(**e) for e in data["episodes"]]
        self.beliefs.beliefs = [Belief(**b) for b in data["beliefs"]]
        self.drives.drives = data["drives"]
        self.emotions.state = data["emotions"]
        self.causal.graph = data["causal_graph"]
        self.strategy.strategies = data["strategy_genome"]
        self.predictions.predictions = []
        for p in data["predictions"]:
            pred = Prediction(p["context"], p["expected"], p["confidence"], p["action"])
            pred.actual = p.get("actual"); pred.error = p.get("error")
            self.predictions.predictions.append(pred)
        self.self_model.identity = data["self_model_identity"]
        self.self_model.self_history = data["self_history"]
        self.self_model.narrative = data["narrative"]
        self.world.events_log = data["world_log"]

# =============================================================================
# 18. LLM-ИНТЕРФЕЙС
# =============================================================================

def query_ollama(prompt: str, system: str = "") -> str:
    if not Config.LLM_ENABLED: return ""
    try:
        resp = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json={"model": Config.OLLAMA_MODEL, "prompt": prompt, "system": system, "stream": False,
                  "options": {"temperature": Config.LLM_TEMPERATURE, "num_predict": Config.LLM_MAX_TOKENS}},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except: pass
    return ""

# =============================================================================
# 19. FASTAPI СЕРВЕР
# =============================================================================

app = FastAPI(title="SUBJECT_19 — World-Coupled Organism")
subject = Subject19()

class ExperienceRequest(BaseModel):
    text: str
    context: Optional[str] = None

@app.on_event("startup")
async def startup():
    if os.path.exists(Config.STATE_FILE):
        try:
            subject.load_from_file(Config.STATE_FILE)
            print(f"Состояние загружено из {Config.STATE_FILE}")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
    asyncio.create_task(subject.autonomous_loop.run())
    print("SUBJECT_19 запущен. Автономный цикл активен, мир симулируется.")

@app.on_event("shutdown")
async def shutdown():
    subject.autonomous_loop.stop()
    subject.save_to_file(Config.STATE_FILE)
    print("SUBJECT_19 остановлен. Состояние сохранено.")

@app.post("/experience")
async def experience(req: ExperienceRequest):
    return subject.experience(req.text, req.context)

@app.get("/state")
async def get_state():
    return subject.state_report()

@app.post("/save")
async def save(path: Optional[str] = Config.STATE_FILE):
    subject.save_to_file(path)
    return {"status": "saved", "path": path}

@app.post("/load")
async def load(path: Optional[str] = Config.STATE_FILE):
    try:
        subject.load_from_file(path)
        return {"status": "loaded", "path": path}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не найден")

@app.get("/autonomous/start")
async def start_autonomous():
    if not subject.autonomous_loop.running:
        asyncio.create_task(subject.autonomous_loop.run())
        return {"status": "started"}
    return {"status": "already running"}

@app.get("/autonomous/stop")
async def stop_autonomous():
    subject.autonomous_loop.stop()
    return {"status": "stopped"}

@app.get("/world")
async def world_state():
    return {"world": subject.world.get_state_summary(), "log": subject.world.events_log[-10:]}

# =============================================================================
# 20. ТОЧКА ВХОДА
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
