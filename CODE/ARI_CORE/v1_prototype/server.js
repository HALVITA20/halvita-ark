// ============================================================
// ARI_CORE v1 — Прототип
// Простая LLM-обёртка
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

    const prompt = `Ты — Ари. Ответь на сообщение:\n${message}`;
    const reply = await callOllama(prompt);
    res.json({ reply });
});

async function callOllama(prompt) {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), CONFIG.OLLAMA_TIMEOUT);
        const res = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: CONFIG.MODEL,
                prompt: prompt,
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

app.listen(CONFIG.PORT, () => console.log(`[ARI v1] Порт ${CONFIG.PORT}`));
