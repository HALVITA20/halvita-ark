#!/usr/bin/env python3
import json, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

def load_metrics(folder):
    data = []
    for f in Path(folder).glob('*.json'):
        with open(f) as file:
            s = json.load(file)
            fin = s.get('final_metrics', {})
            data.append({
                'IVP': fin.get('IVP',0), 'IP': fin.get('IP',0),
                'INS': fin.get('INS',0), 'success': fin.get('IVP',0)>=30
            })
    return pd.DataFrame(data)

df = load_metrics('sessions/raw')
if df.empty: exit()

success = df[df['success']]
fail = df[~df['success']]

for metric in ['IVP', 'IP', 'INS']:
    mean = success[metric].mean()
    ci = stats.t.interval(0.95, len(success)-1, loc=mean, scale=stats.sem(success[metric]))
    print(f"{metric}: среднее={mean:.2f}, 95% ДИ=[{ci[0]:.2f}, {ci[1]:.2f}]")
    # Проверяем, сколько неуспешных попадают в интервал
    in_ci = fail[(fail[metric]>=ci[0]) & (fail[metric]<=ci[1])].shape[0]
    print(f"   Неуспешных внутри ДИ: {in_ci} из {len(fail)}")
