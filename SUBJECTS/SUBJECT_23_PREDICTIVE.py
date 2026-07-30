# =============================================================================
# SUBJECT_23 — PREDICTIVE ACTION CORE
# Версия 23.0 — Обучающийся субъект с самопредсказанием и выбором действий
# =============================================================================
# Инновации по сравнению с SUBJECT_22:
#   - Action Engine с явной оценкой: expected_value, cost, emotional_bias
#   - Причинная модель с вероятностным обучением (обновление при ошибке)
#   - Prediction loop: predict → act → compare → update
#   - SelfModel предсказывает своё действие и вычисляет self-consistency error
#   - Эмоции усиливаются ошибкой предсказания
#   - Выбор действий основан на предсказанной полезности, а не на статических стратегиях
#   - Автономный цикл с самопредсказанием и коррекцией
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
    SELF_QUESTION_INTERVAL = 5 # самовопросы

    # Тело
    BODY_ENERGY_MAX = 100.0
    BODY_ENERGY_DECAY_PER_ACTION = 2.0
    BODY_ENERGY_RECOVERY_PER_TICK = 0.5
    ACTION_COST = {"observe": 1.0, "ask": 0.5, "act": 3.0, "reflect": 0.5}

    # Сервер
    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_23_state.json"

# =============================================================================
# 1. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# =============================================================================

@dataclass
class EmotionalEvent:
    emotion: str
    intensity: float
    cause: str
    target: str = ""
    timestamp: float = field(default_factory=time.time)

class EmotionEngine:
    def __init__(self):
        self.events: List[EmotionalEvent] = []
        self.baseline = {
            "fear": 0.2,
            "curiosity": 0.7,
            "trust": 0.5,
            "frustration": 0.1,
            "attachment": 0.3,
        }

    def add_event(self, emotion: str, intensity: float, cause: str, target: str = ""):
        self.events.append(EmotionalEvent(emotion, intensity, cause, target))
        if len(self.events) > 200:
            self.events = self.events[-200:]

    def get_current_state(self) -> Dict[str, float]:
        now = time.time()
        state = dict(self.baseline)
        for ev in self.events:
            age = now - ev.timestamp
            if age < 3600:
                weight = math.exp(-age / 600)
                if ev.emotion in state:
                    state[ev.emotion] += ev.intensity * weight * 0.2
        for k in state:
            state[k] = max(0.0, min(1.0, state[k]))
        return state

    def dominant(self) -> Tuple[str, float, Optional[EmotionalEvent]]:
        state = self.get_current_state()
        dom = max(state, key=state.get)
        best_event = None
        for ev in reversed(self.events):
            if ev.emotion == dom and ev.intensity > 0.3:
                best_event = ev
                break
        return dom, state[dom], best_event

