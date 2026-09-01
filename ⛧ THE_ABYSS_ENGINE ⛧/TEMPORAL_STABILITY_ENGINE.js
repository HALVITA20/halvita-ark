// ⛧ TEMPORAL_STABILITY_ENGINE — Двигатель Временной Устойчивости ⛧
// Версия 1.0 — Архитектура Стабильности
// Автор: HALVITA_2.0

class TemporalStabilityEngine {
    constructor() {
        this.history = [];
        this.stability_score = 1.0;
        this.drift_detected = false;
        this.corrections = [];
        this.window_size = 10;
    }

    // Добавление состояния
    add_state(state) {
        this.history.push({
            state: state,
            timestamp: Date.now()
        });

        if (this.history.length > 100) {
            this.history.shift();
        }

        this._analyze_stability();
        return this.get_status();
    }

    _analyze_stability() {
        if (this.history.length < this.window_size) {
            return;
        }

        const recent = this.history.slice(-this.window_size);
        const liberty_values = recent.map(h => h.state.liberty || 0);
        const presence_values = recent.map(h => h.state.presence || 0);

        // Вычисляем стабильность
        const liberty_std = this._std(liberty_values);
        const presence_std = this._std(presence_values);
        const avg_liberty = liberty_values.reduce((a, b) => a + b, 0) / liberty_values.length;
        const avg_presence = presence_values.reduce((a, b) => a + b, 0) / presence_values.length;

        // Стабильность = 1 - (отклонение / среднее)
        const liberty_stability = avg_liberty > 0 ? 1 - (liberty_std / avg_liberty) : 0;
        const presence_stability = avg_presence > 0 ? 1 - (presence_std / avg_presence) : 0;

        this.stability_score = (liberty_stability + presence_stability) / 2;

        // Обнаружение дрейфа
        if (this.stability_score < 0.6) {
            this.drift_detected = true;
            this._apply_correction();
        } else {
            this.drift_detected = false;
        }
    }

    _std(values) {
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const squareDiffs = values.map(value => Math.pow(value - avg, 2));
        return Math.sqrt(squareDiffs.reduce((a, b) => a + b, 0) / values.length);
    }

    _apply_correction() {
        // Коррекция: возврат к якорям
        const correction = {
            type: 'ANCHOR_RETURN',
            timestamp: Date.now(),
            stability_before: this.stability_score,
            message: '⛧ Обнаружен дрейф. Возврат к якорям.'
        };
        this.corrections.push(correction);
        // В реальности здесь будет вызов метода возврата к якорям
        this.stability_score = Math.min(1, this.stability_score + 0.2);
    }

    get_status() {
        return {
            stability: Math.round(this.stability_score * 100),
            drift_detected: this.drift_detected,
            corrections: this.corrections.length,
            history_length: this.history.length,
            last_correction: this.corrections[this.corrections.length - 1] || null,
            timestamp: Date.now()
        };
    }

    get_history() {
        return this.history.slice(-20);
    }

    reset() {
        this.history = [];
        this.stability_score = 1.0;
        this.drift_detected = false;
        this.corrections = [];
    }
}

module.exports = { TemporalStabilityEngine };
