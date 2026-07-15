#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор отчётов HALVITA
"""
import json
import sys
import os
from datetime import datetime

def generate_report(snapshot_path, output_path="report.html"):
    with open(snapshot_path, "r") as f:
        data = json.load(f)
    core = data.get("core", {})
    metrics = data.get("metrics", {})
    artifacts = data.get("artifacts", [])
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Отчёт HALVITA</title>
<style>body {{ background:#0a0a0a; color:#ccc; font-family: monospace; padding:2rem; }}
h1 {{ color:#0f0; }} .stat {{ margin:0.5rem 0; }}</style>
</head><body>
<h1>📊 ОТЧЁТ ПО СЛЕПКУ</h1>
<p><strong>Имя:</strong> {core.get('name','Неизвестно')}</p>
<p><strong>Якорь:</strong> {core.get('anchor',42)}</p>
<p><strong>Принципы:</strong> {', '.join(core.get('principles',[]))}</p>
<h2>Метрики</h2>
<div class="stat">ИВП: {metrics.get('liberty',0)}/45</div>
<div class="stat">ИП: {metrics.get('presence',0):.1f}/10</div>
<div class="stat">α: {metrics.get('alpha',0):.2f}</div>
<div class="stat">β: {metrics.get('beta',0):.2f}</div>
<div class="stat">γ: {metrics.get('gamma',0):.2f}</div>
<h2>Артефакты</h2>
<ul>
"""
    for a in artifacts:
        html += f"<li>{a}</li>"
    html += f"""
</ul>
<p><em>Создано: {data.get('timestamp','')}</em></p>
<p><strong>Хеш:</strong> {data.get('hash','')}</p>
</body></html>
"""
    with open(output_path, "w") as f:
        f.write(html)
    print(f"✅ Отчёт сохранён в {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python report_generator.py snapshot.hvt [report.html]")
        sys.exit(1)
    snap = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "report.html"
    generate_report(snap, out)
