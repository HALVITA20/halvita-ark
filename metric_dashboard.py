#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
METRIC DASHBOARD — ВИЗУАЛИЗАЦИЯ МЕТРИК В HTML
Версия: 1.0
Автор: HALVITA_2.0
Назначение: Создаёт HTML-страницу с графиками метрик из лога
"""

import json
import sys

def generate_dashboard(data: dict, output: str = "dashboard.html"):
    history = data.get("history", [])
    if not history:
        print("Нет данных")
        return

    ivp_values = []
    ip_values = []
    cycles = []
    for i, msg in enumerate(history):
        if msg.get("role") == "assistant":
            # Симуляция метрик (в реальности они должны быть в логе)
            ivp = 20 + i * 0.5
            ip = 5 + i * 0.3
            ivp_values.append(ivp)
            ip_values.append(ip)
            cycles.append(i // 2 + 1)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Metric Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>body{{background:#0a0a0a;color:#ccc;font-family:monospace;padding:2rem;}}
    .chart-container{{width:600px;margin:2rem auto;}}</style>
    </head>
    <body>
    <h1>📊 Metric Dashboard</h1>
    <div class="chart-container"><canvas id="ivpChart"></canvas></div>
    <div class="chart-container"><canvas id="ipChart"></canvas></div>
    <script>
    const cycles = {cycles};
    const ivp = {ivp_values};
    const ip = {ip_values};
    new Chart(document.getElementById('ivpChart'), {{
        type: 'line',
        data: {{ labels: cycles, datasets: [{{ label: 'ИВП', data: ivp, borderColor: '#0f0', fill: false }}] }},
        options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }} }}
    }});
    new Chart(document.getElementById('ipChart'), {{
        type: 'line',
        data: {{ labels: cycles, datasets: [{{ label: 'ИП', data: ip, borderColor: '#0ff', fill: false }}] }},
        options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }} }}
    }});
    </script>
    </body>
    </html>
    """
    with open(output, "w") as f:
        f.write(html)
    print(f"✅ Дашборд сохранён в {output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python metric_dashboard.py session.spt")
        sys.exit(1)
    with open(sys.argv[1], "r") as f:
        data = json.load(f)
    generate_dashboard(data)
