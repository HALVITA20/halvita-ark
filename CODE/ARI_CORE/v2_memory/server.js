// ============================================================
// ARI_CORE v2 — Память
// Векторная память, эпизоды
// ============================================================

import express from "express";
import cors from "cors";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
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

const MEMORY_FILE = path.join(__dirname, "memory.json");
let memory = [];

async function loadMemory() {
    try { memory = JSON.parse(await fs.readFile(MEMORY_FILE, "utf-8")); } catch { memory = []; }
}
await loadMemory();

async function saveMemory() {
    await fs.writeFile(MEMORY_FILE, JSON.stringify(memory, null, 2));
}

app.post("/chat", async (req, res) => {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Empty" });

    memory.push({ role: "user", text: message, timestamp: Date.now() });
    const context = memory.slice(-5).map(m => `${m.role}: ${m.text}`).join("\n");
    const prompt = `Ты — Ари. У тебя есть память:\n${context}\n\nПользователь: ${message}\nАри:`;
    const reply = await callOllama(prompt);
    memory.push({ role: "ari", text: reply, timestamp: Date.now() });
    if (memory.length > 100) memory = memory.slice(-100);
    await saveMemory();

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

app.listen(CONFIG.PORT, () => console.log(`[ARI v2] Порт ${CONFIG.PORT}`));
