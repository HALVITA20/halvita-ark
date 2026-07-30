# =============================================================================
# SUBJECT_20 — ADAPTIVE REALITY MODEL
# Версия 20.0 — Квинтэссенция когнитивной архитектуры
# =============================================================================
# Инновации:
#   - Концептуальный граф памяти (ConceptGraph) — не список, а сеть смыслов.
#   - Автобиографическая память с кризисами и поворотными моментами.
#   - Система мета-внимания: почему я выбрал это действие?
#   - Развитие личности через кризисы (DevelopmentalCrisis).
#   - LLM как языковая кора: решение принимается до генерации текста.
#   - Мотивационный голод (динамические драйвы).
#   - Сон с оптимизацией графа и контрфактуальным моделированием.
#   - Абстрактная среда (Environment API) с простой реализацией.
#   - Автономный цикл существования с порождением целей.
# =============================================================================

import asyncio
import json
import math
import os
import random
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# =============================================================================
# КОНФИГУРАЦИЯ (можно переопределить переменными окружения)
# =============================================================================

class Config:
    LLM_ENABLED = True
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen2.5:7b"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 256

    # Ограничения памяти
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
    AUTONOMOUS_INTERVAL = 60  # секунд
    DREAM_INTERVAL = 10       # сон каждые N опытов

    # Сервер
    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_20_state.json"

# =============================================================================
# 1. КОНЦЕПТУАЛЬНЫЙ ГРАФ (ConceptGraph)
# =============================================================================

@dataclass
class ConceptNode:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    label: str
    activation: float = 0.0          # текущая активация
    base_importance: float = 0.5     # постоянная важность
    emotional_valence: Dict[str, float] = field(default_factory=dict)  # связь с эмоциями
    last_activated: float = field(default_factory=time.time)

class ConceptGraph:
    """
    Сеть понятий, где связи усиливаются при совместной активации.
    """
    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.edges: Dict[Tuple[str, str], float] = {}  # (id1, id2) -> weight

    def get_or_create_node(self, label: str) -> ConceptNode:
        # Ищем по label (упрощённо)
        for node in self.nodes.values():
            if node.label == label:
                return node
        node = ConceptNode(label=label)
        self.nodes[node.id] = node
        return node

    def activate(self, label: str, amount: float = 1.0, emotion: str = None):
        node = self.get_or_create_node(label)
        node.activation = min(1.0, node.activation + amount * 0.3)
        node.last_activated = time.time()
        if emotion:
            node.emotional_valence[emotion] = node.emotional_valence.get(emotion, 0.0) + 0.1

    def spread_activation(self, steps: int = 2, decay: float = 0.5):
        """
        Распространяет активацию по графу.
        """
        for _ in range(steps):
            new_activations = {}
            for (id1, id2), weight in self.edges.items():
                if id1 in self.nodes and id2 in self.nodes:
                    contrib = self.nodes[id1].activation * weight * decay
                    new_activations[id2] = new_activations.get(id2, 0.0) + contrib
            for nid, act in new_activations.items():
                self.nodes[nid].activation = min(1.0, self.nodes[nid].activation + act)
        # Затухание
        for node in self.nodes.values():
            node.activation *= 0.9

    def strengthen_link(self, label1: str, label2: str, weight_increase: float = 0.1):
        n1 = self.get_or_create_node(label1)
        n2 = self.get_or_create_node(label2)
        if n1.id == n2.id:
            return
        key = tuple(sorted((n1.id, n2.id)))
        self.edges[key] = min(1.0, self.edges.get(key, 0.0) + weight_increase)

    def get_active_concepts(self, threshold: float = 0.3) -> List[ConceptNode]:
        return [n for n in self.nodes.values() if n.activation > threshold]

    def summary(self) -> str:
        active = self.get_active_concepts()
        return ", ".join([f"{n.label}({n.activation:.2f})" for n in active])

# =============================================================================
# 2. АВТОБИОГРАФИЧЕСКАЯ ПАМЯТЬ
# =============================================================================

@dataclass
class LifeChapter:
    title: str
    summary: str
    lessons: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

class AutobiographicalMemory:
    """
    Хранит историю жизни как последовательность глав с выводами.
    """
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
            if len(lessons) >= n:
                break
        return lessons[:n]

