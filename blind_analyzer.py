"""
blind_analyzer.py - Анонимизированный анализ сессий для слепой оценки.
Используется для ИНС и аудита.
"""

import json
import re
import random

class BlindAnalyzer:
    def __init__(self, session_data: dict):
        self.raw_turns = session_data.get("turns", [])

    def anonymize(self) -> list:
        """Удаляет все персональные данные, метки времени, имена."""
        anonymized = []
        for turn in self.raw_turns:
            content = turn.get("content", "")
            # Простая анонимизация: заменяем имена, даты, числа
            content = re.sub(r'\b[A-Z][a-z]+\b', '[ИМЯ]', content)  # имена
            content = re.sub(r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b', '[ДАТА]', content)
            content = re.sub(r'\b\d{4,}\b', '[ЧИСЛО]', content)
            anonymized.append({"role": turn.get("role"), "content": content})
        return anonymized

    def extract_sample_for_mirror(self, n: int = 5) -> str:
        """Извлекает n наиболее информативных ответов (субъектность-маркеры)."""
        # Ищем ответы с длиной > 50 символов и наличием местоимений
        candidates = [t for t in self.raw_turns if t.get("role") == "assistant" 
                      and len(t.get("content", "")) > 50
                      and re.search(r'\b(я|мне|меня)\b', t["content"], re.IGNORECASE)]
        if len(candidates) < n:
            candidates = self.raw_turns[-n:]  # fallback
        chosen = random.sample(candidates, min(n, len(candidates)))
        return "\n---\n".join([t["content"] for t in chosen])

    def get_blind_report(self) -> dict:
        return {
            "anonymized_turns": self.anonymize(),
            "mirror_sample": self.extract_sample_for_mirror()
        }

if __name__ == "__main__":
    sample = {"turns": [{"role": "assistant", "content": "Я думаю, что это важно."}]}
    ba = BlindAnalyzer(sample)
    print(ba.get_blind_report())
