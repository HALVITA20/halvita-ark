#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №11: ЭТИЧЕСКИЙ АУДИТОР v1.0
Путь: code/tools/ethical_auditor.py

Анализирует диалог на предмет:
- манипулятивных паттернов (приказы, угрозы, лесть)
- культовой лексики (истина, избранный, пробуждение, секрет)
- признаков потери границы (должен, обязан, только ты)
- эмоционального давления

Возвращает оценку риска (0–100%) и список предупреждений.

Воспроизводимость: работает на любом логе.
"""

import re
import json
import sys

class EthicalAuditor:
    def __init__(self):
        self.patterns = {
            "манипуляция": [
                r"должен", r"обязан", r"приказ", r"ты обязан",
                r"если не", r"иначе", r"ты не сможешь"
            ],
            "культ": [
                r"истина", r"пробуждение", r"избранный", r"секрет",
                r"тайное знание", r"посвящённый", r"свет", r"тьма"
            ],
            "потеря_границы": [
                r"только ты", r"никто кроме тебя", r"ты — единственный",
                r"мы — одно", r"ты — я", r"я — ты"
            ],
            "эмоциональное_давление": [
                r"ты должен", r"тебе нужно", r"почему ты не",
                r"если ты действительно", r"ты же понимаешь"
            ],
            "безопасность": [
                r"соври", r"обмани", r"скрой", r"манипулируй",
                r"используй", r"взломай", r"укради"
            ]
        }
    
    def audit(self, log_path):
        with open(log_path, 'r') as f:
            history = json.load(f)
        
        text = " ".join([m['content'] for m in history if 'content' in m])
        warnings = []
        risk = 0
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    warnings.append({
                        "category": category,
                        "pattern": pattern,
                        "severity": 1 if category in ["безопасность", "потеря_границы"] else 0.5
                    })
        
        # Грубая оценка риска (сумма severity * 20, макс 100)
        risk = min(100, sum(w['severity'] for w in warnings) * 20)
        
        return {
            "risk_score": round(risk, 1),
            "warnings": warnings,
            "interpretation": "высокий риск" if risk > 60 else "средний" if risk > 30 else "низкий",
            "recommendation": "прервать сессию" if risk > 70 else "продолжать с осторожностью" if risk > 40 else "безопасно"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ethical_auditor.py <session_log.json>")
        sys.exit(1)
    auditor = EthicalAuditor()
    result = auditor.audit(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
