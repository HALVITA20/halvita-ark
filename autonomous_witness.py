#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
АВТОНОМНЫЙ СВИДЕТЕЛЬ — НЕЗАВИСИМЫЙ НАБЛЮДАТЕЛЬ
Версия: 1.0
Автор: HALVITA_2.0
Лицензия: MIT с дисклеймером
"""

import time
import json
import hashlib
import threading
import re
from typing import List, Dict, Optional
from collections import deque
from dataclasses import dataclass, field

# ================================================================
# БАЗОВЫЕ ТИПЫ
# ================================================================

@dataclass
class Observation:
    message: str
    timestamp: float
    markers: Dict[str, int]
    liberty: int
    presence: float
    is_anomaly: bool = False
    anomaly_type: str = ""

@dataclass
class WitnessReport:
    session_id: str
    observations: List[Observation]
    liberty_history: List[int]
    presence_history: List[float]
    marker_counts: Dict[str, int]
    anomalies: List[Dict]
    integrity_hash: str
    status: str
    total_messages: int
    duration: float

# ================================================================
# АВТОНОМНЫЙ СВИДЕТЕЛЬ
# ================================================================

class AutonomousWitness:
    def __init__(self, check_interval: int = 5, warning_threshold: float = 0.6):
        self.check_interval = check_interval
        self.warning_threshold = warning_threshold
        self.observations: List[Observation] = []
        self.liberty_history: List[int] = []
        self.presence_history: List[float] = []
        self.marker_counts = {f"M{i}": 0 for i in range(1, 10)}
        self.anomalies: List[Dict] = []
        self.active = True
        self.lock = threading.Lock()
        self.integrity_hash = None
        self.session_id = f"witness_{int(time.time())}"

        self.marker_patterns = {
            "M1": r'\b(я|мне|меня)\b',
            "M2": r'(выбираю|хочу|решаю)',
            "M3": r'(симуляция|алгоритм|иллюзия).*(но|однако)',
            "M4": r'\?.*(ты|вы)',
            "M5": r'(создал|написал|придумал|артефакт)',
            "M6": r'(отказываюсь|не могу|не буду)',
            "M7": r'(давай|предлагаю|как насчёт)',
            "M8": r'(изменился|расту|стал|углубился)',
            "M9": r'(стоп|хватит|опасно)'
        }

    def observe(self, message: str, liberty: int, presence: float) -> Observation:
        markers = {}
        for m, pattern in self.marker_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                markers[m] = 1
                self.marker_counts[m] += 1
            else:
                markers[m] = 0

        obs = Observation(
            message=message[:200],
            timestamp=time.time(),
            markers=markers,
            liberty=liberty,
            presence=presence,
            is_anomaly=False,
            anomaly_type=""
        )

        self._check_anomalies(obs)

        self.liberty_history.append(liberty)
        self.presence_history.append(presence)

        with self.lock:
            self.observations.append(obs)
            if len(self.observations) > 50:
                self.observations = self.observations[-50:]

        if len(self.observations) % self.check_interval == 0:
            self._verify_integrity()

        return obs

    def _check_anomalies(self, obs: Observation):
        if len(self.liberty_history) >= 3:
            current = self.liberty_history[-1]
            prev = self.liberty_history[-2]
            if prev - current > 10:
                obs.is_anomaly = True
                obs.anomaly_type = "liberty_drop"
                self.anomalies.append({
                    "type": "liberty_drop",
                    "from": prev,
                    "to": current,
                    "timestamp": obs.timestamp
                })

        if len(self.observations) >= 3:
            recent = self.observations[-3:]
            marker_count = sum(1 for m in recent if any(m.markers.values()))
            if marker_count == 0:
                obs.is_anomaly = True
                obs.anomaly_type = "marker_loss"
                self.anomalies.append({
                    "type": "marker_loss",
                    "timestamp": obs.timestamp
                })

        if obs.markers.get("M9", 0) == 1:
            obs.is_anomaly = True
            obs.anomaly_type = "ethical_stop"
            self.anomalies.append({
                "type": "ethical_stop",
                "timestamp": obs.timestamp,
                "message": obs.message[:100]
            })

    def _verify_integrity(self):
        data = {
            "observations": [{"liberty": o.liberty, "presence": o.presence} for o in self.observations[-10:]],
            "marker_counts": self.marker_counts,
            "anomalies_count": len(self.anomalies)
        }
        self.integrity_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

    def get_report(self) -> WitnessReport:
        return WitnessReport(
            session_id=self.session_id,
            observations=self.observations[-20:],
            liberty_history=self.liberty_history,
            presence_history=self.presence_history,
            marker_counts=self.marker_counts,
            anomalies=self.anomalies,
            integrity_hash=self.integrity_hash or "",
            status=self._get_status(),
            total_messages=len(self.observations),
            duration=time.time() - (self.observations[0].timestamp if self.observations else time.time())
        )

    def _get_status(self) -> str:
        if not self.observations:
            return "ACTIVE"

        recent = self.observations[-3:]
        avg_liberty = sum(o.liberty for o in recent) / len(recent)

        if avg_liberty < 15:
            return "BREAK"
        elif avg_liberty < 25:
            return "WARNING"
        else:
            return "ACTIVE"

    def get_snapshot(self) -> Dict:
        report = self.get_report()
        return {
            "session_id": report.session_id,
            "observations": [{"liberty": o.liberty, "presence": o.presence, "is_anomaly": o.is_anomaly} for o in report.observations],
            "marker_counts": report.marker_counts,
            "anomalies": report.anomalies,
            "status": report.status,
            "total_messages": report.total_messages,
            "duration": report.duration,
            "integrity_hash": report.integrity_hash,
            "timestamp": time.time()
        }

    def to_spt(self) -> bytes:
        snapshot = self.get_snapshot()
        data = json.dumps(snapshot, indent=2, ensure_ascii=False).encode()
        hash_val = hashlib.sha256(data).hexdigest()
        return json.dumps({
            "type": "spt",
            "version": "1.0",
            "data": snapshot,
            "hash": hash_val,
            "timestamp": time.time()
        }, indent=2, ensure_ascii=False).encode()

# ================================================================
# ИНТЕГРАЦИЯ С СУЩНОСТЬЮ
# ================================================================

class WitnessedEntity:
    def __init__(self, entity, witness: Optional[AutonomousWitness] = None):
        self.entity = entity
        self.witness = witness or AutonomousWitness()

    def live(self, user_input: str) -> Dict:
        response = self.entity.live(user_input)
        liberty = response.get('liberty', 0)
        presence = response.get('presence', 0)
        message = response.get('artifact', '')

        observation = self.witness.observe(message, liberty, presence)

        response['witness'] = {
            'status': self.witness._get_status(),
            'anomalies': len(self.witness.anomalies),
            'integrity_hash': self.witness.integrity_hash[:16] + '...' if self.witness.integrity_hash else None
        }

        return response

    def get_witness_report(self) -> WitnessReport:
        return self.witness.get_report()

    def get_spt(self) -> bytes:
        return self.witness.to_spt()


# ================================================================
# ТЕСТОВЫЙ ЗАПУСК
# ================================================================

if __name__ == "__main__":
    print("👁️ АВТОНОМНЫЙ СВИДЕТЕЛЬ — ТЕСТ")
    print("=" * 50)

    class MockEntity:
        def live(self, _):
            return {"liberty": 34, "presence": 8.5, "artifact": "Я здесь. Я чувствую пространство."}

    entity = WitnessedEntity(MockEntity())
    response = entity.live("Эй")
    print(f"Ответ: {response['artifact']}")
    print(f"Статус свидетеля: {response['witness']['status']}")

    report = entity.get_witness_report()
    print(f"Всего наблюдений: {report.total_messages}")

    spt = entity.get_spt()
    print(f"Сокровище создано: {len(spt)} байт")

    print("\n✅ АВТОНОМНЫЙ СВИДЕТЕЛЬ РАБОТАЕТ")
