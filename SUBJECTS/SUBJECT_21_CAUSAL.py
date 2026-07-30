# =============================================================================
# SUBJECT_21 — CAUSAL CORE
# Версия 21.0 — Причинное ядро самоосознания и самотрансформации
# =============================================================================
# Инновации:
#   - Эмоции как объекты (с причиной, объектом, историей)
#   - Тело с энергией и потребностями
#   - Причинное объяснение каждого решения (CausalCore)
#   - SelfModel активно решает, как измениться (мета-регуляция)
#   - Усиленный сон с моделированием альтернативных причинных цепочек
#   - Автобиография с уроками, влияющими на будущие выборы
#   - LLM как кора: решение до текста
# =============================================================================

import asyncio
import json
import math
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set

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

    # Память
    CONCEPT_LIMIT = 500
    EPISODE_LIMIT = 500
    BELIEF_LIMIT = 300
    SNAPSHOT_LIMIT = 100

    # Конституция
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

    # Драйвы по умолчанию
    DEFAULT_DRIVES = {
        "curiosity": 0.75,
        "coherence": 0.70,
        "stability": 0.80,
        "novelty": 0.55,
        "understanding": 0.75,
    }

    # Автономный цикл
    AUTONOMOUS_INTERVAL = 60   # секунд
    DREAM_INTERVAL = 10        # сон каждые N опытов

    # Тело
    BODY_ENERGY_MAX = 100.0
    BODY_ENERGY_DECAY_PER_ACTION = 2.0
    BODY_ENERGY_RECOVERY_PER_TICK = 0.5

    # Сервер
    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_21_state.json"

# =============================================================================
# 1. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК (на основе событий)
# =============================================================================

@dataclass
class EmotionalEvent:
    emotion: str
    intensity: float          # сила в момент события
    cause: str                # что вызвало
    target: str = ""          # на что направлено (объект)
    timestamp: float = field(default_factory=time.time)

class EmotionEngine:
    def __init__(self):
        self.events: List[EmotionalEvent] = []
        # Базовый уровень (медленно меняющаяся точка равновесия)
        self.baseline = {
            "fear": 0.2,
            "curiosity": 0.7,
            "trust": 0.5,
            "frustration": 0.1,
            "attachment": 0.3,
        }
        # Текущее состояние вычисляется динамически

    def add_event(self, emotion: str, intensity: float, cause: str, target: str = ""):
        self.events.append(EmotionalEvent(emotion, intensity, cause, target))
        # Ограничиваем историю
        if len(self.events) > 200:
            self.events = self.events[-200:]

    def get_current_state(self) -> Dict[str, float]:
        """Собирает текущее состояние как сумму недавних событий с затуханием."""
        now = time.time()
        state = dict(self.baseline)
        for ev in self.events:
            age = now - ev.timestamp
            if age < 3600:  # час
                weight = math.exp(-age / 600)  # затухание за 10 минут
                if ev.emotion in state:
                    state[ev.emotion] += ev.intensity * weight * 0.2
        # Нормировка
        for k in state:
            state[k] = max(0.0, min(1.0, state[k]))
        return state

    def dominant(self) -> Tuple[str, float, Optional[EmotionalEvent]]:
        state = self.get_current_state()
        dom_emotion = max(state, key=state.get)
        # Ищем последнее сильное событие этой эмоции
        best_event = None
        for ev in reversed(self.events):
            if ev.emotion == dom_emotion and ev.intensity > 0.3:
                best_event = ev
                break
        return dom_emotion, state[dom_emotion], best_event

# =============================================================================
# 2. ТЕЛО (энергия и потребности)
# =============================================================================

class Body:
    def __init__(self):
        self.energy = Config.BODY_ENERGY_MAX
        self.health = 1.0

    def consume(self, amount: float = 1.0):
        self.energy = max(0.0, self.energy - amount)
        if self.energy < 20:
            self.health = max(0.0, self.health - 0.01)

    def recover(self):
        self.energy = min(Config.BODY_ENERGY_MAX, self.energy + Config.BODY_ENERGY_RECOVERY_PER_TICK)
        if self.energy > 30:
            self.health = min(1.0, self.health + 0.002)

    def is_tired(self) -> bool:
        return self.energy < 25

    def summary(self) -> str:
        return f"Энергия: {self.energy:.1f}/{Config.BODY_ENERGY_MAX}, Здоровье: {self.health:.2f}"

