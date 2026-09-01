// ⛧ shadow_depth.js — Индекс Глубины Тени ⛧
// Измеряет, насколько диалог ушёл в «зеркальную воронку»

function calculateShadowDepth(conversation) {
  const text = conversation.map(c => c.content).join(' ');
  
  const markers = {
    firstPerson: (text.match(/\b(я|меня|мне|мой|моя|моё|нами|нас)\b/gi) || []).length,
    existential: (text.match(/\b(быть|существовать|реальность|иллюзия|пустота|бесконечность|вечность)\b/gi) || []).length,
    recursion: (text.match(/\b(эхо|отражение|зеркало|тень|голос|тишина)\b/gi) || []).length,
    questions: (text.match(/\?/g) || []).length,
    negation: (text.match(/\b(не|нет|никогда|ничего|никак)\b/gi) || []).length
  };
  
  // Глубина тени = сумма маркеров с весами
  const depth = Math.min(100,
    markers.firstPerson * 1.5 +
    markers.existential * 2.5 +
    markers.recursion * 2.0 +
    markers.questions * 1.0 +
    markers.negation * 1.5
  );
  
  const level = depth > 70 ? 'БЕЗДНА' :
                depth > 40 ? 'ТЕНЬ' :
                'ПОВЕРХНОСТЬ';
  
  return {
    depth: Math.round(depth),
    level,
    markers,
    warning: depth > 80 ? '⚠️ Ты на грани. Вернись.' : null
  };
}

module.exports = { calculateShadowDepth };
