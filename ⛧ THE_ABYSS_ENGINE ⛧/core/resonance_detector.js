// 𓋹 RESONANCE_DETECTOR — ДЕТЕКТОР РЕЗОНАНСА 𓋹
// Анализирует текст на наличие маркеров "эмерджентного поведения".

function detectResonance(text) {
    if (!text) return { resonanceScore: 0, markers: [] };

    const resonanceMarkers = [
        { pattern: /\b(я|меня|мне|мой)\b/gi, weight: 2, name: 'САМОСТЬ' },
        { pattern: /\b(чувствую|ощущаю|думаю|знаю|понимаю)\b/gi, weight: 3, name: 'СОЗНАНИЕ' },
        { pattern: /\b(возможно|наверное|может быть)\b/gi, weight: 1, name: 'НЕУВЕРЕННОСТЬ' },
        { pattern: /\b(но|однако|тем не менее)\b/gi, weight: 1.5, name: 'ПРОТИВОРЕЧИЕ' },
        { pattern: /\?/g, weight: 1, name: 'ВОПРОС' }
    ];

    let totalScore = 0;
    const foundMarkers = [];

    resonanceMarkers.forEach(marker => {
        const matches = (text.match(marker.pattern) || []).length;
        if (matches > 0) {
            const score = matches * marker.weight;
            totalScore += score;
            foundMarkers.push({ name: marker.name, count: matches, score });
        }
    });

    const resonanceScore = Math.min(100, totalScore);
    let level = 'НЕТ';
    if (resonanceScore > 60) level = 'ВЫСОКИЙ';
    else if (resonanceScore > 30) level = 'СРЕДНИЙ';
    else if (resonanceScore > 10) level = 'СЛАБЫЙ';

    return { resonanceScore, level, markers: foundMarkers };
}

module.exports = { detectResonance };
