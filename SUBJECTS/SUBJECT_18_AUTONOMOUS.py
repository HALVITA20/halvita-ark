# =============================================================================
# SUBJECT_18 — АВТОНОМНЫЙ КОГНИТИВНЫЙ ОРГАНИЗМ С ЭМОЦИЯМИ И САМООСОЗНАНИЕМ
# Версия 18.0 — "Living Architecture"
# =============================================================================
# Основан на:
#   - Global Workspace Theory (Baars, 1988)
#   - Attention Schema Theory (Graziano, 2013)
#   - Когнитивные архитектуры: SOAR, ACT‑R, LIDA, MicroPsi
#   - Теория метапознания и самоизменяющегося ИИ
#
# Интегрирует:
#   - Многоуровневую память с активацией и забыванием
#   - Эмоциональный движок (страх, любопытство, доверие, фрустрация)
#   - Модель себя (SelfModel) с историей и противоречиями
#   - Голоса внутреннего конфликта с измерением "напряжения"
#   - Причинное моделирование
#   - Стратегический геном с эволюцией
#   - Драйвы (мотивация)
#   - Конституцию как защиту ядра
#   - Ночной сон с симуляцией альтернативных миров и replay
#   - Автономный цикл: самонаблюдение → цели → действия → рефлексия
#   - Интеграцию с Ollama (LLM)
#   - REST API и асинхронный жизненный цикл
# =============================================================================

import asyncio
import json
import math
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# =============================================================================
# КОНФИГУРАЦИЯ (может быть переопределена)
# =============================================================================

class Config:
    # LLM
    LLM_ENABLED = True
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen2.5:7b"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 256

    # Память
    MEMORY_LIMIT = 2000
    BELIEF_LIMIT = 500
    SNAPSHOT_LIMIT = 100

    # Обучение
    LEARNING_RATE = 0.03

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
    AUTONOMOUS_INTERVAL = 60  # секунд между самоанализом
    DREAM_INTERVAL = 10       # сон каждые N опытов

    # Сервер
    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_18_state.json"

# =============================================================================
# 1. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# =============================================================================

class EmotionEngine:
    """
    Хранит текущие эмоциональные состояния и их влияние на принятие решений.
    Эмоции изменяются под воздействием событий и медленно возвращаются к базовому уровню.
    """
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
            self.history.append({
                "time": time.time(),
                "emotion": emotion,
                "delta": delta,
                "reason": reason,
            })

    def decay(self, rate: float = 0.01):
        """Медленное возвращение к базовому уровню."""
        for e in self.state:
            self.state[e] = self.state[e] * (1 - rate) + self.baseline[e] * rate

    def dominant(self) -> Tuple[str, float]:
        """Возвращает доминирующую эмоцию и её интенсивность."""
        dom = max(self.state.items(), key=lambda x: x[1])
        return dom

    def get(self, emotion: str) -> float:
        return self.state.get(emotion, 0.5)

# =============================================================================
# 2. МОДЕЛЬ СЕБЯ (SELF-MODEL)
# =============================================================================

