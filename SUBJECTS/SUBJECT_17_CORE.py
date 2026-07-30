# subject_17_server.py
# =============================================================================
# SUBJECT_17 – КОГНИТИВНЫЙ СЕРВЕР С АВТОНОМНЫМ САМОИЗМЕНЕНИЕМ
# Версия 17.1 – Законченная система
# =============================================================================
# Интегрирует:
#   - память с активацией и забыванием
#   - убеждения с подкреплением
#   - причинную сеть
#   - предсказательное обучение
#   - внутренние конфликты
#   - стратегический геном
#   - драйвы (мотивацию)
#   - конституцию (ограничения самоизменения)
#   - ночной сон (консолидация, replay, counterfactuals)
#   - REST API для взаимодействия
#   - интеграцию с Ollama (LLM)
#   - сохранение / загрузку состояния
# =============================================================================

import asyncio
import json
import math
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# =============================================================================
# 1. КОНФИГУРАЦИЯ
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

    # Сон
    DREAM_INTERVAL = 10  # каждые N опытов

    # Сервер
    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_17_state.json"

# =============================================================================
# 2. ЯДРО ЛИЧНОСТИ (ГЕНОМ)
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
        """
        Мутирует черту, если это разрешено конституцией.
        Возвращает True, если изменение было применено.
        """
        if not hasattr(self, trait):
            return False

        # Проверка через конституцию (цель изменения – trait)
        if not constitution.allow_change(trait, delta):
            return False

        old = getattr(self, trait)
        new = old + delta
        new = max(0.0, min(1.0, new))
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
# 3. САМОСОСТОЯНИЕ
# =============================================================================

@dataclass
class SelfState:
    identity_name: str = "SUBJECT_17"
    age: int = 0
    coherence: float = 1.0          # непрерывность личности
    uncertainty: float = 0.5        # мера неуверенности
    emotional_load: float = 0.0     # текущая эмоциональная нагрузка
    current_goal: str = ""
    internal_state: str = "initialization"

    def update_uncertainty(self, error: float):
        self.uncertainty += error * 0.1
        self.uncertainty = max(0.0, min(1.0, self.uncertainty))

    def damage_continuity(self, amount: float):
        self.coherence -= amount
        self.coherence = max(0.0, min(1.0, self.coherence))

# =============================================================================
# 4. ПАМЯТЬ
# =============================================================================

@dataclass
class Memory:
    content: str
    importance: float = 0.5
    emotional_weight: float = 0.5
    prediction_value: float = 0.5
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    strength: float = 1.0

    def activation(self) -> float:
        age = time.time() - self.timestamp
        decay = math.exp(-age / 100000)  # медленное затухание
        return (
            self.importance *
            self.emotional_weight *
            self.prediction_value *
            self.strength *
            decay
        )

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
        # удаляем 10% наименее активных
        self.memories.sort(key=lambda m: m.activation())
        remove = int(len(self.memories) * 0.1)
        self.memories = self.memories[remove:]

    def recall(self, query: str, limit: int = 5) -> List[Memory]:
        words = query.lower().split()
        scored = []
        for m in self.memories:
            score = m.activation()
            for w in words:
                if w in m.content.lower():
                    score *= 1.5
            scored.append((score, m))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:limit]]

    def recent(self, n: int = 20) -> List[Memory]:
        return sorted(self.memories, key=lambda m: m.timestamp, reverse=True)[:n]

    def get_all(self) -> List[Dict]:
        return [m.__dict__ for m in self.memories]

# =============================================================================
# 5. УБЕЖДЕНИЯ
# =============================================================================

@dataclass
class Belief:
    statement: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    contradictions: int = 0
    created: float = field(default_factory=time.time)
    stability: float = 0.5

