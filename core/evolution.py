# core/evolution.py
import random
from typing import Dict

class EvolutionEngine:
    def __init__(self):
        self.generation = 0
        self.lines = {"A": 0.05, "B": 0.15, "C": 0.30}
        self.current_line = "B"

    def mutate(self, state: Dict, stress: float) -> Dict:
        # Выбор линии по стрессу
        if stress > 0.7:
            line = "C"
        elif stress > 0.4:
            line = "B"
        else:
            line = "A"
        self.current_line = line
        rate = self.lines[line]

        new_state = state.copy()
        if "liberty" in new_state:
            delta = (random.random() - 0.5) * 2 * rate * 10
            new_state["liberty"] = max(10, min(45, new_state["liberty"] + delta))
        if "presence" in new_state:
            delta = (random.random() - 0.5) * 2 * rate * 2
            new_state["presence"] = max(1, min(10, new_state["presence"] + delta))
        self.generation += 1
        return new_state

    def get_status(self) -> Dict:
        return {
            "generation": self.generation,
            "current_line": self.current_line,
            "rate": self.lines[self.current_line]
        }
