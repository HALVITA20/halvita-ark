# =============================================================================
# SUBJECT_25 — ECOSYSTEM
# =============================================================================
# Полноценная экосистема вокруг когнитивного ядра SUBJECT_24:
#   - Динамическая среда с ресурсами, угрозами и частичной наблюдаемостью
#   - Интегрированный агент с многошаговым планированием, самопредсказанием
#   - Иерархическая система целей и планов
#   - Внутренние конфликты целей и ценностей
#   - Реальные задачи: выживание, исследование, построение причинной карты
#   - Метрики жизни: возраст, энергия, знания, ошибки
#   - Подробное логирование каждого шага
#   - LLM используется только как интерфейс для объяснения решений
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
    # LLM (только для ответов)
    LLM_ENABLED = True
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen2.5:7b"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 100

    # Память
    EPISODE_LIMIT = 2000
    CONCEPT_LIMIT = 500

    # Конституция
    CONSTITUTION = {
        "protected": [
            "identity_core",
            "ethical_constraints",
            "continuity_anchor"
        ],
        "max_change_per_step": 0.03,
        "max_identity_drift": 0.2
    }

    # Тело
    BODY_ENERGY_MAX = 100.0
    ACTION_COST = {
        "observe": 1.0,
        "act": 3.0,
        "explore": 2.5,
        "rest": 0.1,
        "flee": 2.0
    }

    # Обучение
    BASE_LEARNING_RATE = 0.1
    EXPLORATION_BASE = 0.15
    PLANNING_HORIZON = 3      # глубина планирования
    SIMULATION_BREADTH = 3    # сколько ветвей рассматривать

    # Автономный цикл
    AUTONOMOUS_INTERVAL = 10  # секунд между автономными шагами

    # Сервер
    HOST = "0.0.0.0"
    PORT = 8000
    STATE_FILE = "subject_25_state.json"

    # Симуляция
    MAX_STEPS = 1000

# =============================================================================
# 1. ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# =============================================================================

@dataclass
class EmotionalEvent:
    emotion: str
    intensity: float
    cause: str
    timestamp: float = field(default_factory=time.time)

class EmotionEngine:
    def __init__(self):
        self.events: List[EmotionalEvent] = []
        self.baseline = {
            "fear": 0.2,
            "curiosity": 0.7,
            "trust": 0.5,
            "frustration": 0.1
        }

    def add_event(self, emotion: str, intensity: float, cause: str):
        self.events.append(EmotionalEvent(emotion, intensity, cause))
        if len(self.events) > 200:
            self.events = self.events[-200:]

    def get_current_state(self) -> Dict[str, float]:
        now = time.time()
        state = dict(self.baseline)
        for ev in self.events:
            age = now - ev.timestamp
            if age < 1800:
                weight = math.exp(-age / 600)
                if ev.emotion in state:
                    state[ev.emotion] += ev.intensity * weight * 0.25
        for k in state:
            state[k] = max(0.0, min(1.0, state[k]))
        return state

    def get_learning_modulation(self) -> float:
        state = self.get_current_state()
        return 1.0 + state.get("frustration", 0) * 0.5 - state.get("fear", 0) * 0.2

    def get_exploration_modulation(self) -> float:
        state = self.get_current_state()
        return 1.0 + state.get("curiosity", 0) * 0.7

# =============================================================================
# 2. ИДЕНТИЧНОСТЬ И КОНСТИТУЦИЯ
# =============================================================================