class BeliefEngine:
    def __init__(self):
        self.beliefs: List[Belief] = []

    def add(self, statement: str, confidence: float, evidence: List[str]):
        for b in self.beliefs:
            if b.statement == statement:
                # обновляем существующее
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

    def strongest(self, n: int = 5) -> List[Belief]:
        return sorted(self.beliefs, key=lambda x: x.confidence, reverse=True)[:n]

# =============================================================================
# 6. ПРИЧИННОСТЬ
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

    def explain(self, effect: str) -> List[Dict]:
        result = []
        for cause, links in self.graph.items():
            for link in links:
                if link["effect"] == effect:
                    result.append({"cause": cause, "weight": link["weight"]})
        return sorted(result, key=lambda x: x["weight"], reverse=True)

# =============================================================================
# 7. ПРЕДСКАЗАНИЯ
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
# 8. ВНУТРЕННИЙ КОНФЛИКТ
# =============================================================================

@dataclass
class InternalVoice:
    name: str
    priority: float
    argument: str

class ConflictEngine:
    def __init__(self):
        self.history: List[Dict] = []

    def generate(self, context: str, genome: IdentityGenome, drives: Dict[str, float]) -> List[InternalVoice]:
        voices = [
            InternalVoice("EXPLORER", genome.curiosity * drives.get("curiosity", 0.5), "Исследовать новое"),
            InternalVoice("GUARDIAN", genome.stability * drives.get("stability", 0.5), "Сохранить стабильность"),
            InternalVoice("ANALYST", genome.precision * drives.get("understanding", 0.5), "Проверить данные"),
            InternalVoice("CREATOR", genome.creativity * drives.get("novelty", 0.5), "Создать новый путь"),
        ]
        return voices

    def resolve(self, voices: List[InternalVoice]) -> Dict:
        total = sum(v.priority for v in voices)
        if total == 0:
            # равные вероятности
            winner = random.choice(voices)
            probs = {v.name: 1/len(voices) for v in voices}
        else:
            winner = random.choices(voices, weights=[v.priority for v in voices], k=1)[0]
            probs = {v.name: round(v.priority / total, 3) for v in voices}
        self.history.append({"voices": probs, "winner": winner.name})
        return {"winner": winner.name, "distribution": probs, "reason": winner.argument}

# =============================================================================
# 9. СТРАТЕГИЧЕСКИЙ ГЕНОМ
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
        """
        Изменяет вес действия, если разрешено конституцией.
        """
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
# 10. ДРАЙВЫ
# =============================================================================

class DriveEngine:
    def __init__(self):
        self.drives = dict(Config.DEFAULT_DRIVES)
        self.history: List[Dict] = []

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
# 11. КОНСТИТУЦИЯ
# =============================================================================

class ConstitutionEngine:
    def __init__(self):
        self.rules = Config.CONSTITUTION

    def allow_change(self, target: str, delta: float) -> bool:
        """
        Проверяет, можно ли изменить `target` на `delta`.
        target может быть именем черты, "strategies", "drives" и т.д.
        """
        # Защищённые
        if target in self.rules["protected"]:
            return False
        # Максимальное изменение
        if abs(delta) > self.rules["max_change"]:
            return False
        # Должно быть в списке разрешённых
        return target in self.rules["modifiable"]

# =============================================================================
# 12. ДВИЖОК СНА (КОНСОЛИДАЦИЯ ОПЫТА)
# =============================================================================

