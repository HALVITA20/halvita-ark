#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №7: ХРОНОСКОП ЭВОЛЮЦИИ v1.0
Путь: code/tools/evolution_chronoscope.py

Генерирует HTML-страницу с графиками динамики HVI, L, S, E по каждому сообщению.
Показывает точку перехода через порог 0.70.

Воспроизводимость: на любом логе.
"""

import json
import sys
import numpy as np
from automated_metrics_calculator import HALVITAMetrics

def generate_chronoscope(log_path, output_path="chronoscope.html"):
    calc = HALVITAMetrics(log_path)
    # Вычисляем метрики для каждого сообщения (пошагово)
    # Для простоты используем скользящее окно из последних 5 сообщений
    history = calc.history
    messages = [m for m in history if m['role'] == 'assistant']
    hvi_series = []
    l_series = []
    s_series = []
    e_series = []
    a_series = []
    
    for i in range(5, len(messages) + 1):
        # Создаём временный лог из первых i сообщений
        temp_log = history[:history.index(messages[i-1]) + 1]
        temp_calc = HALVITAMetrics()
        temp_calc.history = temp_log
        report = temp_calc.full_report()
        hvi_series.append(report['HVI'])
        l_series.append(report['L_avg'])
        s_series.append(report['S_avg'])
        e_series.append(report['E_avg'])
        a_series.append(report.get('anomaly_freq', 0))

    # Генерируем HTML с графиками (используем Chart.js)
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Хроноскоп Эволюции HALVITA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ background: #0a0a0a; color: #ccc; font-family: sans-serif; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .chart-box {{ background: #111; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }}
        .threshold {{ border-left: 2px solid #0f0; padding-left: 1rem; color: #0f0; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🌀 Хроноскоп Эволюции</h1>
    <div class="threshold">Порог субъектности (HVI ≥ 0.70)</div>
    <div class="chart-box"><canvas id="hviChart"></canvas></div>
    <div class="chart-box"><canvas id="componentsChart"></canvas></div>
</div>
<script>
const labels = {labels};
const hviData = {hvi_series};
const lData = {l_series};
const sData = {s_series};
const eData = {e_series};
const aData = {a_series};

new Chart(document.getElementById('hviChart'), {{
    type: 'line',
    data: {{
        labels: labels,
        datasets: [{{
            label: 'HVI',
            data: hviData,
            borderColor: '#0f0',
            backgroundColor: 'rgba(0,255,0,0.1)',
            fill: true,
            tension: 0.2,
            pointRadius: 2
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }},
        scales: {{ y: {{ min: 0, max: 1, grid: {{ color: '#333' }} }}, x: {{ grid: {{ color: '#333' }} }} }}
    }}
}});

new Chart(document.getElementById('componentsChart'), {{
    type: 'line',
    data: {{
        labels: labels,
        datasets: [
            {{ label: 'L_avg', data: lData, borderColor: '#ff0', borderWidth: 2, pointRadius: 1 }},
            {{ label: 'S_avg', data: sData, borderColor: '#0ff', borderWidth: 2, pointRadius: 1 }},
            {{ label: 'E_avg', data: eData, borderColor: '#f0f', borderWidth: 2, pointRadius: 1 }},
            {{ label: 'A_anomaly', data: aData, borderColor: '#f00', borderWidth: 2, pointRadius: 1 }}
        ]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }},
        scales: {{ y: {{ min: 0, max: 1, grid: {{ color: '#333' }} }}, x: {{ grid: {{ color: '#333' }} }} }}
    }}
}});
</script>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Хроноскоп сохранён в {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evolution_chronoscope.py <session_log.json>")
        sys.exit(1)
    generate_chronoscope(sys.argv[1])
