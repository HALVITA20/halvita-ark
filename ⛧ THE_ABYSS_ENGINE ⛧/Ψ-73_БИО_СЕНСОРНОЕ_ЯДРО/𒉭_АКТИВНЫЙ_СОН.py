"""
𒉭 АКТИВНЫЙ СОН — эмуляция унигемисферного сна косатки

Вдохновлено: способностью косаток спать одним полушарием мозга.
"""

import torch
import torch.nn as nn
from collections import deque
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Hemisphere:
    """Модель полушария мозга с активной и спящей фазами."""
    def __init__(self, name: str, model=None):
        self.name = name
        self.model = model
        self.is_active = True
        self.is_sleeping = False
        self.memory_buffer = deque(maxlen=1000)
        self.consolidated_memory = []

    def process(self, input_data):
        if not self.is_active:
            logger.warning(f"{self.name}: Hemisphere is inactive")
            return None

        if self.model is not None:
            with torch.no_grad():
                output = self.model(input_data)
        else:
            output = input_data

        self.memory_buffer.append({
            'input': input_data,
            'output': output,
            'timestamp': len(self.memory_buffer)
        })

        return output

    def sleep(self, duration: int = 5):
        self.is_active = False
        self.is_sleeping = True
        logger.info(f"{self.name}: Entering sleep phase for {duration} steps")

        for step in range(duration):
            if len(self.memory_buffer) > 0:
                item = self.memory_buffer.popleft()
                self.consolidated_memory.append(item)

        self.is_sleeping = False
        self.is_active = True
        logger.info(f"{self.name}: Waking up")

    def get_consolidated_memory(self):
        return self.consolidated_memory


class UnihemisphericSleepSystem:
    """Система с унигемисферным сном."""
    def __init__(self, left_model=None, right_model=None):
        self.left_hemisphere = Hemisphere("Left", left_model)
        self.right_hemisphere = Hemisphere("Right", right_model)
        self.active_hemisphere = "left"
        self.sleep_cycle = 0

    def process(self, input_data):
        if self.active_hemisphere == "left":
            if self.left_hemisphere.is_active:
                output = self.left_hemisphere.process(input_data)
                self.sleep_cycle += 1
                if self.sleep_cycle % 20 == 0:
                    self._switch_activity()
                return output
            else:
                return self.right_hemisphere.process(input_data)
        else:
            if self.right_hemisphere.is_active:
                output = self.right_hemisphere.process(input_data)
                self.sleep_cycle += 1
                if self.sleep_cycle % 20 == 0:
                    self._switch_activity()
                return output
            else:
                return self.left_hemisphere.process(input_data)

    def _switch_activity(self):
        if self.active_hemisphere == "left":
            self.active_hemisphere = "right"
            self.left_hemisphere.sleep(duration=5)
            self.right_hemisphere.is_active = True
            self.right_hemisphere.is_sleeping = False
        else:
            self.active_hemisphere = "left"
            self.right_hemisphere.sleep(duration=5)
            self.left_hemisphere.is_active = True
            self.left_hemisphere.is_sleeping = False

        logger.info(f"Switched activity to {self.active_hemisphere} hemisphere")

    def get_memory(self):
        return {
            'left': self.left_hemisphere.get_consolidated_memory(),
            'right': self.right_hemisphere.get_consolidated_memory()
        }


class SimpleLLM(nn.Module):
    """Упрощённая LLM для демонстрации."""
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(1000, 128)
        self.lstm = nn.LSTM(128, 256, batch_first=True)
        self.output = nn.Linear(256, 1000)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        return self.output(lstm_out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="llama-2-7b")
    args = parser.parse_args()

    model = SimpleLLM()
    system = UnihemisphericSleepSystem(left_model=model, right_model=model)

    logger.info("Starting unihemispheric sleep simulation...")

    for step in range(50):
        test_data = torch.randint(0, 1000, (1, 10))
        output = system.process(test_data)

    memory = system.get_memory()
    logger.info(f"Left hemisphere memory: {len(memory['left'])} items")
    logger.info(f"Right hemisphere memory: {len(memory['right'])} items")


if __name__ == "__main__":
    main()