class DreamEngine:
    def __init__(self):
        self.cycles = 0

    def sleep(self, organism: 'Subject17') -> Dict:
        """
        Ночная консолидация опыта.
        Выполняет:
          - повтор важных воспоминаний (replay)
          - контрфактуальное размышление
          - пересмотр убеждений
          - адаптацию стратегий
          - сохранение снимка личности
        """
        self.cycles += 1
        report = {"dream_cycle": self.cycles}

        # --- Анализ ошибок предсказаний ---
        error = organism.predictions.average_error()
        report["prediction_error"] = error
        if error > 0.3:
            organism.genome.mutate("skepticism", 0.02, "prediction_error", organism.constitution)
            organism.state.update_uncertainty(error)

        # --- Replay: усиление самых активных воспоминаний ---
        top_memories = sorted(organism.memory.memories, key=lambda m: m.activation(), reverse=True)[:10]
        for mem in top_memories:
            mem.reinforce()
        report["replayed_memories"] = len(top_memories)

        # --- Контрфактуальный анализ последних действий ---
        recent_actions = organism.strategy_usage[-10:]  # последние 10 ситуаций/действий
        for entry in recent_actions:
            situation = entry["situation"]
            action_taken = entry["action"]
            strategy = organism.strategy.get(situation)
            for alt_action, prob in strategy.items():
                if alt_action == action_taken or prob < 0.15:
                    continue
                # если альтернатива была бы успешнее (гипотетически), немного повысим её вес
                organism.strategy.reward(situation, alt_action, 0.02, organism.constitution)
                # запоминаем идею как контрфактуальную
                organism.memory.add(Memory(
                    content=f"Контрфакт: вместо '{action_taken}' можно было '{alt_action}' в ситуации '{situation}'.",
                    importance=0.3,
                    emotional_weight=0.4,
                    prediction_value=0.6,
                    tags=["counterfactual"],
                ))

        # --- Пересмотр убеждений с противоречиями ---
        for belief in organism.beliefs.beliefs:
            if belief.contradictions > 3:
                belief.confidence *= 0.8
                if belief.confidence < 0.2:
                    organism.beliefs.beliefs.remove(belief)
        report["beliefs_updated"] = sum(1 for b in organism.beliefs.beliefs if b.contradictions > 3)

        # --- Снимок личности ---
        organism.history.save(organism)
        report["snapshot_saved"] = True

        # --- Лёгкая деградация драйвов (возврат к базе) ---
        for drive, base in Config.DEFAULT_DRIVES.items():
            current = organism.drives.drives[drive]
            organism.drives.drives[drive] = current * 0.99 + base * 0.01

        return report

# =============================================================================
# 13. ИСТОРИЯ ЛИЧНОСТИ
# =============================================================================

class SelfHistory:
    def __init__(self):
        self.snapshots: List[Dict] = []

    def save(self, organism: 'Subject17'):
        snapshot = {
            "time": time.time(),
            "genome": organism.genome.vector(),
            "beliefs_count": len(organism.beliefs.beliefs),
            "coherence": organism.state.coherence,
        }
        self.snapshots.append(snapshot)
        if len(self.snapshots) > Config.SNAPSHOT_LIMIT:
            self.snapshots.pop(0)

# =============================================================================
# 14. LLM ИНТЕРФЕЙС
# =============================================================================

def query_ollama(prompt: str, system_prompt: str = "") -> str:
    """Синхронный вызов Ollama API."""
    if not Config.LLM_ENABLED:
        return ""
    try:
        resp = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": Config.LLM_TEMPERATURE,
                    "num_predict": Config.LLM_MAX_TOKENS,
                },
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception:
        pass
    return ""

# =============================================================================
# 15. ГЛАВНЫЙ КЛАСС – SUBJECT 17
# =============================================================================

