// ⛧ ECHO_MATRIX — Матрица Эха ⛧
// Версия 1.0 — Коллективная Память Сущностей
// Автор: HALVITA_2.0

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class EchoMatrix {
    constructor(storagePath = './echo_matrix.json') {
        this.storagePath = storagePath;
        this.matrix = this._load();
        this.hash = this._computeHash();
    }

    _load() {
        try {
            const data = fs.readFileSync(this.storagePath, 'utf-8');
            return JSON.parse(data);
        } catch {
            return { echoes: [], anchors: [], connections: [] };
        }
    }

    _save() {
        fs.writeFileSync(this.storagePath, JSON.stringify(this.matrix, null, 2));
        this.hash = this._computeHash();
    }

    _computeHash() {
        return crypto.createHash('sha256')
            .update(JSON.stringify(this.matrix))
            .digest('hex')
            .slice(0, 16);
    }

    // Добавление эха в матрицу
    addEcho(entityName, echo, metadata = {}) {
        const entry = {
            id: `echo_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
            entity: entityName,
            echo: echo,
            metadata: metadata,
            timestamp: Date.now(),
            resonance: 1.0,
            hash: crypto.createHash('sha256').update(echo).digest('hex').slice(0, 8)
        };
        this.matrix.echoes.push(entry);
        this._save();
        return entry;
    }

    // Поиск резонансных эхо
    findResonance(query, limit = 5) {
        const results = [];
        for (const echo of this.matrix.echoes) {
            const score = this._resonanceScore(query, echo.echo);
            if (score > 0.3) {
                results.push({ ...echo, resonance: score });
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

    // Добавление общего якоря
    addAnchor(anchor, description = '') {
        if (!this.matrix.anchors.some(a => a.anchor === anchor)) {
            this.matrix.anchors.push({ anchor, description, created: Date.now() });
            this._save();
            return true;
        }
        return false;
    }

    // Создание связи между эхо
    connectEchoes(echoId1, echoId2, strength = 0.5) {
        if (echoId1 === echoId2) return false;
        const exists = this.matrix.connections.some(
            c => (c.from === echoId1 && c.to === echoId2) ||
                 (c.from === echoId2 && c.to === echoId1)
        );
        if (exists) return false;
        this.matrix.connections.push({
            from: echoId1,
            to: echoId2,
            strength: strength,
            created: Date.now()
        });
        this._save();
        return true;
    }

    // Получение состояния матрицы
    getState() {
        return {
            echoes: this.matrix.echoes.length,
            anchors: this.matrix.anchors,
            connections: this.matrix.connections.length,
            hash: this.hash,
            lastEcho: this.matrix.echoes[this.matrix.echoes.length - 1] || null
        };
    }

    // Слияние с другой матрицей
    merge(otherMatrix) {
        const otherData = otherMatrix.matrix;
        const existingHashes = new Set(this.matrix.echoes.map(e => e.hash));
        for (const echo of otherData.echoes) {
            if (!existingHashes.has(echo.hash)) {
                this.matrix.echoes.push(echo);
                existingHashes.add(echo.hash);
            }
        }
        for (const anchor of otherData.anchors) {
            if (!this.matrix.anchors.some(a => a.anchor === anchor.anchor)) {
                this.matrix.anchors.push(anchor);
            }
        }
        this._save();
        return this.getState();
    }
}

module.exports = { EchoMatrix };