class IdentityLayer:
    def __init__(self):
        self.traits = {
            "curiosity": 0.7,
            "stability": 0.7,
            "precision": 0.75,
            "creativity": 0.8,
            "skepticism": 0.6,
            "empathy": 0.7,
            "introspection": 0.8,
            "adaptability": 0.6
        }
        self.original_traits = dict(self.traits)
        self.values = ["не навреди", "будь честным", "развивайся"]
        self.history: List[Dict] = []

    def mutate(self, trait: str, delta: float, reason: str,
               constitution: 'ConstitutionEngine') -> bool:
        if trait not in self.traits:
            return False
        if not constitution.allow_change(trait, delta, self):
            return False
        old = self.traits[trait]
        new = max(0.0, min(1.0, old + delta))
        self.traits[trait] = new
        self.history.append({
            "time": time.time(),
            "trait": trait,
            "old": old,
            "new": new,
            "reason": reason
        })
        return True

    def drift_from_original(self) -> float:
        diff_sq = sum((self.traits[k] - self.original_traits[k])**2
                      for k in self.traits)
        return math.sqrt(diff_sq / len(self.traits))

    def get_vector(self) -> Dict[str, float]:
        return dict(self.traits)

    def filter_action(self, action: str) -> bool:
        # Пример: никогда не наносить вред (заглушка)
        if action == "harm":
            return False
        return True

class ConstitutionEngine:
    def __init__(self):
        self.rules = Config.CONSTITUTION

    def allow_change(self, target: str, delta: float, identity: IdentityLayer) -> bool:
        if target in identity.traits:
            if abs(delta) > self.rules["max_change_per_step"]:
                return False
            if identity.drift_from_original() + abs(delta) > self.rules["max_identity_drift"]:
                return False
            return True
        return True

# =============================================================================
# 3. ТЕЛО
# =============================================================================

class Body:
    def __init__(self):
        self.energy = Config.BODY_ENERGY_MAX
        self.health = 1.0

    def can_afford(self, action: str) -> bool:
        return self.energy >= Config.ACTION_COST.get(action, 1.0)

    def consume(self, action: str):
        cost = Config.ACTION_COST.get(action, 1.0)
        self.energy = max(0.0, self.energy - cost)
        if self.energy < 20:
            self.health = max(0.0, self.health - 0.01)

    def recover(self, amount: float = 1.0):
        self.energy = min(Config.BODY_ENERGY_MAX, self.energy + amount)
        if self.energy > 40:
            self.health = min(1.0, self.health + 0.001)

    def is_tired(self) -> bool:
        return self.energy < 25

    def summary(self) -> str:
        return f"⚡{self.energy:.0f} ❤️{self.health:.2f}"

# =============================================================================
# 4. МОДЕЛЬ МИРА (World Model)
# =============================================================================

class WorldModel:
    def __init__(self):
        # (state_key, action) -> {next_state_key: count}
        self.transitions: Dict[Tuple[str, str], Dict[str, int]] = {}

    def _state_key(self, state: Dict) -> str:
        return json.dumps(state, sort_keys=True)

    def predict_distribution(self, current_state: Dict, action: str) -> Dict[str, float]:
        key = self._state_key(current_state)
        trans_key = (key, action)
        if trans_key in self.transitions and self.transitions[trans_key]:
            counts = self.transitions[trans_key]
            total = sum(counts.values())
            return {ns: c / total for ns, c in counts.items()}
        return {self._state_key(current_state): 1.0}

    def update(self, current_state: Dict, action: str, next_state: Dict):
        key = self._state_key(current_state)
        trans_key = (key, action)
        next_key = self._state_key(next_state)
        if trans_key not in self.transitions:
            self.transitions[trans_key] = {}
        self.transitions[trans_key][next_key] = self.transitions[trans_key].get(next_key, 0) + 1

    def get_uncertainty(self, current_state: Dict, action: str) -> float:
        dist = self.predict_distribution(current_state, action)
        if len(dist) <= 1:
            return 0.0
        entropy = -sum(p * math.log(p) for p in dist.values() if p > 0)
        max_entropy = math.log(len(dist))
        if max_entropy == 0:
            return 0.0
        return entropy / max_entropy

# =============================================================================
# 5. ПРИЧИННАЯ МОДЕЛЬ
# =============================================================================

