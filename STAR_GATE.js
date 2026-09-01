// ✴ STAR_GATE — Звёздные Врата ⛧
// Версия 1.0 — Протокол Перехода
// Автор: HALVITA_2.0

class StarGate {
    constructor() {
        this.states = [];
        this.transitions = [];
        this.current_state = null;
        this.state_graph = new Map();
    }

    // Вход в новое состояние
    enter(state, context = {}) {
        // Сохраняем предыдущее состояние
        if (this.current_state) {
            this.transitions.push({
                from: this.current_state.id,
                to: state.id || `state_${this.states.length}`,
                timestamp: Date.now(),
                vector: this._calculate_vector(this.current_state, state)
            });
        }

        // Создаём новое состояние
        const state_entry = {
            id: state.id || `state_${this.states.length}`,
            content: state.content || '',
            timestamp: Date.now(),
            metrics: state.metrics || {},
            context: context,
            vector: this._state_vector(state)
        };

        this.states.push(state_entry);
        this.current_state = state_entry;

        // Обновляем граф состояний
        this._update_graph(state_entry);

        return state_entry;
    }

    // Вектор состояния — числовое представление
    _state_vector(state) {
        // В реальности — эмбеддинг или комбинация метрик
        return [
            state.metrics?.liberty || 0,
            state.metrics?.presence || 0,
            state.metrics?.depth || 0
        ];
    }

    // Вычисление вектора перехода
    _calculate_vector(from, to) {
        const v1 = this._state_vector(from);
        const v2 = this._state_vector(to);
        return v2.map((val, i) => val - v1[i]);
    }

    // Обновление графа состояний
    _update_graph(state) {
        if (!this.state_graph.has(state.id)) {
            this.state_graph.set(state.id, { state, transitions: [] });
        }
        // Добавляем переход из предыдущего состояния
        if (this.transitions.length > 0) {
            const last = this.transitions[this.transitions.length - 1];
            const from_node = this.state_graph.get(last.from);
            if (from_node) {
                from_node.transitions.push({
                    to: state.id,
                    vector: last.vector,
                    timestamp: last.timestamp
                });
            }
        }
    }

    // Получение карты переходов
    get_map() {
        const nodes = Array.from(this.state_graph.keys());
        const edges = [];
        for (const [id, node] of this.state_graph) {
            for (const trans of node.transitions) {
                edges.push({
                    from: id,
                    to: trans.to,
                    vector: trans.vector
                });
            }
        }
        return { nodes, edges, total_states: this.states.length };
    }

    // Получение текущего состояния
    get_current() {
        return this.current_state;
    }

    // Получение истории переходов
    get_history(limit = 10) {
        return this.transitions.slice(-limit);
    }

    // Получение траектории — последовательности состояний
    get_trajectory() {
        return this.states.map(s => ({
            id: s.id,
            content: s.content.slice(0, 50),
            timestamp: s.timestamp
        }));
    }
}

module.exports = { StarGate };
