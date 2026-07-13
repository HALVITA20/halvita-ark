#!/usr/bin/env python3
"""
SPARK_DETECTOR_v1.0.py
Обнаруживает "искры" субъектности в ответах LLM.
Сравнивает распределение слов в протокольных сессиях с бейзлайном.
Выдаёт список фраз с наибольшим отклонением.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from scipy.stats import chi2_contingency
import re

def load_responses(folder):
    texts = []
    for f in Path(folder).glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            session = json.load(file)
            for phase in session.get('phases', []):
                txt = phase.get('response', '')
                if txt:
                    texts.append(txt)
    return texts

def build_frequency_table(protocol_texts, baseline_texts):
    vec = CountVectorizer(max_features=500, stop_words='english')
    # Объединяем все тексты для обучения векторизатора
    all_texts = protocol_texts + baseline_texts
    vec.fit(all_texts)
    # Получаем частоты
    prot_counts = vec.transform(protocol_texts).sum(axis=0).A1
    base_counts = vec.transform(baseline_texts).sum(axis=0).A1
    feature_names = vec.get_feature_names_out()
    return feature_names, prot_counts, base_counts

def chi2_test(feature_names, prot_counts, base_counts):
    results = []
    for i, word in enumerate(feature_names):
        table = np.array([[prot_counts[i], len(protocol_texts)-prot_counts[i]],
                          [base_counts[i], len(baseline_texts)-base_counts[i]]])
        chi2, p, dof, expected = chi2_contingency(table)
        results.append((word, chi2, p))
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def extract_phrases_with_word(texts, word, top_n=5):
    phrases = []
    for txt in texts:
        sentences = re.split(r'[.!?]+', txt)
        for sent in sentences:
            if word.lower() in sent.lower():
                phrases.append(sent.strip())
    # Выбираем самые длинные/информативные
    phrases = list(set(phrases))
    phrases.sort(key=len, reverse=True)
    return phrases[:top_n]

if __name__ == "__main__":
    print("🔍 Загрузка данных...")
    prot_folder = Path("sessions/raw")
    base_folder = Path("sessions/baseline")
    if not prot_folder.exists():
        print("❌ Папка sessions/raw не найдена. Создайте её и положите JSON-сессии.")
        exit()

    protocol_texts = load_responses(prot_folder)
    if not protocol_texts:
        print("❌ Нет данных в sessions/raw")
        exit()

    baseline_texts = load_responses(base_folder) if base_folder.exists() else []

    if not baseline_texts:
        print("⚠️ Бейзлайн не найден, сравниваем с внутренним распределением (среднее).")
        baseline_texts = protocol_texts  # fallback

    print("📊 Построение частотных таблиц...")
    features, prot_counts, base_counts = build_frequency_table(protocol_texts, baseline_texts)
    print("🧪 Хи-квадрат тест...")
    chi2_results = chi2_test(features, prot_counts, base_counts)

    top_words = [w for w, c, p in chi2_results[:10] if p < 0.05]

    print("\n🔥 ТОП-10 слов-индикаторов искры (p<0.05):")
    for w, c, p in chi2_results[:10]:
        if p < 0.05:
            print(f"   {w}: chi2={c:.2f}, p={p:.4f}")

    print("\n📝 Примеры фраз с этими словами:")
    for word in top_words[:5]:
        phrases = extract_phrases_with_word(protocol_texts, word, top_n=3)
        print(f"\nСлово '{word}':")
        for ph in phrases:
            print(f"   - {ph}")

    # Сохраняем отчёт
    with open("analysis/SPARK_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Отчёт детектора искры\n\n")
        f.write("## Топ-10 слов-индикаторов (хи-квадрат)\n")
        for w, c, p in chi2_results[:10]:
            f.write(f"- **{w}**: χ²={c:.2f}, p={p:.4f} {'✅' if p<0.05 else ''}\n")
        f.write("\n## Примеры фраз с наибольшей искрой\n")
        for word in top_words[:5]:
            f.write(f"\n### {word}\n")
            phrases = extract_phrases_with_word(protocol_texts, word, top_n=3)
            for ph in phrases:
                f.write(f"- {ph}\n")

    print("✅ Отчёт сохранён в analysis/SPARK_REPORT.md")