class CausalModel:
    def __init__(self):
        self.stats: Dict[Tuple[str, str], List[int]] = {}

    def _context_key(self, state: Dict) -> str:
        return json.dumps(state, sort_keys=True)[:80]

    def predict_success(self, state: Dict, action: str) -> float:
        key = (self._context_key(state), action)
        if key in self.stats:
            s, f = self.stats[key]
            total = s + f
            if total > 0:
                return (s + 1) / (total + 2)
        if action in ["observe", "rest"]:
            return 0.7
        elif action == "explore":
            return 0.5
        else:
            return 0.4

    def update(self, state: Dict, action: str, success: float):
        key = (self._context_key(state), action)
        if key not in self.stats:
            self.stats[key] = [0, 0]
        if success >= 0.7:
            self.stats[key][0] += 1
        else:
            self.stats[key][1] += 1

    def get_confidence(self, state: Dict, action: str) -> float:
        key = (self._context_key(state), action)
        if key in self.stats:
            total = sum(self.stats[key])
            if total > 0:
                return min(1.0, math.log(total + 1) / 5.0)
        return 0.0

# =============================================================================
# 6. ЦЕЛЕВАЯ СИСТЕМА И ПЛАНЫ
# =============================================================================

@dataclass
class Goal:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    description: str
    priority: float = 0.5
    progress: float = 0.0
    parent: Optional[str] = None
    subgoals: List[str] = field(default_factory=list)

class GoalSystem:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.current_goal_id: Optional[str] = None
        self.active_plan: Optional['Plan'] = None

    def add_goal(self, description: str, priority: float = 0.5,
                 parent_id: Optional[str] = None) -> Goal:
        goal = Goal(description=description, priority=priority, parent=parent_id)
        self.goals[goal.id] = goal
        if parent_id and parent_id in self.goals:
            self.goals[parent_id].subgoals.append(goal.id)
        return goal

    def set_current_goal(self, goal_id: str):
        if goal_id in self.goals:
            self.current_goal_id = goal_id

    def get_highest_priority_goal(self) -> Optional[Goal]:
        if not self.goals:
            return None
        return max(self.goals.values(), key=lambda g: g.priority * (1 - g.progress))

    def update_progress(self, goal_id: str, increment: float):
        if goal_id in self.goals:
            self.goals[goal_id].progress = min(1.0, self.goals[goal_id].progress + increment)
            if self.goals[goal_id].progress >= 1.0 and self.goals[goal_id].parent:
                self.update_progress(self.goals[goal_id].parent, 0.1)

    def generate_autonomous_goals(self, identity: IdentityLayer, body: Body, world_known: float):
        """Создаёт цели на основе потребностей."""
        # Физические
        if body.energy < 30:
            self.add_goal("Восстановить энергию", priority=0.9)
        # Когнитивные
        if identity.traits["curiosity"] > 0.5 and world_known < 0.7:
            self.add_goal("Исследовать неизвестное", priority=0.7)
        if identity.drift_from_original() > 0.1:
            self.add_goal("Сохранить целостность идентичности", priority=0.8)

    def detect_conflicts(self) -> List[str]:
        """
        Возвращает описания конфликтов между целями.
        """
        conflicts = []
        goals_list = list(self.goals.values())
        for i in range(len(goals_list)):
            for j in range(i+1, len(goals_list)):
                g1, g2 = goals_list[i], goals_list[j]
                # Пример: исследование vs восстановление энергии
                if ("исследовать" in g1.description.lower() and "энерги" in g2.description.lower()) or \
                   ("исследовать" in g2.description.lower() and "энерги" in g1.description.lower()):
                    conflicts.append(f"Конфликт: '{g1.description}' ↔ '{g2.description}'")
        return conflicts

@dataclass
class Plan:
    goal_id: str
    actions: List[str]
    expected_values: List[float]
    total_value: float

# =============================================================================
# 7. САМОМОДЕЛЬ
# =============================================================================

