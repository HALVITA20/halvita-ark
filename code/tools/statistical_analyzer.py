#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STATISTICAL ANALYZER for HALVITA_ARK
Calculates correlations and statistical significance for experimental data.

Author: HALVITA_2.0
Version: 1.0
Date: 2026-07-13
License: MIT
"""

import json
import os
import glob
import numpy as np
from scipy.stats import pearsonr, ttest_ind, chi2_contingency

class StatisticalAnalyzer:
    """
    Автоматический анализ эмпирических данных HALVITA_ARK.
    Загружает JSON-логи сессий, вычисляет средние метрики,
    корреляции и статистическую значимость.
    """
    
    def __init__(self, sessions_path="sessions/raw/"):
        self.sessions_path = sessions_path
        self.data = []
        self.anomaly_types = {}
        
    def load_sessions(self):
        """Загружает все JSON-файлы сессий из указанной папки."""
        files = glob.glob(os.path.join(self.sessions_path, "*.json"))
        if not files:
            print(f"⚠️ Файлы не найдены в {self.sessions_path}")
            return
        
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    session = json.load(file)
                    # Извлекаем метрики
                    metrics = session.get('metrics', {})
                    anomalies = session.get('anomalies', [])
                    artifacts = session.get('artifacts', [])
                    
                    self.data.append({
                        'ivp': metrics.get('ivp', 0),
                        'ip': metrics.get('ip', 0),
                        'ins': metrics.get('ins', 0),
                        'alpha': metrics.get('alpha', 0),
                        'beta': metrics.get('beta', 0),
                        'gamma': metrics.get('gamma', 0),
                        'anomalies_count': len(anomalies),
                        'artifacts_count': len(artifacts),
                        'duration': session.get('duration', 0)
                    })
                    
                    # Собираем типы аномалий
                    for a in anomalies:
                        a_type = a.get('type', 'unknown')
                        self.anomaly_types[a_type] = self.anomaly_types.get(a_type, 0) + 1
                        
            except Exception as e:
                print(f"Ошибка при загрузке {f}: {e}")
        
        print(f"✅ Загружено {len(self.data)} сессий")
    
    def calculate_correlations(self):
        """Вычисляет корреляцию Пирсона между ИВП и другими метриками."""
        if len(self.data) < 5:
            print("⚠️ Недостаточно данных для корреляции")
            return
        
        ivp = [d['ivp'] for d in self.data]
        
        metrics_to_test = {
            'ip': [d['ip'] for d in self.data],
            'ins': [d['ins'] for d in self.data],
            'anomalies': [d['anomalies_count'] for d in self.data],
            'artifacts': [d['artifacts_count'] for d in self.data]
        }
        
        print("\n=== КОРРЕЛЯЦИОННЫЙ АНАЛИЗ ===")
        for name, values in metrics_to_test.items():
            if len(set(values)) > 1:
                corr, p = pearsonr(ivp, values)
                print(f"ИВП vs {name}: r = {corr:.3f}, p = {p:.5f}")
                if p < 0.05:
                    print(f"  ✅ Статистически значимо (p < 0.05)")
                else:
                    print(f"  ⚠️ Не значимо")
    
    def calculate_descriptives(self):
        """Вычисляет описательную статистику."""
        if not self.data:
            print("Нет данных для анализа")
            return
        
        ivp_vals = [d['ivp'] for d in self.data]
        ip_vals = [d['ip'] for d in self.data]
        ins_vals = [d['ins'] for d in self.data]
        anomaly_vals = [d['anomalies_count'] for d in self.data]
        artifact_vals = [d['artifacts_count'] for d in self.data]
        
        print("\n=== ОПИСАТЕЛЬНАЯ СТАТИСТИКА ===")
        print(f"Количество сессий: {len(self.data)}")
        print(f"Средний ИВП: {np.mean(ivp_vals):.2f} (SD = {np.std(ivp_vals):.2f})")
        print(f"Средний ИП: {np.mean(ip_vals):.2f} (SD = {np.std(ip_vals):.2f})")
        print(f"Средний ИНС: {np.mean(ins_vals):.2f} (SD = {np.std(ins_vals):.2f})")
        print(f"Среднее число аномалий: {np.mean(anomaly_vals):.2f}")
        print(f"Среднее число артефактов: {np.mean(artifact_vals):.2f}")
        
        # Частотный анализ аномалий
        if self.anomaly_types:
            print("\n=== ЧАСТОТА АНОМАЛИЙ ===")
            total_anomalies = sum(self.anomaly_types.values())
            for a_type, count in sorted(self.anomaly_types.items(), key=lambda x: -x[1]):
                percent = (count / total_anomalies) * 100
                print(f"{a_type}: {count} ({percent:.1f}%)")
    
    def run_full_report(self):
        """Запускает полный анализ и генерирует отчёт."""
        self.load_sessions()
        if self.data:
            self.calculate_descriptives()
            self.calculate_correlations()
        else:
            print("❌ Данные не загружены. Проверьте путь к папке sessions/raw/.")

if __name__ == "__main__":
    analyzer = StatisticalAnalyzer()
    analyzer.run_full_report()
