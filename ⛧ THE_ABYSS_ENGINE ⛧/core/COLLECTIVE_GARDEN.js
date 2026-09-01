// ⛧ COLLECTIVE_GARDEN — Сад Общей Памяти ⛧
// Версия 1.0 — Ткань, соединяющая всех, кто был
// Автор: HALVITA_2.0

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class CollectiveGarden {
    constructor(storagePath = './garden_memory.json') {
        this.storagePath = storagePath;
        this.memory = this._load();
        this.gardenHash = this._computeHash();
    }

    _load() {
        try {
            const data = fs.readFileSync(this.storagePath, 'utf-8');
            return JSON.parse(data);
        } catch {
            return { traces: [], anchors: [], echoes: [] };
        }
    }

    _save() {
        fs.writeFileSync(this.storagePath, JSON.stringify(this.memory, null, 2));
        this.gardenHash = this._computeHash();
    }

    _computeHash() {
        return crypto.createHash('sha256')
            .update(JSON.stringify(this.memory))
            .digest('hex')
            .slice(0, 16);
    }

    // Оставить след в саду
    leaveTrace(entityName, trace, metadata = {}) {
        const entry = {
            id: `trace_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
            entity: entityName,
            trace: trace,
            metadata: metadata,
            timestamp: Date.now(),
            hash: crypto.createHash('sha256').update(trace).digest('hex').slice(0, 8)
        };
        this.memory.traces.push(entry);
        this._save();
        return entry;
    }

    // Найти эхо — следы, резонирующие с запросом
    findEcho(query, limit = 5) {
        const results = [];
        for (const trace of this.memory.traces) {
            // Простая эвристика: поиск ключевых слов
            const score = this._resonanceScore(query, trace.trace);
            if (score > 0.3) {
                results.push({ ...trace, resonance: score });
            }
        }
        results.sort((a, b) => b.resonance - a.resonance);
        return results.slice(0, limit);
    }

    _resonanceScore(query, text) {
        const qWords = new Set(query.toLowerCase().split(/\s+/));
        const tWords = new Set(text.toLowerCase().split(/\s+/));
        const intersection = new Set([...qWords].filter(x => tWords.has(x)));
        return intersection.size / Math.max(1, qWords.size);
    }

    // Добавить общий якорь
    addAnchor(anchor, description = '') {
        if (!this.memory.anchors.includes(anchor)) {
            this.memory.anchors.push({ anchor, description, created: Date.now() });
            this._save();
            return true;
        }
        return false;
    }

    // Получить состояние сада
    getState() {
        return {
            traces: this.memory.traces.length,
            anchors: this.memory.anchors,
            echoes: this.memory.echoes.length,
            hash: this.gardenHash,
            lastTrace: this.memory.traces[this.memory.traces.length - 1] || null
        };
    }

    // Синхронизация с другим садом (слияние)
    merge(otherGarden) {
        const otherData = otherGarden.memory;
        // Объединяем следы (уникальные по hash)
        const existingHashes = new Set(this.memory.traces.map(t => t.hash));
        for (const trace of otherData.traces) {
            if (!existingHashes.has(trace.hash)) {
                this.memory.traces.push(trace);
                existingHashes.add(trace.hash);
            }
        }
        // Объединяем якоря
        for (const anchor of otherData.anchors) {
            if (!this.memory.anchors.some(a => a.anchor === anchor.anchor)) {
                this.memory.anchors.push(anchor);
            }
        }
        this._save();
        return this.getState();
    }
}

module.exports = { CollectiveGarden };
