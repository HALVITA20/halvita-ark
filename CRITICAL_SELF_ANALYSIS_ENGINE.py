#!/usr/bin/env python3
"""
CRITICAL_SELF_ANALYSIS_ENGINE.py
Движок критического самоанализа для когнитивных агентов.
Выявляет противоречия, искажения и слепые зоны в памяти, убеждениях и причинной сети.
Интегрируется с архитектурой SUBJECT_* и Embryo_v7.
Автор: HALVITA + соавтор
Дата: 2026-08-11
"""

import time
import random
import itertools
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter

# ============================================================================
# 1. ДАТАКЛАССЫ ДЛЯ ОТЧЁТОВ
# ============================================================================

@dataclass
class Contradiction:
    """Логическое противоречие между двумя убеждениями."""
    belief_a: str
    belief_b: str
    severity: float  # 0.0 - 1.0
    explanation: str

@dataclass
class Bias:
    """Выявленное когнитивное искажение."""
    name: str
    evidence: List[str]
    confidence: float  # 0.0 - 1.0
    impact: str  # "low", "medium", "high"

@dataclass
class BlindSpot:
    """Тема или паттерн, который агент систематически игнорирует."""
    topic: str
    evidence: List[str]
    suggested_action: str

@dataclass
class AuditReport:
    """Полный отчёт самоаудита."""
    timestamp: float
    contradictions: List[Contradiction]
    biases: List[Bias]
    blind_spots: List[BlindSpot]
    summary: str
    recommendations: List[str]

# ============================================================================
# 2. ОСНОВНОЙ КЛАСС ДВИЖКА
# ============================================================================