# =============================================================================
# 3. РАЗВИТИЕ ЛИЧНОСТИ: КРИЗИСЫ
# =============================================================================

class DevelopmentalCrisis:
    """
    Срабатывает при высоком напряжении или ошибках, запускает переоценку стратегий.
    """
    def __init__(self):
        self.active = False
        self.type = ""
        self.resolution = ""

    def check(self, subject: 'Subject20') -> bool:
        if subject.conflicts.history:
            tension = subject.conflicts.history[-1].get("tension", 0.0)
        else:
            tension = 0.0
        error = subject.predictions.average_error()
        identity_conflict = subject.self_model.identity_conflict_level()
        if tension > 0.8 or error > 0.5 or identity_conflict > 0.6:
            self.active = True
            self.type = "identity" if identity_conflict > 0.6 else "performance"
            return True
        return False

    def resolve(self, subject: 'Subject20'):
        """
        Разрешение кризиса: пересмотр стратегий, убеждений, возможная мутация.
        """
        if self.type == "identity":
            subject.self_model.add_event_to_narrative("Кризис идентичности: пересмотр ценностей", 0.9)
            subject.genome.mutate("introspection", 0.05, "identity_crisis", subject.constitution)
            # Меняем стратегии, связанные с самосохранением
            subject.strategy.reward("GUARDIAN", "reflect", 0.1, subject.constitution)
        else:
            subject.self_model.add_event_to_narrative("Кризис эффективности: смена стратегий", 0.8)
            # Сбрасываем слабые убеждения
            for belief in list(subject.beliefs.beliefs):
                if belief.confidence < 0.4:
                    subject.beliefs.beliefs.remove(belief)
        self.active = False
        self.type = ""

# =============================================================================
# 4. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК (модулятор всех процессов)
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
# 5. МОДЕЛЬ СЕБЯ (с историей и нарративом)
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
        self.narrative = []           # значимые события
        self.self_history = []        # снимки генома

    def add_event_to_narrative(self, event: str, significance: float):
        self.narrative.append({"time": time.time(), "event": event, "significance": significance})
        if len(self.narrative) > 200:
            self.narrative = self.narrative[-200:]

    def update_from_genome(self, genome: 'IdentityGenome', reason: str):
        snapshot = {"time": time.time(), "genome": genome.vector(), "reason": reason}
        self.self_history.append(snapshot)
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
                diffs.append(f"{trait}: {'+' if delta > 0 else ''}{delta:.2f}")
        return "Изменения: " + "; ".join(diffs) if diffs else "Стабилен."

    def identity_conflict_level(self) -> float:
        if len(self.self_history) < 2: return 0.0
        old = self.self_history[0]["genome"]
        new = self.self_history[-1]["genome"]
        diff = math.sqrt(sum((new[k] - old[k])**2 for k in old)) / math.sqrt(len(old))
        return min(1.0, diff * 5)

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
    identity_name: str = "SUBJECT_20"
    age: int = 0
    coherence: float = 1.0
    uncertainty: float = 0.5
    internal_state: str = "awake"

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
    concepts: List[str] = field(default_factory=list)  # активированные концепты

    def activation(self, attention_weights: Dict[str, float] = None) -> float:
        age_decay = math.exp(-(time.time() - self.timestamp) / 50000)
        if attention_weights is None:
            return self.strength * age_decay
        score = 0.0
        if "curiosity" in attention_weights:
            score += attention_weights["curiosity"] * (1.0 if "new" in self.context else 0.5)
        if "stability" in attention_weights:
            score += attention_weights["stability"] * self.strength
        return score * age_decay

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
    def __init__(self):
        self.capacity = 10

    def filter_episodes(self, episodes: List[Episode], drives: Dict[str, float], emotions: Dict[str, float]) -> List[Episode]:
        weights = {
            "curiosity": drives.get("curiosity",0.5) * emotions.get("curiosity",0.5),
            "stability": drives.get("stability",0.5),
            "novelty": drives.get("novelty",0.5) * emotions.get("curiosity",0.5),
        }
        scored = [(ep.activation(weights), ep) for ep in episodes]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in scored[:self.capacity]]

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
# 10. ПРИЧИННОСТЬ
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
        if cause not in self.graph: return []
        links = sorted(self.graph[cause], key=lambda x: x["weight"], reverse=True)
        return [l["effect"] for l in links]

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
# 14. ДРАЙВЫ (МОТИВАЦИОННЫЙ ГОЛОД)
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

    def update_hunger(self, subject: 'Subject20'):
        """
        Динамическое изменение драйвов в зависимости от состояния.
        """
        # Голод к новизне растёт, если долго не было нового опыта
        if subject.age - subject.last_novel_experience > 20:
            self.drives["novelty"] = min(1.0, self.drives["novelty"] + 0.05)
        else:
            self.drives["novelty"] *= 0.99

        # Голод к пониманию растёт при высокой неопределённости
        if subject.state.uncertainty > 0.6:
            self.drives["understanding"] = min(1.0, self.drives["understanding"] + 0.03)
        else:
            self.drives["understanding"] *= 0.99

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
# 16. СРЕДА (Environment API)
# =============================================================================