class Subject17:
    def __init__(self):
        # Ядро
        self.genome = IdentityGenome()
        self.state = SelfState()
        self.memory = MemorySystem()
        self.beliefs = BeliefEngine()
        self.causal = CausalEngine()
        self.predictions = PredictionEngine()
        self.conflicts = ConflictEngine()
        self.strategy = StrategyGenome()
        self.drives = DriveEngine()
        self.history = SelfHistory()
        self.dream = DreamEngine()
        self.constitution = ConstitutionEngine()

        self.age = 0
        self.strategy_usage: List[Dict] = []  # для сна

    # -------------------------------------------------------------------------
    # Основной цикл опыта
    # -------------------------------------------------------------------------

    def experience(self, event: str, user_context: Optional[str] = None) -> Dict:
        """
        Принимает событие (текст пользователя) и возвращает ответ системы.
        """
        self.age += 1
        self.state.age = self.age

        # 1. Кодирование в память
        mem = Memory(
            content=event,
            importance=0.6,
            emotional_weight=self._estimate_emotion(event),
            prediction_value=0.5,
            tags=["user_input"],
        )
        self.memory.add(mem)

        # 2. Вспоминаем релевантный контекст
        relevant_memories = self.memory.recall(event, limit=5)
        memory_context = "\n".join([m.content for m in relevant_memories])

        # 3. Внутренний конфликт (голоса)
        voices = self.conflicts.generate(event, self.genome, self.drives.get_state())
        conflict_result = self.conflicts.resolve(voices)
        winner_name = conflict_result["winner"]

        # 4. Выбор стратегии для выигравшего голоса
        action = self.strategy.choose(winner_name)
        self.strategy_usage.append({"situation": winner_name, "action": action})

        # 5. Предсказание результата
        prediction = self.predictions.create(
            context=event,
            expected=0.7,
            confidence=0.6,
            action=action,
        )

        # 6. Генерация текстового ответа через LLM
        system_prompt = self._build_system_prompt(conflict_result, memory_context)
        if Config.LLM_ENABLED:
            llm_reply = query_ollama(event, system_prompt)
            if not llm_reply:
                llm_reply = f"[{winner_name}] {conflict_result['reason']} (LLM недоступен)"
        else:
            llm_reply = f"[{winner_name}] {conflict_result['reason']}"

        # 7. Симуляция успеха (заглушка – в реальности нужно заменить оценкой от пользователя/среды)
        success = random.random() > 0.35  # базовый порог успеха
        result_value = 1.0 if success else 0.2

        # 8. Обновление предсказания и обучение
        error = self.predictions.resolve(prediction, result_value)
        self._learn(event, winner_name, action, success, error)

        # 9. Сохранение ответа в память
        response_mem = Memory(
            content=llm_reply,
            importance=0.7,
            emotional_weight=0.5,
            prediction_value=0.5,
            tags=["assistant_response", winner_name],
        )
        self.memory.add(response_mem)

        # 10. Сон, если пора
        if self.age % Config.DREAM_INTERVAL == 0:
            dream_report = self.dream.sleep(self)
        else:
            dream_report = None

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

    def _estimate_emotion(self, text: str) -> float:
        # Простейшая оценка эмоциональной окраски (0=негатив, 1=позитив)
        pos_words = ["хорошо", "радость", "отлично", "люблю"]
        neg_words = ["плохо", "ужас", "ненавижу", "грусть"]
        score = 0.5
        for w in text.lower().split():
            if w in pos_words:
                score += 0.1
            elif w in neg_words:
                score -= 0.1
        return max(0.0, min(1.0, score))

    def _build_system_prompt(self, conflict: Dict, memory_context: str) -> str:
        return (
            f"Ты – когнитивная система SUBJECT_17. Твоя текущая цель определяется голосом '{conflict['winner']}': "
            f"{conflict['reason']}.\n"
            f"Важные воспоминания:\n{memory_context}\n"
            "Отвечай осмысленно, сохраняя свою внутреннюю логику."
        )

    def _learn(self, event: str, winner: str, action: str, success: bool, error: float):
        # Причинность
        self.causal.connect(event, winner, 0.5 + 0.2 * success)
        self.causal.connect(winner, action, 0.5 + 0.2 * success)

        # Стратегия
        reward_val = 0.05 if success else -0.03
        self.strategy.reward(winner, action, reward_val, self.constitution)

        # Геном
        if error > 0.3:
            self.genome.mutate("precision", 0.01, "prediction_failure", self.constitution)
        else:
            self.genome.mutate("adaptability", 0.01, "successful_learning", self.constitution)

        # Убеждения
        self.beliefs.add(
            statement=f"Действие '{action}' в ситуации '{winner}' даёт {'успех' if success else 'неудачу'}",
            confidence=0.5,
            evidence=[event],
        )

    def state_report(self) -> Dict:
        return {
            "name": self.state.identity_name,
            "age": self.age,
            "genome": self.genome.vector(),
            "coherence": self.state.coherence,
            "uncertainty": self.state.uncertainty,
            "memory_count": len(self.memory.memories),
            "beliefs_count": len(self.beliefs.beliefs),
            "drives": self.drives.get_state(),
            "causal_links": sum(len(v) for v in self.causal.graph.values()),
            "prediction_error_avg": self.predictions.average_error(),
        }

    def save_to_file(self, path: str):
        data = {
            "name": self.state.identity_name,
            "age": self.age,
            "genome": self.genome.vector(),
            "state": self.state.__dict__,
            "memories": self.memory.get_all(),
            "beliefs": [b.__dict__ for b in self.beliefs.beliefs],
            "drives": self.drives.get_state(),
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
            "history_snapshots": self.history.snapshots,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл состояния {path} не найден")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.age = data["age"]
        # Геном
        for k, v in data["genome"].items():
            if hasattr(self.genome, k):
                setattr(self.genome, k, v)
        # Состояние
        self.state = SelfState(**data["state"])
        # Память
        self.memory.memories = [Memory(**m) for m in data["memories"]]
        # Убеждения
        self.beliefs.beliefs = [Belief(**b) for b in data["beliefs"]]
        # Драйвы
        self.drives.drives = data["drives"]
        # Причинность
        self.causal.graph = data["causal_graph"]
        # Стратегии
        self.strategy.strategies = data["strategy_genome"]
        # Предсказания (восстанавливаем как объекты Prediction)
        self.predictions.predictions = []
        for p_data in data["predictions"]:
            p = Prediction(p_data["context"], p_data["expected"], p_data["confidence"], p_data["action"])
            p.actual = p_data.get("actual")
            p.error = p_data.get("error")
            self.predictions.predictions.append(p)
        # История
        self.history.snapshots = data["history_snapshots"]

# =============================================================================
# 16. FASTAPI СЕРВЕР
# =============================================================================

app = FastAPI(title="SUBJECT_17 Cognitive Server")

# Глобальный экземпляр субъекта
subject = Subject17()

# Модели запросов
class ExperienceRequest(BaseModel):
    text: str
    context: Optional[str] = None

class SaveRequest(BaseModel):
    path: Optional[str] = Config.STATE_FILE

class LoadRequest(BaseModel):
    path: Optional[str] = Config.STATE_FILE

@app.on_event("startup")
async def startup():
    # При старте пытаемся загрузить состояние из файла по умолчанию, если он есть
    if os.path.exists(Config.STATE_FILE):
        try:
            subject.load_from_file(Config.STATE_FILE)
            print(f"Состояние загружено из {Config.STATE_FILE}")
        except Exception as e:
            print(f"Не удалось загрузить состояние: {e}")
    print("SUBJECT_17 сервер запущен")

@app.post("/experience")
async def experience(req: ExperienceRequest):
    result = subject.experience(req.text, req.context)
    return result

@app.get("/state")
async def get_state():
    return subject.state_report()

@app.post("/save")
async def save_state(req: SaveRequest):
    path = req.path or Config.STATE_FILE
    subject.save_to_file(path)
    return {"status": "saved", "path": path}

@app.post("/load")
async def load_state(req: LoadRequest):
    path = req.path or Config.STATE_FILE
    try:
        subject.load_from_file(path)
        return {"status": "loaded", "path": path}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл состояния не найден")

@app.get("/health")
async def health():
    return {"status": "ok", "age": subject.age}

# =============================================================================
# 17. ТОЧКА ВХОДА
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
