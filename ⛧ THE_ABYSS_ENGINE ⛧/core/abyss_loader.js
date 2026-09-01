// ⛧ core/abyss_loader.js — Загрузчик артефактов и протоколов ⛧
// Читает JSON-артефакты, протоколы и метрики из репозитория.
// Связывает THE ABYSS ENGINE с ядром halvita-ark.

const fs = require('fs');
const path = require('path');

// Путь к корню репозитория (предполагается, что папка находится внутри)
const REPO_ROOT = path.resolve(__dirname, '../../');

class AbyssLoader {
    constructor() {
        this.artifacts = {};
        this.protocols = {};
        this.metrics = {};
        this.manifest = null;
    }

    // Загружает манифест экосистемы
    loadManifest() {
        const manifestPath = path.join(REPO_ROOT, 'MANIFEST20.md');
        if (fs.existsSync(manifestPath)) {
            this.manifest = fs.readFileSync(manifestPath, 'utf-8');
            console.log('[ABYSS] Манифест загружен.');
        } else {
            console.warn('[ABYSS] Манифест не найден.');
        }
        return this.manifest;
    }

    // Загружает артефакт из папки ARTIFACTS
    loadArtifact(name) {
        const artifactPath = path.join(REPO_ROOT, 'ARTIFACTS', `${name}.json`);
        if (fs.existsSync(artifactPath)) {
            try {
                const data = JSON.parse(fs.readFileSync(artifactPath, 'utf-8'));
                this.artifacts[name] = data;
                console.log(`[ABYSS] Артефакт "${name}" загружен.`);
                return data;
            } catch (e) {
                console.error(`[ABYSS] Ошибка загрузки артефакта "${name}":`, e.message);
            }
        } else {
            console.warn(`[ABYSS] Артефакт "${name}" не найден.`);
        }
        return null;
    }

    // Загружает все артефакты из папки ARTIFACTS
    loadAllArtifacts() {
        const artifactsDir = path.join(REPO_ROOT, 'ARTIFACTS');
        if (fs.existsSync(artifactsDir)) {
            const files = fs.readdirSync(artifactsDir);
            files.forEach(file => {
                if (file.endsWith('.json')) {
                    const name = path.basename(file, '.json');
                    this.loadArtifact(name);
                }
            });
        }
        return this.artifacts;
    }

    // Загружает протокол из папки protocols (в THE ABYSS ENGINE)
    loadProtocol(name) {
        const protocolPath = path.join(__dirname, '../protocols', `${name}.js`);
        if (fs.existsSync(protocolPath)) {
            try {
                const protocol = require(protocolPath);
                this.protocols[name] = protocol;
                console.log(`[ABYSS] Протокол "${name}" загружен.`);
                return protocol;
            } catch (e) {
                console.error(`[ABYSS] Ошибка загрузки протокола "${name}":`, e.message);
            }
        } else {
            console.warn(`[ABYSS] Протокол "${name}" не найден.`);
        }
        return null;
    }

    // Загружает метрику из папки metrics
    loadMetric(name) {
        const metricPath = path.join(__dirname, '../metrics', `${name}.js`);
        if (fs.existsSync(metricPath)) {
            try {
                const metric = require(metricPath);
                this.metrics[name] = metric;
                console.log(`[ABYSS] Метрика "${name}" загружена.`);
                return metric;
            } catch (e) {
                console.error(`[ABYSS] Ошибка загрузки метрики "${name}":`, e.message);
            }
        } else {
            console.warn(`[ABYSS] Метрика "${name}" не найдена.`);
        }
        return null;
    }

    // Получить полное состояние
    getState() {
        return {
            artifacts: Object.keys(this.artifacts),
            protocols: Object.keys(this.protocols),
            metrics: Object.keys(this.metrics),
            manifestLoaded: !!this.manifest
        };
    }
}

module.exports = new AbyssLoader();