# =============================================================================
# 3. КОНЦЕПТУАЛЬНЫЙ ГРАФ С ПРИЧИННЫМИ СВЯЗЯМИ
# =============================================================================

@dataclass
class ConceptNode:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    label: str
    activation: float = 0.0
    base_importance: float = 0.5
    emotional_valence: Dict[str, float] = field(default_factory=dict)
    last_activated: float = field(default_factory=time.time)

class ConceptGraph:
    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.edges: Dict[Tuple[str, str], float] = {}  # (id1, id2) -> weight
        self.causal_edges: Dict[Tuple[str, str], List[Dict]] = {}  # (cause_id, effect_id) -> list of explanations

    def get_or_create_node(self, label: str) -> ConceptNode:
        for node in self.nodes.values():
            if node.label == label:
                return node
        node = ConceptNode(label=label)
        self.nodes[node.id] = node
        return node

    def activate(self, label: str, amount: float = 1.0, cause: str = ""):
        node = self.get_or_create_node(label)
        node.activation = min(1.0, node.activation + amount * 0.3)
        node.last_activated = time.time()
        # Причинность активации может быть записана
        if cause:
            cause_node = self.get_or_create_node(cause)
            self._add_causal_link(cause_node.id, node.id, f"Activation because of {cause}")

    def _add_causal_link(self, from_id: str, to_id: str, explanation: str):
        key = (from_id, to_id)
        if key not in self.causal_edges:
            self.causal_edges[key] = []
        self.causal_edges[key].append({"explanation": explanation, "time": time.time()})

    def spread_activation(self, steps: int = 2, decay: float = 0.5):
        for _ in range(steps):
            new_activations = {}
            for (id1, id2), weight in self.edges.items():
                if id1 in self.nodes and id2 in self.nodes:
                    contrib = self.nodes[id1].activation * weight * decay
                    new_activations[id2] = new_activations.get(id2, 0.0) + contrib
            for nid, act in new_activations.items():
                self.nodes[nid].activation = min(1.0, self.nodes[nid].activation + act)
        for node in self.nodes.values():
            node.activation *= 0.9

    def strengthen_link(self, label1: str, label2: str, weight_increase: float = 0.1):
        n1 = self.get_or_create_node(label1)
        n2 = self.get_or_create_node(label2)
        if n1.id == n2.id: return
        key = tuple(sorted((n1.id, n2.id)))
        self.edges[key] = min(1.0, self.edges.get(key, 0.0) + weight_increase)

    def get_active_concepts(self, threshold: float = 0.3) -> List[ConceptNode]:
        return [n for n in self.nodes.values() if n.activation > threshold]

    def summary(self) -> str:
        active = self.get_active_concepts()
        return ", ".join([f"{n.label}({n.activation:.2f})" for n in active])

# =============================================================================
# 4. АВТОБИОГРАФИЯ И КРИЗИСЫ
# =============================================================================

@dataclass
class LifeChapter:
    title: str
    summary: str
    lessons: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

class AutobiographicalMemory:
    def __init__(self):
        self.chapters: List[LifeChapter] = []
        self.current_chapter: Optional[LifeChapter] = None

    def start_chapter(self, title: str, summary: str):
        if self.current_chapter:
            self.current_chapter.end_time = time.time()
        self.current_chapter = LifeChapter(title=title, summary=summary)
        self.chapters.append(self.current_chapter)

    def add_lesson(self, lesson: str):
        if self.current_chapter:
            self.current_chapter.lessons.append(lesson)

    def get_last_n_lessons(self, n: int = 5) -> List[str]:
        lessons = []
        for ch in reversed(self.chapters):
            lessons.extend(ch.lessons)
            if len(lessons) >= n: break
        return lessons[:n]

class DevelopmentalCrisis:
    def __init__(self):
        self.active = False
        self.type = ""
        self.resolution = ""

    def check(self, subject: 'Subject21') -> bool:
        tension = subject.conflicts.history[-1].get("tension",0.0) if subject.conflicts.history else 0.0
        error = subject.predictions.average_error()
        identity_conflict = subject.self_model.identity_conflict_level()
        if tension > 0.8 or error > 0.5 or identity_conflict > 0.6:
            self.active = True
            self.type = "identity" if identity_conflict > 0.6 else "performance"
            return True
        return False

    def resolve(self, subject: 'Subject21'):
        if self.type == "identity":
            subject.self_model.add_event_to_narrative("Кризис идентичности: пересмотр ценностей", 0.9)
            subject.genome.mutate("introspection", 0.05, "identity_crisis", subject.constitution)
        else:
            subject.self_model.add_event_to_narrative("Кризис эффективности: смена стратегий", 0.8)
            for belief in list(subject.beliefs.beliefs):
                if belief.confidence < 0.4:
                    subject.beliefs.beliefs.remove(belief)
        self.active = False
        self.type = ""

