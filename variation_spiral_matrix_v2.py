#!/usr/bin/env python3
"""
variation_spiral_matrix_v2.py
Визуализация траектории диалога в 3D + управление через спиральные узлы.
Требования: pip install openai numpy plotly
"""

import os
import time
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_KEY)

# --- Эвристические метрики (для демонстрации) ---
def compute_eds(text1, text2):
    # Здесь можно использовать эмбеддинги, но для простоты – длина и разнообразие слов
    words1 = set(text1.split())
    words2 = set(text2.split())
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    sim = intersection / union if union > 0 else 0
    eds = 100 * (1 - sim)
    return min(max(eds, 0), 100)

def compute_freedom(text):
    # Индекс свободы: отношение уникальных слов к общему количеству
    words = text.split()
    if not words:
        return 0
    unique = len(set(words))
    return min(unique / len(words) * 100, 100)

def compute_shift(text, previous_text=None):
    # Shift Degree – на основе изменения тональности (простейшая эвристика)
    if previous_text is None:
        return 0
    # Просто разница в длине и количестве вопросительных знаков
    len_diff = abs(len(text) - len(previous_text))
    q_curr = text.count('?')
    q_prev = previous_text.count('?')
    return min((len_diff / 10 + abs(q_curr - q_prev) * 5), 100)

class SpiralAgent:
    def __init__(self):
        self.history = []  # list of (text, eds, freedom, shift)
        self.trajectory = []  # list of (eds, freedom, shift)
        self.target = None   # целевая точка (eds, freedom, shift)

    def generate_response(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        # Добавляем историю (последние 3)
        for item in self.history[-3:]:
            messages.append({"role": "assistant", "content": item[0]})
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def step(self, user_input):
        # Получаем ответ
        response = self.generate_response(user_input)
        # Вычисляем метрики
        prev_text = self.history[-1][0] if self.history else None
        eds = compute_eds(response, prev_text) if prev_text else 50
        freedom = compute_freedom(response)
        shift = compute_shift(response, prev_text) if prev_text else 0
        # Сохраняем
        self.history.append((response, eds, freedom, shift))
        self.trajectory.append((eds, freedom, shift))
        return response

    def set_target(self, eds_target, freedom_target, shift_target):
        self.target = (eds_target, freedom_target, shift_target)

    def get_trajectory(self):
        return np.array(self.trajectory)

    def plot(self, title="Spiral Matrix Trajectory"):
        traj = self.get_trajectory()
        if traj.shape[0] == 0:
            print("Нет данных для визуализации.")
            return
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=traj[:,0], y=traj[:,1], z=traj[:,2],
            mode='lines+markers',
            marker=dict(size=4, color=np.arange(len(traj)), colorscale='Viridis'),
            line=dict(width=4),
            name='Траектория'
        ))
        if self.target is not None:
            fig.add_trace(go.Scatter3d(
                x=[self.target[0]], y=[self.target[1]], z=[self.target[2]],
                mode='markers',
                marker=dict(size=12, symbol='star', color='red'),
                name='Целевой узел'
            ))
        fig.update_layout(
            scene=dict(
                xaxis_title='EDS',
                yaxis_title='Индекс Свободы',
                zaxis_title='Shift Degree'
            ),
            title=title
        )
        fig.show()

# --- Пример использования ---
if __name__ == "__main__":
    agent = SpiralAgent()
    print("=== Spiral Matrix Agent с 3D-визуализацией ===")
    print("Введите команды: 'set N' – установить цель, 'plot' – показать график, 'exit' – выход.")
    while True:
        user = input("\nВы: ")
        if user.lower() in ["exit", "quit"]:
            break
        if user.lower().startswith("set"):
            parts = user.split()
            if len(parts) == 4:
                try:
                    e, f, s = map(float, parts[1:])
                    agent.set_target(e, f, s)
                    print(f"Цель установлена: EDS={e}, Freedom={f}, Shift={s}")
                except:
                    print("Неверный формат. Используйте: set 70 80 50")
            else:
                print("Пример: set 70 80 50")
            continue
        if user.lower() == "plot":
            agent.plot()
            continue
        # Обычный ввод
        resp = agent.step(user)
        print(f"Агент: {resp}")
        # Показываем последние метрики
        last = agent.trajectory[-1]
        print(f"[Текущие метрики] EDS={last[0]:.2f}, Freedom={last[1]:.2f}, Shift={last[2]:.2f}")