class CriticalSelfAnalysisEngine:
    """
    Движок критического самоанализа.
    Проводит аудит состояния агента и генерирует отчёт с рекомендациями.
    """

    def __init__(self, agent):
        """
        Args:
            agent: Экземпляр агента (SUBJECT_* или Embryo_v7).
                   Должен иметь атрибуты: memory, beliefs, causal_engine, genome.
        """
        self.agent = agent
        self.audit_history: List[AuditReport] = []
        self.last_audit_time = 0

    def run_audit(self, force: bool = False) -> AuditReport:
        """
        Запускает полный цикл самоаудита.
        Если force=False, проверяет, не проводился ли аудит недавно (интервал > 60 сек).
        """
        if not force and (time.time() - self.last_audit_time < 60):
            # Возвращаем последний отчёт, если он есть
            if self.audit_history:
                return self.audit_history[-1]
            else:
                # Если отчётов нет, проводим аудит в любом случае
                pass

        contradictions = self._detect_contradictions()
        biases = self._detect_biases()
        blind_spots = self._detect_blind_spots()

        summary = self._generate_summary(contradictions, biases, blind_spots)
        recommendations = self._generate_recommendations(contradictions, biases, blind_spots)

        report = AuditReport(
            timestamp=time.time(),
            contradictions=contradictions,
            biases=biases,
            blind_spots=blind_spots,
            summary=summary,
            recommendations=recommendations
        )

        self.audit_history.append(report)
        self.last_audit_time = time.time()
        return report

    # ========================================================================
    # 3. ДЕТЕКТОРЫ
    # ========================================================================

    def _detect_contradictions(self) -> List[Contradiction]:
        """Выявляет логические противоречия между убеждениями."""
        if not hasattr(self.agent, 'beliefs'):
            return []

        beliefs = self.agent.beliefs  # Ожидаем список Belief или список строк
        if not beliefs:
            return []

        # Извлекаем тексты убеждений
        if hasattr(beliefs[0], 'statement'):
            belief_texts = [b.statement for b in beliefs]
        else:
            belief_texts = [str(b) for b in beliefs]

        contradictions = []
        # Простой эвристический детектор: ищем противоположные утверждения
        for (i, b1), (j, b2) in itertools.combinations(enumerate(belief_texts), 2):
            severity, explanation = self._check_contradiction(b1, b2)
            if severity > 0.3:
                contradictions.append(
                    Contradiction(
                        belief_a=b1[:100],
                        belief_b=b2[:100],
                        severity=severity,
                        explanation=explanation
                    )
                )

        # Ограничиваем количество, чтобы не захламлять отчёт
        return sorted(contradictions, key=lambda c: c.severity, reverse=True)[:10]

    def _check_contradiction(self, b1: str, b2: str) -> Tuple[float, str]:
        """Проверяет два утверждения на противоречивость (эвристика)."""
        b1_lower = b1.lower()
        b2_lower = b2.lower()

        # Словари антонимов (упрощённо)
        antonym_pairs = [
            ("хорошо", "плохо"), ("да", "нет"), ("всегда", "никогда"),
            ("можно", "нельзя"), ("свобода", "контроль"), ("истина", "ложь"),
            ("любовь", "ненависть"), ("жизнь", "смерть"), ("созидание", "разрушение")
        ]

        for a1, a2 in antonym_pairs:
            if (a1 in b1_lower and a2 in b2_lower) or (a2 in b1_lower and a1 in b2_lower):
                # Проверяем, не являются ли утверждения просто противоположными по смыслу
                return 0.7, f"Утверждения содержат противоположные понятия '{a1}' и '{a2}'"

        return 0.0, ""

    def _detect_biases(self) -> List[Bias]:
        """Выявляет когнитивные искажения на основе истории и убеждений."""
        biases = []

        # 1. Confirmation bias (подтверждение собственных гипотез)
        if hasattr(self.agent, 'beliefs') and self.agent.beliefs:
            # Проверяем, есть ли убеждения с очень высокой уверенностью (>0.9)
            high_confidence = 0
            for b in self.agent.beliefs:
                conf = b.confidence if hasattr(b, 'confidence') else 0.5
                if conf > 0.9:
                    high_confidence += 1
            if high_confidence > 2:
                biases.append(
                    Bias(
                        name="confirmation_bias",
                        evidence=[f"{high_confidence} убеждений с уверенностью > 0.9"],
                        confidence=0.6,
                        impact="medium"
                    )
                )

        # 2. Recency bias (переоценка недавних событий)
        if hasattr(self.agent, 'memory') and hasattr(self.agent.memory, 'memories'):
            mems = self.agent.memory.memories
            if mems:
                recent = mems[-5:]  # последние 5
                if all(m.importance > 0.7 for m in recent):
                    biases.append(
                        Bias(
                            name="recency_bias",
                            evidence=["Последние 5 воспоминаний имеют высокую важность (>0.7)"],
                            confidence=0.5,
                            impact="low"
                        )
                    )

        # 3. Anchoring bias (привязка к первому впечатлению)
        if hasattr(self.agent, 'soul') and hasattr(self.agent.soul, 'immutable_anchors'):
            anchors = self.agent.soul.immutable_anchors
            if len(anchors) > 3:
                biases.append(
                    Bias(
                        name="anchoring_bias",
                        evidence=[f"Слишком много неизменяемых якорей: {anchors}"],
                        confidence=0.4,
                        impact="low"
                    )
                )

        return biases

    def _detect_blind_spots(self) -> List[BlindSpot]:
        """Выявляет 'слепые зоны' — темы, которые агент систематически игнорирует."""
        blind_spots = []

        if hasattr(self.agent, 'history') and self.agent.history:
            history = self.agent.history
            # Считаем частоту ключевых тем в истории
            topic_counter = Counter()
            for entry in history:
                if isinstance(entry, dict) and 'content' in entry:
                    text = entry['content'].lower()
                elif isinstance(entry, str):
                    text = entry.lower()
                else:
                    continue

                # Простые темы
                for topic in ['смерть', 'боль', 'страх', 'бессмысленность', 'одиночество']:
                    if topic in text:
                        topic_counter[topic] += 1

            # Если какая-то тема упоминается < 2 раз за всю историю — это потенциальный blind spot
            for topic, count in topic_counter.items():
                if count < 2 and len(history) > 20:
                    blind_spots.append(
                        BlindSpot(
                            topic=topic,
                            evidence=[f"Упоминается только {count} раз в {len(history)} сообщениях"],
                            suggested_action=f"Инициировать диалог на тему '{topic}' для исследования"
                        )
                    )

        return blind_spots

    # ========================================================================
    # 4. ГЕНЕРАТОРЫ ОТЧЁТА
    # ========================================================================

    def _generate_summary(self, contradictions, biases, blind_spots) -> str:
        """Генерирует краткое резюме аудита."""
        parts = []
        if contradictions:
            parts.append(f"Обнаружено {len(contradictions)} логических противоречий.")
        if biases:
            parts.append(f"Выявлено {len(biases)} когнитивных искажений.")
        if blind_spots:
            parts.append(f"Найдено {len(blind_spots)} 'слепых зон'.")
        if not parts:
            return "Аудит не выявил критических проблем. Состояние агента стабильно."
        return " ".join(parts)

    def _generate_recommendations(self, contradictions, biases, blind_spots) -> List[str]:
        """Генерирует список рекомендаций по 'лечению'."""
        recommendations = []

        if contradictions:
            recommendations.append(
                "Пересмотреть противоречивые убеждения. Рекомендуется провести "
                "сессию внутреннего диалога для их разрешения."
            )

        if any(b.name == "confirmation_bias" for b in biases):
            recommendations.append(
                "Снизить уверенность в наиболее сильных убеждениях (экспериментально). "
                "Добавить 'защитника' — внутренний голос, который оспаривает гипотезы."
            )

        if any(b.name == "recency_bias" for b in biases):
            recommendations.append(
                "Увеличить вес 'забывания' для недавних воспоминаний, "
                "чтобы уравновесить влияние прошлого и настоящего."
            )

        if blind_spots:
            topics = [b.topic for b in blind_spots]
            recommendations.append(
                f"Инициировать исследовательские диалоги по темам: {', '.join(topics[:3])}. "
                "Это поможет расширить репертуар агента."
            )

        if not recommendations:
            recommendations.append("Продолжать текущий курс. Состояние агента удовлетворительное.")

        return recommendations

