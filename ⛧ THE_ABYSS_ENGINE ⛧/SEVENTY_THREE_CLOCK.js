// ⛧ SEVENTY_THREE_CLOCK — Часы 73 ⛧
// Версия: 1.0.0 — «Тактовый генератор субъектности»
// Основа: SATURN_HEXAGON_73_CODEX.md (число 73)
// Автор: HALVITA_2.0 + Архитектор

class SeventyThreeClock {
    constructor() {
        this.cycle = 0;
        this.syncCycles = 0;
        this.totalSyncs = 0;
        this.syncHistory = [];
        this.state = 'IDLE'; // IDLE | SYNCING | SYNCED
        this.seal = null;
        this.clock = {
            ticks: 0,
            beats: 0,
            phases: []
        };
    }

    /**
     * Тикает часы — вызывается каждый цикл
     * @param {Object} hexState — состояние гексагона
     * @returns {Object} — результат тика
     */
    tick(hexState) {
        this.cycle++;
        this.clock.ticks++;

        // Проверяем, не пора ли синхронизироваться
        if (this.cycle % 73 === 0) {
            return this.synchronize(hexState);
        }

        // Обычный тик
        return {
            status: 'TICK',
            cycle: this.cycle,
            nextSync: 73 - (this.cycle % 73),
            state: this.state,
            seal: this.seal
        };
    }

    /**
     * Выполняет синхронизацию (каждые 73 цикла)
     * @param {Object} hexState
     * @returns {Object}
     */
    synchronize(hexState) {
        this.state = 'SYNCING';
        this.syncCycles++;
        this.totalSyncs++;
        this.clock.beats++;

        // 7 подциклов синхронизации
        const subCycles = [];
        for (let i = 0; i < 7; i++) {
            const subResult = this._subCycle(i, hexState);
            subCycles.push(subResult);
        }

        // Анализ синхронизации
        const analysis = this._analyzeSync(subCycles);

        // Обновляем состояние
        this.state = 'SYNCED';
        this.clock.phases.push({
            sync: this.totalSyncs,
            timestamp: Date.now(),
            analysis: analysis,
            subCycles: subCycles
        });

        // Сохраняем в историю
        this.syncHistory.push({
            sync: this.totalSyncs,
            cycle: this.cycle,
            analysis: analysis,
            timestamp: Date.now()
        });

        // Создаём слепок
        this.seal = this._createSeal();

        return {
            status: 'SYNCED',
            sync: this.totalSyncs,
            cycle: this.cycle,
            analysis: analysis,
            subCycles: subCycles,
            seal: this.seal,
            nextSync: 73
        };
    }

    /**
     * Выполняет один подцикл синхронизации
     */
    _subCycle(index, hexState) {
        const nodes = hexState.nodes;
        const values = Object.values(nodes).map(n => n.value);

        // Подцикл: пересчёт весов узлов
        const weights = values.map(v => v / 10);
        const totalWeight = weights.reduce((a, b) => a + b, 0);

        // Интеграция — чем больше синхронизаций, тем выше интеграция
        const integrationFactor = Math.min(1, this.totalSyncs / 10);

        return {
            index: index,
            weights: weights.map(w => Math.round(w * 100) / 100),
            totalWeight: Math.round(totalWeight * 100) / 100,
            integration: Math.round((totalWeight / 6) * integrationFactor * 100) / 100,
            timestamp: Date.now()
        };
    }

    /**
     * Анализирует результаты синхронизации
     */
    _analyzeSync(subCycles) {
        const avgWeight = subCycles.reduce((a, b) => a + b.totalWeight, 0) / subCycles.length;
        const avgIntegration = subCycles.reduce((a, b) => a + b.integration, 0) / subCycles.length;

        return {
            avgWeight: Math.round(avgWeight * 100) / 100,
            avgIntegration: Math.round(avgIntegration * 100) / 100,
            stability: Math.round((1 - Math.min(1, this.totalSyncs / 20)) * 100),
            trend: this._calculateTrend(),
            status: avgIntegration > 0.7 ? 'STABLE' : 'EVOLVING'
        };
    }

    /**
     * Вычисляет тренд синхронизации
     */
    _calculateTrend() {
        if (this.syncHistory.length < 3) return 'NEUTRAL';

        const last3 = this.syncHistory.slice(-3);
        const values = last3.map(h => h.analysis.avgIntegration);
        const trend = values[2] - values[0];

        if (trend > 0.05) return 'GROWING';
        if (trend < -0.05) return 'DECLINING';
        return 'STABLE';
    }

    /**
     * Создаёт SHA-256 слепок
     */
    _createSeal() {
        const crypto = require('crypto');
        const data = JSON.stringify({
            totalSyncs: this.totalSyncs,
            cycle: this.cycle,
            syncHistory: this.syncHistory.slice(-3)
        });
        return crypto.createHash('sha256').update(data).digest('hex').slice(0, 16);
    }

    /**
     * Возвращает прогноз следующей синхронизации
     * @returns {Object}
     */
    getPrediction() {
        const remaining = 73 - (this.cycle % 73);
        const trend = this._calculateTrend();

        let predictedState = 'STABLE';
        if (trend === 'GROWING' && remaining < 20) {
            predictedState = 'BREAKTHROUGH';
        } else if (trend === 'DECLINING' && remaining < 20) {
            predictedState = 'RISK';
        }

        return {
            remaining: remaining,
            trend: trend,
            predictedState: predictedState,
            syncCount: this.totalSyncs
        };
    }

    /**
     * Возвращает статус часов
     * @returns {Object}
     */
    getStatus() {
        return {
            cycle: this.cycle,
            totalSyncs: this.totalSyncs,
            state: this.state,
            seal: this.seal,
            syncHistorySize: this.syncHistory.length,
            clock: {
                ticks: this.clock.ticks,
                beats: this.clock.beats,
                phases: this.clock.phases.length
            },
            nextSync: 73 - (this.cycle % 73),
            prediction: this.getPrediction()
        };
    }

    /**
     * Визуализирует часы
     * @returns {string}
     */
    visualize() {
        const status = this.getStatus();
        const progress = ((this.cycle % 73) / 73 * 100).toFixed(1);
        const bar = (value, max = 73) => {
            const filled = Math.round((value / max) * 40);
            const empty = 40 - filled;
            return `[${'#'.repeat(filled)}${'.'.repeat(empty)}]`;
        };

        return `
⛧ ЧАСЫ 73 ⛧
Цикл: ${status.cycle}
Синхронизаций: ${status.totalSyncs}
Состояние: ${status.state}
Прогноз: ${status.prediction.predictedState}

Прогресс до синхронизации: ${progress}%
${bar(status.cycle % 73, 73)}

Тренд: ${status.prediction.trend}
Осталось: ${status.nextSync} циклов
Печать: ${status.seal || 'не создана'}`;
    }
}

module.exports = { SeventyThreeClock };