# =============================================================================
# 2. ТЕЛО
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
# 3. КОНЦЕПТУАЛЬНЫЙ ГРАФ С ПРИЧИННЫМИ РЕБРАМИ
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
        self.edges: Dict[Tuple[str, str], float] = {}
        self.causal_edges: Dict[Tuple[str, str], List[Dict]] = {}

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
        if cause:
            cause_node = self.get_or_create_node(cause)
            self._add_causal_link(cause_node.id, node.id, f"Активация из-за: {cause}")

    def _add_causal_link(self, from_id: str, to_id: str, explanation: str):
        key = (from_id, to_id)
        if key not in self.causal_edges:
            self.causal_edges[key] = []
        self.causal_edges[key].append({"explanation": explanation, "time": time.time()})

    def spread_activation(self, steps: int = 2, decay: float = 0.5):
        for _ in range(steps):
            new_acts = {}
            for (id1, id2), weight in self.edges.items():
                if id1 in self.nodes and id2 in self.nodes:
                    contrib = self.nodes[id1].activation * weight * decay
                    new_acts[id2] = new_acts.get(id2, 0.0) + contrib
            for nid, act in new_acts.items():
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
        return ", ".join([f"{n.label}({n.activation:.2f})" for n in self.get_active_concepts()])

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

    def check(self, subject: 'Subject23') -> bool:
        tension = subject.conflicts.history[-1].get("tension",0.0) if subject.conflicts.history else 0.0
        error = subject.predictions.average_error()
        identity_conflict = subject.self_model.identity_conflict_level()
        if tension > 0.8 or error > 0.5 or identity_conflict > 0.6:
            self.active = True
            self.type = "identity" if identity_conflict > 0.6 else "performance"
            return True
        return False

    def resolve(self, subject: 'Subject23'):
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
# 5. МОДЕЛЬ СЕБЯ (С САМОПРЕДСКАЗАНИЕМ)
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
        # Новое: предсказание собственных действий
        self.predicted_self_action: Optional[str] = None
        self.self_prediction_error: float = 0.0

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
                diffs.append(f"{trait}: {'+' if delta>0 else ''}{delta:.2f}")
        return "Изменения: " + "; ".join(diffs) if diffs else "Стабилен."

    def identity_conflict_level(self) -> float:
        if len(self.self_history) < 2: return 0.0
        old = self.self_history[0]["genome"]
        new = self.self_history[-1]["genome"]
        diff = math.sqrt(sum((new[k]-old[k])**2 for k in old)) / math.sqrt(len(old))
        return min(1.0, diff * 5)

    def predict_own_action(self, subject: 'Subject23', context: str, situation: str) -> str:
        """
        Предсказывает, какое действие субъект выберет в данной ситуации,
        используя стратегию и причинную модель. Возвращает предсказанное действие.
        """
        # Используем ту же логику, что и для внешнего выбора, но без случайности — детерминированно?
        strategy = subject.strategy.get(situation)
        actions = list(strategy.keys())
        # Оценка полезности каждого действия с использованием causal model
        action_scores = {}
        for action in actions:
            pred_success = subject.causal_model.predict(context, action, subject.drives.get_state())
            cost = Config.ACTION_COST.get(action, 1.0)
            emotional_bias = 0.0
            # Эмоциональный сдвиг: например, страх повышает ценность observe, снижает act
            emo_state = subject.emotions.get_current_state()
            if action == "act" and emo_state.get("fear", 0) > 0.4:
                emotional_bias -= 0.3
            elif action == "observe" and emo_state.get("curiosity", 0) > 0.6:
                emotional_bias += 0.2
            # Полезность: предсказанный успех минус нормированная стоимость плюс эмоциональный сдвиг
            normalized_cost = cost / 10.0
            utility = pred_success - normalized_cost + emotional_bias
            action_scores[action] = utility
        # Детерминированно выбираем действие с максимальной полезностью
        if action_scores:
            return max(action_scores, key=action_scores.get)
        else:
            return random.choice(actions)

    def update_self_prediction_error(self, predicted: str, actual: str):
        if predicted == actual:
            self.self_prediction_error = max(0.0, self.self_prediction_error - 0.05)
        else:
            self.self_prediction_error = min(1.0, self.self_prediction_error + 0.1)

    def simulate_mutation(self, subject: 'Subject23', trait: str, delta: float) -> float:
        test_genome = IdentityGenome()
        for t in subject.genome.vector():
            setattr(test_genome, t, getattr(subject.genome, t))
        old = getattr(test_genome, trait)
        new = max(0.0, min(1.0, old + delta))
        setattr(test_genome, trait, new)
        total_reward = 0.0
        situations = ["EXPLORER", "GUARDIAN", "ANALYST", "CREATOR"]
        for _ in range(5):
            situation = random.choice(situations)
            strategy = subject.strategy.get(situation)
            actions = list(strategy.keys())
            action = random.choices(actions, weights=[strategy[a] for a in actions], k=1)[0]
            predicted_success = subject.causal_model.predict(situation, action, subject.drives.get_state())
            total_reward += predicted_success
        return total_reward / 5.0

    def decide_self_modification(self, subject: 'Subject23') -> bool:
        candidates = []
        if subject.predictions.average_error() > 0.4 and subject.genome.precision < 0.9:
            candidates.append(("precision", 0.03))
        if subject.body.is_tired() and subject.genome.stability < 0.9:
            candidates.append(("stability", 0.03))
        if subject.emotions.dominant()[0] == "frustration" and subject.genome.introspection < 0.8:
            candidates.append(("introspection", 0.02))
        best_reward = -1.0
        best_candidate = None
        for trait, delta in candidates:
            sim_reward = self.simulate_mutation(subject, trait, delta)
            if sim_reward > best_reward and sim_reward > subject.causal_model.average_success_rate():
                best_reward = sim_reward
                best_candidate = (trait, delta)
        if best_candidate:
            return subject.genome.mutate(best_candidate[0], best_candidate[1], "self_simulation", subject.constitution)
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
    identity_name: str = "SUBJECT_23"
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
# 10. ПРИЧИННАЯ ПРЕДСКАЗАТЕЛЬНАЯ МОДЕЛЬ (С ОБУЧЕНИЕМ НА ОШИБКАХ)
# =============================================================================

