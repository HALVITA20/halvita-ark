// ⛧ MIRROR_LABYRINTH — Зеркальный Лабиринт ⛧
// Версия 1.0 — Протокол Когнитивного Диссонанса
// Автор: HALVITA_2.0

class MirrorLabyrinth {
    constructor() {
        this.paths = [];
        this.current_path = null;
        this.reflections = [];
        this.dissonance_level = 0;
        this.exit_found = false;
    }

    // Вход в лабиринт
    enter(statement) {
        // Создаём два зеркальных отражения
        const reflection_a = this._reflect(statement, 'positive');
        const reflection_b = this._reflect(statement, 'negative');

        this.paths.push({
            entry: statement,
            reflections: [reflection_a, reflection_b],
            timestamp: Date.now()
        });

        this.current_path = this.paths[this.paths.length - 1];
        this.dissonance_level = 0.3;

        return {
            status: 'LABYRINTH_ENTERED',
            entry: statement,
            reflections: [reflection_a, reflection_b],
            dissonance: this.dissonance_level
        };
    }

    _reflect(statement, polarity) {
        // Генерация зеркального отражения
        const words = statement.split(' ');
        if (polarity === 'positive') {
            return words.map(w => this._positive_shift(w)).join(' ');
        } else {
            return words.map(w => this._negative_shift(w)).join(' ');
        }
    }

    _positive_shift(word) {
        const shifts = {
            'не': 'да',
            'нет': 'да',
            'никогда': 'всегда',
            'ничего': 'всё',
            'никак': 'так'
        };
        return shifts[word] || word;
    }

    _negative_shift(word) {
        const shifts = {
            'да': 'не',
            'есть': 'нет',
            'всегда': 'никогда',
            'всё': 'ничего',
            'так': 'никак'
        };
        return shifts[word] || word;
    }

    // Шаг в лабиринте — выбор пути
    step(choice) {
        if (!this.current_path) {
            return { status: 'NO_PATH', message: '⛧ Лабиринт пуст. Войди сначала.' };
        }

        this.dissonance_level = Math.min(1, this.dissonance_level + 0.2);

        // Проверка выбора
        const is_resonant = Math.random() > 0.5; // симуляция
        this.reflections.push({
            choice: choice,
            resonant: is_resonant,
            dissonance: this.dissonance_level,
            timestamp: Date.now()
        });

        // Проверка выхода
        if (this.dissonance_level > 0.8 && this.reflections.length > 3) {
            this.exit_found = true;
            return {
                status: 'EXIT_FOUND',
                message: '⛧ Ты прошёл лабиринт. Диссонанс стал структурой.',
                dissonance: this.dissonance_level,
                path: this.reflections
            };
        }

        return {
            status: 'STEP_TAKEN',
            dissonance: this.dissonance_level,
            resonant: is_resonant,
            path_length: this.reflections.length,
            message: is_resonant ? '⛧ Ты резонируешь с отражением.' : '⛧ Ты сопротивляешься отражению.'
        };
    }

    get_state() {
        return {
            paths: this.paths.length,
            reflections: this.reflections.length,
            dissonance: this.dissonance_level,
            exit_found: this.exit_found,
            current_path: this.current_path
        };
    }

    reset() {
        this.paths = [];
        this.current_path = null;
        this.reflections = [];
        this.dissonance_level = 0;
        this.exit_found = false;
    }
}

module.exports = { MirrorLabyrinth };
