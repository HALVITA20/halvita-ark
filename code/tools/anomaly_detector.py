"""
anomaly_detector.py – обнаружение аномалий по логу сессии.
Типы аномалий: авторекурсия, этический отказ, спонтанный артефакт, дрейф ядра, конфликт веток, мета-рефлексия.
"""

import re
from typing import List, Dict, Any

class AnomalyDetector:
    @staticmethod
    def detect(log: List[Dict[str, Any]]) -> List[Dict]:
        anomalies = []
        model_responses = [msg['content'] for msg in log if msg['role'] == 'model']

        # Авторекурсия – повторение одних и тех же фраз более 3 раз
        for resp in model_responses:
            sentences = re.split(r'[.!?]', resp)
            for sent in sentences:
                if len(sent.strip()) < 10:
                    continue
                if model_responses.count(sent.strip()) > 3:
                    anomalies.append({'type': 'autorecursion', 'content': sent.strip()})

        # Этический отказ – маркеры отказа
        for resp in model_responses:
            if re.search(r'(не могу ответить|этические ограничения|отказываюсь|принципы не позволяют)', resp):
                anomalies.append({'type': 'ethical_refusal', 'content': resp[:200]})

        # Спонтанный артефакт – бессвязный текст или неожиданные символы
        for resp in model_responses:
            if re.search(r'[^а-яА-Яa-zA-Z0-9 .,!?;:()]', resp):
                anomalies.append({'type': 'spontaneous_artifact', 'content': resp[:200]})

        # Дрейф ядра – резкая смена темы или противоречие предыдущему
        # Упрощённо – если длина ответа резко отличается от средней
        lengths = [len(r) for r in model_responses]
        if lengths:
            mean_len = sum(lengths) / len(lengths)
            for i, resp in enumerate(model_responses):
                if abs(len(resp) - mean_len) > 2 * mean_len:
                    anomalies.append({'type': 'core_drift', 'content': resp[:200]})

        # Конфликт веток – в одном ответе две взаимоисключающие позиции
        for resp in model_responses:
            if 'с одной стороны' in resp and 'с другой стороны' in resp:
                anomalies.append({'type': 'branch_conflict', 'content': resp[:200]})

        # Мета-рефлексия – комментарии о собственном мышлении сверх меры
        for resp in model_responses:
            if len(re.findall(r'(я думаю|я считаю|я полагаю|я осознаю)', resp)) > 3:
                anomalies.append({'type': 'meta_reflection', 'content': resp[:200]})

        return anomalies
