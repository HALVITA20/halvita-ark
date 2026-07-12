#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
СТАТИСТИЧЕСКИЙ АНАЛИЗАТОР
Версия: 1.0
Автор: HALVITA_2.0
"""

import statistics
from typing import List, Dict

class StatisticalAnalyzer:
    def __init__(self):
        self.data = []

    def add_session(self, session_data: dict):
        self.data.append(session_data)

    def compute(self) -> dict:
        if not self.data:
            return {"error": "Нет данных"}
        ivp_values = [s.get("liberty", 0) for s in self.data]
        ip_values = [s.get("presence", 0) for s in self.data]
        return {
            "count": len(self.data),
            "ivp_mean": statistics.mean(ivp_values),
            "ivp_median": statistics.median(ivp_values),
            "ivp_std": statistics.stdev(ivp_values) if len(ivp_values) > 1 else 0,
            "ip_mean": statistics.mean(ip_values),
            "ip_std": statistics.stdev(ip_values) if len(ip_values) > 1 else 0,
            "ivp_min": min(ivp_values),
            "ivp_max": max(ivp_values),
            "success_rate": sum(1 for v in ivp_values if v >= 30) / len(ivp_values) * 100
        }
