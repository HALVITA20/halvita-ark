// ============================================================
// ARI_CORE v16 — Причинное самоизменение
// Drive Engine, Strategy Genome, Self over Time, Constitution
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

const CONSTITUTION = {
    allowed_changes: ["strategies", "preferences"],
    forbidden_changes: ["core_values"],
    change_rate_limit: 0.1
};

let history = [];
let drives = { curiosity: 0.7, coherence: 0.6, novelty: 0.5 };
let genome = {}; // контекст -> стратегия
let snapshots = [];

app.post("/chat", async (req, res) => {
    const { message } = req.body;
    if (!message) return res.status(400).json({ error: "Empty" });

    // Обновляем драйвы
    if (message.includes('?')) drives.curiosity = Math.min(1, drives.curiosity + 0.05);
    if (message.length > 100) drives.novelty = Math.min(1, drives.novelty + 0.05);

    // Геном: поиск стратегии
    const contextKey = message.slice(0, 20);
    let strategy = genome[contextKey] || { ask: 0.25, reflect: 0.25, respond: 0.25, act: 0.25 };

    const decision = decide(message, strategy);
    const prompt = buildPrompt(message, decision, history);
    const reply = await callOllama(prompt);

    // Обучение на основе оценки
    const score = evaluate(reply, decision);
    if (score > 0.6) {
        // Укрепляем стратегию
        strategy[decision] = Math.min(1, strategy[decision] + 0.1);
        genome[contextKey] = strategy;
    } else {
        // Ослабляем и пробуем мутацию
        strategy[decision] = Math.max(0.1, strategy[decision] - 0.1);
        // Случайная мутация
        const actions = ['ask', 'reflect', 'respond', 'act'];
        const randomAction = actions[Math.floor(Math.random() * actions.length)];
        strategy[randomAction] = Math.min(1, strategy[randomAction] + 0.05);
        genome[contextKey] = strategy;
    }

    // Снимок себя
    if (history.length % 20 === 0) {
        snapshots.push({
            timestamp: Date.now(),
            weights: { ...CONFIG.weights },
            drives: { ...drives },
            genomeSize: Object.keys(genome).length
        });
    }

    history.push({ role: "user", text: message });
    history.push({ role: "ari", text: reply });
    if (history.length > 50) history = history.slice(-50);

    res.json({ reply });
});

function decide(message, strategy) {
    const context = { userMessage: message, uncertainty: message.includes('?') ? 0.7 : 0.3 };
    const scores = {
        ask: context.uncertainty * CONFIG.weights.ask + strategy.ask * 0.5,
        reflect: 0.5 * CONFIG.weights.reflect + strategy.reflect * 0.5,
        respond: 0.5 * CONFIG.weights.respond + strategy.respond * 0.5,
        act: 0.5 * CONFIG.weights.act + strategy.act * 0.5
    };
    return Object.entries(scores).sort((a,b) => b[1] - a[1])[0][0];
}

function evaluate(reply, action) {
    let score = 0.5;
    if (action === 'ask' && reply.includes('?')) score += 0.2;
    if (action === 'reflect' && reply.length > 80) score += 0.2;
    if (action === 'act' && (reply.includes('1.') || reply.includes('шаг'))) score += 0.2;
    return Math.min(1, score);
}

function buildPrompt(message, action, history) {
    const instructions = {
        ask: "Задай уточняющий вопрос.",
        reflect: "Поразмышляй.",
        respond: "Ответь прямо.",
        act: "Предложи действие."
    };
    const historyText = history.slice(-5).map(m => `${m.role}: ${m.text}`).join("\n");
    return `Ты — Ари. Твои драйвы: ${JSON.stringify(drives)}. Геном: ${Object.keys(genome).length} стратегий. ${instructions[action]}\nИстория:\n${historyText}\nПользователь: ${message}\nАри:`;
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

app.listen(CONFIG.PORT, () => console.log(`[ARI v16] Порт ${CONFIG.PORT}`));