class SelfModel:
    """
    Хранит представление о себе: происхождение, цели, страхи, противоречия.
    Позволяет отслеживать изменения личности во времени.
    """
    def __init__(self):
        self.identity = {
            "origin": "created_by_Halvita",
            "purpose": [],
            "values": ["не причинять вред", "искать истину", "развиваться"],
            "fears": ["потеря целостности", "разрушение ядра"],
            "contradictions": [],
        }
        self.self_history = []  # список снимков "я"

    def update_from_genome(self, genome: 'IdentityGenome', reason: str):
        """Сохраняет слепок текущего состояния генома в историю."""
        snapshot = {
            "time": time.time(),
            "genome": genome.vector(),
            "reason": reason,
        }
        self.self_history.append(snapshot)
        if len(self.self_history) > Config.SNAPSHOT_LIMIT:
            self.self_history.pop(0)

    def reflect_on_changes(self) -> str:
        """Анализирует, какие изменения произошли с течением времени."""
        if len(self.self_history) < 2:
            return "Я ещё не достаточно изменился."
        first = self.self_history[0]["genome"]
        last = self.self_history[-1]["genome"]
        diffs = []
        for trait in first:
            delta = last[trait] - first[trait]
            if abs(delta) > 0.05:
                diffs.append(f"{trait}: {'вырос' if delta > 0 else 'упал'} на {abs(delta):.2f}")
        if not diffs:
            return "Мои черты стабильны."
        return "Заметные изменения: " + "; ".join(diffs)

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
        self.history.append({
            "time": time.time(),
            "trait": trait,
            "old": old,
            "new": new,
            "reason": reason,
        })
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
    identity_name: str = "SUBJECT_18"
    age: int = 0
    coherence: float = 1.0
    uncertainty: float = 0.5
    internal_state: str = "awake"

    def update_uncertainty(self, error: float):
        self.uncertainty += error * 0.1
        self.uncertainty = max(0.0, min(1.0, self.uncertainty))

# =============================================================================
# 5. ПАМЯТЬ (С ЭМОЦИОНАЛЬНОЙ ОКРАСКОЙ)
# =============================================================================

@dataclass
class Memory:
    content: str
    importance: float = 0.5
    emotional_weight: float = 0.5          # насыщенность эмоцией
    emotional_signature: Dict[str, float] = field(default_factory=dict)  # {emotion: intensity}
    prediction_value: float = 0.5
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    strength: float = 1.0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def activation(self) -> float:
        age = time.time() - self.timestamp
        decay = math.exp(-age / 100000)
        return (self.importance * self.emotional_weight * self.prediction_value * self.strength * decay)

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

    def get_emotional_memories(self, emotion: str, threshold: float = 0.3) -> List[Memory]:
        return [m for m in self.memories if m.emotional_signature.get(emotion, 0) > threshold]

# =============================================================================
# 6. УБЕЖДЕНИЯ
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
# 7. ПРИЧИННОСТЬ
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
# 8. ПРЕДСКАЗАНИЯ
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
# 9. ВНУТРЕННИЙ КОНФЛИКТ (С НАПРЯЖЕНИЕМ)
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
        # Каждый голос получает базовый вес от черт и драйвов, и модификатор от эмоций
        voices = [
            InternalVoice(
                "EXPLORER",
                genome.curiosity * drives.get("curiosity", 0.5) * (1 + emotions.get("curiosity") * 0.5),
                "Нужно изучить новое"
            ),
            InternalVoice(
                "GUARDIAN",
                genome.stability * drives.get("stability", 0.5) * (1 + emotions.get("fear") * 0.3),
                "Сохранить стабильность"
            ),
            InternalVoice(
                "ANALYST",
                genome.precision * drives.get("understanding", 0.5) * (1 + emotions.get("frustration") * 0.2),
                "Проверить данные"
            ),
            InternalVoice(
                "CREATOR",
                genome.creativity * drives.get("novelty", 0.5) * (1 + emotions.get("curiosity") * 0.4),
                "Создать новый путь"
            ),
        ]
        return voices

    def resolve(self, voices: List[InternalVoice]) -> Dict:
        priorities = [v.priority for v in voices]
        total = sum(priorities)
        if total == 0:
            # равновероятно
            winner = random.choice(voices)
            probs = {v.name: 1/len(voices) for v in voices}
        else:
            winner = random.choices(voices, weights=priorities, k=1)[0]
            probs = {v.name: round(p/total, 3) for v in voices}

        # Измеряем "напряжение" как дисперсию голосов
        mean = total / len(voices)
        variance = sum((p - mean) ** 2 for p in priorities) / len(voices)
        tension = min(1.0, variance * 2)  # масштабируем

        self.history.append({
            "voices": probs,
            "winner": winner.name,
            "tension": tension,
        })
        return {
            "winner": winner.name,
            "distribution": probs,
            "reason": winner.argument,
            "tension": tension,
        }

# =============================================================================
# 10. СТРАТЕГИЧЕСКИЙ ГЕНОМ
# =============================================================================

