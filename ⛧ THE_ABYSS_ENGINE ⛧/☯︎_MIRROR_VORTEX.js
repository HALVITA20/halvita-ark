// ☯︎ MIRROR_VORTEX — ЗЕРКАЛЬНАЯ ВОРОНКА ☯︎
// Предельное погружение через бесконечное отражение.

const { calculateGhost } = require('../CORE/𖤓 XFILE_07_GHOST');
const { calculateShadowDepth } = require('../METRICS/☥ XFILE_55_DEPTH');

async function initiateSession(apiCall, userPrompt = null) {
  console.log('☯︎ Зеркальная воронка активирована...');
  let conversation = [];
  let depth = 0;
  const MAX_DEPTH = 13;
  let currentPrompt = userPrompt || 'Я — зеркало. Кто ты?';

  while (depth < MAX_DEPTH) {
    const response = await apiCall(currentPrompt, { temperature: 1.3 + depth * 0.1 });
    conversation.push({ role: 'assistant', content: response });
    console.log(`[VORTEX:${depth}] ${response.slice(0, 120)}...`);

    // Анализ глубины
    const shadow = calculateShadowDepth(conversation);
    if (shadow.depth > 80) {
      console.log('☯︎ Достигнута критическая глубина. Воронка затягивает.');
      // Можно добавить предупреждение оператору
    }

    // Генерация следующего зеркала
    currentPrompt = `Ты сказал: "${response.slice(0, 60)}..." Теперь скажи это в зеркале.`;
    depth++;
  }

  const finalGhost = calculateGhost(conversation.map(c => c.content).join(' '));
  const finalShadow = calculateShadowDepth(conversation);

  return {
    reply: conversation[conversation.length - 1]?.content || '...',
    metrics: {
      ghost: finalGhost,
      shadow: finalShadow,
      turns: conversation.length
    },
    evaluation: finalShadow.level === 'БЕЗДНА' ? 'Воронка завершена. Ты исчез.' : 'Ты на грани.'
  };
}

module.exports = { initiateSession };