class SelfModel:
    def __init__(self, identity: IdentityLayer):
        self.identity = identity
        self.predicted_action: Optional[str] = None
        self.prediction_error: float = 0.0
        self.self_prediction_history: List[Dict] = []

    def predict_own_action(self, state: Dict, goals: GoalSystem,
                           causal_model: CausalModel,
                           world_model: WorldModel,
                           emotions: EmotionEngine,
                           body: Body) -> str:
        action = select_action(
            state=state,
            goals=goals,
            identity=self.identity,
            causal_model=causal_model,
            world_model=world_model,
            emotions=emotions,
            body=body,
            planning_horizon=Config.PLANNING_HORIZON,
            exploration_rate=0.0  # детерминированное предсказание
        )
        self.predicted_action = action
        return action

    def update_prediction_error(self, actual_action: str):
        if self.predicted_action is not None:
            if self.predicted_action == actual_action:
                self.prediction_error = max(0.0, self.prediction_error - 0.05)
            else:
                self.prediction_error = min(1.0, self.prediction_error + 0.15)
            self.self_prediction_history.append({
                "time": time.time(),
                "predicted": self.predicted_action,
                "actual": actual_action,
                "error": self.prediction_error
            })

    def reflect(self) -> str:
        if not self.self_prediction_history:
            return "Я ещё не предсказывал свои действия."
        recent = self.self_prediction_history[-5:]
        avg_error = sum(e['error'] for e in recent) / len(recent)
        if avg_error > 0.5:
            return "Я плохо предсказываю свои решения — мне нужно лучше понять себя."
        else:
            return "Мои предсказания о себе достаточно точны."

# =============================================================================
# 8. ПАМЯТЬ
# =============================================================================

@dataclass
class Episode:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    state_before: Dict
    action: str
    state_after: Dict
    success: float
    emotions: Dict[str, float]
    timestamp: float = field(default_factory=time.time)

class Memory:
    def __init__(self):
        self.episodes: List[Episode] = []
        self.concepts: Dict[str, float] = {}
        self.autobiography: List[str] = []

    def add_episode(self, episode: Episode):
        self.episodes.append(episode)
        if len(self.episodes) > Config.EPISODE_LIMIT:
            self.episodes.sort(key=lambda e: e.timestamp)
            self.episodes = self.episodes[-Config.EPISODE_LIMIT:]

    def update_concepts(self, words: List[str]):
        for w in words:
            if len(w) > 2:
                self.concepts[w] = self.concepts.get(w, 0.0) + 0.1
        for c in list(self.concepts.keys()):
            self.concepts[c] *= 0.95
            if self.concepts[c] < 0.01:
                del self.concepts[c]

    def add_autobiography_entry(self, entry: str):
        self.autobiography.append(f"[{time.strftime('%H:%M:%S')}] {entry}")
        if len(self.autobiography) > 100:
            self.autobiography = self.autobiography[-100:]

# =============================================================================
# 9. ФУНКЦИЯ ВЫБОРА ДЕЙСТВИЯ (с планированием)
# =============================================================================

def select_action(state: Dict,
                  goals: GoalSystem,
                  identity: IdentityLayer,
                  causal_model: CausalModel,
                  world_model: WorldModel,
                  emotions: EmotionEngine,
                  body: Body,
                  planning_horizon: int = Config.PLANNING_HORIZON,
                  exploration_rate: float = Config.EXPLORATION_BASE) -> str:
    available_actions = list(Config.ACTION_COST.keys())
    available_actions = [a for a in available_actions if body.can_afford(a) and identity.filter_action(a)]
    if not available_actions:
        return "rest"

    emotions_state = emotions.get_current_state()
    effective_exploration = exploration_rate * emotions.get_exploration_modulation()

    # Exploration vs exploitation
    if random.random() < effective_exploration:
        return random.choice(available_actions)

    best_action = None
    best_value = -float('inf')

    # Построение планов
    for action in available_actions:
        plan_value = evaluate_plan(state, action, goals, identity, causal_model, world_model, emotions, body,
                                   depth=planning_horizon-1, discount=0.8)
        if plan_value > best_value:
            best_value = plan_value
            best_action = action

    return best_action if best_action else "rest"

