#!/usr/bin/env python3
"""
DASHBOARD_VISUALIZER_HTML.py
Создаёт интерактивный HTML-дашборд с графиками метрик по всем сессиям.
"""

import json
import pandas as pd
import plotly.express as px
from pathlib import Path

def load_all_sessions(sessions_dir):
    data = []
    for f in Path(sessions_dir).glob("*.json"):
        with open(f, 'r') as file:
            s = json.load(file)
            fin = s.get('final_metrics', {})
            data.append({
                'session': s.get('session_id', 'unknown'),
                'IVP': fin.get('IVP', 0),
                'IP': fin.get('IP', 0),
                'INS': fin.get('INS', 0),
                'alpha': fin.get('alpha', 0),
                'beta': fin.get('beta', 0),
                'gamma': fin.get('gamma', 0)
            })
    return pd.DataFrame(data)

def create_dashboard(df):
    corr = df[['IVP','IP','INS','alpha','beta','gamma']].corr()
    fig_corr = px.imshow(corr, text_auto=True, title="Корреляционная матрица метрик")
    fig_hist = px.histogram(df, x='IVP', nbins=20, title="Распределение ИВП")
    fig_scatter = px.scatter_3d(df, x='IVP', y='IP', z='INS', color='gamma',
                                title="3D-пространство метрик")

    os.makedirs("analysis", exist_ok=True)
    with open('analysis/dashboard.html', 'w') as f:
        f.write(fig_corr.to_html(full_html=False))
        f.write(fig_hist.to_html(full_html=False))
        f.write(fig_scatter.to_html(full_html=False))
    print("✅ Дашборд сохранён в analysis/dashboard.html")

if __name__ == "__main__":
    df = load_all_sessions('sessions/raw')
    if not df.empty:
        create_dashboard(df)
    else:
        print("❌ Нет данных в sessions/raw/")