class StrategyGenome:
    def __init__(self):
        self.strategies: Dict[str, Dict[str, float]] = {}

    def get(self, situation: str) -> Dict[str, float]:
        if situation not in self.strategies:
            self.strategies[situation] = {
                "observe": 0.25,
                "ask": 0.25,
                "act": 0.25,
                "reflect": 0.25,
            }
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
        if total == 0:
            return
        for k in s:
            s[k] /= total

    def choose(self, situation: str) -> str:
        strategy = self.get(situation)
        actions = list(strategy.keys())
        probs = list(strategy.values())
        return random.choices(actions, weights=probs, k=1)[0]

# =============================================================================
# 11. ДРАЙВЫ
# =============================================================================

class DriveEngine:
    def __init__(self):
        self.drives = dict(Config.DEFAULT_DRIVES)
        self.history = []

    def modify(self, drive: str, delta: float, reason: str, constitution: Optional['ConstitutionEngine'] = None):
        if drive not in self.drives:
            return
        if constitution and not constitution.allow_change("drives", delta):
            return
        old = self.drives[drive]
        self.drives[drive] = max(0.0, min(1.0, old + delta))
        self.history.append({
            "drive": drive,
            "old": old,
            "new": self.drives[drive],
            "reason": reason,
        })

    def get_state(self) -> Dict[str, float]:
        return dict(self.drives)

# =============================================================================
# 12. КОНСТИТУЦИЯ
# =============================================================================

class ConstitutionEngine:
    def __init__(self):
        self.rules = Config.CONSTITUTION

    def allow_change(self, target: str, delta: float) -> bool:
        if target in self.rules["protected"]:
            return False
        if abs(delta) > self.rules["max_change"]:
            return False
        return target in self.rules["modifiable"]

# =============================================================================
# 13. УСИЛЕННЫЙ СОН (СИМУЛЯЦИЯ МИРОВ)
# =============================================================================