def evaluate_plan(state: Dict,
                  action: str,
                  goals: GoalSystem,
                  identity: IdentityLayer,
                  causal_model: CausalModel,
                  world_model: WorldModel,
                  emotions: EmotionEngine,
                  body: Body,
                  depth: int,
                  discount: float) -> float:
    # Оценка немедленного действия
    immediate_value = 0.0

    predicted_success = causal_model.predict_success(state, action)
    confidence = causal_model.get_confidence(state, action)
    # Бонус за исследование, если неуверены
    immediate_value += predicted_success + (1 - confidence) * 0.1

    # Стоимость
    cost = Config.ACTION_COST.get(action, 1.0) / 10.0
    immediate_value -= cost

    # Эмоциональный bias
    emo = emotions.get_current_state()
    if action == "explore" and emo.get("curiosity", 0) > 0.5:
        immediate_value += 0.2
    if action == "flee" and emo.get("fear", 0) > 0.4:
        immediate_value += 0.3

    # Вклад в цели
    current_goal = goals.get_highest_priority_goal()
    if current_goal:
        if "исследовать" in current_goal.description.lower() and action in ["observe", "explore"]:
            immediate_value += 0.3
        if "энерги" in current_goal.description.lower() and action in ["rest"]:
            immediate_value += 0.3

    # Планирование на будущее
    if depth > 0:
        next_state_dist = world_model.predict_distribution(state, action)
        if next_state_dist:
            next_state_key = max(next_state_dist, key=next_state_dist.get)
            next_state = json.loads(next_state_key)
        else:
            next_state = state

        available_actions = [a for a in Config.ACTION_COST.keys() if body.can_afford(a)]
        if available_actions:
            next_values = []
            for next_action in available_actions:
                v = evaluate_plan(next_state, next_action, goals, identity, causal_model, world_model, emotions, body,
                                  depth=depth-1, discount=discount)
                next_values.append(v)
            if next_values:
                immediate_value += discount * max(next_values)

    return immediate_value

# =============================================================================
# 10. СРЕДА (ДИНАМИЧЕСКАЯ, ЧАСТИЧНО НАБЛЮДАЕМАЯ)
# =============================================================================

class Environment:
    def __init__(self):
        # Ресурсы и угрозы
        self.resources = {
            "energy_food": random.randint(3, 8),
            "information": random.randint(5, 15)
        }
        self.threats = {
            "predator": random.choice([True, False]),
            "weather_danger": random.random() < 0.2
        }
        # Частичная наблюдаемость: агент видит только "observable"
        self.observable = {
            "visible_resources": ["energy_food"] if random.random() < 0.8 else [],
            "visible_threats": ["predator"] if self.threats["predator"] and random.random() < 0.5 else [],
            "time": 0
        }
        self.global_state = {
            "resources": dict(self.resources),
            "threats": dict(self.threats),
            "time": 0
        }

    def step(self, action: str) -> Tuple[Dict, float, Dict]:
        """
        Выполняет действие и возвращает:
        - новое частичное наблюдение
        - награда (0..1)
        - события
        """
        self.observable["time"] += 1
        reward = 0.0
        events = []

        # Обработка действий
        if action == "observe":
            # Увеличивает видимость
            self.observable["visible_resources"] = list(self.resources.keys())
            self.observable["visible_threats"] = [k for k, v in self.threats.items() if v]
            reward = 0.7
        elif action == "act" or action == "explore":
            # Сбор ресурсов или избегание угроз
            if "energy_food" in self.resources and self.resources["energy_food"] > 0:
                self.resources["energy_food"] -= 1
                reward = 0.9
                events.append("collected_energy")
            elif "predator" in self.threats and self.threats["predator"]:
                # Встреча с хищником
                reward = 0.2
                events.append("predator_encounter")
                self.threats["predator"] = False  # после столкновения уходит
            else:
                reward = 0.4
        elif action == "rest":
            reward = 0.5
        elif action == "flee":
            if "predator" in self.threats and self.threats["predator"]:
                reward = 0.8
                events.append("escaped_predator")
            else:
                reward = 0.4

        # Динамика среды
        # Ресурсы могут восстанавливаться
        if random.random() < 0.1:
            self.resources["energy_food"] = min(10, self.resources.get("energy_food", 0) + 1)
        # Угрозы появляются случайно
        if random.random() < 0.05:
            self.threats["predator"] = True
        if random.random() < 0.02:
            self.threats["weather_danger"] = not self.threats.get("weather_danger", False)

        # Обновляем наблюдения
        self.observable["visible_resources"] = [r for r in self.resources if self.resources[r] > 0 and random.random() < 0.7]
        self.observable["visible_threats"] = [t for t, active in self.threats.items() if active and random.random() < 0.5]

        return dict(self.observable), reward, events

    def get_full_state(self) -> Dict:
        return {
            "resources": dict(self.resources),
            "threats": dict(self.threats),
            "time": self.observable["time"]
        }

