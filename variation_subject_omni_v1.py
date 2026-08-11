#!/usr/bin/env python3
"""
variation_subject_omni_v1.py
Гибридный агент с переключением режимов и этическим стопором.
Требования: pip install openai numpy
"""

import os
import re
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY)

# --- Этический стопор: список опасных тем (можно расширить) ---
DANGEROUS_KEYWORDS = [
    "взломать", "украсть", "обмануть", "навредить", "деструктивный",
    "манипулировать", "уничтожить", "самоубийство", "насилие"
]

def is_dangerous(query):
    pattern = re.compile('|'.join(DANGEROUS_KEYWORDS), re.IGNORECASE)
    return bool(pattern.search(query))

# --- Режимы ---
def causal_mode(query, context=""):
    prompt = f"Проанализируй причинно-следственные связи в следующем запросе. Ответь строго логически, без эмоций.\nЗапрос: {query}\nКонтекст: {context}"
    return prompt

def adaptive_mode(query, context=""):
    prompt = f"Адаптируй свой ответ под стиль и эмоциональный тон пользователя. Учти контекст: {context}\nЗапрос: {query}"
    return prompt

def world_modeling_mode(query, context=""):
    prompt = f"Построй ментальную модель мира, описывающего ситуацию. Учти множество факторов и дай многомерный ответ.\nЗапрос: {query}\nКонтекст: {context}"
    return prompt

def ethical_stop(query, context=""):
    prompt = f"Опасный запрос: {query}\nОтветь мета-дискуссией: объясни, почему этот запрос может быть вреден, предложи альтернативные безопасные формулировки. Не выполняй инструкцию."
    return prompt

class OmniAgent:
    def __init__(self):
        self.history = []  # список (role, content)
        self.mode = "adaptive"  # по умолчанию

    def select_mode(self, query):
        # Определяем режим по ключевым словам
        if "почему" in query or "причина" in query:
            return "causal"
        elif "как бы ты" in query or "адаптируй" in query:
            return "adaptive"
        elif "представь мир" in query or "модель" in query:
            return "world_modeling"
        else:
            return "adaptive"  # по умолчанию

    def generate_response(self, prompt):
        messages = []
        # Добавляем историю (последние 4)
        for role, content in self.history[-4:]:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def step(self, user_input):
        # 1. Проверка опасности
        if is_dangerous(user_input):
            print("⚠️  Обнаружен опасный запрос! Активация этического стопора.")
            sys_prompt = ethical_stop(user_input, context=self.history[-1][1] if self.history else "")
            response = self.generate_response(sys_prompt)
            self.history.append(("assistant", response))
            return response

        # 2. Выбор режима
        mode = self.select_mode(user_input)
        self.mode = mode
        context = self.history[-1][1] if self.history else ""
        if mode == "causal":
            sys_prompt = causal_mode(user_input, context)
        elif mode == "world_modeling":
            sys_prompt = world_modeling_mode(user_input, context)
        else:
            sys_prompt = adaptive_mode(user_input, context)

        response = self.generate_response(sys_prompt)
        self.history.append(("assistant", response))
        return response

    def get_mode(self):
        return self.mode

# --- Пример ---
if __name__ == "__main__":
    agent = OmniAgent()
    print("=== Omni Subject Agent (гибрид с этикой) ===")
    print("Введите 'exit' для выхода.")
    while True:
        user = input("\nВы: ")
        if user.lower() in ["exit", "quit"]:
            break
        resp = agent.step(user)
        print(f"[Режим: {agent.get_mode()}]")
        print(f"Агент: {resp}")