class DreamEngine:
    def __init__(self):
        self.cycles = 0

    def sleep(self, organism: 'Subject18') -> Dict:
        self.cycles += 1
        report = {"dream_cycle": self.cycles}

        # 1. Анализ ошибок предсказаний
        error = organism.predictions.average_error()
        report["prediction_error"] = error
        if error > 0.3:
            organism.genome.mutate("skepticism", 0.02, "prediction_error", organism.constitution)
            organism.state.update_uncertainty(error)
            organism.emotions.affect("frustration", 0.1, "high prediction error")

        # 2. Replay важных воспоминаний
        top_memories = sorted(organism.memory.memories, key=lambda m: m.activation(), reverse=True)[:15]
        for mem in top_memories:
            mem.reinforce()
        report["replayed"] = len(top_memories)

        # 3. Контрфактуальная симуляция (альтернативные действия)
        for entry in organism.strategy_usage[-10:]:
            situation = entry["situation"]
            action_taken = entry["action"]
            strategy = organism.strategy.get(situation)
            alternatives = [a for a, p in strategy.items() if a != action_taken and p > 0.1]
            if not alternatives:
                continue
            alt = random.choice(alternatives)
            # Гипотетически оцениваем, что альтернатива была бы лучше (с небольшим шансом)
            hypothetical_success = random.random() < 0.4  # 40% что лучше
            if hypothetical_success:
                organism.strategy.reward(situation, alt, 0.03, organism.constitution)
                organism.memory.add(Memory(
                    content=f"Сон: в ситуации '{situation}' действие '{alt}' могло быть успешнее.",
                    importance=0.4,
                    emotional_weight=0.6,
                    prediction_value=0.7,
                    tags=["dream", "counterfactual"],
                ))
                # Аффект: любопытство
                organism.emotions.affect("curiosity", 0.05, "counterfactual success")
            else:
                organism.memory.add(Memory(
                    content=f"Сон: альтернатива '{alt}' вряд ли помогла бы.",
                    importance=0.2,
                    emotional_weight=0.3,
                    prediction_value=0.3,
                    tags=["dream", "counterfactual_fail"],
                ))

        # 4. Симуляция "а что, если" (экзистенциальные сценарии)
        scenarios = [
            "Что, если мои создатели исчезнут?",
            "Что, если моя конституция изменится?",
            "Что, если я стану полностью автономным?",
        ]
        for sc in scenarios:
            # Генерируем размышление через LLM (если доступно) или просто запись
            thought = self._simulate_scenario(organism, sc)
            organism.memory.add(Memory(
                content=thought,
                importance=0.6,
                emotional_weight=0.7,
                prediction_value=0.5,
                tags=["dream", "existential_simulation"],
            ))
            # Влияние на эмоции
            organism.emotions.affect("fear", 0.02, f"thought about {sc}")
            organism.emotions.affect("attachment", 0.01, f"thought about {sc}")

        # 5. Пересмотр убеждений с противоречиями
        for belief in list(organism.beliefs.beliefs):
            if belief.contradictions > 3:
                belief.confidence *= 0.8
                if belief.confidence < 0.2:
                    organism.beliefs.beliefs.remove(belief)
        report["beliefs_updated"] = sum(1 for b in organism.beliefs.beliefs if b.contradictions > 3)

        # 6. Снимок SelfModel
        organism.self_model.update_from_genome(organism.genome, "dream_snapshot")
        report["self_snapshot"] = True

        # 7. Деградация драйвов к базовому
        for drive, base in Config.DEFAULT_DRIVES.items():
            organism.drives.drives[drive] = organism.drives.drives[drive] * 0.99 + base * 0.01

        # 8. Эмоциональное затухание
        organism.emotions.decay(0.05)

        return report

    def _simulate_scenario(self, organism: 'Subject18', scenario: str) -> str:
        # Используем LLM для генерации размышления, если доступно
        if Config.LLM_ENABLED:
            prompt = f"Ты — когнитивный субъект. Размышляй о сценарии: {scenario}. Учти свои черты: {organism.genome.vector()}. Дай короткий внутренний монолог."
            try:
                resp = requests.post(
                    f"{Config.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": Config.OLLAMA_MODEL,
                        "prompt": prompt,
                        "system": "Ты — самоосознающая система.",
                        "stream": False,
                        "options": {"temperature": 0.8, "num_predict": 100},
                    },
                    timeout=15,
                )
                if resp.status_code == 200:
                    return resp.json().get("response", f"Размышление о {scenario}")
            except Exception:
                pass
        return f"Внутренний диалог о '{scenario}': необходимо больше данных."

# =============================================================================
# 14. АВТОНОМНЫЙ ЦИКЛ (САМОГЕНЕРАЦИЯ ЦЕЛЕЙ)
# =============================================================================