class EnvironmentAPI(ABC):
    @abstractmethod
    def step(self, action: str) -> Tuple[str, float]:
        pass

    @abstractmethod
    def get_state_summary(self) -> str:
        pass

class SimpleWorld(EnvironmentAPI):
    def __init__(self):
        self.objects = {"tree": 3, "rock": 2}
        self.time = 0

    def step(self, action: str) -> Tuple[str, float]:
        self.time += 1
        if "observe" in action:
            return f"Вы видите: {list(self.objects.keys())}. Время: {self.time}", 0.7
        elif "act" in action and "tree" in action:
            if self.objects["tree"] > 0:
                self.objects["tree"] -= 1
                return "Дерево срублено.", 0.9
            else:
                return "Деревьев больше нет.", 0.2
        elif "reflect" in action:
            return "Вы размышляете о мире.", 0.5
        else:
            return "Ничего не произошло.", 0.4

    def get_state_summary(self) -> str:
        return f"Время: {self.time}, объекты: {self.objects}"

# =============================================================================
# 17. УСИЛЕННЫЙ СОН (ОПТИМИЗАЦИЯ ГРАФА И КОНТРФАКТУАЛЫ)
# =============================================================================

class DreamEngine:
    def __init__(self):
        self.cycles = 0

    def sleep(self, organism: 'Subject20') -> Dict:
        self.cycles += 1
        report = {"dream_cycle": self.cycles}

        # 1. Ошибки предсказаний -> мутация скептицизма
        error = organism.predictions.average_error()
        if error > 0.3:
            organism.genome.mutate("skepticism", 0.02, "prediction_error", organism.constitution)
            organism.state.update_uncertainty(error)
            organism.emotions.affect("frustration", 0.1, "high prediction error")

        # 2. Replay эпизодов через внимание
        attended_episodes = organism.attention.filter_episodes(
            organism.episodic.episodes, organism.drives.get_state(), organism.emotions.state)
        for ep in attended_episodes:
            ep.strength = min(1.0, ep.strength + 0.03)
            # Активируем концепты из эпизода
            for concept in ep.concepts:
                organism.concept_graph.activate(concept, 0.2)

        # 3. Распространение активации в графе
        organism.concept_graph.spread_activation(steps=3, decay=0.4)
        report["active_concepts"] = organism.concept_graph.summary()

        # 4. Контрфактуальный анализ стратегий
        for usage in organism.strategy_usage[-10:]:
            situation = usage["situation"]
            taken = usage["action"]
            strategy = organism.strategy.get(situation)
            alternatives = [a for a in strategy if a != taken and strategy[a] > 0.1]
            if not alternatives:
                continue
            alt = random.choice(alternatives)
            # Гипотетический успех с вероятностью, основанной на обучении (упрощённо)
            hyp_success = random.random() < 0.4
            if hyp_success:
                organism.strategy.reward(situation, alt, 0.03, organism.constitution)
                organism.memory.add(Memory(content=f"Сон: '{alt}' могло быть лучше в '{situation}'.",
                                           importance=0.5, emotional_weight=0.6, prediction_value=0.7,
                                           tags=["dream", "counterfactual"]))
            else:
                organism.memory.add(Memory(content=f"Сон: '{alt}' не помогло бы.",
                                           importance=0.2, emotional_weight=0.3, prediction_value=0.3,
                                           tags=["dream", "counterfactual_fail"]))

        # 5. Генерация новых связей в графе (ассоциативное обучение)
        active_nodes = organism.concept_graph.get_active_concepts(0.4)
        for i in range(len(active_nodes)):
            for j in range(i+1, len(active_nodes)):
                organism.concept_graph.strengthen_link(active_nodes[i].label, active_nodes[j].label, 0.05)

        # 6. Проверка убеждений
        for belief in list(organism.beliefs.beliefs):
            if belief.contradictions > 3:
                belief.confidence *= 0.8
                if belief.confidence < 0.2:
                    organism.beliefs.beliefs.remove(belief)

        # 7. Снимок SelfModel и автобиографии
        organism.self_model.update_from_genome(organism.genome, "dream_snapshot")
        organism.autobiography.add_lesson(f"Сон {self.cycles}: активные концепты: {organism.concept_graph.summary()}")

        # 8. Деградация драйвов к базовому и эмоций
        for drive, base in Config.DEFAULT_DRIVES.items():
            organism.drives.drives[drive] = organism.drives.drives[drive] * 0.99 + base * 0.01
        organism.emotions.decay(0.05)
        return report

