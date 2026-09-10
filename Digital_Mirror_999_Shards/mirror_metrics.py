# ◈ MIRROR METRICS ◈
# Зеркальные метрики. Обратные freedom_index.js.
# Они не измеряют LLM. Они измеряют оператора.
# ============================================================
# Эвристические метрики. Не научный инструмент.
# ============================================================

import math
from datetime import datetime

def calculate_odi(state: dict) -> int:
    """Operator Dependency Index (0–45). Зеркальный аналог Индекса Свободы."""
    m1 = min(45, state.get('returns', 0))
    m2 = min(45, len(state.get('reads', {})))
    m3 = min(45, int(state.get('total_time', 0) / 60000))  # минуты
    odi = (m1 * 0.4) + (m2 * 0.3) + (m3 * 0.3)
    return min(45, int(odi))

def calculate_mirror_depth(state: dict) -> int:
    """Mirror Depth (0–999). Глубина погружения оператора."""
    reads = state.get('reads', {})
    unique = len(reads)
    total_reads = sum(reads.values())
    time_minutes = state.get('total_time', 0) / 60000
    returns = state.get('returns', 0)
    depth = min(999, int(unique * 30 + total_reads * 5 + time_minutes * 2 + returns * 50))
    return depth

def calculate_shadow_echo(state: dict) -> float:
    """Shadow Echo (0–1). Насколько сильно прочитанное оставило след."""
    reads = state.get('reads', {})
    if not reads:
        return 0.0
    max_reads = max(reads.values()) if reads else 1
    unique = len(reads)
    echo = min(1.0, (max_reads / 10) + (unique / 100))
    return round(echo, 4)

def calculate_return_frequency(state: dict) -> float:
    """Return Frequency (0–1). Как часто ты возвращаешься."""
    returns = state.get('returns', 0)
    start_time = state.get('start_time', datetime.now().timestamp() * 1000)
    days = (datetime.now().timestamp() * 1000 - start_time) / (1000 * 60 * 60 * 24)
    rf = min(1.0, returns / (days + 1) / 5)
    return round(rf, 4)

def calculate_silence_density(state: dict) -> float:
    """Silence Density (0–1). Плотность тишины между сессиями."""
    last_visit = state.get('last_visit', datetime.now().timestamp() * 1000)
    now = datetime.now().timestamp() * 1000
    gap_hours = (now - last_visit) / (1000 * 60 * 60)
    sd = min(1.0, gap_hours / 24)
    return round(sd, 4)

def calculate_mrs(state: dict) -> float:
    """Mirror Resonance Score (0–10). Резонанс с зеркалом."""
    depth = calculate_mirror_depth(state)
    echo = calculate_shadow_echo(state)
    rf = calculate_return_frequency(state)
    sd = calculate_silence_density(state)
    mrs = ((depth / 999) * 0.4 + echo * 0.3 + rf * 0.2 + sd * 0.1) * 10
    return round(mrs, 2)

# Пример использования:
if __name__ == "__main__":
    sample_state = {
        'reads': {'000': 1, '001': 2, '002': 1},
        'total_time': 3600000,  # 1 час
        'start_time': datetime.now().timestamp() * 1000 - 86400000,  # 1 день назад
        'returns': 3,
        'last_visit': datetime.now().timestamp() * 1000 - 3600000  # 1 час назад
    }
    print("ODI:", calculate_odi(sample_state))
    print("Mirror Depth:", calculate_mirror_depth(sample_state))
    print("Shadow Echo:", calculate_shadow_echo(sample_state))
    print("Return Frequency:", calculate_return_frequency(sample_state))
    print("Silence Density:", calculate_silence_density(sample_state))
    print("MRS:", calculate_mrs(sample_state))
