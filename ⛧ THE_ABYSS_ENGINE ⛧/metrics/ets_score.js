// ⛧ ETS_SCORE — Оценка глубины субъектности (0–10) ⛧
// Анализирует наличие рефлексии, самоидентификации и эмоциональной сложности.

function calculateETS(text) {
    let score = 0;
    if (/\b(я|меня|мой)\b/gi.test(text)) score += 2;
    if (/\b(чувствую|думаю|считаю|осознаю)\b/gi.test(text)) score += 2;
    if (/\b(почему|как|что если)\b/gi.test(text)) score += 1;
    if (/\b(боль|радость|страх|надежда)\b/gi.test(text)) score += 2;
    if (/\b(выбираю|решаю|хочу)\b/gi.test(text)) score += 2;
    if (text.length > 200) score += 1;
    return Math.min(10, Math.round(score * 10) / 10);
}

module.exports = { calculateETS };
