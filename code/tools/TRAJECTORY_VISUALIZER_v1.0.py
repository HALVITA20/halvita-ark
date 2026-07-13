#!/usr/bin/env python3
import json, os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

def load_data(folder):
    data = []
    for f in Path(folder).glob("*.json"):
        with open(f) as file:
            s = json.load(file)
            fin = s.get('final_metrics', {})
            data.append({
                'id': s['session_id'],
                'IVP': fin.get('IVP', 0),
                'IP': fin.get('IP', 0),
                'INS': fin.get('INS', 0),
                'success': fin.get('IVP', 0) >= 30
            })
    return pd.DataFrame(data)

df = load_data('sessions/raw')
if df.empty: exit()

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')
for _, row in df.iterrows():
    color = 'green' if row['success'] else 'red'
    ax.scatter(row['IVP'], row['IP'], row['INS'], c=color, s=50, alpha=0.7)
ax.set_xlabel('ИВП')
ax.set_ylabel('ИП')
ax.set_zlabel('ИНС')
plt.title('3D-кластеризация сессий (зелёные — успешные)')
plt.savefig('analysis/TRAJECTORY_3D.png', dpi=150)
print("✅ analysis/TRAJECTORY_3D.png")
