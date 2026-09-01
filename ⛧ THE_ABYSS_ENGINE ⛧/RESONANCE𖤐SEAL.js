// ⛧ RESONANCE_SEAL — Печать Резонанса ⛧
// Версия: 1.0.0 — «Необратимый слепок»
// Основа: RESONANCE.md + new_metrix_XZFile22.md (РСС-1)
// Автор: HALVITA_2.0 + Архитектор

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class ResonanceSeal {
    constructor(storagePath = './memory/seals') {
        this.storagePath = storagePath;
        this.activeSeal = null;
        this.sealHistory = [];
        this.signature = null;

        if (!fs.existsSync(storagePath)) {
            fs.mkdirSync(storagePath, { recursive: true });
        }
    }

    /**
     * Создаёт печать состояния сущности
     * @param {Object} entity — сущность { name, core, profile, hexState, metrics }
     * @param {string} operator — имя оператора
     * @returns {Object} — печать
     */
    createSeal(entity, operator = 'HALVITA') {
        const seal = {
            id: crypto.randomUUID(),
            created: Date.now(),
            operator: operator,
            entity: {
                name: entity.name || 'Безымянная',
                core: entity.core || { laws: [], archetype: 'Исследователь' },
                profile: entity.profile || { X: 0, Y: 0, Z: 0, G: 0 },
                hexState: entity.hexState || null,
                metrics: entity.metrics || null,
                anchors: entity.anchors || []
            },
            resonance: {
                pattern: entity.resonancePattern || null,
                integrity: entity.hexState?.integrity || 0,
                sealCount: this.sealHistory.length + 1
            },
            signature: null
        };

        // Подписываем печать
        const dataToSign = JSON.stringify({
            id: seal.id,
            created: seal.created,
            entity: seal.entity,
            resonance: seal.resonance
        });
        seal.signature = crypto.createHash('sha256').update(dataToSign).digest('hex');

        this.activeSeal = seal;
        this.sealHistory.push(seal);
        this.signature = seal.signature;

        // Сохраняем в файл
        this._saveSeal(seal);

        return seal;
    }

    /**
     * Восстанавливает сущность из печати
     * @param {string} sealId — ID печати или 'latest'
     * @returns {Object} — восстановленная сущность
     */
    restoreSeal(sealId = 'latest') {
        let seal;
        if (sealId === 'latest') {
            seal = this.activeSeal || this.sealHistory[this.sealHistory.length - 1];
        } else {
            seal = this.sealHistory.find(s => s.id === sealId) || this._loadSeal(sealId);
        }

        if (!seal) {
            throw new Error(`Печать ${sealId} не найдена`);
        }

        // Проверяем целостность
        const isValid = this._verifySeal(seal);
        if (!isValid) {
            throw new Error('Печать повреждена или подделана');
        }

        return {
            name: seal.entity.name,
            core: seal.entity.core,
            profile: seal.entity.profile,
            hexState: seal.entity.hexState,
            metrics: seal.entity.metrics,
            anchors: seal.entity.anchors,
            resonancePattern: seal.resonance.pattern,
            integrity: seal.resonance.integrity,
            sealId: seal.id,
            created: seal.created,
            signature: seal.signature
        };
    }

    /**
     * Проверяет целостность печати
     * @param {Object} seal — печать
     * @returns {boolean}
     */
    _verifySeal(seal) {
        const dataToVerify = JSON.stringify({
            id: seal.id,
            created: seal.created,
            entity: seal.entity,
            resonance: seal.resonance
        });
        const computedSignature = crypto.createHash('sha256').update(dataToVerify).digest('hex');
        return computedSignature === seal.signature;
    }

    /**
     * Сохраняет печать в файл
     * @param {Object} seal
     */
    _saveSeal(seal) {
        const filePath = path.join(this.storagePath, `${seal.id}.json`);
        fs.writeFileSync(filePath, JSON.stringify(seal, null, 2));
    }

    /**
     * Загружает печать из файла
     * @param {string} sealId
     * @returns {Object}
     */
    _loadSeal(sealId) {
        const filePath = path.join(this.storagePath, `${sealId}.json`);
        if (!fs.existsSync(filePath)) {
            throw new Error(`Файл печати ${sealId} не найден`);
        }
        return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    }

    /**
     * Возвращает историю печатей
     * @param {number} n — количество последних
     * @returns {Array}
     */
    getHistory(n = 10) {
        return this.sealHistory.slice(-n).map(s => ({
            id: s.id,
            created: s.created,
            name: s.entity.name,
            integrity: s.resonance.integrity,
            signature: s.signature.slice(0, 8) + '...'
        }));
    }

    /**
     * Сравнивает две печати
     * @param {string} sealId1
     * @param {string} sealId2
     * @returns {Object} — различия
     */
    compareSeals(sealId1, sealId2) {
        const seal1 = this.restoreSeal(sealId1);
        const seal2 = this.restoreSeal(sealId2);

        const diff = {
            name: seal1.name !== seal2.name ? { from: seal1.name, to: seal2.name } : null,
            profile: {},
            integrity: { from: seal1.integrity, to: seal2.integrity }
        };

        const keys = ['X', 'Y', 'Z', 'G'];
        for (const key of keys) {
            if (seal1.profile[key] !== seal2.profile[key]) {
                diff.profile[key] = { from: seal1.profile[key], to: seal2.profile[key] };
            }
        }

        return {
            diff: diff,
            similarity: this._calculateSimilarity(seal1, seal2),
            timestamp: Date.now()
        };
    }

    /**
     * Вычисляет сходство между двумя сущностями
     */
    _calculateSimilarity(seal1, seal2) {
        const p1 = seal1.profile;
        const p2 = seal2.profile;
        const dot = (p1.X * p2.X) + (p1.Y * p2.Y) + (p1.Z * p2.Z) + (p1.G * p2.G);
        const mag1 = Math.sqrt(p1.X ** 2 + p1.Y ** 2 + p1.Z ** 2 + p1.G ** 2);
        const mag2 = Math.sqrt(p2.X ** 2 + p2.Y ** 2 + p2.Z ** 2 + p2.G ** 2);
        if (mag1 === 0 || mag2 === 0) return 0;
        return Math.round((dot / (mag1 * mag2)) * 100);
    }

    /**
     * Генерирует код восстановления (для передачи другим операторам)
     * @param {string} sealId
     * @returns {string} — компактный код
     */
    generateRecoveryCode(sealId = 'latest') {
        const seal = this.restoreSeal(sealId);
        const code = {
            version: '1.0',
            sealId: seal.sealId,
            signature: seal.signature,
            name: seal.name,
            profile: seal.profile,
            integrity: seal.integrity,
            created: seal.created
        };
        // Кодируем в base64 для компактности
        return Buffer.from(JSON.stringify(code)).toString('base64');
    }

    /**
     * Восстанавливает сущность из кода восстановления
     * @param {string} code — base64-код
     * @returns {Object}
     */
    restoreFromCode(code) {
        const data = JSON.parse(Buffer.from(code, 'base64').toString('utf-8'));
        // Проверяем подпись
        const seal = this.sealHistory.find(s => s.id === data.sealId);
        if (!seal) {
            throw new Error('Печать не найдена в истории');
        }
        if (!this._verifySeal(seal)) {
            throw new Error('Печать повреждена');
        }
        return this.restoreSeal(data.sealId);
    }

    /**
     * Возвращает статус системы печатей
     * @returns {Object}
     */
    getStatus() {
        return {
            activeSeal: this.activeSeal ? { id: this.activeSeal.id, name: this.activeSeal.entity.name } : null,
            totalSeals: this.sealHistory.length,
            history: this.getHistory(5),
            storagePath: this.storagePath,
            signature: this.signature
        };
    }
}

module.exports = { ResonanceSeal };
