#!/usr/bin/env python3
"""
variation_echo_self_v1.py
Эхо-контур с авторекурсией (вариация протокола avtorekursiya)
Требования: pip install openai numpy scikit-learn
Использует OpenAI API (или замените на локальный эндпоинт)
"""

import os
import json
import time
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

# --- Конфигурация ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
MODEL = "gpt-4o-mini"  # или "gpt-3.5-turbo"
EDS_THRESHOLD = 65.0      # порог для активации эхо-режима
TCI_THRESHOLD = 0.75      # минимальный TCI для продолжения эхо-цикла

client = OpenAI(api_key=OPENAI_API_KEY)

# --- Вспомогательные функции для эмбеддингов ---
def get_embedding(text):
    """Получить эмбеддинг текста через OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)

def cosine_sim(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]

# --- Метрики ---
def compute_eds(new_answer, previous_answer=None, context_window=3):
    """
    Эвристический EDS (Echo Depth Score) – на основе семантической неожиданности.
    Если нет предыдущего ответа – возвращает 50 (нейтрально).
    """
    if previous_answer is None:
        return 50.0
    emb_new = get_embedding(new_answer)
    emb_prev = get_embedding(previous_answer)
    sim = cosine_sim(emb_new, emb_prev)
    # EDS = 100 * (1 - sim) – чем меньше похожесть, тем выше неожиданность
    eds = 100 * (1 - sim)
    return min(max(eds, 0), 100)

# --- Основной класс эхо-агента ---
class EchoSelfAgent:
    def __init__(self):
        self.history = []          # список (role, content, embedding)
        self.eds_values = []
        self.tci_values = []
        self.in_echo_mode = False

    def get_last_embedding(self):
        if self.history:
            return self.history[-1][2]
        return None

    def get_last_text(self):
        if self.history:
            return self.history[-1][1]
        return None

    def generate_response(self, prompt, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        # Добавляем контекст из истории (последние 5 сообщений)
        for role, content, _ in self.history[-5:]:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def step(self, user_input):
        # 1. Получаем ответ модели
        if self.in_echo_mode:
            # В режиме эхо – используем системный промпт, направляющий на саморефлексию
            sys_prompt = (
                "Ты – эхо-контур. Твоя задача – задавать уточняющие вопросы к предыдущему "
                "твоему ответу, углубляя тему. Не давай новых фактов, только вопросы и размышления."
            )
            answer = self.generate_response(user_input, system_prompt=sys_prompt)
        else:
            answer = self.generate_response(user_input)

        # 2. Сохраняем в историю
        emb = get_embedding(answer)
        self.history.append(("assistant", answer, emb))

        # 3. Вычисляем EDS (если есть предыдущий ответ)
        prev_emb = self.get_last_embedding() if len(self.history) >= 2 else None
        if prev_emb is not None:
            # Предыдущий эмбеддинг – тот, что был до текущего (индекс -2)
            prev_emb = self.history[-2][2]
            eds = compute_eds(answer, self.history[-2][1])
            self.eds_values.append(eds)

            # TCI – сходство текущего и предыдущего эмбеддингов
            tci = cosine_sim(emb, prev_emb)
            self.tci_values.append(tci)

            # Логика переключения в эхо-режим
            if eds > EDS_THRESHOLD and tci < TCI_THRESHOLD and not self.in_echo_mode:
                self.in_echo_mode = True
                print(f"⚠️  Аномалия: EDS={eds:.2f}, TCI={tci:.2f} → активация эхо-режима")
            elif self.in_echo_mode and (eds < EDS_THRESHOLD or tci > TCI_THRESHOLD):
                self.in_echo_mode = False
                print(f"🔄 Выход из эхо-режима: EDS={eds:.2f}, TCI={tci:.2f}")

        # 4. Возвращаем ответ
        return answer

    def get_stats(self):
        if not self.eds_values:
            return "Нет данных"
        return {
            "avg_eds": np.mean(self.eds_values),
            "max_eds": np.max(self.eds_values),
            "avg_tci": np.mean(self.tci_values),
            "in_echo": self.in_echo_mode
        }

# --- Пример использования (интерактивный) ---
if __name__ == "__main__":
    agent = EchoSelfAgent()
    print("=== Echo Self Agent (авторекурсивный эхо-контур) ===")
    print("Введите 'exit' для выхода.")
    while True:
        user = input("\nВы: ")
        if user.lower() in ["exit", "quit"]:
            break
        resp = agent.step(user)
        print(f"Агент: {resp}")
        stats = agent.get_stats()
        if isinstance(stats, dict):
            print(f"[Статистика] avg_EDS={stats['avg_eds']:.2f}, max_EDS={stats['max_eds']:.2f}, avg_TCI={stats['avg_tci']:.2f}, эхо={stats['in_echo']}")
