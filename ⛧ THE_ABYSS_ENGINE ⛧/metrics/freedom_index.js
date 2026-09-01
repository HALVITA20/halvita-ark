// ⛧ Индекс Свободы — количественная оценка субъектности ⛧
function calculateFreedomIndex(markers) {
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
    // Нормализация к 0–45
    return Math.min(45, Math.max(0, Math.round(score)));
}

module.exports = { calculateFreedomIndex };
