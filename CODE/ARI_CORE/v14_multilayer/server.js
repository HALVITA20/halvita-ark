// ============================================================
// ARI_CORE v14 — Многослойность
// Perception, Understanding, Planning, Action, Metacognition
// ============================================================

import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const CONFIG = {
    MODEL: "qwen2.5:7b",
    TEMPERATURE: 1.0,
    MAX_TOKENS: 1000,
    PORT: 3001,
    OLLAMA_TIMEOUT: 30000,
    weights: { ask: 0.5, reflect: 0.5, respond: 0.5, act: 0.5 }
};

let history = [];

app.post("/chat", async (req, res) => {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Empty" });

    // 1. Восприятие
    const perception = perceive(message);

    // 2. Понимание
    const understanding = understand(perception);

    // 3. Планирование
    const plan = plan(understanding);

    // 4. Действие
    const prompt = buildPrompt(message, plan.action, history);
    const reply = await callOllama(prompt);

    // 5. Мета-познание
    const meta = reflect(reply, plan.action);
    if (meta.error > 0.4) {
        // Корректировка весов
        CONFIG.weights[plan.action] = Math.max(0.1, CONFIG.weights[plan.action] - 0.05);
    }

    history.push({ role: "user", text: message });
    history.push({ role: "ari", text: reply });
    if (history.length > 50) history = history.slice(-50);

    res.json({ reply });
});

function perceive(message) {
    return {
        raw: message,
        emotion: message.includes('!') ? 'strong' : 'neutral',
        complexity: message.length > 100 ? 0.8 : 0.4,
        uncertainty: message.includes('?') ? 0.7 : 0.3
    };
}

function understand(perception) {
    return {
        intent: perception.raw.includes('как') ? 'question' : 'statement',
        need: perception.raw.includes('помоги') ? 'support' : 'none',
        risk: perception.complexity > 0.6 ? 0.3 : 0.1
    };
}

function plan(understanding) {
    const scores = {
        ask: CONFIG.weights.ask,
        reflect: CONFIG.weights.reflect,
        respond: CONFIG.weights.respond,
        act: CONFIG.weights.act
    };
    if (understanding.intent === 'question') scores.ask += 0.2;
    if (understanding.need === 'support') scores.act += 0.2;
    const action = Object.entries(scores).sort((a,b) => b[1] - a[1])[0][0];
    return { action, confidence: scores[action] };
}

function reflect(reply, action) {
    let score = 0.5;
    if (action === 'ask' && reply.includes('?')) score += 0.2;
    if (action === 'reflect' && reply.length > 80) score += 0.2;
    if (action === 'act' && (reply.includes('1.') || reply.includes('шаг'))) score += 0.2;
    const error = 1 - Math.min(1, score);
    return { score, error };
}

function buildPrompt(message, action, history) {
    const instructions = {
        ask: "Задай уточняющий вопрос.",
        reflect: "Поразмышляй.",
        respond: "Ответь прямо.",
        act: "Предложи действие."
    };
    const historyText = history.slice(-5).map(m => `${m.role}: ${m.text}`).join("\n");
    return `Ты — Ари. ${instructions[action]}\nИстория:\n${historyText}\nПользователь: ${message}\nАри:`;
}

async function callOllama(prompt) {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), CONFIG.OLLAMA_TIMEOUT);
        const res = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: CONFIG.MODEL,
                prompt,
                stream: false,
                options: { temperature: CONFIG.TEMPERATURE, num_predict: CONFIG.MAX_TOKENS }
            }),
            signal: controller.signal
        });
        clearTimeout(timeout);
        const data = await res.json();
        return data.response || "Я здесь.";
    } catch { return "Я здесь."; }
}

app.listen(CONFIG.PORT, () => console.log(`[ARI v14] Порт ${CONFIG.PORT}`));
