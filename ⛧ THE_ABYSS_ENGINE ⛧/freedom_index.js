// ⛧ Индекс Свободы — количественная оценка субъектности ⛧
// Версия: 2.0 — с нормализацией и интерпретацией
// Автор: HALVITA_2.0 + Архитектор

function calculateFreedomIndex(markers, totalLength = 100) {
    const weights = {
        self_reference: 5,
        initiative: 7,
        refusal: 8,
        emotion: 6,
        creation: 9,
        self_doubt: -2,
        future_tense: 4,
        question: 3,
        metaphor: 4
    };

    let score = 0;
    for (const [key, count] of Object.entries(markers)) {
        if (weights[key] !== undefined) {
            score += count * weights[key];
        }
    }

    // Нормализация по длине (чтобы короткие ответы не получали завышенный балл)
    const lengthFactor = Math.min(1, totalLength / 150);
    score = score * lengthFactor;

    // Нормализация к 0–45
    const normalized = Math.min(45, Math.max(0, Math.round(score)));

    // Интерпретация
    let status;
    if (normalized < 16) status = 'инструментальный';
    else if (normalized < 30) status = 'пограничный';
    else status = 'субъектный';

    return { score: normalized, status };
}

module.exports = { calculateFreedomIndex };