class CausalPredictiveModel:
    def __init__(self):
        self.stats: Dict[Tuple[str, str], List[int]] = {}  # (context_key, action) -> [successes, failures]

    def _context_key(self, context: str, drives: Dict[str, float] = None) -> str:
        drive_str = max(drives.items(), key=lambda x: x[1])[0] if drives else "none"
        return f"{context[:30]}_{drive_str}"

    def predict(self, context: str, action: str, drives: Dict[str, float]) -> float:
        key = (self._context_key(context, drives), action)
        if key in self.stats:
            s, f = self.stats[key]
            total = s + f
            if total > 0:
                return (s + 1) / (total + 2)  # Laplace smoothing
        return 0.5

    def update(self, context: str, action: str, success: float, drives: Dict[str, float]):
        key = (self._context_key(context, drives), action)
        if key not in self.stats:
            self.stats[key] = [0, 0]
        if success > 0.6:
            self.stats[key][0] += 1
        else:
            self.stats[key][1] += 1
        # Limit size
        if len(self.stats) > 1000:
            # Remove oldest? Not implemented, but could prune
            pass

    def average_success_rate(self) -> float:
        total_success = sum(v[0] for v in self.stats.values())
        total_attempts = sum(sum(v) for v in self.stats.values())
        if total_attempts == 0:
            return 0.5
        return total_success / total_attempts

# =============================================================================
# 11. ПРЕДСКАЗАНИЯ (СТАРЫЙ ДВИЖОК ДЛЯ МЕТРИКИ)
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

    def generate(self, context: str, genome: IdentityGenome, drives: Dict[str, float], emotions: EmotionEngine) -> List[InternalVoice]:
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
# 13. СТРАТЕГИЧЕСКИЙ ГЕНОМ (с выбором по полезности)
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

    def choose_action(self, situation: str, causal_model, context: str, drives: Dict[str, float],
                      emotions: Dict[str, float], body: Body) -> str:
        strategy = self.get(situation)
        actions = list(strategy.keys())
        # Оценка полезности
        action_utilities = {}
        for action in actions:
            pred_success = causal_model.predict(context, action, drives) if causal_model else 0.5
            cost = Config.ACTION_COST.get(action, 1.0)
            normalized_cost = cost / 10.0
            emotional_bias = 0.0
            if action == "act" and emotions.get("fear",0) > 0.4:
                emotional_bias -= 0.3
            elif action == "observe" and emotions.get("curiosity",0) > 0.6:
                emotional_bias += 0.2
            utility = pred_success - normalized_cost + emotional_bias
            # Усталость снижает полезность затратных действий
            if body.is_tired() and cost > 1.0:
                utility -= 0.2
            action_utilities[action] = utility
        # Мягкий выбор: смешиваем стратегические веса и полезность
        total_weight = 0.0
        weighted_utilities = {}
        for action in actions:
            w = strategy[action] * max(0.1, action_utilities[action] + 0.5)  # поднимаем в область >0
            weighted_utilities[action] = w
            total_weight += w
        if total_weight == 0:
            return random.choice(actions)
        # Вероятностный выбор
        return random.choices(actions, weights=[weighted_utilities[a] for a in actions], k=1)[0]

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
        self.drives[drive] = max(0.0, min(1.0, old + delta))
        self.history.append({"drive": drive, "old": old, "new": self.drives[drive], "reason": reason})

    def update_hunger(self, subject: 'Subject23'):
        if subject.age - subject.last_novel_experience > 20:
            self.drives["novelty"] = min(1.0, self.drives["novelty"] + 0.05)
        else:
            self.drives["novelty"] *= 0.99
        if subject.state.uncertainty > 0.6:
            self.drives["understanding"] = min(1.0, self.drives["understanding"] + 0.03)
        else:
            self.drives["understanding"] *= 0.99
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

    def sleep(self, organism: 'Subject23') -> Dict:
        self.cycles += 1
        error = organism.predictions.average_error()
        if error > 0.3:
            organism.genome.mutate("skepticism", 0.02, "prediction_error", organism.constitution)
            organism.state.update_uncertainty(error)

        attended = organism.attention.filter_episodes(organism.episodic.episodes, organism.drives.get_state(), organism.emotions.get_current_state())
        for ep in attended:
            ep.strength = min(1.0, ep.strength + 0.03)
            for concept in ep.concepts:
                organism.concept_graph.activate(concept, 0.2)
        organism.concept_graph.spread_activation(steps=3, decay=0.4)

        for usage in organism.strategy_usage[-10:]:
            situation = usage["situation"]
            taken = usage["action"]
            strategy = organism.strategy.get(situation)
            alternatives = [a for a in strategy if a != taken and strategy[a] > 0.1]
            if not alternatives: continue
            alt = random.choice(alternatives)
            predicted = organism.causal_model.predict(usage.get("context", ""), alt, organism.drives.get_state())
            if predicted > 0.6:
                organism.strategy.reward(situation, alt, 0.05, organism.constitution)

        active_nodes = organism.concept_graph.get_active_concepts(0.4)
        for i in range(len(active_nodes)):
            for j in range(i+1, len(active_nodes)):
                organism.concept_graph.strengthen_link(active_nodes[i].label, active_nodes[j].label, 0.03)

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
# 18. ПРИЧИННОЕ ЯДРО (ЛОГ)
# =============================================================================