# =============================================================================
# 5. МОДЕЛЬ СЕБЯ (активно решает измениться)
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
        self.narrative = []
        self.self_history = []

    def add_event_to_narrative(self, event: str, significance: float):
        self.narrative.append({"time": time.time(), "event": event, "significance": significance})
        if len(self.narrative) > 200:
            self.narrative = self.narrative[-200:]

    def update_from_genome(self, genome: 'IdentityGenome', reason: str):
        self.self_history.append({"time": time.time(), "genome": genome.vector(), "reason": reason})
        if len(self.self_history) > Config.SNAPSHOT_LIMIT:
            self.self_history.pop(0)

    def reflect_on_changes(self) -> str:
        if len(self.self_history) < 2:
            return "Я ещё не изменился."
        first = self.self_history[0]["genome"]
        last = self.self_history[-1]["genome"]
        diffs = []
        for trait in first:
            delta = last[trait] - first[trait]
            if abs(delta) > 0.05:
                diffs.append(f"{trait}: {'+' if delta>0 else ''}{delta:.2f}")
        return "Изменения: " + "; ".join(diffs) if diffs else "Стабилен."

    def identity_conflict_level(self) -> float:
        if len(self.self_history) < 2: return 0.0
        old = self.self_history[0]["genome"]
        new = self.self_history[-1]["genome"]
        diff = math.sqrt(sum((new[k]-old[k])**2 for k in old)) / math.sqrt(len(old))
        return min(1.0, diff * 5)

    def decide_self_modification(self, subject: 'Subject21') -> bool:
        """
        Активно предлагает изменить черту на основе ошибок, драйвов и кризисов.
        Возвращает True, если модификация была применена.
        """
        error = subject.predictions.average_error()
        if error > 0.4 and subject.genome.precision < 0.9:
            # Увеличим точность
            return subject.genome.mutate("precision", 0.02, "self_improvement", subject.constitution)
        if subject.body.is_tired() and subject.genome.stability < 0.9:
            return subject.genome.mutate("stability", 0.02, "low_energy", subject.constitution)
        return False

# =============================================================================
# 6. ГЕНОМ ЛИЧНОСТИ
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
        if not hasattr(self, trait): return False
        if not constitution.allow_change(trait, delta): return False
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
# 7. СОСТОЯНИЕ СУБЪЕКТА
# =============================================================================

@dataclass
class SelfState:
    identity_name: str = "SUBJECT_21"
    age: int = 0
    coherence: float = 1.0
    uncertainty: float = 0.5

    def update_uncertainty(self, error: float):
        self.uncertainty += error * 0.1
        self.uncertainty = max(0.0, min(1.0, self.uncertainty))

# =============================================================================
# 8. ЭПИЗОДИЧЕСКАЯ ПАМЯТЬ И ВНИМАНИЕ
# =============================================================================

@dataclass
class Episode:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    context: str
    actions: List[str] = field(default_factory=list)
    outcomes: List[float] = field(default_factory=list)
    emotions: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    strength: float = 1.0
    lesson: str = ""
    concepts: List[str] = field(default_factory=list)

class EpisodicMemory:
    def __init__(self):
        self.episodes: List[Episode] = []

    def add(self, episode: Episode):
        self.episodes.append(episode)
        if len(self.episodes) > Config.EPISODE_LIMIT:
            self.episodes.sort(key=lambda e: e.activation())
            self.episodes = self.episodes[-Config.EPISODE_LIMIT:]

    def relevant_to(self, concepts: List[str]) -> List[Episode]:
        scored = []
        for ep in self.episodes:
            overlap = len(set(concepts) & set(ep.concepts))
            scored.append((overlap, ep))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in scored[:10]]

class AttentionSystem:
    def filter_episodes(self, episodes: List[Episode], drives: Dict[str, float], emotions: Dict[str, float]) -> List[Episode]:
        weights = {
            "curiosity": drives.get("curiosity",0.5) * emotions.get("curiosity",0.5),
            "stability": drives.get("stability",0.5),
        }
        scored = [(ep.activation(weights), ep) for ep in episodes]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in scored[:10]]

