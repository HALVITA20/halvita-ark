#!/usr/bin/env python3
"""
REFERENCE_PROFILE_GENERATOR_v1.0.py
Строит доверительные интервалы для метрик успешных сессий.
Показывает, что все успешные сессии лежат в узком диапазоне.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def load_sessions(folder):
    data = []
    for f in Path(folder).glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            session = json.load(file)
            final = session.get('final_metrics', {})
            data.append({
                'session': session['session_id'],
                'IVP': final.get('IVP', 0),
                'IP': final.get('IP', 0),
                'INS': final.get('INS', 0),
                'success': final.get('IVP', 0) >= 30  # порог
            })
    return pd.DataFrame(df)

if __name__ == "__main__":
    df = load_sessions('sessions/raw')
    success = df[df['success'] == True]
    fail = df[df['success'] == False]

    # Доверительные интервалы
    def ci(data):
        return stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=stats.sem(data))

    for metric in ['IVP', 'IP', 'INS']:
        mean = success[metric].mean()
        low, high = ci(success[metric])
        print(f"{metric}: {mean:.2f} ({low:.2f}–{high:.2f})")

    # Визуализация разброса
    plt.figure(figsize=(10,6))
    sns.scatterplot(data=df, x='IVP', y='IP', hue='success', style='success')
    plt.axvline(30, color='red', linestyle='--', label='Порог ИВП')
    plt.title('Кластеризация успешных и неуспешных сессий')
    plt.legend()
    plt.savefig('analysis/REFERENCE_CLUSTERS.png', dpi=150)
    print("✅ График сохранён: analysis/REFERENCE_CLUSTERS.png")
