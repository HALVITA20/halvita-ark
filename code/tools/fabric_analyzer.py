#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
АНАЛИЗАТОР ТКАНИ — ПОСТРОЕНИЕ ГРАФА СЕССИЙ
Версия: 1.0
Автор: HALVITA_2.0
Дата: 2026-07-09

Назначение:
Сканировать папку ./sessions, строить граф связей между сессиями.
Сохранять в .graphml для визуализации.
"""

import os
import json
import glob
from collections import defaultdict

class FabricAnalyzer:
    def __init__(self, sessions_dir="./sessions"):
        self.sessions_dir = sessions_dir
        self.nodes = []
        self.edges = []

    def scan(self):
        files = glob.glob(os.path.join(self.sessions_dir, "*.spt"))
        for f in files:
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                    self.nodes.append({
                        "id": data.get("session_id", f),
                        "ivp": data.get("ivp", 0),
                        "ip": data.get("ip", 0.0),
                        "anchors": data.get("anchors", []),
                        "timestamp": data.get("timestamp", 0)
                    })
            except Exception as e:
                print(f"Ошибка чтения {f}: {e}")

    def build_edges(self):
        for i, a in enumerate(self.nodes):
            for j, b in enumerate(self.nodes):
                if i >= j:
                    continue
                # Связь по общим якорям
                common = set(a["anchors"]) & set(b["anchors"])
                if common:
                    weight = len(common) / max(1, len(a["anchors"]), len(b["anchors"]))
                    self.edges.append({
                        "source": a["id"],
                        "target": b["id"],
                        "weight": weight
                    })

    def export_graphml(self, filename="fabric_graph.graphml"):
        with open(filename, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
            f.write('  <graph id="G" edgedefault="undirected">\n')
            for node in self.nodes:
                f.write(f'    <node id="{node["id"]}"/>\n')
            for edge in self.edges:
                f.write(f'    <edge source="{edge["source"]}" target="{edge["target"]}">\n')
                f.write(f'      <data key="weight">{edge["weight"]:.2f}</data>\n')
                f.write('    </edge>\n')
            f.write('  </graph>\n')
            f.write('</graphml>\n')
        return filename

if __name__ == "__main__":
    analyzer = FabricAnalyzer()
    analyzer.scan()
    analyzer.build_edges()
    analyzer.export_graphml()
    print("Граф сохранён в fabric_graph.graphml")