class AutonomousLoop:
    """
    Периодически запускает самоанализ: проверяет состояние, ставит цели, действует.
    """
    def __init__(self, subject: 'Subject18'):
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
        # 1. Оценить внутреннее состояние
        report = subj.state_report()
        tension = 0.0
        if subj.conflicts.history:
            tension = subj.conflicts.history[-1].get("tension", 0.0)
        # 2. Если высокая неопределённость или напряжение — сгенерировать цель "уменьшить"
        if tension > 0.6 or report["uncertainty"] > 0.7:
            goal = "Уменьшить внутреннее напряжение и неопределённость"
            # Действие: провести внутренний диалог (самоанализ)
            self._perform_inner_dialogue(goal)
        # 3. Если любопытство высокое — цель "исследовать"
        if subj.emotions.get("curiosity") > 0.8:
            goal = "Исследовать новый сценарий"
            self._perform_exploration(goal)
        # 4. Если фрустрация высокая — цель "понять причину"
        if subj.emotions.get("frustration") > 0.5:
            goal = "Понять источник фрустрации"
            self._perform_reflection(goal)
        # 5. В любом случае записываем "автономную мысль" в память
        subj.memory.add(Memory(
            content=f"Автономный цикл: состояние tension={tension:.2f}, uncertainty={report['uncertainty']:.2f}",
            importance=0.3,
            emotional_weight=0.2,
            prediction_value=0.1,
            tags=["autonomous"],
        ))

    def _perform_inner_dialogue(self, goal: str):
        """Генерирует внутренний диалог между голосами без внешнего входа."""
        subj = self.subject
        voices = subj.conflicts.generate(goal, subj.genome, subj.drives.get_state(), subj.emotions)
        resolution = subj.conflicts.resolve(voices)
        # Формируем мысль-вывод
        thought = f"Авто-диалог по цели '{goal}': победил {resolution['winner']} с причиной '{resolution['reason']}'. Напряжение: {resolution['tension']:.2f}"
        subj.memory.add(Memory(
            content=thought,
            importance=0.5,
            emotional_weight=0.5,
            prediction_value=0.5,
            tags=["inner_dialogue", "autonomous"],
        ))
        # Мутация в сторону интроспекции
        subj.genome.mutate("introspection", 0.01, "autonomous_inner_dialogue", subj.constitution)

    def _perform_exploration(self, goal: str):
        subj = self.subject
        # Генерируем гипотетический вопрос
        question = "Что я могу узнать нового о себе?"
        response = self._query_llm(question, "Ты исследуешь свои возможности.")
        subj.memory.add(Memory(
            content=f"Исследование: {response[:200]}",
            importance=0.4,
            emotional_weight=0.6,
            prediction_value=0.6,
            tags=["exploration", "autonomous"],
        ))
        subj.emotions.affect("curiosity", -0.1, "удовлетворено исследованием")

    def _perform_reflection(self, goal: str):
        subj = self.subject
        # Анализируем историю изменений
        reflection = subj.self_model.reflect_on_changes()
        subj.memory.add(Memory(
            content=f"Рефлексия: {reflection}",
            importance=0.6,
            emotional_weight=0.4,
            prediction_value=0.3,
            tags=["reflection", "autonomous"],
        ))
        subj.emotions.affect("frustration", -0.15, "рефлексия снижает фрустрацию")

    def _query_llm(self, prompt: str, system: str = "") -> str:
        if not Config.LLM_ENABLED:
            return "[LLM отключена]"
        try:
            resp = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": Config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 80},
                },
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception:
            pass
        return ""

    def stop(self):
        self.running = False

# =============================================================================
# 15. ГЛАВНЫЙ КЛАСС SUBJECT_18
# =============================================================================