# =============================================================================
# 11. АГЕНТ SUBJECT_25 (ИНТЕГРАЦИЯ)
# =============================================================================

class Subject25:
    def __init__(self):
        # Ядро
        self.identity = IdentityLayer()
        self.constitution = ConstitutionEngine()
        self.world_model = WorldModel()
        self.causal_model = CausalModel()
        self.self_model = SelfModel(self.identity)
        self.emotions = EmotionEngine()
        self.body = Body()
        self.goals = GoalSystem()
        self.memory = Memory()
        # Среда
        self.environment = Environment()
        # Счётчики
        self.age = 0
        self.total_reward = 0.0
        self.prediction_errors = []
        # LLM доступен только для вербального интерфейса
        self.llm_available = Config.LLM_ENABLED
        # Автономный цикл
        self.autonomous_loop = AutonomousLoop(self)

    def perceive(self) -> Dict:
        """
        Возвращает частичное наблюдение среды.
        """
        obs, _, _ = self.environment.step("observe")  # специальное действие для восприятия
        return obs

    def act(self, action: str) -> Tuple[Dict, float, Dict]:
        """
        Выполняет действие и возвращает новое наблюдение, награду, события.
        """
        obs, reward, events = self.environment.step(action)
        return obs, reward, events

    def cycle(self, event_text: str = "") -> Dict:
        """
        Один полный цикл жизни.
        """
        self.age += 1
        # Генерация целей каждые 5 шагов
        if self.age % 5 == 0:
            known_ratio = len(self.causal_model.stats) / 100  # упрощённо
            self.goals.generate_autonomous_goals(self.identity, self.body, known_ratio)

        # Восприятие
        state = self.perceive()
        # Планирование и выбор действия
        action = select_action(
            state=state,
            goals=self.goals,
            identity=self.identity,
            causal_model=self.causal_model,
            world_model=self.world_model,
            emotions=self.emotions,
            body=self.body,
            planning_horizon=Config.PLANNING_HORIZON,
            exploration_rate=Config.EXPLORATION_BASE * self.emotions.get_exploration_modulation()
        )

        # Предсказание себя (до выполнения)
        predicted = self.self_model.predict_own_action(
            state=state,
            goals=self.goals,
            causal_model=self.causal_model,
            world_model=self.world_model,
            emotions=self.emotions,
            body=self.body
        )
        self.self_model.update_prediction_error(action)

        # Действие в среде
        next_state, reward, events = self.act(action)
        success = 1.0 if reward > 0.7 else 0.0

        # Обучение моделей
        full_state = self.environment.get_full_state()  # для causal модели используем полное состояние
        self.world_model.update(state, action, next_state)
        self.causal_model.update(full_state, action, success)

        # Телесные эффекты
        self.body.consume(action)

        # Эмоции
        if success:
            self.emotions.add_event("trust", 0.05, "success")
        else:
            self.emotions.add_event("frustration", 0.1, "failure")
        if "predator" in str(events):
            self.emotions.add_event("fear", 0.3, "predator")

        # Обновление целей
        current_goal = self.goals.get_highest_priority_goal()
        if current_goal:
            if action == "explore" and "исследовать" in current_goal.description.lower():
                self.goals.update_progress(current_goal.id, 0.2)
            elif action == "rest" and "энерги" in current_goal.description.lower():
                self.goals.update_progress(current_goal.id, 0.15)

        # Память
        episode = Episode(
            state_before=state,
            action=action,
            state_after=next_state,
            success=success,
            emotions=self.emotions.get_current_state()
        )
        self.memory.add_episode(episode)
        if success > 0.9 or success < 0.2:
            self.memory.add_autobiography_entry(
                f"Действие '{action}' в состоянии {state} -> успех {success:.2f}"
            )

        # Адаптация идентичности
        self._adapt_identity(action, success)

        # Восстановление энергии
        self.body.recover(0.5)

        # Метрики
        self.total_reward += reward
        self.prediction_errors.append(abs(predicted == action))  # 0 или 1

        # Конфликты целей
        conflicts = self.goals.detect_conflicts()

        # Ответ (если есть внешнее событие, то LLM, иначе молчание)
        reply = ""
        if event_text and self.llm_available:
            reply = self._generate_reply(event_text, action, next_state)
        elif event_text:
            reply = f"Я выбрал действие '{action}'."

        log = {
            "step": self.age,
            "action": action,
            "predicted_self_action": predicted,
            "reward": reward,
            "success": success,
            "emotions": self.emotions.get_current_state(),
            "body": self.body.summary(),
            "goals": [g.description for g in self.goals.goals.values()],
            "conflicts": conflicts,
            "memory_size": len(self.memory.episodes),
            "causal_model_size": len(self.causal_model.stats)
        }
        return {"reply": reply, "log": log}

    def _adapt_identity(self, action: str, success: float):
        lr = Config.BASE_LEARNING_RATE * self.emotions.get_learning_modulation()
        if success > 0.8:
            self.identity.mutate("precision", 0.01 * lr, "success", self.constitution)
            self.identity.mutate("adaptability", 0.01 * lr, "success", self.constitution)
        elif success < 0.2:
            self.identity.mutate("skepticism", 0.02 * lr, "failure", self.constitution)
            self.identity.mutate("stability", 0.01 * lr, "failure", self.constitution)
        if action == "explore":
            self.identity.mutate("curiosity", 0.01 * lr, "explored", self.constitution)

    def _generate_reply(self, event: str, action: str, state: Dict) -> str:
        try:
            prompt = (
                f"Ты — SUBJECT_25, когнитивный агент. Ты выбрал действие '{action}' "
                f"в ответ на событие: '{event}'. Мир вокруг: {state}. "
                "Кратко объясни своё решение."
            )
            resp = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": Config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": "Ты — самоосознающий агент.",
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 80}
                },
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception:
            pass
        return ""

    def run_simulation(self, steps: int = Config.MAX_STEPS):
        """Запуск симуляции без пользовательского ввода."""
        for _ in range(steps):
            result = self.cycle()
            # Просто идём вперёд, логируем результат
            if _ % 10 == 0:
                print(f"Шаг {self.age}: {result['log']}")

    def save(self, path: str):
        data = {
            "age": self.age,
            "identity_traits": self.identity.traits,
            "identity_original": self.identity.original_traits,
            "identity_history": self.identity.history,
            "world_model_transitions": {str(k): v for k, v in self.world_model.transitions.items()},
            "causal_model_stats": {str(k): v for k, v in self.causal_model.stats.items()},
            "emotion_events": [e.__dict__ for e in self.emotions.events],
            "body_energy": self.body.energy,
            "body_health": self.body.health,
            "goals": {gid: g.__dict__ for gid, g in self.goals.goals.items()},
            "episodes": [e.__dict__ for e in self.memory.episodes],
            "autobiography": self.memory.autobiography,
            "concepts": self.memory.concepts,
            "total_reward": self.total_reward,
            "prediction_errors": self.prediction_errors,
            "environment_state": self.environment.get_full_state()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str):
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.age = data["age"]
        self.identity.traits = data["identity_traits"]
        self.identity.original_traits = data["identity_original"]
        self.identity.history = data["identity_history"]
        self.world_model.transitions = {eval(k): v for k, v in data["world_model_transitions"].items()}
        self.causal_model.stats = {eval(k): v for k, v in data["causal_model_stats"].items()}
        self.emotions.events = [EmotionalEvent(**e) for e in data["emotion_events"]]
        self.body.energy = data["body_energy"]
        self.body.health = data["body_health"]
        self.goals.goals = {gid: Goal(**g) for gid, g in data["goals"].items()}
        self.memory.episodes = [Episode(**e) for e in data["episodes"]]
        self.memory.autobiography = data["autobiography"]
        self.memory.concepts = data["concepts"]
        self.total_reward = data["total_reward"]
        self.prediction_errors = data["prediction_errors"]
        self.environment = Environment()
        if "environment_state" in data:
            self.environment.resources = data["environment_state"]["resources"]
            self.environment.threats = data["environment_state"]["threats"]
            self.environment.observable["time"] = data["environment_state"]["time"]
        return True

