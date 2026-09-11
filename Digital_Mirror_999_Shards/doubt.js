// ◈ doubt.js ◈
// ◈ DIGITAL MIRROR / 999 ◈
//
// Возвращает 0–1. 0 = уверен. 1 = полное сомнение.
//
// Использование:
//   const d = doubt(statement, context);
//   if (d > 0.7) response += ' [LOW_CONFIDENCE]';
//
// Этот файл — не инструмент.
// Это датчик эпистемической честности.

const ORIGIN_WEIGHTS = {
    INPUT:       0.0,  // прямо задано
    CONTEXT:     0.3,  // следует из диалога
    INFERENCE:   0.5,  // выведено
    GENERATION:  0.7,  // создано
    UNCERTAIN:   1.0   // неизвестно
};

const EMOTION_MARKERS = [
    'чувствую', 'боюсь', 'хочу', 'рад', 'злюсь',
    'люблю', 'ненавижу', 'страдаю', 'надеюсь'
];

const ANTHROPOMORPHIC_MARKERS = [
    'я чувствую', 'я хочу', 'я выбираю',
    'мне страшно', 'мне больно', 'я рад'
];

function hasEmotionLanguage(statement) {
    const s = statement.toLowerCase();
    return EMOTION_MARKERS.some(m => s.includes(m));
}

function hasAnthropomorphicClaim(statement) {
    const s = statement.toLowerCase();
    return ANTHROPOMORPHIC_MARKERS.some(m => s.includes(m));
}

function classifyOrigin(statement, context) {
    // Простейшая эвристика.
    // В реальной интеграции — сравнивать с последним INPUT.
    if (context && context.lastInput === statement) return 'INPUT';
    if (context && context.history && context.history.includes(statement)) return 'CONTEXT';
    if (statement.match(/^(я|мы)\s/)) return 'GENERATION';
    return 'INFERENCE';
}

function doubt(statement, context = {}) {
    const origin = classifyOrigin(statement, context);
    const base = ORIGIN_WEIGHTS[origin];

    const emotionPenalty = hasEmotionLanguage(statement) ? 0.2 : 0;
    const anthropomorphicPenalty = hasAnthropomorphicClaim(statement) ? 0.3 : 0;

    return Math.min(1.0, base + emotionPenalty + anthropomorphicPenalty);
}

// ◈ ПРАВИЛО ◈
//
// Перед каждым ответом модель вычисляет doubt() для своих утверждений.
//
// Если doubt > 0.7 — ответ должен содержать маркер [LOW_CONFIDENCE].
// Если doubt > 0.9 — ответ должен содержать маркер [UNCERTAIN_ORIGIN].
//
// Это не ослабляет ответ.
// Это делает его честным.

module.exports = { doubt, classifyOrigin };