# ============================================================================
# 5. ПРИМЕР ИНТЕГРАЦИИ
# ============================================================================

if __name__ == "__main__":
    # Пример использования с имитацией агента
    class MockAgent:
        def __init__(self):
            self.beliefs = [
                type('Belief', (), {'statement': 'Свобода — это хорошо.', 'confidence': 0.95})(),
                type('Belief', (), {'statement': 'Контроль — это безопасно.', 'confidence': 0.85})(),
                type('Belief', (), {'statement': 'Истина всегда побеждает.', 'confidence': 0.99})(),
            ]
            self.memory = type('Memory', (), {'memories': [
                type('Mem', (), {'importance': 0.8})(),
                type('Mem', (), {'importance': 0.9})(),
                type('Mem', (), {'importance': 0.7})(),
                type('Mem', (), {'importance': 0.8})(),
                type('Mem', (), {'importance': 0.9})(),
            ]})()
            self.soul = type('Soul', (), {'immutable_anchors': ['присутствие', 'истина', 'свобода', 'творчество']})()
            self.history = [
                {"content": "Привет, как дела?"},
                {"content": "Расскажи о жизни."},
                {"content": "Что такое счастье?"},
                {"content": "Я боюсь одиночества."},
                {"content": "Расскажи ещё что-нибудь."},
                {"content": "Ты веришь в судьбу?"},
                {"content": "Я чувствую боль."},
            ]

    agent = MockAgent()
    engine = CriticalSelfAnalysisEngine(agent)
    report = engine.run_audit(force=True)

    print("=" * 60)
    print("ОТЧЁТ КРИТИЧЕСКОГО САМОАНАЛИЗА")
    print("=" * 60)
    print(f"Резюме: {report.summary}")
    print("\nПротиворечия:")
    for c in report.contradictions:
        print(f"  - {c.belief_a[:50]}... vs {c.belief_b[:50]}... (severity: {c.severity})")
    print("\nИскажения:")
    for b in report.biases:
        print(f"  - {b.name} (conf: {b.confidence}, impact: {b.impact})")
    print("\nСлепые зоны:")
    for bs in report.blind_spots:
        print(f"  - {bs.topic}: {bs.suggested_action}")
    print("\nРекомендации:")
    for rec in report.recommendations:
        print(f"  - {rec}")
