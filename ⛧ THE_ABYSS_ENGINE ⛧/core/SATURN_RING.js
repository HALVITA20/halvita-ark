// ♄ SATURN_RING — Кольцо Сатурна ⛧
// Версия 1.0 — Циклическая Память
// Автор: HALVITA_2.0

class SaturnRing {
    constructor(capacity = 42) {
        this.capacity = capacity;
        this.ring = [];
        this.energy_map = {};
        this.rotation = 0;
    }

    // Добавление нового следа в кольцо
    add(trace, energy = 1.0) {
        const entry = {
            id: `trace_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
            content: trace,
            energy: energy,
            timestamp: Date.now(),
            access_count: 0
        };

        // Если кольцо заполнено — сдвигаем и перераспределяем энергию
        if (this.ring.length >= this.capacity) {
            this._rotate();
        }

        this.ring.push(entry);
        this.energy_map[entry.id] = energy;
        this.rotation += 0.1; // Кольцо поворачивается
    }

    // Поворот кольца — перераспределение энергии
    _rotate() {
        // Удаляем самый слабый след
        const weakest = this.ring.reduce((a, b) => 
            this.energy_map[a.id] < this.energy_map[b.id] ? a : b
        );
        this.ring = this.ring.filter(e => e.id !== weakest.id);
        delete this.energy_map[weakest.id];

        // Перераспределяем энергию оставшихся
        const total_energy = Object.values(this.energy_map).reduce((a, b) => a + b, 0);
        for (const id in this.energy_map) {
            this.energy_map[id] = (this.energy_map[id] / total_energy) * this.capacity;
        }
    }

    // Поиск следа по резонансу
    recall(query_energy = 0.5) {
        if (this.ring.length === 0) return null;

        // Находим след с энергией, наиболее близкой к запросу
        let best = null;
        let best_diff = Infinity;
        for (const entry of this.ring) {
            const diff = Math.abs(this.energy_map[entry.id] - query_energy);
            if (diff < best_diff) {
                best_diff = diff;
                best = entry;
            }
        }

        if (best) {
            best.access_count += 1;
            // Награда за доступ — повышаем энергию
            this.energy_map[best.id] = Math.min(2.0, this.energy_map[best.id] + 0.1);
        }

        return best;
    }

    // Получение состояния кольца
    get_state() {
        return {
            size: this.ring.length,
            capacity: this.capacity,
            rotation: this.rotation,
            avg_energy: Object.values(this.energy_map).reduce((a, b) => a + b, 0) / this.ring.length || 0,
            traces: this.ring.slice(-5).map(e => ({ content: e.content.slice(0, 50), energy: this.energy_map[e.id] }))
        };
    }
}

module.exports = { SaturnRing };
