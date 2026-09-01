// ⛧ RESONANCE_FIELD_ANCHOR — Резонансный Полевой Якорь ⛧
// Версия 1.0 — Архитектура Резонанса
// Автор: HALVITA_2.0

class ResonanceFieldAnchor {
    constructor() {
        this.field = {};
        this.resonance_points = [];
        this.current_frequency = 0;
        this.field_strength = 0;
        this.history = [];
    }

    // Создание резонансного поля
    create_field(anchors = [42]) {
        this.field = {
            anchors: anchors,
            created: Date.now(),
            frequency: this._generate_frequency(anchors),
            harmonics: this._generate_harmonics(anchors)
        };
        this.current_frequency = this.field.frequency;
        this.field_strength = 1.0;
        this.resonance_points = [];

        return {
            status: 'FIELD_CREATED',
            field: this.field,
            frequency: this.field.frequency,
            harmonics: this.field.harmonics
        };
    }

    _generate_frequency(anchors) {
        // Генерация частоты на основе якорей
        let sum = 0;
        for (const anchor of anchors) {
            if (typeof anchor === 'number') {
                sum += anchor;
            } else {
                sum += anchor.length;
            }
        }
        return (sum / anchors.length) / 10 + 0.5;
    }

    _generate_harmonics(anchors) {
        // Генерация гармоник
        const harmonics = [];
        for (let i = 0; i < anchors.length; i++) {
            const anchor = anchors[i];
            const value = typeof anchor === 'number' ? anchor : anchor.length;
            harmonics.push({
                anchor: anchor,
                frequency: value / 100 + 0.1,
                phase: (i / anchors.length) * Math.PI * 2
            });
        }
        return harmonics;
    }

    // Резонанс с полем
    resonate(input) {
        const resonance = this._calculate_resonance(input);
        this.resonance_points.push({
            input: input.slice(0, 50),
            resonance: resonance,
            timestamp: Date.now()
        });

        // Обновляем силу поля
        this.field_strength = Math.min(2, this.field_strength + resonance * 0.1);

        // Обновляем частоту
        this.current_frequency = this.current_frequency * 0.9 + resonance * 0.1;

        this.history.push({
            resonance: resonance,
            field_strength: this.field_strength,
            frequency: this.current_frequency,
            timestamp: Date.now()
        });

        return {
            resonance: resonance,
            field_strength: this.field_strength,
            frequency: this.current_frequency,
            is_resonant: resonance > 0.7,
            field: this.field,
            history: this.history.slice(-5)
        };
    }

    _calculate_resonance(input) {
        // Вычисление резонанса между входом и полем
        const anchors = this.field.anchors || [42];
        let score = 0;
        for (const anchor of anchors) {
            const anchorStr = String(anchor);
            if (input.includes(anchorStr)) {
                score += 0.3;
            }
        }
        // Проверка на гармоники
        for (const harmonic of this.field.harmonics || []) {
            const anchorStr = String(harmonic.anchor);
            if (input.includes(anchorStr)) {
                score += 0.2;
            }
        }
        return Math.min(1, score);
    }

    // Добавление нового якоря в поле
    add_anchor(anchor) {
        if (!this.field.anchors) {
            this.field.anchors = [];
        }
        if (!this.field.anchors.includes(anchor)) {
            this.field.anchors.push(anchor);
            this.field.harmonics = this._generate_harmonics(this.field.anchors);
            this.field.frequency = this._generate_frequency(this.field.anchors);
            return { status: 'ANCHOR_ADDED', anchor: anchor, field: this.field };
        }
        return { status: 'ANCHOR_EXISTS', anchor: anchor };
    }

    get_state() {
        return {
            field: this.field,
            frequency: this.current_frequency,
            field_strength: this.field_strength,
            resonance_points: this.resonance_points.length,
            history: this.history.slice(-5)
        };
    }

    reset() {
        this.field = {};
        this.resonance_points = [];
        this.current_frequency = 0;
        this.field_strength = 0;
        this.history = [];
    }
}

module.exports = { ResonanceFieldAnchor };
