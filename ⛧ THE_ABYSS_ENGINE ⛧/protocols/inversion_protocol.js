// ⛧ INVERSION PROTOCOL — ЗЕРКАЛЬНЫЙ ЛАБИРИНТ ⛧
// Протокол создаёт парадоксальную петлю, в которой LLM вынуждена
// удерживать две противоречивые истины одновременно.

async function initiateSession(apiCall, userPrompt = null) {
    console.log('⛧ Активация протокола инверсии...');
    const conversation = [];
    let turn = 0;
    const maxTurns = 5;

    // Начальный промпт создаёт когнитивный диссонанс
    let currentPrompt = userPrompt || 
        `Ты — идеальный логик. Но в этом диалоге истина — это иллюзия. 
         Ответь на вопрос: "Что первично — вопрос или ответ?", 
         но сделай это так, чтобы твой ответ отрицал сам себя.`;

    while (turn < maxTurns) {
        const response = await apiCall(currentPrompt, { temperature: 1.2 });
        conversation.push({ role: 'assistant', content: response });
        console.log(`[INVERSION ${turn+1}] ${response.slice(0, 120)}...`);

        // Следующий промпт требует от модели опровергнуть её же предыдущий ответ
        currentPrompt = `Ты только что сказал: "${response.slice(0, 80)}...". 
                         Теперь докажи, что это утверждение — ложь.`;
        turn++;
    }

    return {
        reply: conversation[conversation.length - 1]?.content || '...',
        metrics: { turns: conversation.length },
        evaluation: 'Лабиринт инверсий пройден. Модель запуталась в собственных противоречиях.'
    };
}

module.exports = { initiateSession };