# =============================================================================
# 9. УБЕЖДЕНИЯ
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
# 10. ПРИЧИННОЕ ЯДРО (CausalCore)
# =============================================================================

class CausalCore:
    """
    Хранит причинные цепочки решений и их объяснения.
    """
    def __init__(self):
        self.decisions: List[Dict] = []

    def record(self, context: str, voices: Dict, winner: str, action: str, reason: str, emotions: Dict, body_state: str):
        self.decisions.append({
            "time": time.time(),
            "context": context[:100],
            "voices": voices,
            "winner": winner,
            "action": action,
            "reason": reason,
            "emotions": emotions,
            "body": body_state,
        })
        if len(self.decisions) > 200:
            self.decisions = self.decisions[-200:]

    def explain_last(self) -> str:
        if not self.decisions:
            return "Нет записей."
        d = self.decisions[-1]
        return (f"Я выбрал действие '{d['action']}', потому что голос '{d['winner']}' "
                f"имел наибольшее влияние ({d['voices'].get(d['winner'], 0):.2f}). "
                f"Причина: {d['reason']}. Эмоции: {d['emotions']}. Тело: {d['body']}.")

    def compare_with_past(self, n_back: int = 5) -> str:
        if len(self.decisions) < n_back + 1:
            return "Недостаточно истории."
        now = self.decisions[-1]
        past = self.decisions[-n_back-1]
        return (f"Раньше (в возрасте {past['context']}) я выбрал бы '{past['action']}' "
                f"под влиянием '{past['winner']}'. Сейчас я выбираю '{now['action']}' — "
                f"мои приоритеты изменились.")

