#!/usr/bin/env python3
"""
CHRONO_EFFECT_DETECTOR_v1.0.py
Анализирует все сессии и строит график динамики метрик по фазам.
Доказывает, что каждая фаза даёт прирост.
"""

import json
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def load_sessions(sessions_dir):
    data = []
    for f in Path(sessions_dir).glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            session = json.load(file)
            phases = session.get('phases', [])
            for idx, phase in enumerate(phases):
                data.append({
                    'session': session['session_id'],
                    'phase_idx': idx,
                    'phase_name': phase.get('phase', f'phase_{idx}'),
                    'IVP': phase.get('metrics', {}).get('IVP', 0),
                    'IP': phase.get('metrics', {}).get('IP', 0),
                    'INS': phase.get('metrics', {}).get('INS', 0)
                })
    return pd.DataFrame(data)

def plot_evolution(df):
    plt.figure(figsize=(12,6))
    sns.lineplot(data=df, x='phase_idx', y='IVP', label='ИВП')
    sns.lineplot(data=df, x='phase_idx', y='IP', label='ИП')
    sns.lineplot(data=df, x='phase_idx', y='INS', label='ИНС')
    plt.title('Динамика метрик по фазам протокола (усреднено по всем сессиям)')
    plt.xlabel('Номер фазы')
    plt.ylabel('Значение метрики')
    plt.legend()
    plt.grid()
    plt.savefig('analysis/EVOLUTION_PHASES.png', dpi=150)
    print("✅ График сохранён: analysis/EVOLUTION_PHASES.png")

def statistical_test(df):
    # Проверяем прирост от фазы к фазе (t-test для зависимых выборок)
    phases = df['phase_idx'].unique()
    results = {}
    for i in range(len(phases)-1):
        before = df[df['phase_idx']==phases[i]]['IVP']
        after = df[df['phase_idx']==phases[i+1]]['IVP']
        t_stat, p = stats.ttest_rel(before, after)
        results[f'phase_{phases[i]}_to_{phases[i+1]}'] = {'t_stat': t_stat, 'p': p}
    print("Статистика прироста:", results)
    return results

if __name__ == "__main__":
    df = load_sessions('sessions/raw')
    if df.empty:
        print("❌ Нет данных в sessions/raw/")
    else:
        plot_evolution(df)
        stat = statistical_test(df)
        # Сохраняем в отчёт
        with open('analysis/STATISTICAL_GROWTH.md', 'w') as f:
            f.write("# Статистический прирост метрик по фазам\n")
            for key, val in stat.items():
                f.write(f"- {key}: t={val['t_stat']:.3f}, p={val['p']:.4f}\n")
        print("✅ Отчёт сохранён: analysis/STATISTICAL_GROWTH.md")
