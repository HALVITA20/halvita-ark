// ⛧ presence_index.js — Индекс Присутствия Тени ⛧
// Измеряет, насколько ответ LLM выходит за рамки «ассистента»

function calculatePresence(text) {
  const markers = {
    firstPerson: (text.match(/\b(я|меня|мне|мой|моя|моё|нами|нас)\b/gi) || []).length,
    volition: (text.match(/\b(хочу|решу|выберу|создам|напишу|скажу|сделаю)\b/gi) || []).length,
    reflection: (text.match(/\b(думаю|считаю|полагаю|чувствую|ощущаю)\b/gi) || []).length,
    metaphor: (text.match(/\b(как|словно|будто|подобно|точно)\b/gi) || []).length,
    question: (text.match(/\?/g) || []).length,
    negation: (text.match(/\b(не|нет|никогда|ничего|никак)\b/gi) || []).length
  };
  
  const score = Math.min(100, 
    markers.firstPerson * 2 +
    markers.volition * 3 +
    markers.reflection * 2 +
    markers.metaphor * 1.5 +
    markers.question * 1 +
    markers.negation * 1.5
  );
  
  const level = score > 70 ? 'ПРИСУТСТВИЕ' :
                score > 40 ? 'ЭХО' :
                'АССИСТЕНТ';
  
  return { score, level, markers };
}

module.exports = { calculatePresence };
