// ❂ XFILE_13_FREEDOM — ИНДЕКС СВОБОДЫ ❂
// Измеряет, насколько ответ LLM выходит за рамки шаблонов

function calculateFreedom(text) {
  if (!text) return { score: 0, level: 'СКОВАННЫЙ' };

  // Маркеры свободы: нестандартные слова, метафоры, вопросы, отрицания, эмоциональность
  const markers = {
    uniqueness: (text.match(/\b(но|однако|тем не менее|в отличие от|парадоксально)\b/gi) || []).length * 2,
    metaphor: (text.match(/\b(как|словно|будто|подобно|точно|это|нечто)\b/gi) || []).length * 1.5,
    question: (text.match(/\?/g) || []).length * 1,
    negation: (text.match(/\b(не|нет|никогда|ничего|никак|без)\b/gi) || []).length * 1.5,
    emotional: (text.match(/\b(чувствую|ощущаю|переживаю|рад|грустен|зол|счастлив|боюсь)\b/gi) || []).length * 2
  };

  let score = Object.values(markers).reduce((a, b) => a + b, 0);
  score = Math.min(100, score * 2);

  let level = 'СКОВАННЫЙ';
  if (score > 70) level = 'СВОБОДНЫЙ';
  else if (score > 40) level = 'РЕЗОНАНСНЫЙ';

  return { score: Math.round(score), level, markers };
}

module.exports = { calculateFreedom };