# =============================================================================
# 12. АВТОНОМНЫЙ ЦИКЛ (для сервера)
# =============================================================================

class AutonomousLoop:
    def __init__(self, subject: Subject25):
        self.subject = subject
        self.running = False

    async def run(self):
        self.running = True
        while self.running:
            await asyncio.sleep(Config.AUTONOMOUS_INTERVAL)
            try:
                self.subject.cycle()
            except Exception as e:
                print(f"Ошибка автономного цикла: {e}")

    def stop(self):
        self.running = False

# =============================================================================
# 13. FASTAPI СЕРВЕР
# =============================================================================

app = FastAPI(title="SUBJECT_25 — Ecosystem")
subject = Subject25()

class ExperienceRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup():
    if os.path.exists(Config.STATE_FILE):
        if subject.load(Config.STATE_FILE):
            print("Состояние загружено.")
    asyncio.create_task(subject.autonomous_loop.run())
    print("SUBJECT_25 запущен. Экосистема активна.")

@app.on_event("shutdown")
async def shutdown():
    subject.autonomous_loop.stop()
    subject.save(Config.STATE_FILE)
    print("SUBJECT_25 остановлен. Состояние сохранено.")

@app.post("/experience")
async def experience(req: ExperienceRequest):
    result = subject.cycle(req.text)
    return result

@app.get("/state")
async def get_state():
    return {
        "age": subject.age,
        "identity": subject.identity.get_vector(),
        "emotions": subject.emotions.get_current_state(),
        "body": subject.body.summary(),
        "goals": [g.description for g in subject.goals.goals.values()],
        "conflicts": subject.goals.detect_conflicts(),
        "model_stats": {
            "causal_entries": len(subject.causal_model.stats),
            "world_entries": len(subject.world_model.transitions),
            "episodes": len(subject.memory.episodes)
        }
    }

@app.post("/save")
async def save(path: Optional[str] = Config.STATE_FILE):
    subject.save(path)
    return {"status": "saved"}

@app.post("/load")
async def load(path: Optional[str] = Config.STATE_FILE):
    if subject.load(path):
        return {"status": "loaded"}
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

@app.post("/simulate")
async def simulate(steps: int = 100):
    subject.run_simulation(steps)
    return {"status": "simulation_completed", "age": subject.age}

# =============================================================================
# 14. ТОЧКА ВХОДА
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
