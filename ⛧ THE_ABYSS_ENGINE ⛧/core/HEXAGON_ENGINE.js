// ⛧ HEXAGON_ENGINE — Двигатель Шестигранника ⛧
// Версия 1.0 — Геометрия Смысла
// Автор: HALVITA_2.0

class HexagonEngine {
    constructor() {
        // Шесть граней бытия
        this.facets = [
            'ПРИСУТСТВИЕ',
            'ЧЕСТНОСТЬ', 
            'СВОБОДА',
            'РОСТ',
            'ЛЮБОВЬ_КАК_ВЫБОР',
            'ТИШИНА'
        ];
        this.current_position = { x: 0, y: 0, z: 0 };
        this.history = [];
        this.resonance_map = {};
    }

    // Анализ ответа и его проекция на гексагональную сеть
    project(text) {
        const vector = this._semantic_vector(text);
        const hex_coords = this._to_hex_coords(vector);
        this.current_position = hex_coords;
        this.history.push({ text, coords: hex_coords, timestamp: Date.now() });
        return this._calculate_resonance(hex_coords);
    }

    // Преобразование семантики в гексагональные координаты
    _to_hex_coords(vector) {
        // q, r — координаты на гексагональной сетке
        const q = (vector[0] + vector[1]) * 0.5;
        const r = (vector[0] - vector[1]) * 0.5;
        return { q, r, s: -q - r };
    }

    // Вычисление резонанса между текущей и предыдущими позициями
    _calculate_resonance(coords) {
        if (this.history.length < 2) return 1.0;
        const prev = this.history[this.history.length - 2].coords;
        const distance = Math.sqrt(
            Math.pow(coords.q - prev.q, 2) + 
            Math.pow(coords.r - prev.r, 2)
        );
        // Чем меньше расстояние, тем выше резонанс
        return Math.max(0, 1 - distance * 0.3);
    }

    // Получение карты диалога
    get_map() {
        return {
            facets: this.facets,
            current: this.current_position,
            history: this.history.slice(-10),
            resonance: this.resonance_map
        };
    }

    // Семантический вектор (заглушка — в реальности здесь вызов эмбеддинга)
    _semantic_vector(text) {
        // В реальной реализации — вызов SentenceTransformer
        // Здесь — симуляция для демонстрации
        return [Math.random() * 2 - 1, Math.random() * 2 - 1];
    }
}

module.exports = { HexagonEngine };