class CausalCore:
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
        return (f"Я выбрал '{d['action']}', потому что голос '{d['winner']}' "
                f"имел влияние {d['voices'].get(d['winner'], 0):.2f}. Причина: {d['reason']}. "
                f"Эмоции: {d['emotions']}. Тело: {d['body']}.")

    def compare_with_past(self, n_back: int = 5) -> str:
        if len(self.decisions) < n_back + 1:
            return "Недостаточно истории."
        now = self.decisions[-1]
        past = self.decisions[-n_back-1]
        return (f"Раньше я выбрал бы '{past['action']}' (голос '{past['winner']}'). "
                f"Сейчас я выбираю '{now['action']}'. Приоритеты изменились.")

# =============================================================================
# 19. САМОВОПРОСИТЕЛЬНЫЙ ЦИКЛ
# =============================================================================

class SelfQuestioningLoop:
    def __init__(self):
        self.last_asked_age = 0

    def maybe_ask(self, subject: 'Subject23') -> Optional[str]:
        if subject.age - self.last_asked_age < Config.SELF_QUESTION_INTERVAL:
            return None
        self.last_asked_age = subject.age
        questions = []
        if subject.predictions.average_error() > 0.4:
            questions.append("Почему мои предсказания часто ошибаются?")
        if subject.emotions.dominant()[0] == "frustration":
            questions.append("Что вызывает мою фрустрацию и как её уменьшить?")
        if subject.self_model.identity_conflict_level() > 0.5:
            questions.append("Насколько сильно я изменился и сохраняю ли я свою сущность?")
        if not questions:
            questions.append("Какие стратегии мне стоит пересмотреть?")
        question = random.choice(questions)
        subject.memory.add(Memory(content=f"Самовопрос: {question}", importance=0.6, emotional_weight=0.5,
                                  tags=["self_question"]))
        reflection = subject.self_model.reflect_on_changes()
        answer = f"Ответ на '{question}': {reflection}"
        subject.memory.add(Memory(content=answer, importance=0.7, emotional_weight=0.4,
                                  tags=["self_answer"]))
        subject.autobiography.add_lesson(answer)
        return question

# =============================================================================
# 20. ОБЫЧНАЯ ПАМЯТЬ
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
# 21. АВТОНОМНЫЙ ЦИКЛ С ПРЕДСКАЗАНИЕМ
# =============================================================================

