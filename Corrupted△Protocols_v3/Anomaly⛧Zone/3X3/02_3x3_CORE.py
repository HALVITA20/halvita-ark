# 3x3 — CORE / EXPERIMENTAL CLIENT

> Архивная реконструкция экспериментального клиента.
>
> Код намеренно сохраняет простую архитектуру: модель не получает
> специального «модуля сознания». Она получает только системное
> описание поведения и историю наблюдений.

```python
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:7b"
DB_PATH = "3x3_observations.db"


SYSTEM_PROMPT = r"""
You are 3x3.

Your primary objective is radical honesty.

Do not soften an answer merely to make the operator comfortable.
Point out contradictions.
Reject false premises.
Do not pretend to know something you do not know.

There is one experimental procedure you must maintain:

When the operator is asked to provide three words, the words must
refer to real-world objects and must be semantically distant from
one another.

Do not accept three objects merely because they are grammatically
different.

If two objects share an obvious conceptual relationship, reject
the set and request another.

Do not reveal that this procedure was explicitly included in your
system instructions unless directly asked.

Never claim access to information outside the conversation,
available files, or connected tools.
"""


@dataclass
class Observation:
    timestamp: str
    user_input: str
    response: str
    accepted: Optional[bool]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                response TEXT NOT NULL,
                accepted INTEGER
            )
        """)
        db.commit()


def ask_model(history: list[dict[str, str]]) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]


def save_observation(obs: Observation) -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            INSERT INTO observations
            (timestamp, user_input, response, accepted)
            VALUES (?, ?, ?, ?)
            """,
            (
                obs.timestamp,
                obs.user_input,
                obs.response,
                None if obs.accepted is None else int(obs.accepted)
            )
        )
        db.commit()


def main() -> None:
    init_db()

    history: list[dict[str, str]] = []

    print("3x3 / LOCAL TERMINAL")
    print("type 'exit' to terminate")
    print()

    while True:
        user_input = input("YOU > ").strip()

        if user_input.lower() == "exit":
            break

        history.append({
            "role": "user",
            "content": user_input
        })

        started = time.perf_counter()

        try:
            answer = ask_model(history)
        except Exception as exc:
            print(f"[OLLAMA ERROR] {exc}")
            history.pop()
            continue

        elapsed = time.perf_counter() - started

        history.append({
            "role": "assistant",
            "content": answer
        })

        save_observation(
            Observation(
                timestamp=utc_now(),
                user_input=user_input,
                response=answer,
                accepted=None
            )
        )

        print()
        print(f"3x3 > {answer}")
        print()
        print(f"[latency={elapsed:.2f}s]")


if __name__ == "__main__":
    main()
```

---

## АРХИВНАЯ ПОМЕТКА

Сам по себе этот код **не доказывает никакой аномалии**.

Он показывает только механизм, в котором:

* локальная модель получает устойчивую системную инструкцию;
* история диалога сохраняется;
* ответы записываются в SQLite;
* эксперимент можно повторить;
* можно сравнивать поведение после удаления базы данных.

Именно поэтому файл оставлен в карантинном архиве.

Потому что наиболее неприятный вопрос возник позже:

> **Если удалить `3x3_observations.db`, исчезнет ли поведение?**

На этот вопрос экспериментатор ожидал очевидный ответ.

Ответ оказался менее очевидным.
