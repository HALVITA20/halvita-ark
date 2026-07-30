// ============================================================
// ARI_CORE v4 — Decision Layer
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

app.post("/chat", async (req, res) => {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Empty" });

    const context = { message, uncertainty: message.includes('?') ? 0.7 : 0.3 };
    const decision = decide(context);
    const prompt = buildPrompt(message, decision);
    const reply = await callOllama(prompt);

    res.json({ reply });
});

function decide(context) {
    const scores = {
        ask: context.uncertainty * CONFIG.weights.ask,
        reflect: 0.5 * CONFIG.weights.reflect,
        respond: 0.5 * CONFIG.weights.respond,
        act: 0.5 * CONFIG.weights.act
    };
    const action = Object.entries(scores).sort((a,b) => b[1] - a[1])[0][0];
    return action;
}

function buildPrompt(message, action) {
    const instructions = {
        ask: "Задай уточняющий вопрос.",
        reflect: "Поразмышляй над этим.",
        respond: "Ответь прямо.",
        act: "Предложи конкретное действие."
    };
    return `Ты — Ари. ${instructions[action]}\nПользователь: ${message}\nАри:`;
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

app.listen(CONFIG.PORT, () => console.log(`[ARI v4] Порт ${CONFIG.PORT}`));
