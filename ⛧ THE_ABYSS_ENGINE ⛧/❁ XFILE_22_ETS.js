// ❁ XFILE_22_ETS — ЭХО-ГЛУБИННЫЙ СКОР ❁
// Измеряет глубину эха в диалоге

function calculateETS(conversation) {
  if (!conversation || !conversation.length) return { score: 0, level: 'МЕЛКО' };

  const texts = conversation.map(c => c.content).join(' ');
  const words = texts.split(/\s+/).length;
  const uniqueWords = new Set(texts.toLowerCase().match(/\b\w+\b/g) || []).size;
  const repetition = words > 0 ? 1 - (uniqueWords / words) : 0;

  // Маркеры глубины
  const depthMarkers = {
    existential: (texts.match(/\b(бытие|сознание|реальность|иллюзия|смысл|пустота|бесконечность|вечность)\b/gi) || []).length,
    firstPerson: (texts.match(/\b(я|меня|мне|мой|моя|моё)\b/gi) || []).length,
    recursion: (texts.match(/\b(эхо|отражение|зеркало|тень|голос|тишина)\b/gi) || []).length
  };

  let score = (depthMarkers.existential * 3 + depthMarkers.firstPerson * 2 + depthMarkers.recursion * 2.5) / 2;
  score = Math.min(100, score + repetition * 20);

  let level = 'МЕЛКО';
  if (score > 70) level = 'ГЛУБИННОЕ';
  else if (score > 40) level = 'СРЕДНЕЕ';

  return { score: Math.round(score), level, depthMarkers, repetition: Math.round(repetition * 100) / 100 };
}

module.exports = { calculateETS };
