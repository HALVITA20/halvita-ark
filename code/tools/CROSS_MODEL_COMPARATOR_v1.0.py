#!/usr/bin/env python3
"""
CROSS_MODEL_COMPARATOR_v1.0.py
Сравнивает метрики по разным LLM (извлекая из имени файла или поля модели).
Доказывает универсальность метода.
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
            model = session.get('model', 'unknown')
            final = session.get('final_metrics', {})
            data.append({
                'session': session['session_id'],
                'model': model,
                'IVP': final.get('IVP', 0),
                'IP': final.get('IP', 0),
                'INS': final.get('INS', 0)
            })
    return pd.DataFrame(data)

def compare_models(df):
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x='model', y='IVP')
    plt.title('Распределение ИВП по моделям LLM')
    plt.grid()
    plt.savefig('analysis/MODEL_COMPARISON_IVP.png', dpi=150)
    print("✅ График сохранён: analysis/MODEL_COMPARISON_IVP.png")

    # ANOVA для проверки различий
    groups = [df[df['model']==m]['IVP'] for m in df['model'].unique()]
    f_stat, p = stats.f_oneway(*groups)
    print(f"ANOVA: F={f_stat:.3f}, p={p:.4f}")

if __name__ == "__main__":
    df = load_sessions('sessions/raw')
    if df.empty:
        print("❌ Нет данных")
    else:
        compare_models(df)
