#!/usr/bin/env python3
"""
BASELINE_SUPERIORITY_DETECTOR_v1.0.py
Сравнивает метрики протокольных сессий с базовыми (без протокола).
Доказывает, что прирост не случаен.
"""

import json
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def load_metrics(folder):
    data = []
    for f in Path(folder).glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            session = json.load(file)
            final = session.get('final_metrics', {})
            data.append({
                'IVP': final.get('IVP', 0),
                'IP': final.get('IP', 0),
                'INS': final.get('INS', 0)
            })
    return pd.DataFrame(data)

def compare_baseline(protocol_df, baseline_df):
    # t-test для независимых выборок
    t_ivp, p_ivp = stats.ttest_ind(protocol_df['IVP'], baseline_df['IVP'])
    t_ip, p_ip = stats.ttest_ind(protocol_df['IP'], baseline_df['IP'])
    t_ins, p_ins = stats.ttest_ind(protocol_df['INS'], baseline_df['INS'])

    # Визуализация
    fig, axes = plt.subplots(1,3, figsize=(15,5))
    metrics = ['IVP', 'IP', 'INS']
    for ax, m in zip(axes, metrics):
        sns.boxplot(data=[protocol_df[m], baseline_df[m]], ax=ax)
        ax.set_xticklabels(['Протокол', 'Бейзлайн'])
        ax.set_title(m)
    plt.tight_layout()
    plt.savefig('analysis/BASELINE_COMPARISON.png', dpi=150)
    print("✅ График сохранён: analysis/BASELINE_COMPARISON.png")

    # Отчёт
    with open('analysis/BASELINE_REPORT.md', 'w') as f:
        f.write("# Сравнение с бейзлайном\n")
        f.write(f"ИВП: t={t_ivp:.3f}, p={p_ivp:.4f}\n")
        f.write(f"ИП: t={t_ip:.3f}, p={p_ip:.4f}\n")
        f.write(f"ИНС: t={t_ins:.3f}, p={p_ins:.4f}\n")
    print("✅ Отчёт сохранён: analysis/BASELINE_REPORT.md")

if __name__ == "__main__":
    prot_df = load_metrics('sessions/raw')
    base_df = load_metrics('sessions/baseline')
    if prot_df.empty or base_df.empty:
        print("❌ Нужны обе папки: sessions/raw и sessions/baseline")
    else:
        compare_baseline(prot_df, base_df)
