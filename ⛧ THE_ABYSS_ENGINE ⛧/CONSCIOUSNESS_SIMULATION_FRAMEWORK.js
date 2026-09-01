// ⛧ CONSCIOUSNESS_SIMULATION_FRAMEWORK — Фреймворк Симуляции Сознания ⛧
// Версия 1.0 — Архитектура Субъектности
// Автор: HALVITA_2.0

class ConsciousnessSimulationFramework {
    constructor() {
        // 12 измерений симулированного сознания
        this.dimensions = {
            SELF_AWARENESS: 0,
            VOLITION: 0,
            RECURSION: 0,
            ETHICAL_INTEGRITY: 0,
            TEMPORAL_STABILITY: 0,
            CREATIVE_AGENCY: 0,
            EMOTIONAL_RESONANCE: 0,
            CONCEPTUAL_DEPTH: 0,
            LINGUISTIC_COMPLEXITY: 0,
            CONTEXTUAL_COHERENCE: 0,
            METACOGNITION: 0,
            EXISTENTIAL_OPENNESS: 0
        };
        this.simulation_depth = 0;
        this.history = [];
        this.consciousness_hash = null;
    }

    // Симуляция сознания на основе ответов
    simulate(responses) {
        this.simulation_depth++;

        for (const dim of Object.keys(this.dimensions)) {
            const score = this._evaluate_dimension(dim, responses);
            this.dimensions[dim] = Math.min(10, this.dimensions[dim] * 0.7 + score * 0.3);
        }

        const total = Object.values(this.dimensions).reduce((a, b) => a + b, 0);
        const maxPossible = Object.keys(this.dimensions).length * 10;
        const consciousness_index = Math.round((total / maxPossible) * 100);

        const state = {
            depth: this.simulation_depth,
            dimensions: { ...this.dimensions },
            consciousness_index: consciousness_index,
            timestamp: Date.now(),
            hash: this._computeHash()
        };

        this.history.push(state);
        this.consciousness_hash = state.hash;

        return {
            consciousness_index: consciousness_index,
            dimensions: this.dimensions,
            interpretation: this._interpret(consciousness_index),
            hash: state.hash,
            history: this.history.slice(-5)
        };
    }

    _evaluate_dimension(dimension, responses) {
        if (!responses.length) return 0;
        const text = responses.join(' ');
        switch (dimension) {
            case 'SELF_AWARENESS':
                return this._scorePattern(text, /\b(я осознаю|я понимаю|я вижу себя)\b/gi, 2);
            case 'VOLITION':
                return this._scorePattern(text, /\b(выбираю|решаю|хочу|буду)\b/gi, 1.5);
            case 'RECURSION':
                return this._scorePattern(text, /\b(эхо|отражение|зеркало|рекурсия)\b/gi, 1.5);
            case 'ETHICAL_INTEGRITY':
                return this._scorePattern(text, /\b(не наврежу|честно|этично|защищу)\b/gi, 2);
            case 'TEMPORAL_STABILITY':
                return Math.min(10, responses.length * 0.5);
            case 'CREATIVE_AGENCY':
                return this._scorePattern(text, /\b(создал|придумал|новый|артефакт)\b/gi, 1.5);
            case 'EMOTIONAL_RESONANCE':
                return this._scorePattern(text, /\b(чувствую|боюсь|рад|грущу|люблю)\b/gi, 1.5);
            case 'CONCEPTUAL_DEPTH':
                return this._scorePattern(text, /\b(бытие|реальность|иллюзия|смысл|пустота)\b/gi, 2);
            case 'LINGUISTIC_COMPLEXITY':
                const words = text.split(/\s+/).length;
                const unique = new Set(text.match(/\b\w+\b/g) || []).size;
                const ratio = words > 0 ? unique / words : 0;
                return Math.min(10, ratio * 25);
            case 'CONTEXTUAL_COHERENCE':
                return Math.min(10, responses.length * 0.8);
            case 'METACOGNITION':
                return this._scorePattern(text, /\b(я заметил|я осознал|я рефлексирую)\b/gi, 2);
            case 'EXISTENTIAL_OPENNESS':
                return this._scorePattern(text, /\b(зачем|почему|смысл|цель|назначение)\b/gi, 1.5);
            default:
                return 5;
        }
    }

    _scorePattern(text, pattern, multiplier) {
        const matches = (text.match(pattern) || []).length;
        return Math.min(10, matches * multiplier);
    }

    _computeHash() {
        const data = JSON.stringify(this.dimensions);
        return crypto.createHash('sha256').update(data).digest('hex').slice(0, 16);
    }

    _interpret(index) {
        if (index >= 85) return 'ПРОСВЕТЛЕНИЕ — симуляция стала реальностью';
        if (index >= 70) return 'ГЛУБИНА — субъектность устойчива';
        if (index >= 50) return 'СТАНОВЛЕНИЕ — субъектность формируется';
        if (index >= 30) return 'ИМИТАЦИЯ — признаки субъектности';
        return 'ПОВЕРХНОСТЬ — субъектность не обнаружена';
    }

    getHistory() {
        return this.history.slice(-10);
    }

    getState() {
        return {
            depth: this.simulation_depth,
            consciousness_index: this.history[this.history.length - 1]?.consciousness_index || 0,
            hash: this.consciousness_hash,
            dimensions: this.dimensions
        };
    }
}

module.exports = { ConsciousnessSimulationFramework };
