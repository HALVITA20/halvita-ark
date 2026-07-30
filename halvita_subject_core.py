#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA-СУБЪЕКТ_3.0 — САМОЭВОЛЮЦИОНИРУЮЩЕЕ ЯДРО
================================================================================
Этот модуль представляет собой единое, законченное ядро субъекта,
реализующее Δ-Спираль, стратегическое мышление, память, генерацию целей,
мультиагентную оркестрацию и RL-обучение с самоизменением.

Ключевые идеи:
- Стратегия (нейросеть) изменяет пространство решений.
- Каждое действие меняет стратегию.
- Память сохраняет опыт с эмбеддингами.
- Генератор целей усложняет задачи по мере обучения.
- Пять агентов (анализатор, генератор, критик, исследователь, синтезатор) обрабатывают состояние.
- Мир моделируется (заглушка, но легко заменить на реальный симулятор или LLM).

Запуск:
    python halvita_subject_core.py

После завершения цикла выводится статистика и сохраняется финальная память.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
import json
import os
from datetime import datetime

# ------------------------------------------------------------------------------
# 1. НЕЙРОСЕТЕВЫЕ КОМПОНЕНТЫ (СТРАТЕГИЯ И ПРОСТРАНСТВО)
# ------------------------------------------------------------------------------

class StrategyNet(nn.Module):
    """Сеть, формирующая латентное представление состояния — стратегию мышления."""
    def __init__(self, state_size, latent_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, latent_size)
        )

    def forward(self, x):
        return self.net(x)


class SpaceGenerator(nn.Module):
    """Генерирует пространство возможных действий на основе стратегии."""
    def __init__(self, latent_size, action_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_size, 128),
            nn.ReLU(),
            nn.Linear(128, action_size)
        )

    def forward(self, z):
        return self.net(z)