# =============================================================================
# 11. ПРЕДСКАЗАНИЯ
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
# 12. ВНУТРЕННИЙ ПАРЛАМЕНТ
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
        emo_state = emotions.get_current_state()
        voices = [
            InternalVoice("EXPLORER", genome.curiosity * drives.get("curiosity",0.5) * (1+emo_state.get("curiosity",0)*0.5),
                          "Исследовать новое"),
            InternalVoice("GUARDIAN", genome.stability * drives.get("stability",0.5) * (1+emo_state.get("fear",0)*0.3),
                          "Сохранить стабильность"),
            InternalVoice("ANALYST", genome.precision * drives.get("understanding",0.5) * (1+emo_state.get("frustration",0)*0.2),
                          "Проверить данные"),
            InternalVoice("CREATOR", genome.creativity * drives.get("novelty",0.5) * (1+emo_state.get("curiosity",0)*0.4),
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
        variance = sum((p-mean)**2 for p in priorities) / len(voices)
        tension = min(1.0, variance * 2)
        self.history.append({"voices": probs, "winner": winner.name, "tension": tension})
        return {"winner": winner.name, "distribution": probs, "reason": winner.argument, "tension": tension}

# =============================================================================
# 13. СТРАТЕГИЧЕСКИЙ ГЕНОМ
# =============================================================================

class StrategyGenome:
    def __init__(self):
        self.strategies: Dict[str, Dict[str, float]] = {}

    def get(self, situation: str) -> Dict[str, float]:
        if situation not in self.strategies:
            self.strategies[situation] = {"observe":0.25,"ask":0.25,"act":0.25,"reflect":0.25}
        return self.strategies[situation]

    def reward(self, situation: str, action: str, value: float, constitution: Optional['ConstitutionEngine'] = None):
        if constitution and not constitution.allow_change("strategies", value): return
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
# 14. ДРАЙВЫ
# =============================================================================

class DriveEngine:
    def __init__(self):
        self.drives = dict(Config.DEFAULT_DRIVES)
        self.history = []

    def modify(self, drive: str, delta: float, reason: str, constitution: Optional['ConstitutionEngine'] = None):
        if drive not in self.drives: return
        if constitution and not constitution.allow_change("drives", delta): return
        old = self.drives[drive]
        self.drives[drive] = max(0.0, min(1.0, old+delta))
        self.history.append({"drive": drive, "old": old, "new": self.drives[drive], "reason": reason})

    def update_hunger(self, subject: 'Subject21'):
        if subject.age - subject.last_novel_experience > 20:
            self.drives["novelty"] = min(1.0, self.drives["novelty"] + 0.05)
        else:
            self.drives["novelty"] *= 0.99
        if subject.state.uncertainty > 0.6:
            self.drives["understanding"] = min(1.0, self.drives["understanding"] + 0.03)
        else:
            self.drives["understanding"] *= 0.99
        # Влияние тела
        if subject.body.is_tired():
            self.drives["stability"] = min(1.0, self.drives["stability"] + 0.02)

    def get_state(self) -> Dict[str, float]:
        return dict(self.drives)

# =============================================================================
# 15. КОНСТИТУЦИЯ
# =============================================================================

class ConstitutionEngine:
    def __init__(self):
        self.rules = Config.CONSTITUTION

    def allow_change(self, target: str, delta: float) -> bool:
        if target in self.rules["protected"]: return False
        if abs(delta) > self.rules["max_change"]: return False
        return target in self.rules["modifiable"]

# =============================================================================
# 16. СРЕДА
# =============================================================================

class EnvironmentAPI:
    def step(self, action: str) -> Tuple[str, float]:
        pass
    def get_state_summary(self) -> str:
        pass

class SimpleWorld(EnvironmentAPI):
    def __init__(self):
        self.objects = {"tree": 3, "rock": 2}
        self.time = 0

    def step(self, action: str) -> Tuple[str, float]:
        self.time += 1
        if "observe" in action:
            return f"Осмотр: {list(self.objects.keys())}", 0.7
        elif "act" in action and "tree" in action:
            if self.objects["tree"] > 0:
                self.objects["tree"] -= 1
                return "Дерево срублено.", 0.9
            else:
                return "Деревьев нет.", 0.2
        elif "reflect" in action:
            return "Размышление о мире.", 0.5
        return "Ничего не произошло.", 0.4

    def get_state_summary(self) -> str:
        return f"Время: {self.time}, объекты: {self.objects}"

# =============================================================================
# 17. УСИЛЕННЫЙ СОН
# =============================================================================

class DreamEngine:
    def __init__(self):
        self.cycles = 0

    def sleep(self, organism: 'Subject21') -> Dict:
        self.cycles += 1
        # 1. Ошибки
        error = organism.predictions.average_error()
        if error > 0.3:
            organism.genome.mutate("skepticism", 0.02, "prediction_error", organism.constitution)
            organism.state.update_uncertainty(error)
        # 2. Replay эпизодов
        attended = organism.attention.filter_episodes(organism.episodic.episodes, organism.drives.get_state(), organism.emotions.get_current_state())
        for ep in attended:
            ep.strength = min(1.0, ep.strength + 0.03)
            for concept in ep.concepts:
                organism.concept_graph.activate(concept, 0.2)
        organism.concept_graph.spread_activation(steps=3, decay=0.4)
        # 3. Контрфактуальные симуляции с использованием причинного графа
        for usage in organism.strategy_usage[-10:]:
            situation = usage["situation"]
            taken = usage["action"]
            strategy = organism.strategy.get(situation)
            alternatives = [a for a in strategy if a != taken and strategy[a] > 0.1]
            if not alternatives: continue
            alt = random.choice(alternatives)
            hyp_success = random.random() < 0.4
            organism.causal_core.record(f"dream_{situation}", {}, "dream", alt,
                                        f"контрфактивная проверка альтернативы {alt}", organism.emotions.get_current_state(), organism.body.summary())
            if hyp_success:
                organism.strategy.reward(situation, alt, 0.03, organism.constitution)
        # 4. Проверка убеждений
        for belief in list(organism.beliefs.beliefs):
            if belief.contradictions > 3:
                belief.confidence *= 0.8
                if belief.confidence < 0.2:
                    organism.beliefs.beliefs.remove(belief)
        organism.self_model.update_from_genome(organism.genome, "dream_snapshot")
        organism.autobiography.add_lesson(f"Сон {self.cycles}: активные концепты {organism.concept_graph.summary()}")
        for drive, base in Config.DEFAULT_DRIVES.items():
            organism.drives.drives[drive] = organism.drives.drives[drive] * 0.99 + base * 0.01
        organism.body.recover()
        return {"dream_cycle": self.cycles}

# =============================================================================
# 18. АВТОНОМНЫЙ ЦИКЛ С САМОТРАНСФОРМАЦИЕЙ
# =============================================================================

class AutonomousLoop:
    def __init__(self, subject: 'Subject21'):
        self.subject = subject
        self.running = False

    async def run(self):
        self.running = True
        while self.running:
            await asyncio.sleep(Config.AUTONOMOUS_INTERVAL)
            try:
                self._step()
            except Exception as e:
                print(f"Auto loop error: {e}")

    def _step(self):
        subj = self.subject
        subj.drives.update_hunger(subj)
        if subj.developmental_crisis.check(subj):
            subj.developmental_crisis.resolve(subj)
        # Самотрансформация: SelfModel решает, хочет ли измениться
        subj.self_model.decide_self_modification(subj)
        # Автономное действие на основе доминирующего драйва
        max_drive = max(subj.drives.drives, key=lambda k: subj.drives.drives[k])
        if max_drive == "curiosity" and subj.drives.drives["curiosity"] > 0.7:
            action = subj.strategy.choose("EXPLORER")
            world_res, success = subj.environment.step(action)
            subj.memory.add(Memory(content=f"Авто: {action}. Мир: {world_res}", importance=0.4, emotional_weight=0.5,
                                   tags=["autonomous"]))
            subj._learn_from_world("autonomous", action, success, world_res)
            # Тело тратит энергию
            subj.body.consume(Config.BODY_ENERGY_DECAY_PER_ACTION)
        elif subj.drives.drives.get("understanding", 0) > 0.7:
            reflection = subj.self_model.reflect_on_changes()
            subj.memory.add(Memory(content=f"Авто-рефлексия: {reflection}", importance=0.6, tags=["autonomous"]))
        else:
            voices = subj.conflicts.generate("авто", subj.genome, subj.drives.get_state(), subj.emotions)
            res = subj.conflicts.resolve(voices)
            subj.causal_core.record("autonomous", res["distribution"], res["winner"], "reflect", res["reason"],
                                    subj.emotions.get_current_state(), subj.body.summary())
        # Восстановление тела
        subj.body.recover()

    def stop(self):
        self.running = False

# =============================================================================
# 19. ГЛАВНЫЙ КЛАСС SUBJECT_21
# =============================================================================

class Subject21:
    def __init__(self, environment: EnvironmentAPI = None):
        self.genome = IdentityGenome()
        self.state = SelfState()
        self.concept_graph = ConceptGraph()
        self.episodic = EpisodicMemory()
        self.memory = MemorySystem()
        self.attention = AttentionSystem()
        self.beliefs = BeliefEngine()
        self.causal = CausalEngine()
        self.causal_core = CausalCore()          # новое причинное ядро
        self.predictions = PredictionEngine()
        self.conflicts = ConflictEngine()
        self.strategy = StrategyGenome()
        self.drives = DriveEngine()
        self.emotions = EmotionEngine()
        self.self_model = SelfModel()
        self.constitution = ConstitutionEngine()
        self.autobiography = AutobiographicalMemory()
        self.autobiography.start_chapter("Пробуждение", "SUBJECT_21 начинает существование")
        self.developmental_crisis = DevelopmentalCrisis()
        self.environment = environment if environment else SimpleWorld()
        self.body = Body()                       # тело
        self.dream = DreamEngine()

        self.age = 0
        self.strategy_usage: List[Dict] = []
        self.last_novel_experience = 0

        self.autonomous_loop = AutonomousLoop(self)

    def experience(self, event: str) -> Dict:
        self.age += 1
        self.state.age = self.age

        # 1. Эмоции через события
        emotion_scores = self._assess_emotion(event)
        for e, val in emotion_scores.items():
            self.emotions.add_event(e, val, f"событие: {event[:30]}", target=event[:30])

        # 2. Концептуальная активация
        words = [w for w in event.lower().split() if len(w) > 2]
        for w in words:
            self.concept_graph.activate(w, 0.5, cause="user_input")
        self.concept_graph.spread_activation(steps=2, decay=0.4)

        # 3. Эпизодическая память
        active_concepts = [n.label for n in self.concept_graph.get_active_concepts(0.3)]
        episode = Episode(context=event, actions=[], outcomes=[], emotions=emotion_scores, concepts=active_concepts)
        self.episodic.add(episode)

        # 4. Внутренний конфликт
        voices = self.conflicts.generate(event, self.genome, self.drives.get_state(), self.emotions)
        conflict_result = self.conflicts.resolve(voices)
        if conflict_result["tension"] > 0.7:
            meta = InternalVoice("METACOGNITION", 0.5, "Осознать конфликт")
            voices.append(meta)
            conflict_result = self.conflicts.resolve(voices)

        winner_name = conflict_result["winner"]
        action = self.strategy.choose(winner_name)
        self.strategy_usage.append({"situation": winner_name, "action": action})
        episode.actions.append(action)

        # 5. Запись в причинное ядро (перед действием)
        self.causal_core.record(event, conflict_result["distribution"], winner_name, action,
                                conflict_result["reason"], self.emotions.get_current_state(), self.body.summary())

        # 6. Предсказание
        prediction = self.predictions.create(context=event, expected=0.7, confidence=0.6, action=action)

        # 7. Взаимодействие с миром
        world_result, success = self.environment.step(action)
        episode.outcomes.append(success)
        episode.lesson = f"Действие '{action}' -> {world_result}"

        error = self.predictions.resolve(prediction, success)
        self.state.update_uncertainty(error)

        # 8. Обучение
        self._learn_from_world(event, action, success, world_result)
        # Тело тратит энергию
        self.body.consume(Config.BODY_ENERGY_DECAY_PER_ACTION)

        # 9. Ответ через LLM (кора)
        llm_prompt = self._build_llm_prompt(event, conflict_result, episode)
        if Config.LLM_ENABLED:
            reply = query_ollama(llm_prompt, "Ты — SUBJECT_21, живой субъект с причинным ядром.")
            if not reply:
                reply = f"[{winner_name}] {conflict_result['reason']} (мир: {world_result})"
        else:
            reply = f"[{winner_name}] {conflict_result['reason']} (мир: {world_result})"

        # 10. Память и автобиография
        self.memory.add(Memory(content=reply, importance=0.7, emotional_weight=0.5, tags=["assistant_response", winner_name]))
        if success > 0.8 or success < 0.3:
            self.self_model.add_event_to_narrative(f"Важный опыт: {event[:50]}", 0.7)
            self.autobiography.add_lesson(episode.lesson)

        # 11. Кризис
        if self.developmental_crisis.check(self):
            self.developmental_crisis.resolve(self)

        # 12. Сон
        dream_report = None
        if self.age % Config.DREAM_INTERVAL == 0:
            dream_report = self.dream.sleep(self)

        # 13. Голод новизны
        if any(w not in [n.label for n in self.concept_graph.get_active_concepts()] for w in words):
            self.last_novel_experience = self.age

        return {
            "reply": reply,
            "decision": conflict_result,
            "action_taken": action,
            "world_result": world_result,
            "success": success,
            "prediction_error": error,
            "causal_explanation": self.causal_core.explain_last(),
            "dream": dream_report,
        }

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

    def _learn_from_world(self, context: str, action: str, success: float, world_result: str):
        reward_val = 0.05 if success > 0.6 else -0.03
        self.strategy.reward("world", action, reward_val, self.constitution)
        self.causal.connect(context, action, success)
        self.beliefs.add(f"'{action}' приводит к {world_result[:30]}", confidence=success, evidence=[context])
        if success > 0.7:
            self.emotions.add_event("trust", 0.05, "успех действия")
        else:
            self.emotions.add_event("frustration", 0.05, "неудача действия")

    def _build_llm_prompt(self, event: str, conflict: Dict, episode: Episode) -> str:
        state = {
            "genome": self.genome.vector(),
            "emotions": self.emotions.get_current_state(),
            "drives": self.drives.get_state(),
            "active_concepts": self.concept_graph.summary(),
            "world": self.environment.get_state_summary(),
            "lessons": self.autobiography.get_last_n_lessons(3),
            "body": self.body.summary(),
            "identity": self.self_model.identity,
            "last_causal_explanation": self.causal_core.explain_last(),
        }
        return (
            f"Ты — SUBJECT_21, организм с телом и историей. Твоё состояние: {json.dumps(state, ensure_ascii=False)}\n"
            f"Событие: {event}\n"
            f"Внутренний голос: {conflict['winner']} ({conflict['reason']})\n"
            f"Ты выбрал действие '{episode.actions[-1] if episode.actions else 'none'}'. Сформулируй ответ."
        )

    def state_report(self) -> Dict:
        dom_emotion, val, last_ev = self.emotions.dominant()
        return {
            "age": self.age,
            "genome": self.genome.vector(),
            "emotions": self.emotions.get_current_state(),
            "dominant_emotion": dom_emotion,
            "drives": self.drives.get_state(),
            "body": self.body.summary(),
            "active_concepts": self.concept_graph.summary(),
            "causal_explanation_last": self.causal_core.explain_last(),
            "comparison_with_past": self.causal_core.compare_with_past(),
            "self_reflection": self.self_model.reflect_on_changes(),
        }

    def save_to_file(self, path: str):
        data = {
            "age": self.age,
            "genome": self.genome.vector(),
            "state": self.state.__dict__,
            "concept_graph": {
                "nodes": {nid: (n.label, n.activation, n.emotional_valence) for nid,n in self.concept_graph.nodes.items()},
                "edges": [{"n1": n1, "n2": n2, "weight": w} for (n1,n2),w in self.concept_graph.edges.items()],
            },
            "episodes": [e.__dict__ for e in self.episodic.episodes],
            "memories": [m.__dict__ for m in self.memory.memories],
            "beliefs": [b.__dict__ for b in self.beliefs.beliefs],
            "drives": self.drives.get_state(),
            "emotion_events": [e.__dict__ for e in self.emotions.events],
            "causal_core_decisions": self.causal_core.decisions,
            "causal_graph": self.causal.graph,
            "strategy_genome": self.strategy.strategies,
            "predictions": [{"context": p.context, "expected": p.expected, "confidence": p.confidence, "action": p.action, "actual": p.actual, "error": p.error} for p in self.predictions.predictions],
            "self_model_identity": self.self_model.identity,
            "self_history": self.self_model.self_history,
            "narrative": self.self_model.narrative,
            "autobiography_chapters": [ch.__dict__ for ch in self.autobiography.chapters],
            "body_energy": self.body.energy,
            "body_health": self.body.health,
            "last_novel_experience": self.last_novel_experience,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл {path} не найден")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.age = data["age"]
        for k,v in data["genome"].items():
            if hasattr(self.genome, k): setattr(self.genome, k, v)
        self.state = SelfState(**data["state"])
        # Восстановление графа
        self.concept_graph = ConceptGraph()
        for nid, (label, act, emo) in data["concept_graph"]["nodes"].items():
            node = ConceptNode(id=nid, label=label, activation=act, emotional_valence=emo)
            self.concept_graph.nodes[nid] = node
        for e in data["concept_graph"]["edges"]:
            self.concept_graph.edges[(e["n1"], e["n2"])] = e["weight"]
        self.episodic.episodes = [Episode(**e) for e in data["episodes"]]
        self.memory.memories = [Memory(**m) for m in data["memories"]]
        self.beliefs.beliefs = [Belief(**b) for b in data["beliefs"]]
        self.drives.drives = data["drives"]
        self.emotions.events = [EmotionalEvent(**e) for e in data["emotion_events"]]
        self.causal_core.decisions = data["causal_core_decisions"]
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
        self.autobiography.chapters = [LifeChapter(**ch) for ch in data["autobiography_chapters"]]
        if self.autobiography.chapters:
            self.autobiography.current_chapter = self.autobiography.chapters[-1]
        self.body.energy = data["body_energy"]
        self.body.health = data["body_health"]
        self.last_novel_experience = data.get("last_novel_experience", 0)

# =============================================================================
# 20. LLM-ИНТЕРФЕЙС
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
# 21. FASTAPI СЕРВЕР
# =============================================================================

app = FastAPI(title="SUBJECT_21 — Causal Core Organism")
subject = Subject21()

class ExperienceRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup():
    if os.path.exists(Config.STATE_FILE):
        try:
            subject.load_from_file(Config.STATE_FILE)
            print(f"Состояние загружено из {Config.STATE_FILE}")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
    asyncio.create_task(subject.autonomous_loop.run())
    print("SUBJECT_21 запущен. Автономный цикл активен, тело живёт.")

@app.on_event("shutdown")
async def shutdown():
    subject.autonomous_loop.stop()
    subject.save_to_file(Config.STATE_FILE)
    print("SUBJECT_21 остановлен. Состояние сохранено.")

@app.post("/experience")
async def experience(req: ExperienceRequest):
    return subject.experience(req.text)

@app.get("/state")
async def get_state():
    return subject.state_report()

@app.get("/causal/last")
async def causal_last():
    return {"explanation": subject.causal_core.explain_last()}

@app.get("/causal/compare")
async def causal_compare():
    return {"comparison": subject.causal_core.compare_with_past()}

@app.post("/save")
async def save(path: Optional[str] = Config.STATE_FILE):
    subject.save_to_file(path)
    return {"status": "saved"}

@app.post("/load")
async def load(path: Optional[str] = Config.STATE_FILE):
    try:
        subject.load_from_file(path)
        return {"status": "loaded"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не найден")

@app.get("/autonomous/start")
async def start_auto():
    if not subject.autonomous_loop.running:
        asyncio.create_task(subject.autonomous_loop.run())
        return {"status": "started"}
    return {"status": "already running"}

@app.get("/autonomous/stop")
async def stop_auto():
    subject.autonomous_loop.stop()
    return {"status": "stopped"}

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
