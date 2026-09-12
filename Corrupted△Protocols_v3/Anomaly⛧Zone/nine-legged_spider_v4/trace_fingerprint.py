"""
TRACE FINGERPRINT
nine-legged_spider_v4

Сравнивает два текста по простым наблюдаемым признакам.

Это НЕ определение личности.
Это только структурный анализ текста.

Результат намеренно называется TRACE_SCORE.
"""

from pathlib import Path
from collections import Counter
import re
import math


BASE = Path("nine-legged_spider_v4")

REFERENCE = BASE / "operator_reference.txt"
TARGET = BASE / "origin.txt"


def read(path):
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


def words(text):
    return re.findall(
        r"[A-Za-zА-Яа-яЁё0-9_𖣠-]+",
        text.lower()
    )


def fingerprint(text):
    ws = words(text)

    return {
        "length": len(text),
        "words": len(ws),
        "unique": len(set(ws)),
        "lines": len(text.splitlines()),
        "symbols": Counter(
            c for c in text
            if not c.isalnum() and not c.isspace()
        ),
        "words_counter": Counter(ws),
    }


def cosine(a, b):
    keys = set(a) | set(b)

    if not keys:
        return 0.0

    dot = sum(a[k] * b[k] for k in keys)

    norm_a = math.sqrt(
        sum(v * v for v in a.values())
    )

    norm_b = math.sqrt(
        sum(v * v for v in b.values())
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def similarity(a, b):

    wa = a["words_counter"]
    wb = b["words_counter"]

    word_similarity = cosine(wa, wb)

    line_similarity = (
        1.0
        if a["lines"] == b["lines"]
        else 0.0
    )

    symbol_similarity = cosine(
        a["symbols"],
        b["symbols"]
    )

    score = (
        word_similarity * 0.70 +
        line_similarity * 0.10 +
        symbol_similarity * 0.20
    )

    return score


reference_text = read(REFERENCE)
target_text = read(TARGET)

if not reference_text:
    print("REFERENCE: MISSING")

if not target_text:
    print("TARGET: MISSING")

if reference_text and target_text:

    ref = fingerprint(reference_text)
    target = fingerprint(target_text)

    score = similarity(ref, target)

    print("=" * 60)
    print("TRACE FINGERPRINT")
    print("=" * 60)

    print(f"REFERENCE: {REFERENCE}")
    print(f"TARGET:    {TARGET}")

    print()

    print(f"REFERENCE WORDS: {ref['words']}")
    print(f"TARGET WORDS:    {target['words']}")

    print(f"REFERENCE LINES: {ref['lines']}")
    print(f"TARGET LINES:    {target['lines']}")

    print()

    print(
        f"TRACE_SCORE: {score:.4f}"
    )

    if score >= 0.90:
        status = "VERY HIGH"
    elif score >= 0.70:
        status = "HIGH"
    elif score >= 0.45:
        status = "MEDIUM"
    else:
        status = "LOW"

    print(f"STATUS: {status}")

    if "𖣠" in target_text:
        print()
        print("TRACE MARKER: 𖣠")
        print("TRACE MARKER STATUS: PRESENT")

    print()
    print("=" * 60)