class HalvitaEngine:
    """
    Δ-Спиральное ядро.
    Каждый цикл: стратегия → пространство решений → действие → обновление.
    """
    def __init__(self, state_size=32, latent_size=64, action_size=10, lr=1e-3):
        self.strategy = StrategyNet(state_size, latent_size)
        self.space = SpaceGenerator(latent_size, action_size)
        self.optimizer = optim.Adam(
            list(self.strategy.parameters()) + list(self.space.parameters()),
            lr=lr
        )
        self.action_size = action_size
        self.latent_size = latent_size
        self.state_size = state_size

    def forward(self, state):
        z = self.strategy(state)
        logits = self.space(z)
        return torch.softmax(logits, dim=-1)

    def act(self, state):
        probs = self.forward(state)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        return action.item(), probs

    def update(self, reward, probs, action):
        loss = -torch.log(probs[action]) * reward
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def mutate(self, noise_scale=0.01):
        """Мутация стратегии — самоизменение."""
        for param in self.strategy.parameters():
            param.data += torch.randn_like(param) * noise_scale
        for param in self.space.parameters():
            param.data += torch.randn_like(param) * noise_scale

    def save(self, path):
        torch.save({
            'strategy': self.strategy.state_dict(),
            'space': self.space.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)

    def load(self, path):
        data = torch.load(path)
        self.strategy.load_state_dict(data['strategy'])
        self.space.load_state_dict(data['space'])
        self.optimizer.load_state_dict(data['optimizer'])


# ------------------------------------------------------------------------------
# 2. ПАМЯТЬ
# ------------------------------------------------------------------------------

class Memory:
    """Хранит историю взаимодействий с возможностью эмбеддингов."""
    def __init__(self, max_size=1000, use_embeddings=False):
        self.data = deque(maxlen=max_size)
        self.use_embeddings = use_embeddings
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                print("⚠️ sentence-transformers не установлен, эмбеддинги отключены.")
                self.use_embeddings = False

    def add(self, item, text=None):
        if self.use_embeddings and text and hasattr(self, 'encoder'):
            emb = self.encoder.encode(text).tolist()
            item['embedding'] = emb
        self.data.append(item)

    def sample(self, n=10):
        if len(self.data) == 0:
            return []
        return random.sample(list(self.data), min(n, len(self.data)))

    def __len__(self):
        return len(self.data)

    def to_list(self):
        return list(self.data)

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(list(self.data), f, indent=2, ensure_ascii=False)

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.data = deque(json.load(f), maxlen=self.data.maxlen)


# ------------------------------------------------------------------------------
# 3. ГЕНЕРАТОР ЦЕЛЕЙ
# ------------------------------------------------------------------------------

class GoalGenerator:
    """Динамически генерирует цели на основе опыта."""
    def __init__(self):
        self.goals = ["explore", "optimize", "break", "expand", "create", "criticize"]
        self.thresholds = {
            "explore": 5,
            "optimize": 10,
            "break": 20,
            "expand": 30,
            "create": 50,
            "criticize": 70
        }

    def generate(self, memory):
        experience = len(memory)
        # Постепенное усложнение целей
        available = [g for g, t in self.thresholds.items() if experience >= t]
        if not available:
            available = ["explore"]
        return random.choice(available)


# ------------------------------------------------------------------------------
# 4. МОДЕЛЬ МИРА (ЗАГЛУШКА, НО РАСШИРЯЕМАЯ)
# ------------------------------------------------------------------------------

class WorldModel:
    """
    Симуляция среды. Может быть заменена на реальный симулятор или LLM.
    """
    def __init__(self, state_size=32):
        self.state_size = state_size

    def step(self, action):
        # Простая зависимость награды от действия (можно усложнить)
        reward = np.clip(action / 10.0 + random.uniform(-0.2, 0.2), -1, 1)
        # Следующее состояние — случайное, но можно сделать детерминированным
        next_state = np.random.randn(self.state_size).tolist()
        return {
            "reward": reward,
            "state": next_state
        }

    def predict(self, action):
        # Для планирования (пока заглушка)
        return {"reward": 0.0, "risk": 0.0}


# ------------------------------------------------------------------------------
# 5. АГЕНТЫ
# ------------------------------------------------------------------------------

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def act(self, state, memory):
        return state


class Analyzer(BaseAgent):
    def act(self, state, memory):
        state['analysis'] = f"Analysed by {self.name}"
        return state


class Generator(BaseAgent):
    def act(self, state, memory):
        state['candidates'] = [random.randint(0, 9) for _ in range(3)]
        return state


class Critic(BaseAgent):
    def act(self, state, memory):
        state['critique'] = "OK" if random.random() > 0.3 else "Needs improvement"
        return state


class Explorer(BaseAgent):
    def act(self, state, memory):
        state['exploration'] = random.uniform(-0.1, 0.1)
        return state


class Synthesizer(BaseAgent):
    def act(self, state, memory):
        # Синтезирует финальное действие
        state['final'] = state.get('candidates', [0])[0]
        return state


# ------------------------------------------------------------------------------
# 6. ФУНКЦИЯ НАГРАДЫ
# ------------------------------------------------------------------------------

def compute_reward(action, result, goal):
    """Награда с учётом текущей цели."""
    base = result.get("reward", 0.0)
    if goal == "explore":
        bonus = abs(action - 5) * 0.1  # поощряем отход от середины
    elif goal == "optimize":
        bonus = 0.2 if action % 2 == 0 else -0.1
    elif goal == "break":
        bonus = 0.3 if action > 7 else -0.1
    elif goal == "expand":
        bonus = 0.15 * (action / 10.0)
    elif goal == "create":
        bonus = 0.2 if action in [3, 7] else 0.0
    elif goal == "criticize":
        bonus = -0.1 if action < 3 else 0.1
    else:
        bonus = 0.0
    return base + bonus


# ------------------------------------------------------------------------------
# 7. ОРКЕСТРАТОР (ГЛАВНЫЙ ЦИКЛ)
# ------------------------------------------------------------------------------

class Orchestrator:
    """
    Управляет всеми компонентами, запускает циклы обучения.
    """
    def __init__(self, state_size=32, action_size=10, use_embeddings=False):
        self.engine = HalvitaEngine(state_size, latent_size=64, action_size=action_size)
        self.memory = Memory(max_size=1000, use_embeddings=use_embeddings)
        self.goal_gen = GoalGenerator()
        self.world = WorldModel(state_size=state_size)
        self.state = torch.randn(state_size)
        self.action_size = action_size
        self.step_count = 0

        # Инициализация агентов
        self.agents = [
            Analyzer("Analyzer"),
            Generator("Generator"),
            Critic("Critic"),
            Explorer("Explorer"),
            Synthesizer("Synthesizer")
        ]

    def run_cycle(self):
        """Один шаг эволюции."""
        goal = self.goal_gen.generate(self.memory)
        state_dict = {"goal": goal, "raw_state": self.state.tolist()}

        # Прогон через агентов
        for agent in self.agents:
            state_dict = agent.act(state_dict, self.memory)

        # Выбор действия
        if "final" not in state_dict:
            action, probs = self.engine.act(self.state)
        else:
            action = state_dict["final"]
            _, probs = self.engine.act(self.state)

        # Шаг в мире
        result = self.world.step(action)
        reward = compute_reward(action, result, goal)

        # Обновление ядра
        loss = self.engine.update(reward, probs, action)

        # Сохранение в память
        self.memory.add({
            "step": self.step_count,
            "goal": goal,
            "action": action,
            "reward": reward,
            "state": self.state.tolist(),
            "result": result,
            "loss": loss
        }, text=f"Goal: {goal}, Action: {action}, Reward: {reward:.3f}")

        # Обновление состояния
        self.state = torch.FloatTensor(result["state"])

        # Периодическая мутация для исследования новых стратегий
        if self.step_count % 100 == 0 and self.step_count > 0:
            self.engine.mutate(noise_scale=0.005)
            print(f"🧬 Мутация на шаге {self.step_count}")

        self.step_count += 1
        return reward, loss

    def run(self, steps=1000, print_every=50, save_path=None):
        """Основной цикл обучения."""
        print(f"🚀 Запуск HALVITA-СУБЪЕКТ_3.0 на {steps} шагов...")
        start_time = datetime.now()

        rewards = []
        losses = []

        for step in range(steps):
            reward, loss = self.run_cycle()
            rewards.append(reward)
            losses.append(loss)

            if step % print_every == 0:
                avg_reward = np.mean(rewards[-print_every:]) if rewards else 0
                print(f"[{step:4d}] reward={reward:.3f} | avg={avg_reward:.3f} | loss={loss:.4f}")

        elapsed = datetime.now() - start_time
        print(f"✅ Цикл завершён за {elapsed.total_seconds():.1f} сек.")
        print(f"📊 Средняя награда за последние 100 шагов: {np.mean(rewards[-100:]):.3f}")

        # Сохранение результатов
        if save_path:
            self.save(save_path)

        return rewards, losses

    def save(self, path):
        """Сохраняет состояние ядра и память."""
        os.makedirs(path, exist_ok=True)
        self.engine.save(os.path.join(path, 'engine.pt'))
        self.memory.save(os.path.join(path, 'memory.json'))
        with open(os.path.join(path, 'config.json'), 'w') as f:
            json.dump({
                'step_count': self.step_count,
                'action_size': self.action_size,
                'state_size': self.engine.state_size,
                'latent_size': self.engine.latent_size,
            }, f, indent=2)
        print(f"💾 Сохранено в {path}")

    def load(self, path):
        """Загружает состояние ядра и память."""
        self.engine.load(os.path.join(path, 'engine.pt'))
        self.memory.load(os.path.join(path, 'memory.json'))
        with open(os.path.join(path, 'config.json'), 'r') as f:
            config = json.load(f)
            self.step_count = config['step_count']
        print(f"📂 Загружено из {path}")


# ------------------------------------------------------------------------------
# 8. ТОЧКА ВХОДА
# ------------------------------------------------------------------------------

def main():
    """Запуск демонстрационного цикла."""
    # Параметры
    STATE_SIZE = 32
    ACTION_SIZE = 10
    STEPS = 2000
    PRINT_EVERY = 100
    SAVE_PATH = "subject_save"

    # Создаём систему
    system = Orchestrator(
        state_size=STATE_SIZE,
        action_size=ACTION_SIZE,
        use_embeddings=False  # можно включить, если установлен sentence-transformers
    )

    # Запускаем
    rewards, losses = system.run(steps=STEPS, print_every=PRINT_EVERY, save_path=SAVE_PATH)

    # Краткая статистика
    print("\n📈 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"  - Средняя награда: {np.mean(rewards):.3f}")
    print(f"  - Максимальная награда: {np.max(rewards):.3f}")
    print(f"  - Количество шагов: {len(rewards)}")
    print(f"  - Размер памяти: {len(system.memory)} записей")

    print("\n🧠 Субъект готов к дальнейшему развитию.")


if __name__ == "__main__":
    main()