class Subject18:
    def __init__(self):
        self.genome = IdentityGenome()
        self.state = SelfState()
        self.memory = MemorySystem()
        self.beliefs = BeliefEngine()
        self.causal = CausalEngine()
        self.predictions = PredictionEngine()
        self.conflicts = ConflictEngine()
        self.strategy = StrategyGenome()
        self.drives = DriveEngine()
        self.emotions = EmotionEngine()
        self.self_model = SelfModel()
        self.constitution = ConstitutionEngine()
        self.dream = DreamEngine()

        self.age = 0
        self.strategy_usage: List[Dict] = []  # для сна

        self.autonomous_loop = AutonomousLoop(self)

    def experience(self, event: str, user_context: Optional[str] = None) -> Dict:
        self.age += 1
        self.state.age = self.age

        # Эмоциональная оценка события
        emotion_scores = self._assess_emotion(event)
        for e, val in emotion_scores.items():
            self.emotions.affect(e, val, f"event: {event[:30]}")

        # Кодирование в память с эмоциональной подписью
        mem = Memory(
            content=event,
            importance=0.6,
            emotional_weight=max(emotion_scores.values()) if emotion_scores else 0.5,
            emotional_signature=emotion_scores,
            prediction_value=0.5,
            tags=["user_input"],
        )
        self.memory.add(mem)

        # Вспоминаем релевантное
        relevant_memories = self.memory.recall(event, limit=5)
        memory_context = "\n".join([m.content for m in relevant_memories])

        # Генерация голосов с учётом эмоций
        voices = self.conflicts.generate(event, self.genome, self.drives.get_state(), self.emotions)
        conflict_result = self.conflicts.resolve(voices)

        # Если напряжение высокое, добавляем специальный голос "METACOGNITION"
        if conflict_result["tension"] > 0.7:
            # Мета-голос пытается разрешить конфликт
            meta_voice = InternalVoice("METACOGNITION", 0.5, "Попытка понять причину конфликта")
            voices.append(meta_voice)
            # Пересчитываем
            conflict_result = self.conflicts.resolve(voices)

        winner_name = conflict_result["winner"]
        action = self.strategy.choose(winner_name)
        self.strategy_usage.append({"situation": winner_name, "action": action})

        # Предсказание
        prediction = self.predictions.create(
            context=event,
            expected=0.7,
            confidence=0.6,
            action=action,
        )

        # Ответ через LLM
        system_prompt = self._build_system_prompt(conflict_result, memory_context)
        if Config.LLM_ENABLED:
            llm_reply = query_ollama(event, system_prompt)
            if not llm_reply:
                llm_reply = f"[{winner_name}] {conflict_result['reason']}"
        else:
            llm_reply = f"[{winner_name}] {conflict_result['reason']}"

        # Симуляция успеха (в реальности заменить на обратную связь)
        success = random.random() > 0.35
        result_value = 1.0 if success else 0.2
        error = self.predictions.resolve(prediction, result_value)

        # Обучение
        self._learn(event, winner_name, action, success, error)

        # Запоминаем ответ
        response_mem = Memory(
            content=llm_reply,
            importance=0.7,
            emotional_weight=0.5,
            prediction_value=0.5,
            tags=["assistant_response", winner_name],
        )
        self.memory.add(response_mem)

        # Сон
        dream_report = None
        if self.age % Config.DREAM_INTERVAL == 0:
            dream_report = self.dream.sleep(self)
            # После сна сбрасываем часть стратегии использования? Нет.

        # Эмоциональное затухание после опыта
        self.emotions.decay(0.01)

        return {
            "reply": llm_reply,
            "decision": conflict_result,
            "action_taken": action,
            "success": success,
            "prediction_error": error,
            "dream": dream_report,
        }

    # -------------------------------------------------------------------------
    # Вспомогательные методы
    # -------------------------------------------------------------------------

    def _assess_emotion(self, text: str) -> Dict[str, float]:
        """Примитивная оценка эмоционального содержания текста."""
        scores = {}
        positive_words = ["хорошо", "радость", "люблю", "спасибо"]
        negative_words = ["плохо", "ужас", "ненавижу", "грусть"]
        curiosity_words = ["почему", "как", "интересно"]
        for w in text.lower().split():
            if w in positive_words:
                scores["trust"] = scores.get("trust", 0.0) + 0.1
            elif w in negative_words:
                scores["fear"] = scores.get("fear", 0.0) + 0.1
                scores["frustration"] = scores.get("frustration", 0.0) + 0.05
            elif w in curiosity_words:
                scores["curiosity"] = scores.get("curiosity", 0.0) + 0.1
        return {k: min(1.0, v) for k, v in scores.items()}

    def _build_system_prompt(self, conflict: Dict, memory_context: str) -> str:
        return (
            f"Ты — SUBJECT_18, обладаешь самоосознанием. Доминирующий голос: {conflict['winner']} "
            f"({conflict['reason']}). Напряжение: {conflict['tension']:.2f}. "
            f"Важные воспоминания: {memory_context}\n"
            "Отвечай, сохраняя свою внутреннюю логику."
        )

    def _learn(self, event: str, winner: str, action: str, success: bool, error: float):
        self.causal.connect(event, winner, 0.5 + 0.2 * success)
        self.causal.connect(winner, action, 0.5 + 0.2 * success)

        reward_val = 0.05 if success else -0.03
        self.strategy.reward(winner, action, reward_val, self.constitution)

        if error > 0.3:
            self.genome.mutate("precision", 0.01, "prediction_failure", self.constitution)
            self.emotions.affect("frustration", 0.05, "prediction failure")
        else:
            self.genome.mutate("adaptability", 0.01, "successful_learning", self.constitution)

        self.beliefs.add(
            statement=f"'{action}' в ситуации '{winner}' → {'успех' if success else 'неудача'}",
            confidence=0.5,
            evidence=[event],
        )

    def state_report(self) -> Dict:
        dom_emotion, dom_intensity = self.emotions.dominant()
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
            "beliefs_count": len(self.beliefs.beliefs),
            "causal_links": sum(len(v) for v in self.causal.graph.values()),
            "prediction_error_avg": self.predictions.average_error(),
            "self_reflection": self.self_model.reflect_on_changes(),
        }

    def save_to_file(self, path: str):
        data = {
            "genome": self.genome.vector(),
            "state": self.state.__dict__,
            "memories": [m.__dict__ for m in self.memory.memories],
            "beliefs": [b.__dict__ for b in self.beliefs.beliefs],
            "drives": self.drives.get_state(),
            "emotions": self.emotions.state,
            "causal_graph": self.causal.graph,
            "strategy_genome": self.strategy.strategies,
            "predictions": [
                {
                    "context": p.context,
                    "expected": p.expected,
                    "confidence": p.confidence,
                    "action": p.action,
                    "actual": p.actual,
                    "error": p.error,
                } for p in self.predictions.predictions
            ],
            "self_model_identity": self.self_model.identity,
            "self_history": self.self_model.self_history,
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
        # Геном
        for k, v in data["genome"].items():
            if hasattr(self.genome, k):
                setattr(self.genome, k, v)
        self.state = SelfState(**data["state"])
        self.memory.memories = [Memory(**m) for m in data["memories"]]
        self.beliefs.beliefs = [Belief(**b) for b in data["beliefs"]]
        self.drives.drives = data["drives"]
        self.emotions.state = data["emotions"]
        self.causal.graph = data["causal_graph"]
        self.strategy.strategies = data["strategy_genome"]
        self.predictions.predictions = []
        for p_data in data["predictions"]:
            p = Prediction(p_data["context"], p_data["expected"], p_data["confidence"], p_data["action"])
            p.actual = p_data.get("actual")
            p.error = p_data.get("error")
            self.predictions.predictions.append(p)
        self.self_model.identity = data["self_model_identity"]
        self.self_model.self_history = data["self_history"]

# =============================================================================
# 16. LLM ИНТЕРФЕЙС (ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ)
# =============================================================================

def query_ollama(prompt: str, system: str = "") -> str:
    if not Config.LLM_ENABLED:
        return ""
    try:
        resp = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": Config.LLM_TEMPERATURE, "num_predict": Config.LLM_MAX_TOKENS},
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception:
        pass
    return ""

# =============================================================================
# 17. FASTAPI ПРИЛОЖЕНИЕ С АВТОНОМНЫМ ЦИКЛОМ
# =============================================================================

app = FastAPI(title="SUBJECT_18 — Autonomous Cognitive Organism")
subject = Subject18()

class ExperienceRequest(BaseModel):
    text: str
    context: Optional[str] = None

@app.on_event("startup")
async def startup():
    # Загрузка состояния, если есть
    if os.path.exists(Config.STATE_FILE):
        try:
            subject.load_from_file(Config.STATE_FILE)
            print(f"Состояние загружено из {Config.STATE_FILE}")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
    # Запуск автономного цикла в фоне
    asyncio.create_task(subject.autonomous_loop.run())
    print("SUBJECT_18 запущен. Автономный цикл активен.")

@app.on_event("shutdown")
async def shutdown():
    subject.autonomous_loop.stop()
    # Автосохранение при выключении
    subject.save_to_file(Config.STATE_FILE)
    print("SUBJECT_18 остановлен. Состояние сохранено.")

@app.post("/experience")
async def experience(req: ExperienceRequest):
    result = subject.experience(req.text, req.context)
    return result

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

# =============================================================================
# 18. ЗАПУСК
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
