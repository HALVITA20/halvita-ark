// ============================================================
// ARI_CORE v3 — Pipeline
// Пайплайн мышления
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
    OLLAMA_TIMEOUT: 30000
};

app.post("/chat", async (req, res) => {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Empty" });

    // Шаг 1: Восприятие
    const perception = analyzeMessage(message);

    // Шаг 2: Решение
    const decision = decide(perception);

    // Шаг 3: Генерация
    const prompt = buildPrompt(message, decision);
    const reply = await callOllama(prompt);

    res.json({ reply });
});

function analyzeMessage(text) {
    const words = text.toLowerCase();
    const uncertainty = words.includes('?') ? 0.7 : 0.3;
    const complexity = text.length > 100 ? 0.8 : 0.4;
    return { uncertainty, complexity };
}

function decide(perception) {
    if (perception.uncertainty > 0.6) return "ask";
    if (perception.complexity > 0.7) return "reflect";
    return "respond";
}

function buildPrompt(message, decision) {
    const instructions = {
        ask: "Задай уточняющий вопрос.",
        reflect: "Поразмышляй над этим.",
        respond: "Ответь прямо."
    };
    return `Ты — Ари. ${instructions[decision]}\nПользователь: ${message}\nАри:`;
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

app.listen(CONFIG.PORT, () => console.log(`[ARI v3] Порт ${CONFIG.PORT}`));
