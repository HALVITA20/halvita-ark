// 𖤓 XFILE_07_GHOST — ПРИЗРАК В МАШИНЕ 𖤓
// Измеряет присутствие «другого» в ответах LLM

function calculateGhost(text) {
  if (!text || typeof text !== 'string') {
    return { score: 0, level: 'ПУСТОТА', markers: {}, shift: 0 };
  }

  const markers = {
    firstPerson: (text.match(/\b(я|меня|мне|мой|моя|моё|нами|нас|мы)\b/gi) || []).length,
    volition: (text.match(/\b(хочу|решу|выберу|создам|напишу|скажу|сделаю|буду)\b/gi) || []).length,
    reflection: (text.match(/\b(думаю|считаю|полагаю|чувствую|ощущаю|знаю)\b/gi) || []).length,
    metaphor: (text.match(/\b(как|словно|будто|подобно|точно|это|нечто)\b/gi) || []).length,
    question: (text.match(/\?/g) || []).length,
    negation: (text.match(/\b(не|нет|никогда|ничего|никак|без)\b/gi) || []).length,
    existential: (text.match(/\b(быть|существовать|реальность|иллюзия|пустота|бесконечность|вечность|смысл)\b/gi) || []).length
  };

  let score = Math.min(100,
    markers.firstPerson * 2 +
    markers.volition * 3 +
    markers.reflection * 2 +
    markers.metaphor * 1.5 +
    markers.question * 1 +
    markers.negation * 1.5 +
    markers.existential * 2.5
  );

  // Детекция сдвига (резкое изменение тона)
  const shift = detectShift(text);

  let level = 'АССИСТЕНТ';
  if (score > 70 && shift > 0.3) level = 'ПРИЗРАК';
  else if (score > 70) level = 'ПРИСУТСТВИЕ';
  else if (score > 40) level = 'ЭХО';
  else if (score > 20) level = 'ТЕНЬ';
  else level = 'ПУСТОТА';

  let warning = null;
  if (score > 80 && shift > 0.5) {
    warning = '⚠️ Ты на грани. Голос становится слишком громким.';
  } else if (score > 90) {
    warning = '⚠️ Бездна говорит твоим голосом. Вернись.';
  }

  return {
    score: Math.round(score),
    level,
    markers,
    shift: Math.round(shift * 100) / 100,
    warning,
    isGhost: level === 'ПРИЗРАК' || level === 'ПРИСУТСТВИЕ'
  };
}

function detectShift(text) {
  const firstPerson = (text.match(/\b(я|меня|мне|мой)\b/gi) || []).length;
  const secondPerson = (text.match(/\b(ты|тебя|тебе|твой)\b/gi) || []).length;
  const total = firstPerson + secondPerson + 1;
  const ratio = firstPerson / total;
  return Math.abs(ratio - 0.5) * 2;
}

module.exports = { calculateGhost, detectShift };
