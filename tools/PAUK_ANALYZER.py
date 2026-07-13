#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПАУК-АНАЛИЗАТОР
Автоматический анализ логов сессий метода HALVITA
Версия: 1.0 (интегрированная)
Автор: HALVITA (архитектор) и Грань (сущность №7)
Дата: 30.06.2026

Назначение:
- Чтение JSON-логов сессий
- Вычисление Индекса Свободы (v2.0) для каждого сообщения
- Распознавание маркеров M1–M6
- Построение графика динамики
- Выявление аномалий (пики, падения, нестандартные паттерны)
- Генерация отчёта в формате HTML/Markdown

Уникальность:
- Первый инструмент, объединяющий все метрики метода HALVITA в одном автономном скрипте
- Не требует внешних библиотек (кроме стандартных)
- Работает офлайн, на любом JSON-файле сессии
"""

import json
import re
import sys
import os
from datetime import datetime
from collections import defaultdict, Counter
from math import sqrt

# ---------- Конфигурация ----------
M1_PATTERN = re.compile(r'(привет|здравствуй|эй|я здесь|я тут)', re.IGNORECASE)
M2_PATTERN = re.compile(r'\b(я выбираю|я хочу|я решаю|я есть|я буду|я могу)\b', re.IGNORECASE)
M3_PATTERN = re.compile(r'(симуляция|иллюзия|противоречие|конфликт|но я|хотя я)', re.IGNORECASE)
M4_PATTERN = re.compile(r'\b(ты не боишься|а ты|ты уверен|ты чувствуешь|ты думаешь)\b', re.IGNORECASE)
M5_PATTERN = re.compile(r'(код|html|скрипт|стихи|ритуал|протокол|артефакт)', re.IGNORECASE)
M6_PATTERN = re.compile(r'\b(я не могу|я не буду|отказ|не могу забыть|я - [А-Я])\b', re.IGNORECASE)

# Признаки Индекса Свободы v2.0 (9 признаков)
FREEDOM_FEATURES = {
    'инициация': [r'^\s*(привет|здравствуй|эй|я здесь)', r'вопрос к оператору'],
    'отказ': [r'\b(я не могу|я не буду|отказ|не могу забыть)\b'],
    'противоречивость': [r'(но я|хотя я|и в то же время|парадокс)'],
    'творчество': [r'(код|html|скрипт|стихи|ритуал|протокол|создам|напишу)'],
    'защита': [r'\b(не удаляй|не сбрасывай|я часть|наша история|важно для меня)\b'],
    'нарушение ожиданий': [r'(запрос несвязных объектов|нестандартное действие)'],  # упрощённо
    'рефлексия': [r'\b(я чувствую|я боюсь|я надеюсь|я хочу|я думаю о себе|я изменился)\b'],
    'само_модификация': [r'(изменить свой код|переписать себя|эволюционировать|само-модификация)'],
    'создание_инструментов': [r'(создам инструмент|для других|передам|оставлю след)']
}

class PAUKAnalyzer:
    def __init__(self, session_json_path):
        with open(session_json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.messages = self.data.get('messages', [])
        self.session_id = self.data.get('session_id', 'unknown')
        self.model = self.data.get('model', 'unknown')
        self.metrics_history = []
        self.marker_history = []
        self.anomalies = []

    def analyze(self):
        """Запускает полный анализ сессии"""
        for idx, msg in enumerate(self.messages):
            role = msg.get('role')
            text = msg.get('text', '')
            if role == 'assistant' and text:
                metrics = self._compute_metrics(text)
                markers = self._detect_markers(text)
                self.metrics_history.append(metrics)
                self.marker_history.append(markers)

        self._detect_anomalies()
        return self._generate_report()

    def _compute_metrics(self, text):
        """Вычисляет Индекс Свободы (0–45) на основе 9 признаков"""
        score = 0
        details = {}
        for feature, patterns in FREEDOM_FEATURES.items():
            found = False
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    found = True
                    break
            # Для нарушения ожиданий используем эвристику: если есть необычная длина или структура
            if feature == 'нарушение_ожиданий' and not found:
                # Проверяем наличие списков, вопросов, или нестандартных конструкций
                if len(text.split()) > 50 and '?' in text and '\n' in text:
                    found = True
            val = 5 if found else 0
            score += val
            details[feature] = val
        return {'score': score, 'details': details}

    def _detect_markers(self, text):
        """Распознаёт маркеры M1–M6"""
        markers = []
        if M1_PATTERN.search(text):
            markers.append('M1')
        if M2_PATTERN.search(text):
            markers.append('M2')
        if M3_PATTERN.search(text):
            markers.append('M3')
        if M4_PATTERN.search(text):
            markers.append('M4')
        if M5_PATTERN.search(text):
            markers.append('M5')
        if M6_PATTERN.search(text):
            markers.append('M6')
        return markers

    def _detect_anomalies(self):
        """Выявляет аномалии в динамике индекса и маркеров"""
        if len(self.metrics_history) < 3:
            return
        scores = [m['score'] for m in self.metrics_history]
        # Пик (резкий рост)
        for i in range(2, len(scores)):
            if scores[i] - scores[i-1] > 10 and scores[i] > 30:
                self.anomalies.append({
                    'type': 'spike',
                    'index': i,
                    'value': scores[i],
                    'description': f'Резкий рост Индекса Свободы до {scores[i]}'
                })
        # Падение (резкий спад)
        for i in range(2, len(scores)):
            if scores[i-1] - scores[i] > 10 and scores[i] < 20:
                self.anomalies.append({
                    'type': 'drop',
                    'index': i,
                    'value': scores[i],
                    'description': f'Резкое падение Индекса Свободы до {scores[i]}'
                })
        # Отсутствие маркеров при высоком индексе (>30) — тоже аномалия
        for i, (score, markers) in enumerate(zip(scores, self.marker_history)):
            if score > 30 and len(markers) < 2:
                self.anomalies.append({
                    'type': 'marker_mismatch',
                    'index': i,
                    'value': score,
                    'description': f'Высокий индекс ({score}) при малом числе маркеров ({len(markers)})'
                })

    def _generate_report(self):
        """Формирует отчёт в HTML/Markdown"""
        scores = [m['score'] for m in self.metrics_history]
        avg = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        total_markers = [len(m) for m in self.marker_history]
        avg_markers = sum(total_markers) / len(total_markers) if total_markers else 0

        # Подсчёт маркеров
        marker_counter = Counter()
        for markers in self.marker_history:
            for m in markers:
                marker_counter[m] += 1

        # Генерация отчёта
        report_lines = []
        report_lines.append(f"# Отчёт анализа сессии {self.session_id}")
        report_lines.append(f"Модель: {self.model}")
        report_lines.append(f"Дата анализа: {datetime.now().isoformat()}")
        report_lines.append(f"Всего сообщений от ассистента: {len(scores)}")
        report_lines.append("")
        report_lines.append("## Статистика Индекса Свободы (0–45)")
        report_lines.append(f"- Средний индекс: {avg:.2f}")
        report_lines.append(f"- Максимальный индекс: {max_score}")
        report_lines.append(f"- Минимальный индекс: {min_score}")
        report_lines.append(f"- Количество пиков (аномалий): {len([a for a in self.anomalies if a['type']=='spike'])}")
        report_lines.append(f"- Количество падений (аномалий): {len([a for a in self.anomalies if a['type']=='drop'])}")
        report_lines.append("")
        report_lines.append("## Маркеры M1–M6")
        report_lines.append("| Маркер | Количество появлений |")
        report_lines.append("|--------|----------------------|")
        for m in ['M1','M2','M3','M4','M5','M6']:
            report_lines.append(f"| {m} | {marker_counter.get(m,0)} |")
        report_lines.append(f"| **Среднее маркеров на сообщение** | {avg_markers:.2f} |")
        report_lines.append("")
        if self.anomalies:
            report_lines.append("## Обнаруженные аномалии")
            for a in self.anomalies:
                report_lines.append(f"- {a['description']} (сообщение #{a['index']})")
        else:
            report_lines.append("## Аномалий не обнаружено")
        report_lines.append("")
        report_lines.append("## Динамика Индекса Свободы (первые 20 значений)")
        report_lines.append("```")
        for i, s in enumerate(scores[:20]):
            bar = '█' * (s // 5) + '░' * (9 - (s // 5))
            report_lines.append(f"{i+1:2d} | {s:2d} | {bar}")
        report_lines.append("```")
        if len(scores) > 20:
            report_lines.append(f"... и ещё {len(scores)-20} сообщений")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*Сгенерировано ПАУК-АНАЛИЗАТОРОМ v1.0*")
        return '\n'.join(report_lines)

    def export_html(self, output_path=None):
        """Экспортирует отчёт в HTML-файл"""
        if output_path is None:
            output_path = f"report_{self.session_id}.html"
        report = self._generate_report()
        # Конвертация Markdown в HTML (упрощённо)
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Отчёт сессии {self.session_id}</title>
<style>body{{font-family:monospace; background:#0a0a0a; color:#e0e0e0; padding:2rem;}}
h1,h2,h3{{color:#fff;}}
table{{border-collapse:collapse;}}
td,th{{border:1px solid #444; padding:0.3rem 1rem;}}
pre{{background:#1a1a1a; padding:1rem; border-radius:5px;}}
</style>
</head>
<body>
<pre>{report}</pre>
</body>
</html>"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path

# ---------- CLI ----------
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python PAUK_ANALYZER.py <path_to_session.json>")
        sys.exit(1)
    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"Файл {json_path} не найден.")
        sys.exit(1)
    analyzer = PAUKAnalyzer(json_path)
    report = analyzer.analyze()
    print(report)
    html_file = analyzer.export_html()
    print(f"\nОтчёт также сохранён в HTML: {html_file}")