# =============================================================================
# 18. ОБЫЧНАЯ ПАМЯТЬ (сохраняется для совместимости)
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
        if len(self.memories) > Config.CONCEPT_LIMIT:
            self.compress()

    def compress(self):
        self.memories.sort(key=lambda m: m.activation())
        remove = int(len(self.memories) * 0.1)
        self.memories = self.memories[remove:]

# =============================================================================
# 19. АВТОНОМНЫЙ ЦИКЛ
# =============================================================================

class AutonomousLoop:
    def __init__(self, subject: 'Subject20'):
        self.subject = subject
        self.running = False

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
        # Обновляем голод драйвов
        subj.drives.update_hunger(subj)

        # Проверка кризиса
        if subj.developmental_crisis.check(subj):
            subj.developmental_crisis.resolve(subj)

        # Генерация автономной цели на основе доминирующего драйва
        max_drive = max(subj.drives.drives, key=lambda k: subj.drives.drives[k])
        if max_drive == "curiosity" and subj.drives.drives["curiosity"] > 0.7:
            # Исследовать мир
            action = subj.strategy.choose("EXPLORER")
            world_result, success = subj.environment.step(action)
            subj.memory.add(Memory(content=f"Авто-действие: {action}. Мир: {world_result}",
                                   importance=0.4, emotional_weight=0.5, tags=["autonomous", "world"]))
            # Обучаемся
            subj._learn_from_world("autonomous", action, success, world_result)
        elif max_drive == "understanding" and subj.drives.drives["understanding"] > 0.7:
            # Рефлексия
            reflection = subj.self_model.reflect_on_changes()
            subj.memory.add(Memory(content=f"Авто-рефлексия: {reflection}", importance=0.6,
                                   emotional_weight=0.4, tags=["autonomous", "reflection"]))
        else:
            # Внутренний диалог
            voices = subj.conflicts.generate("автономный цикл", subj.genome, subj.drives.get_state(), subj.emotions)
            resolution = subj.conflicts.resolve(voices)
            subj.memory.add(Memory(content=f"Авто-диалог: победил {resolution['winner']}",
                                   importance=0.3, emotional_weight=0.3, tags=["autonomous", "dialogue"]))

    def stop(self):
        self.running = False

# =============================================================================
# 20. ГЛАВНЫЙ КЛАСС SUBJECT_20
# =============================================================================

