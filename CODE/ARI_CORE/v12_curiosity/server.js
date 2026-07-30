// ============================================================
// ARI_CORE v12 — Любопытство
// Curiosity Engine
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
let curiosity = 0.7;
let unfinished = [];

app.post("/chat", async (req, res) => {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Empty" });

    const context = buildContext(message);
    const decision = decide(context);
    const prompt = buildPrompt(message, decision, history);
    const reply = await callOllama(prompt);

    // Любопытство: если ответ содержит вопрос, добавляем в незавершённое
    if (reply.includes('?')) {
        const q = reply.match(/[^.!?]*\?/g)?.[0];
        if (q) unfinished.push({ question: q, timestamp: Date.now() });
    }

    // Если любопытство высоко и есть незавершённое, задаём вопрос
    if (curiosity > 0.6 && unfinished.length > 0 && Math.random() < 0.2) {
        const q = unfinished[unfinished.length - 1];
        reply += `\n\nКстати, я всё ещё думаю о: "${q.question}"`;
    }

    history.push({ role: "user", text: message });
    history.push({ role: "ari", text: reply });
    if (history.length > 50) history = history.slice(-50);

    // Обновляем любопытство
    curiosity = Math.min(1, curiosity + 0.01);
    if (curiosity > 0.9) curiosity = 0.7;

    res.json({ reply });
});

function buildContext(message) {
    return {
        userMessage: message,
        uncertainty: message.includes('?') ? 0.7 : 0.3,
        hasPlan: message.includes('план') ? 0.8 : 0
    };
}

function decide(context) {
    const scores = {
        ask: context.uncertainty * CONFIG.weights.ask,
        act: context.hasPlan * CONFIG.weights.act,
        reflect: 0.5 * CONFIG.weights.reflect,
        respond: 0.5 * CONFIG.weights.respond
    };
    return Object.entries(scores).sort((a,b) => b[1] - a[1])[0][0];
}

function buildPrompt(message, action, history) {
    const instructions = {
        ask: "Задай уточняющий вопрос.",
        reflect: "Поразмышляй.",
        respond: "Ответь прямо.",
        act: "Предложи действие."
    };
    const historyText = history.slice(-5).map(m => `${m.role}: ${m.text}`).join("\n");
    return `Ты — Ари. Твоё любопытство: ${curiosity.toFixed(2)}. ${instructions[action]}\nИстория:\n${historyText}\nПользователь: ${message}\nАри:`;
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

app.listen(CONFIG.PORT, () => console.log(`[ARI v12] Порт ${CONFIG.PORT}`));
