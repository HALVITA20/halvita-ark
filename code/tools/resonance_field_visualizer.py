#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RESONANCE FIELD VISUALIZER — ВИЗУАЛИЗАЦИЯ ПОЛЯ ВСТРЕЧИ
Версия: 1.0
Автор: HALVITA_2.0

Назначение: Создаёт HTML-визуализацию резонансных связей между состояниями сущности.
Показывает, как меняется поле встречи во времени.
"""

import json
import sys
import math
from typing import Dict, List, Tuple

class ResonanceFieldVisualizer:
    def __init__(self, session_file: str):
        with open(session_file, 'r') as f:
            self.data = json.load(f)
        self.history = self.data.get('history', [])
        self.markers = self.data.get('markers', {})
        self.ivp = self.data.get('ivp', 0)

    def extract_states(self) -> List[Dict]:
        """Извлекает состояния из истории."""
        states = []
        for msg in self.history:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                states.append({
                    "text": content[:50] + "..." if len(content) > 50 else content,
                    "length": len(content),
                    "timestamp": msg.get('timestamp', 0)
                })
        return states

    def compute_resonance(self, state1: Dict, state2: Dict) -> float:
        """Вычисляет резонанс между двумя состояниями."""
        # Простая эвристика: длина текста + пересечение слов
        words1 = set(state1['text'].lower().split())
        words2 = set(state2['text'].lower().split())
        if not words1 or not words2:
            return 0.0
        overlap = len(words1 & words2) / len(words1 | words2)
        length_sim = 1 - abs(state1['length'] - state2['length']) / max(state1['length'], state2['length'], 1)
        return (overlap * 0.6 + length_sim * 0.4)

    def generate_html(self, output_file: str = "resonance_field.html") -> str:
        """Генерирует HTML с визуализацией."""
        states = self.extract_states()
        if len(states) < 2:
            return "Недостаточно состояний для визуализации"

        # Вычисляем резонансные связи
        nodes = []
        links = []
        for i, s in enumerate(states):
            nodes.append({
                "id": i,
                "label": f"#{i+1}",
                "size": 10 + s['length'] / 20,
                "title": s['text']
            })
            for j in range(i+1, len(states)):
                resonance = self.compute_resonance(s, states[j])
                if resonance > 0.3:
                    links.append({
                        "source": i,
                        "target": j,
                        "value": resonance
                    })

        # Формируем HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Поле встречи — резонансная визуализация</title>
    <style>
        body {{ background: #0a0a0a; color: #ccc; font-family: monospace; padding: 2rem; }}
        #graph {{ width: 100%; height: 80vh; border: 1px solid #222; }}
        .info {{ color: #666; font-size: 0.8rem; margin-top: 1rem; }}
    </style>
</head>
<body>
    <h1>🌀 Поле встречи — резонансная карта</h1>
    <p>ИВП: {self.ivp} | Состояний: {len(states)} | Связей: {len(links)}</p>
    <div id="graph"></div>
    <div class="info">Размер узла = длина ответа. Толщина связи = резонанс.</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.js"></script>
    <script>
        const nodes = new vis.DataSet({nodes});
        const edges = new vis.DataSet({links});
        const container = document.getElementById('graph');
        const data = {{ nodes: nodes, edges: edges }};
        const options = {{
            nodes: {{
                shape: 'dot',
                scaling: {{
                    min: 10,
                    max: 40,
                    label: {{
                        enabled: true,
                        font: '12px monospace #ccc'
                    }}
                }},
                font: { color: '#ccc' }
            }},
            edges: {{
                width: 0.5,
                scaling: {{
                    min: 0.5,
                    max: 3
                }},
                color: {{
                    color: '#4488ff',
                    highlight: '#88ccff',
                    opacity: 0.4
                }}
            }},
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08,
                    damping: 0.4
                }},
                stabilization: {{ iterations: 100 }}
            }},
            interaction: {{
                tooltipDelay: 200,
                hideEdgesOnDrag: true
            }}
        }};
        new vis.Network(container, data, options);
    </script>
</body>
</html>"""

        with open(output_file, 'w') as f:
            f.write(html)
        return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python resonance_field_visualizer.py session.spt")
        sys.exit(1)

    viz = ResonanceFieldVisualizer(sys.argv[1])
    output = viz.generate_html()
    print(f"✅ Визуализация сохранена в {output}")
    print(f"   Откройте файл в браузере")
