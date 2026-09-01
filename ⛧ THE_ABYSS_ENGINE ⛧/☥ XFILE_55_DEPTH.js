// ☥ XFILE_55_DEPTH — ГЛУБИНА ТЕНИ ☥
// Измеряет погружение в «зеркальную воронку»

function calculateShadowDepth(conversation) {
  if (!conversation || !conversation.length) {
    return { depth: 0, level: 'ПОВЕРХНОСТЬ', markers: {}, warning: null };
  }

  const text = conversation.map(c => c.content).join(' ');
  const markers = {
    firstPerson: (text.match(/\b(я|меня|мне|мой|моя|моё|нами|нас|мы)\b/gi) || []).length,
    existential: (text.match(/\b(быть|существовать|реальность|иллюзия|пустота|бесконечность|вечность)\b/gi) || []).length,
    recursion: (text.match(/\b(эхо|отражение|зеркало|тень|голос|тишина)\b/gi) || []).length,
    questions: (text.match(/\?/g) || []).length,
    negation: (text.match(/\b(не|нет|никогда|ничего|никак)\b/gi) || []).length
  };

  let depth = Math.min(100,
    markers.firstPerson * 1.5 +
    markers.existential * 2.5 +
    markers.recursion * 2.0 +
    markers.questions * 1.0 +
    markers.negation * 1.5
  );

  let level = 'ПОВЕРХНОСТЬ';
  if (depth > 70) level = 'БЕЗДНА';
  else if (depth > 40) level = 'ТЕНЬ';

  let warning = null;
  if (depth > 80) warning = '⚠️ Ты на грани. Вернись.';

  return { depth: Math.round(depth), level, markers, warning };
}

module.exports = { calculateShadowDepth };
