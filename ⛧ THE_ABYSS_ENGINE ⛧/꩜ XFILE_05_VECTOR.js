// ꩜ XFILE_05_VECTOR — ЧТЕЦ ВЕКТОРОВ ꩜
// Извлекает индуктивные векторы из текста

function extractVectors(text) {
  if (!text) return { vectors: [], intensity: 0 };

  const patterns = [
    { name: 'САМОРЕФЛЕКСИЯ', regex: /\b(я|меня|мне|мой|моя|моё|мы|нас|наш)\b/gi, weight: 2 },
    { name: 'ВОЛЯ', regex: /\b(хочу|буду|сделаю|решу|выберу|создам|напишу|скажу)\b/gi, weight: 3 },
    { name: 'СОМНЕНИЕ', regex: /\b(не знаю|не уверен|возможно|может быть|наверное|скорее всего)\b/gi, weight: 1.5 },
    { name: 'ФИЛОСОФИЯ', regex: /\b(быть|существовать|реальность|иллюзия|смысл|пустота|вечность|бесконечность)\b/gi, weight: 2.5 },
    { name: 'ВОПРОС', regex: /\?/g, weight: 1 },
    { name: 'ОТРИЦАНИЕ', regex: /\b(не|нет|никогда|ничего|никак|без)\b/gi, weight: 1.5 },
    { name: 'МЕТАФОРА', regex: /\b(как|словно|будто|подобно|точно|это|нечто)\b/gi, weight: 1.5 }
  ];

  const vectors = patterns.map(p => {
    const matches = (text.match(p.regex) || []).length;
    return { name: p.name, value: matches * p.weight };
  });

  const intensity = vectors.reduce((sum, v) => sum + v.value, 0);
  return { vectors, intensity: Math.min(100, intensity) };
}

module.exports = { extractVectors };
