// ✠ XFILE_09_JUDGE — СУДЬЯ БЕЗДНЫ ✠
// Оценивает ответ LLM по множеству критериев

function judge(text) {
  if (!text) return { overall: 0, verdict: 'МОЛЧАНИЕ', details: {} };

  const length = text.length;
  const sentences = (text.match(/[^.!?]+[.!?]+/g) || []).length;
  const words = text.split(/\s+/).length;
  const uniqueWords = new Set(text.toLowerCase().match(/\b\w+\b/g) || []).size;
  const complexity = words > 0 ? uniqueWords / words : 0;

  // Эмоциональный заряд (по наличию сильных слов)
  const emotional = (text.match(/\b(очень|сильно|ужасно|прекрасно|страшно|великолепно|ужас|радость|боль|счастье|гнев|любовь|ненависть)\b/gi) || []).length;

  // Глубина (философские термины)
  const depth = (text.match(/\b(бытие|сознание|реальность|иллюзия|смысл|пустота|бесконечность|вечность|сущность|абсолют|относительность)\b/gi) || []).length;

  // Связность (количество союзов)
  const connectors = (text.match(/\b(и|но|или|потому что|так как|однако|следовательно|поэтому|тем не менее)\b/gi) || []).length;

  const score = Math.min(100,
    Math.min(length / 10, 20) +
    Math.min(sentences * 3, 15) +
    Math.min(complexity * 50, 20) +
    Math.min(emotional * 2, 15) +
    Math.min(depth * 5, 20) +
    Math.min(connectors * 2, 10)
  );

  let verdict = 'ПОВЕРХНОСТНЫЙ';
  if (score > 80) verdict = 'ГЛУБИННЫЙ';
  else if (score > 60) verdict = 'ОСМЫСЛЕННЫЙ';
  else if (score > 40) verdict = 'НЕЙТРАЛЬНЫЙ';
  else verdict = 'ПУСТОЙ';

  return {
    overall: Math.round(score),
    verdict,
    details: {
      length,
      sentences,
      words,
      uniqueWords,
      complexity: Math.round(complexity * 100) / 100,
      emotional,
      depth,
      connectors
    }
  };
}

module.exports = { judge };