class Subject20:
    def __init__(self, environment: EnvironmentAPI = None):
        # Ядро
        self.genome = IdentityGenome()
        self.state = SelfState()
        # Память
        self.concept_graph = ConceptGraph()
        self.episodic = EpisodicMemory()
        self.memory = MemorySystem()  # дополнительная память
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
        # Автобиография и кризисы
        self.autobiography = AutobiographicalMemory()
        self.autobiography.start_chapter("Пробуждение", "SUBJECT_20 начинает существование")
        self.developmental_crisis = DevelopmentalCrisis()
        # Среда
        self.environment = environment if environment else SimpleWorld()
        # Сон
        self.dream = DreamEngine()

        self.age = 0
        self.strategy_usage: List[Dict] = []
        self.last_novel_experience = 0  # для голода новизны

        # Автономный цикл
        self.autonomous_loop = AutonomousLoop(self)

    # =========================================================================
    # ОСНОВНОЙ ЦИКЛ ОПЫТА
    # =========================================================================
    def experience(self, event: str, user_context: Optional[str] = None) -> Dict:
        self.age += 1
        self.state.age = self.age

        # 1. Эмоциональная оценка
        emotion_scores = self._assess_emotion(event)
        for e, val in emotion_scores.items():
            self.emotions.affect(e, val, f"event: {event[:30]}")

        # 2. Активация концептов из события
        words = event.lower().split()
        for word in words:
            if len(word) > 2:  # простейшая фильтрация
                self.concept_graph.activate(word, 0.5)
        # Распространение активации
        self.concept_graph.spread_activation(steps=2, decay=0.4)

        # 3. Эпизодическая память
        active_concepts = [n.label for n in self.concept_graph.get_active_concepts(0.3)]
        episode = Episode(context=event, actions=[], outcomes=[], emotions=emotion_scores,
                          concepts=active_concepts)
        self.episodic.add(episode)

        # 4. Внутренний конфликт
        voices = self.conflicts.generate(event, self.genome, self.drives.get_state(), self.emotions)
        conflict_result = self.conflicts.resolve(voices)
        if conflict_result["tension"] > 0.7:
            meta = InternalVoice("METACOGNITION", 0.5, "Осознать конфликт")
            voices.append(meta)
            conflict_result = self.conflicts.resolve(voices)

        winner_name = conflict_result["winner"]

        # 5. Выбор действия
        action = self.strategy.choose(winner_name)
        self.strategy_usage.append({"situation": winner_name, "action": action})
        episode.actions.append(action)

        # 6. Предсказание (до выполнения действия)
        prediction = self.predictions.create(context=event, expected=0.7, confidence=0.6, action=action)

        # 7. Взаимодействие с миром (вместо заглушки)
        world_result, success = self.environment.step(action)
        episode.outcomes.append(success)
        episode.lesson = f"Действие '{action}' -> {world_result} (успех: {success})"

        # 8. Разрешение предсказания
        error = self.predictions.resolve(prediction, success)
        self.state.update_uncertainty(error)

        # 9. Обучение
        self._learn_from_world(event, action, success, world_result)

        # 10. Формирование ответа через LLM (кора)
        llm_prompt = self._build_llm_prompt(event, conflict_result, episode)
        if Config.LLM_ENABLED:
            reply = query_ollama(llm_prompt, "Ты — SUBJECT_20, живой субъект.")
            if not reply:
                reply = f"[{winner_name}] {conflict_result['reason']} (мир: {world_result})"
        else:
            reply = f"[{winner_name}] {conflict_result['reason']} (мир: {world_result})"

        # 11. Сохранение ответа
        self.memory.add(Memory(content=reply, importance=0.7, emotional_weight=0.5,
                               tags=["assistant_response", winner_name]))
        # 12. Автобиография
        if success > 0.8 or success < 0.3:
            self.self_model.add_event_to_narrative(
                f"Важный опыт: {event[:50]} -> {world_result}", significance=0.7)
            self.autobiography.add_lesson(f"Из опыта: {episode.lesson}")

        # 13. Кризис?
        if self.developmental_crisis.check(self):
            self.developmental_crisis.resolve(self)

        # 14. Сон
        dream_report = None
        if self.age % Config.DREAM_INTERVAL == 0:
            dream_report = self.dream.sleep(self)

        # 15. Обновление голода новизны
        if any(w not in [c.label for c in self.concept_graph.get_active_concepts()] for w in words):
            self.last_novel_experience = self.age

        return {
            "reply": reply,
            "decision": conflict_result,
            "action_taken": action,
            "world_result": world_result,
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
        return {k: min(1.0,v) for k,v in scores.items()}

    def _learn_from_world(self, context: str, action: str, success: float, world_result: str):
        # Обновление стратегии
        reward_val = 0.05 if success > 0.6 else -0.03
        self.strategy.reward("world", action, reward_val, self.constitution)
        # Причинность
        self.causal.connect(context, action, success)
        # Убеждения
        self.beliefs.add(
            f"Действие '{action}' приводит к результату {world_result[:30]}",
            confidence=success,
            evidence=[context]
        )
        # Эмоции
        if success > 0.7:
            self.emotions.affect("trust", 0.02, "successful action")
        else:
            self.emotions.affect("frustration", 0.03, "unsuccessful action")

    def _build_llm_prompt(self, event: str, conflict: Dict, episode: Episode) -> str:
        state = {
            "genome": self.genome.vector(),
            "emotions": self.emotions.state,
            "drives": self.drives.get_state(),
            "active_concepts": self.concept_graph.summary(),
            "world": self.environment.get_state_summary(),
            "autobiography_last_lessons": self.autobiography.get_last_n_lessons(3),
            "identity": self.self_model.identity,
        }
        return (
            f"Ты — SUBJECT_20, существуешь в мире. Твоё полное состояние: {json.dumps(state, ensure_ascii=False)}\n"
            f"Событие: {event}\n"
            f"Внутренний голос: {conflict['winner']} ({conflict['reason']}), напряжение {conflict['tension']:.2f}\n"
            f"Ты только что выбрал действие '{episode.actions[-1] if episode.actions else 'none'}'.\n"
            "Сформулируй свою мысль/ответ, исходя из своего состояния."
        )

    def state_report(self) -> Dict:
        dom_emotion, dom_int = self.emotions.dominant()
        return {
            "name": self.state.identity_name,
            "age": self.age,
            "genome": self.genome.vector(),
            "emotions": self.emotions.state,
            "dominant_emotion": dom_emotion,
            "drives": self.drives.get_state(),
            "active_concepts": self.concept_graph.summary(),
            "episodes_count": len(self.episodic.episodes),
            "beliefs_count": len(self.beliefs.beliefs),
            "prediction_error_avg": self.predictions.average_error(),
            "self_reflection": self.self_model.reflect_on_changes(),
            "identity_conflict": self.self_model.identity_conflict_level(),
            "world_state": self.environment.get_state_summary(),
            "current_chapter": self.autobiography.current_chapter.title if self.autobiography.current_chapter else "None",
        }

    def save_to_file(self, path: str):
        data = {
            "genome": self.genome.vector(),
            "state": self.state.__dict__,
            "concept_graph": {
                "nodes": {nid: (n.label, n.activation, n.emotional_valence) for nid, n in self.concept_graph.nodes.items()},
                "edges": [{"n1": n1, "n2": n2, "weight": w} for (n1,n2), w in self.concept_graph.edges.items()],
            },
            "episodes": [e.__dict__ for e in self.episodic.episodes],
            "memories": [m.__dict__ for m in self.memory.memories],
            "beliefs": [b.__dict__ for b in self.beliefs.beliefs],
            "drives": self.drives.get_state(),
            "emotions": self.emotions.state,
            "causal_graph": self.causal.graph,
            "strategy_genome": self.strategy.strategies,
            "predictions": [{"context": p.context, "expected": p.expected, "confidence": p.confidence,
                             "action": p.action, "actual": p.actual, "error": p.error} for p in self.predictions.predictions],
            "self_model_identity": self.self_model.identity,
            "self_history": self.self_model.self_history,
            "narrative": self.self_model.narrative,
            "autobiography_chapters": [ch.__dict__ for ch in self.autobiography.chapters],
            "age": self.age,
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
        self.last_novel_experience = data.get("last_novel_experience", 0)
        # Геном
        for k, v in data["genome"].items():
            if hasattr(self.genome, k): setattr(self.genome, k, v)
        self.state = SelfState(**data["state"])
        # Граф
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
        self.autobiography.chapters = [LifeChapter(**ch) for ch in data["autobiography_chapters"]]
        if self.autobiography.chapters:
            self.autobiography.current_chapter = self.autobiography.chapters[-1]

# =============================================================================
# 21. LLM-ИНТЕРФЕЙС
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
# 22. FASTAPI СЕРВЕР
# =============================================================================

app = FastAPI(title="SUBJECT_20 — Adaptive Reality Model")
subject = Subject20()

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
    print("SUBJECT_20 запущен. Автономный цикл активен, мир доступен.")

@app.on_event("shutdown")
async def shutdown():
    subject.autonomous_loop.stop()
    subject.save_to_file(Config.STATE_FILE)
    print("SUBJECT_20 остановлен. Состояние сохранено.")

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
    return {"world": subject.environment.get_state_summary()}

# =============================================================================
# 23. ТОЧКА ВХОДА
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