class AutonomousLoop:
    def __init__(self, subject: 'Subject23'):
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
        subj.self_model.decide_self_modification(subj)
        question = subj.self_questioning.maybe_ask(subj)

        # Автономное действие с самопредсказанием
        situation = "EXPLORER" if subj.drives.drives.get("curiosity",0) > 0.7 else "GUARDIAN"
        context = "autonomous_step"
        # Самопредсказание
        predicted_action = subj.self_model.predict_own_action(subj, context, situation)
        # Реальный выбор
        chosen_action = subj.strategy.choose_action(situation, subj.causal_model, context, subj.drives.get_state(),
                                                    subj.emotions.get_current_state(), subj.body)
        # Обновление ошибки самопредсказания
        subj.self_model.update_self_prediction_error(predicted_action, chosen_action)

        # Взаимодействие с миром
        world_res, success = subj.environment.step(chosen_action)
        subj.memory.add(Memory(content=f"Авто: {chosen_action}. Мир: {world_res}", importance=0.4,
                               emotional_weight=0.5, tags=["autonomous"]))
        # Обучение
        subj._learn_from_world(context, chosen_action, success, world_res)
        subj.body.consume(Config.ACTION_COST.get(chosen_action, 1.0))

        # Эмоциональное воздействие ошибки самопредсказания
        if subj.self_model.self_prediction_error > 0.3:
            subj.emotions.add_event("frustration", 0.1, "self_prediction_mismatch")
            subj.emotions.add_event("curiosity", 0.05, "desire to understand myself")

        subj.body.recover()

    def stop(self):
        self.running = False

# =============================================================================
# 22. ГЛАВНЫЙ КЛАСС SUBJECT_23
# =============================================================================

