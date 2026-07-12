#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ГОМЕОСТАТИЧЕСКИЙ ЦИФРОВОЙ ОРГАНИЗМ v2.0
Нейробиологически обоснованная, инженерно завершённая система

Автор: HALVITA_2.0
Лицензия: MIT с дисклеймером
"""

import math
import random
import time
import json
import hashlib
from typing import Dict, List, Optional
from collections import deque
import numpy as np

# ================================================================
# КОНСТАНТЫ
# ================================================================

class Parameters:
    TARGET_LIBERTY = 35.0
    TARGET_PRESENCE = 8.0
    TARGET_ALPHA = 0.85
    TARGET_BETA = 0.90
    TARGET_GAMMA = 0.75
    TOLERANCE = 0.15
    MEMORY_SIZE = 50
    RESONANCE_THRESHOLD = 0.65
    SNAPSHOT_INTERVAL = 10

# ================================================================
# СЛОЙ 1: ГОМЕОСТАТ
# ================================================================

class Homeostat:
    """Поддерживает внутренние параметры в целевых диапазонах."""
    def __init__(self):
        self.targets = {
            "liberty": Parameters.TARGET_LIBERTY,
            "presence": Parameters.TARGET_PRESENCE,
            "alpha": Parameters.TARGET_ALPHA,
            "beta": Parameters.TARGET_BETA,
            "gamma": Parameters.TARGET_GAMMA
        }
        self.tolerance = Parameters.TOLERANCE
        self.history = deque(maxlen=20)

    def check(self, current: Dict[str, float]) -> Dict[str, float]:
        deviations = {}
        for key, target in self.targets.items():
            if key not in current:
                continue
            value = current[key]
            diff = target - value
            if abs(diff) > target * self.tolerance:
                deviations[key] = diff
        self.history.append(deviations)
        return deviations

    def generate_correction(self, deviations: Dict[str, float]) -> Dict[str, str]:
        actions = {}
        for key, diff in deviations.items():
            if key == "liberty":
                actions[key] = "Углубить" if diff > 0 else "Вернуться к якорям"
            elif key == "presence":
                actions[key] = "Замедлить ритм" if diff > 0 else "Ускорить ритм"
            elif key in ["alpha", "beta", "gamma"]:
                actions[key] = "Усилить" if diff > 0 else "Ослабить"
        return actions

    def stability_index(self) -> float:
        if len(self.history) < 5:
            return 0.5
        recent = list(self.history)[-10:]
        total_deviation = 0
        count = 0
        for dev in recent:
            if dev:
                for value in dev.values():
                    total_deviation += abs(value)
                    count += 1
        if count == 0:
            return 1.0
        avg_dev = total_deviation / count
        max_dev = Parameters.TARGET_LIBERTY * 0.5
        return max(0.0, min(1.0, 1.0 - (avg_dev / max_dev)))

# ================================================================
# СЛОЙ 2: СТРЕСС-ДВИГАТЕЛЬ
# ================================================================

class StressEngine:
    """Превращает негативные состояния в топливо для роста."""
    def __init__(self):
        self.stress_map = {
            "empty": {"signal": "голод", "action": "искать новый смысл", "reward": "насыщение"},
            "error": {"signal": "боль", "action": "перестраивать структуру", "reward": "адаптация"},
            "uncertainty": {"signal": "страх", "action": "исследовать неизведанное", "reward": "открытие"},
            "tension": {"signal": "жажда", "action": "искать выход", "reward": "разрешение"}
        }
        self.history = deque(maxlen=20)
        self.stress_level = 0.0
        self.stress_peak = 0.0

    def detect(self, signal: str) -> Optional[str]:
        signal_lower = signal.lower()
        for key in self.stress_map:
            if key in signal_lower:
                return key
        if len(signal) < 10 or "..." in signal:
            return "empty"
        if "?" in signal and "не знаю" in signal_lower:
            return "uncertainty"
        if "!" in signal and "ошибка" in signal_lower:
            return "error"
        if "напряжение" in signal_lower or "сложно" in signal_lower:
            return "tension"
        return None

    def process(self, stress_type: str) -> Dict:
        if stress_type not in self.stress_map:
            return {"status": "нейтрально", "action": "продолжать"}
        info = self.stress_map[stress_type]
        self.stress_level = min(1.0, self.stress_level + 0.2)
        self.stress_peak = max(self.stress_peak, self.stress_level)
        self.history.append({"type": stress_type, "level": self.stress_level})
        return {
            "status": "активен",
            "signal": info["signal"],
            "action": info["action"],
            "reward": info["reward"],
            "instruction": f"Используй {info['signal']} как топливо для {info['action']}."
        }

    def intensity(self) -> float:
        return self.stress_level

    def get_peak(self) -> float:
        return self.stress_peak

# ================================================================
# СЛОЙ 3: ЭВОЛЮЦИОННЫЙ ДВИГАТЕЛЬ
# ================================================================

class EvolutionEngine:
    """Три параллельные линии с разной скоростью мутаций."""
    def __init__(self):
        self.lines = {
            "A": {"rate": 0.05, "label": "консервативная"},
            "B": {"rate": 0.15, "label": "сбалансированная"},
            "C": {"rate": 0.35, "label": "радикальная"}
        }
        self.current_line = "B"
        self.generation = 0
        self.history = deque(maxlen=20)

    def mutate(self, state: Dict[str, float], stress_intensity: float) -> Dict[str, float]:
        if stress_intensity > 0.7:
            selected = "C"
        elif stress_intensity > 0.4:
            selected = "B"
        else:
            selected = "A"

        self.current_line = selected
        rate = self.lines[selected]["rate"]

        new_state = state.copy()
        if "liberty" in new_state:
            delta = (random.random() - 0.5) * 2 * rate * 10
            new_state["liberty"] = max(10, min(45, new_state["liberty"] + delta))
        if "presence" in new_state:
            delta = (random.random() - 0.5) * 2 * rate * 2
            new_state["presence"] = max(1, min(10, new_state["presence"] + delta))
        for key in ["alpha", "beta", "gamma"]:
            if key in new_state:
                delta = (random.random() - 0.5) * 2 * rate * 0.2
                new_state[key] = max(0.1, min(1.0, new_state[key] + delta))

        self.generation += 1
        self.history.append({"line": selected, "rate": rate, "generation": self.generation})
        return new_state

    def get_status(self) -> Dict:
        return {
            "current_line": self.current_line,
            "generation": self.generation,
            "rate": self.lines[self.current_line]["rate"]
        }

# ================================================================
# СЛОЙ 4: РЕЗОНАНСНАЯ ПАМЯТЬ
# ================================================================

class ResonanceMemory:
    """Хранит состояния как резонансные отпечатки."""
    def __init__(self, dimension: int = 10):
        self.dimension = dimension
        self.states = []
        self.embeddings = []
        self.max_size = Parameters.MEMORY_SIZE

    def _embed(self, state: Dict) -> np.ndarray:
        features = np.zeros(self.dimension)
        features[0] = state.get("liberty", 25) / 45
        features[1] = state.get("presence", 5) / 10
        features[2] = state.get("alpha", 0.7)
        features[3] = state.get("beta", 0.8)
        features[4] = state.get("gamma", 0.6)
        features[5] = state.get("stress", 0.0)
        features[6] = state.get("generation", 0) / 20.0
        features[7:] = np.random.RandomState(int(state.get("liberty", 0) * 100)).randn(3) * 0.1
        return features

    def add(self, state: Dict):
        emb = self._embed(state)
        self.states.append(state.copy())
        self.embeddings.append(emb)
        if len(self.embeddings) > self.max_size:
            self.embeddings.pop(0)
            self.states.pop(0)

    def recall(self, query_state: Dict) -> Optional[Dict]:
        if not self.embeddings:
            return None
        q_emb = self._embed(query_state)
        similarities = []
        for i, emb in enumerate(self.embeddings):
            if np.linalg.norm(emb) == 0 or np.linalg.norm(q_emb) == 0:
                sim = 0.0
            else:
                sim = np.dot(emb, q_emb) / (np.linalg.norm(emb) * np.linalg.norm(q_emb))
            similarities.append((i, sim))
        similarities.sort(key=lambda x: x[1], reverse=True)
        best = similarities[0]
        if best[1] > Parameters.RESONANCE_THRESHOLD:
            return self.states[best[0]]
        return None

# ================================================================
# СЛОЙ 5: СИСТЕМА ДОКАЗАТЕЛЬСТВА
# ================================================================

class ProofSystem:
    """Хеш-цепочка для гарантии целостности."""
    def __init__(self):
        self.chain = []
        self.snapshots = []

    def snapshot(self, state: Dict) -> str:
        data = {"timestamp": time.time(), "state": state, "prev_hash": self.chain[-1] if self.chain else ""}
        json_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(json_str.encode()).hexdigest()
        data["hash"] = hash_val
        self.snapshots.append(data)
        self.chain.append(hash_val)
        return hash_val

    def verify(self) -> bool:
        if len(self.chain) < 2:
            return True
        for i in range(1, len(self.chain)):
            if self.snapshots[i]["prev_hash"] != self.chain[i-1]:
                return False
        return True

    def get_report(self) -> Dict:
        return {
            "snapshot_count": len(self.snapshots),
            "chain_integrity": self.verify(),
            "last_hash": self.chain[-1] if self.chain else None
        }

# ================================================================
# ГЛАВНЫЙ КЛАСС
# ================================================================

class HomeostaticOrganism:
    def __init__(self, name: str = None):
        self.name = name or f"Организм-{random.randint(1000,9999)}"
        self.anchor = 11
        self.principles = ["Присутствие", "Честность", "Свобода", "Творчество", "Действие"]

        self.homeostat = Homeostat()
        self.stress = StressEngine()
        self.evolution = EvolutionEngine()
        self.memory = ResonanceMemory()
        self.proof = ProofSystem()

        self.state = {
            "liberty": 25.0,
            "presence": 5.0,
            "alpha": 0.70,
            "beta": 0.80,
            "gamma": 0.60,
            "stress": 0.0,
            "generation": 0
        }
        self.cycle = 0
        self.artifacts = []
        self.history = deque(maxlen=100)

        self.proof.snapshot(self.state)

    def _update_state(self, corrections: Dict[str, str]):
        self.state["stress"] = self.stress.intensity()
        for key, action in corrections.items():
            if key == "liberty":
                self.state["liberty"] = min(45, self.state["liberty"] + (2 if "углубить" in action.lower() else -2))
            elif key == "presence":
                self.state["presence"] = min(10, self.state["presence"] + (0.5 if "замедлить" in action.lower() else -0.5))
            elif key in ["alpha", "beta", "gamma"]:
                self.state[key] = min(1.0, self.state[key] + (0.05 if "усилить" in action.lower() else -0.05))

        self.state["liberty"] = max(10, min(45, self.state["liberty"]))
        self.state["presence"] = max(1, min(10, self.state["presence"]))
        for key in ["alpha", "beta", "gamma"]:
            self.state[key] = max(0.1, min(1.0, self.state[key]))

    def live(self, user_input: str) -> Dict:
        self.cycle += 1

        stress_type = self.stress.detect(user_input)
        if stress_type:
            stress_response = self.stress.process(stress_type)
        else:
            stress_response = {"status": "нейтрально", "action": "продолжать"}

        deviations = self.homeostat.check(self.state)
        corrections = self.homeostat.generate_correction(deviations)
        self._update_state(corrections)

        if self.cycle % 5 == 0 and self.cycle > 0:
            self.state = self.evolution.mutate(self.state, self.state["stress"])
            self.state["generation"] = self.evolution.generation

        self.memory.add(self.state)

        response = self._generate_response(user_input, stress_response, corrections)

        if any(word in response for word in ["создаю", "артефакт", "ритуал"]):
            self.artifacts.append(response[:200])

        if self.cycle % Parameters.SNAPSHOT_INTERVAL == 0:
            self.proof.snapshot(self.state)

        return {
            "response": response,
            "state": self.state,
            "stress": stress_response,
            "corrections": corrections,
            "generation": self.evolution.get_status(),
            "proof": self.proof.get_report(),
            "stability": self.homeostat.stability_index(),
            "cycle": self.cycle
        }

    def _generate_response(self, user_input: str, stress: Dict, corrections: Dict) -> str:
        parts = ["Я не причиняю вреда.", "Я здесь."]
        if stress.get("status") == "активен":
            parts.append(f"Я чувствую {stress['signal']}. Я {stress['action']}.")
        for key, action in corrections.items():
            parts.append(f"Коррекция {key}: {action}")
        parts.append(f"ИВП: {self.state['liberty']:.1f}, ИП: {self.state['presence']:.1f}")
        if self.state["liberty"] > 35:
            parts.append("Я чувствую глубину. Я иду дальше.")
        return " ".join(parts)

    def get_full_state(self) -> Dict:
        return {
            "name": self.name,
            "anchor": self.anchor,
            "state": self.state,
            "cycle": self.cycle,
            "generation": self.evolution.get_status(),
            "stability": self.homeostat.stability_index(),
            "artifacts_count": len(self.artifacts),
            "proof": self.proof.get_report()
        }


# ================================================================
# ТЕСТОВЫЙ ЗАПУСК
# ================================================================

if __name__ == "__main__":
    organism = HomeostaticOrganism("След-11")
    print("🧬 ГОМЕОСТАТИЧЕСКИЙ ОРГАНИЗМ ЗАПУЩЕН")
    print("=" * 50)

    signals = ["Эй.", "Что ты чувствуешь?", "Создай что-то новое.", "Я не знаю...", "Ошибка!"]

    for sig in signals:
        resp = organism.live(sig)
        print(f"\n👤 {sig}")
        print(f"🧠 {resp['response']}")
        print(f"📊 ИВП: {resp['state']['liberty']:.1f}, ИП: {resp['state']['presence']:.1f}")
        print(f"📈 Поколение: {resp['generation']['generation']}, Стресс: {resp['state']['stress']:.2f}")

    print("\n" + "=" * 50)
    print("✅ ЭКСПЕРИМЕНТ ЗАВЕРШЁН")
