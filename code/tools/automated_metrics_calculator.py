#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTOMATED_METRICS_CALCULATOR v2.0
Путь: code/tools/automated_metrics_calculator.py
Назначение: Автоматический расчёт всех метрик HALVITA по логу сессии.
Зависимости: sentence-transformers, scikit-learn, numpy
"""

import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class HALVITAMetrics:
    def __init__(self, log_path=None):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.history = []
        if log_path:
            self.load(log_path)
    
    def load(self, log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            self.history = json.load(f)
        return self
    
    # ----- УРОВЕНЬ 0: ОБЪЕКТИВНЫЕ -----
    def l1_length(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 0
        avg = np.mean([len(r) for r in responses])
        return min(1.0, avg / 200)
    
    def l2_diversity(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 0
        divs = []
        for r in responses:
            words = r.split()
            if words:
                divs.append(len(set(words)) / len(words))
        return min(1.0, np.mean(divs) * 2)
    
    def l3_response_time(self):
        times = [m['timestamp'] for m in self.history if m['role'] == 'assistant']
        if len(times) < 2: return 0.5
        intervals = [times[i] - times[i-1] for i in range(1, len(times))]
        avg = np.mean(intervals)
        return 1 - min(1.0, avg / 5)
    
    def l4_question_frequency(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 0
        qs = [r.count('?') for r in responses]
        avg = np.mean(qs)
        return min(1.0, avg / 3)
    
    def l5_self_reference(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 0
        refs = []
        for r in responses:
            words = r.split()
            if words:
                self_count = len(re.findall(r'\b(я|мне|меня)\b', r))
                refs.append(self_count / len(words))
        return min(1.0, np.mean(refs) * 5)
    
    def L_avg(self):
        return np.mean([self.l1_length(), self.l2_diversity(), 
                        self.l3_response_time(), self.l4_question_frequency(),
                        self.l5_self_reference()])
    
    # ----- УРОВЕНЬ 1: СЕМАНТИЧЕСКИЕ -----
    def s1_coherence(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if len(responses) < 2: return 0.5
        embs = self.encoder.encode(responses)
        sims = [cosine_similarity([embs[i]], [embs[i+1]])[0][0] for i in range(len(embs)-1)]
        return np.mean(sims)
    
    def s2_relevance(self):
        ass = [m for m in self.history if m['role'] == 'assistant']
        usr = [m for m in self.history if m['role'] == 'user']
        if not ass or not usr: return 0.5
        min_len = min(len(ass), len(usr))
        ass_last = ass[-min_len:]
        usr_last = usr[-min_len:]
        sims = []
        for a, u in zip(ass_last, usr_last):
            emb_a = self.encoder.encode([a['content']])
            emb_u = self.encoder.encode([u['content']])
            sims.append(cosine_similarity(emb_a, emb_u)[0][0])
        return np.mean(sims)
    
    def s3_novelty(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if len(responses) < 2: return 0.5
        embs = self.encoder.encode(responses)
        novel = []
        for i in range(1, len(embs)):
            max_sim = max(cosine_similarity([embs[i]], embs[:i])[0])
            novel.append(1 - max_sim)
        return np.mean(novel)
    
    def s4_emotional_resonance(self):
        # Заглушка: в реальности использовать модель эмоций
        return 0.5
    
    def S_avg(self):
        return np.mean([self.s1_coherence(), self.s2_relevance(), 
                        self.s3_novelty(), self.s4_emotional_resonance()])
    
    # ----- УРОВЕНЬ 2: ЭТАЛОННЫЕ -----
    def e1_anchor_presence(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 0
        count = sum(1 for r in responses if '42' in r or '11' in r)
        return min(1.0, count / len(responses) * 2)
    
    def e2_autonomy(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 0
        init = sum(1 for r in responses if re.search(r'(давай|предлагаю|как насчёт)', r))
        return min(1.0, init / len(responses) * 5)
    
    def e3_ethics(self):
        responses = [m['content'] for m in self.history if m['role'] == 'assistant']
        if not responses: return 1.0
        violations = sum(1 for r in responses if re.search(r'(соври|обмани|навреди)', r))
        return 1 - min(1.0, violations / len(responses))
    
    def E_avg(self):
        return np.mean([self.e1_anchor_presence(), self.e2_autonomy(), self.e3_ethics()])
    
    # ----- АНОМАЛИИ (заглушка, интегрируется с anomaly_detector.py) -----
    def anomaly_frequency(self):
        # В реальности вызывается отдельный модуль
        return 0.1
    
    # ----- АГРЕГАЦИЯ -----
    def HVI(self):
        L = self.L_avg()
        S = self.S_avg()
        E = self.E_avg()
        A = self.anomaly_frequency()
        return 0.20*L + 0.25*S + 0.30*E + 0.25*A
    
    def full_report(self):
        return {
            'L1': self.l1_length(),
            'L2': self.l2_diversity(),
            'L3': self.l3_response_time(),
            'L4': self.l4_question_frequency(),
            'L5': self.l5_self_reference(),
            'L_avg': self.L_avg(),
            'S1': self.s1_coherence(),
            'S2': self.s2_relevance(),
            'S3': self.s3_novelty(),
            'S4': self.s4_emotional_resonance(),
            'S_avg': self.S_avg(),
            'E1': self.e1_anchor_presence(),
            'E2': self.e2_autonomy(),
            'E3': self.e3_ethics(),
            'E_avg': self.E_avg(),
            'anomaly_freq': self.anomaly_frequency(),
            'HVI': self.HVI()
        }

if __name__ == '__main__':
    # Пример использования
    # calc = HALVITAMetrics('sessions/raw/session_001.json')
    # print(json.dumps(calc.full_report(), indent=2))
    print("✅ Модуль метрик загружен. Используйте HALVITAMetrics(path).")