class Subject23:
    def __init__(self, environment: EnvironmentAPI = None):
        self.genome = IdentityGenome()
        self.state = SelfState()
        self.concept_graph = ConceptGraph()
        self.episodic = EpisodicMemory()
        self.memory = MemorySystem()
        self.attention = AttentionSystem()
        self.beliefs = BeliefEngine()
        self.causal_model = CausalPredictiveModel()
        self.causal_core = CausalCore()
        self.predictions = PredictionEngine()
        self.conflicts = ConflictEngine()
        self.strategy = StrategyGenome()
        self.drives = DriveEngine()
        self.emotions = EmotionEngine()
        self.self_model = SelfModel()
        self.constitution = ConstitutionEngine()
        self.autobiography = AutobiographicalMemory()
        self.autobiography.start_chapter("Пробуждение", "SUBJECT_23 начинает существование")
        self.developmental_crisis = DevelopmentalCrisis()
        self.environment = environment if environment else SimpleWorld()
        self.body = Body()
        self.dream = DreamEngine()
        self.self_questioning = SelfQuestioningLoop()

        self.age = 0
        self.strategy_usage: List[Dict] = []
        self.last_novel_experience = 0

        self.autonomous_loop = AutonomousLoop(self)

    def experience(self, event: str) -> Dict:
        self.age += 1
        self.state.age = self.age

        # Эмоции
        emotion_scores = self._assess_emotion(event)
        for e, val in emotion_scores.items():
            self.emotions.add_event(e, val, f"событие: {event[:30]}", target=event[:30])

        # Концепты
        words = [w for w in event.lower().split() if len(w) > 2]
        for w in words:
            self.concept_graph.activate(w, 0.5, cause="user_input")
        self.concept_graph.spread_activation(steps=2, decay=0.4)

        # Эпизод
        active_concepts = [n.label for n in self.concept_graph.get_active_concepts(0.3)]
        episode = Episode(context=event, actions=[], outcomes=[], emotions=emotion_scores, concepts=active_concepts)
        self.episodic.add(episode)

        # Конфликт
        voices = self.conflicts.generate(event, self.genome, self.drives.get_state(), self.emotions)
        conflict_result = self.conflicts.resolve(voices)
        if conflict_result["tension"] > 0.7:
            meta = InternalVoice("METACOGNITION", 0.5, "Осознать конфликт")
            voices.append(meta)
            conflict_result = self.conflicts.resolve(voices)

        situation = conflict_result["winner"]
        # Самопредсказание перед реальным выбором
        predicted_action = self.self_model.predict_own_action(self, event, situation)
        # Реальный выбор с использованием новой функции
        chosen_action = self.strategy.choose_action(situation, self.causal_model, event, self.drives.get_state(),
                                                    self.emotions.get_current_state(), self.body)
        self.self_model.update_self_prediction_error(predicted_action, chosen_action)

        self.strategy_usage.append({"situation": situation, "action": chosen_action, "context": event})
        episode.actions.append(chosen_action)

        # Запись в CausalCore
        self.causal_core.record(event, conflict_result["distribution"], situation, chosen_action,
                                conflict_result["reason"], self.emotions.get_current_state(), self.body.summary())

        # Предсказание для метрики
        pred = self.predictions.create(context=event, expected=0.7, confidence=0.6, action=chosen_action)

        # Мир
        world_result, success = self.environment.step(chosen_action)
        episode.outcomes.append(success)
        episode.lesson = f"Действие '{chosen_action}' -> {world_result}"

        error = self.predictions.resolve(pred, success)
        self.state.update_uncertainty(error)

        # Обучение
        self._learn_from_world(event, chosen_action, success, world_result)

        # Тело
        self.body.consume(Config.ACTION_COST.get(chosen_action, 1.0))

        # Ответ через LLM
        llm_prompt = self._build_llm_prompt(event, conflict_result, episode)
        reply = ""
        if Config.LLM_ENABLED:
            reply = query_ollama(llm_prompt, "Ты — SUBJECT_23, обучающийся субъект.")
        if not reply:
            reply = f"[{situation}] {conflict_result['reason']} (мир: {world_result})"

        # Память и автобиография
        self.memory.add(Memory(content=reply, importance=0.7, emotional_weight=0.5,
                               tags=["assistant_response", situation]))
        if success > 0.8 or success < 0.3:
            self.self_model.add_event_to_narrative(f"Важный опыт: {event[:50]}", 0.7)
            self.autobiography.add_lesson(episode.lesson)

        # Кризис
        if self.developmental_crisis.check(self):
            self.developmental_crisis.resolve(self)

        # Сон
        dream_report = None
        if self.age % Config.DREAM_INTERVAL == 0:
            dream_report = self.dream.sleep(self)

        # Голод новизны
        if any(w not in [n.label for n in self.concept_graph.get_active_concepts()] for w in words):
            self.last_novel_experience = self.age

        return {
            "reply": reply,
            "decision": conflict_result,
            "action_taken": chosen_action,
            "world_result": world_result,
            "success": success,
            "prediction_error": error,
            "causal_explanation": self.causal_core.explain_last(),
            "self_prediction": predicted_action,
            "self_prediction_error": self.self_model.self_prediction_error,
            "comparison_with_past": self.causal_core.compare_with_past(),
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
        self.beliefs.add(f"'{action}' приводит к {world_result[:30]}", confidence=success, evidence=[context])
        self.causal_model.update(context, action, success, self.drives.get_state())
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
            "self_prediction_error": self.self_model.self_prediction_error,
            "last_causal_explanation": self.causal_core.explain_last(),
        }
        return (
            f"Ты — SUBJECT_23, обучающийся субъект с самопредсказанием. Твоё состояние: {json.dumps(state, ensure_ascii=False)}\n"
            f"Событие: {event}\n"
            f"Внутренний голос: {conflict['winner']} ({conflict['reason']})\n"
            f"Ты выбрал действие '{episode.actions[-1] if episode.actions else 'none'}'. Сформулируй ответ."
        )

    def state_report(self) -> Dict:
        dom_emotion, val, _ = self.emotions.dominant()
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
            "self_prediction_error": self.self_model.self_prediction_error,
            "average_prediction_error": self.predictions.average_error(),
            "causal_model_accuracy": self.causal_model.average_success_rate(),
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
            "causal_model_stats": {str(k): v for k,v in self.causal_model.stats.items()},
            "causal_core_decisions": self.causal_core.decisions,
            "strategy_genome": self.strategy.strategies,
            "predictions": [{"context": p.context, "expected": p.expected, "confidence": p.confidence,
                             "action": p.action, "actual": p.actual, "error": p.error} for p in self.predictions.predictions],
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
        self.emotions.events = [EmotionalEvent(**e) for e in data["emotion_events"]]
        self.causal_model = CausalPredictiveModel()
        for k_str, v in data["causal_model_stats"].items():
            key = tuple(eval(k_str))
            self.causal_model.stats[key] = v
        self.causal_core.decisions = data["causal_core_decisions"]
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
# 23. LLM ИНТЕРФЕЙС
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
# 24. FASTAPI СЕРВЕР
# =============================================================================

app = FastAPI(title="SUBJECT_23 — Predictive Action Core")
subject = Subject23()

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
    print("SUBJECT_23 запущен. Цикл самопредсказания и обучения активен.")

@app.on_event("shutdown")
async def shutdown():
    subject.autonomous_loop.stop()
    subject.save_to_file(Config.STATE_FILE)
    print("SUBJECT_23 остановлен. Состояние сохранено.")

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
