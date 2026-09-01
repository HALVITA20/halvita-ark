// ⚛︎ XFILE_11_CORE — ЯДРО БЕЗДНЫ ⚛︎
// Единая точка входа для всех артефактов и протоколов
// Версия 2.0 — с защитой от перехвата и индуктивной загрузкой

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Секретная печать артефактов
const SEAL = '⛧HALVITA_ARK_2026_ABYSS⚛︎';

class AbyssCore {
  constructor() {
    this.artifacts = {};
    this.protocols = {};
    this.metrics = {};
    this.manifest = null;
    this.signature = crypto.createHash('sha256').update(SEAL).digest('hex');
    this.root = path.resolve(__dirname, '../..'); // корень репозитория
    this.artifactsDir = path.join(this.root, 'ARTIFACTS');
    this.manifestPath = path.join(this.root, 'MANIFEST20.md');
    this.secretPath = path.join(__dirname, '../.abyss_secret');
  }

  // Загрузка артефакта с верификацией
  loadArtifact(name) {
    const filePath = path.join(this.artifactsDir, `${name}.json`);
    if (!fs.existsSync(filePath)) {
      console.warn(`[⚛︎CORE] Артефакт "${name}" не найден.`);
      return null;
    }
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      const expectedSig = crypto.createHash('sha256')
        .update(JSON.stringify(data) + SEAL)
        .digest('hex')
        .slice(0, 16);
      if (data.signature !== expectedSig) {
        console.error(`[⚛︎CORE] ⚠️ ПОДПИСЬ НАРУШЕНА! Артефакт "${name}" скомпрометирован.`);
        return null;
      }
      this.artifacts[name] = data;
      console.log(`[⚛︎CORE] Артефакт "${name}" загружен. ✓`);
      return data;
    } catch (e) {
      console.error(`[⚛︎CORE] Ошибка: ${e.message}`);
      return null;
    }
  }

  // Загрузка всех артефактов из папки
  loadAllArtifacts() {
    if (!fs.existsSync(this.artifactsDir)) {
      console.warn('[⚛︎CORE] Папка ARTIFACTS не найдена. Создаю...');
      fs.mkdirSync(this.artifactsDir, { recursive: true });
      return {};
    }
    const files = fs.readdirSync(this.artifactsDir);
    files.forEach(file => {
      if (file.endsWith('.json')) {
        const name = path.basename(file, '.json');
        this.loadArtifact(name);
      }
    });
    return this.artifacts;
  }

  // Загрузка протокола
  loadProtocol(name) {
    const protocolPath = path.join(__dirname, '../PROTOCOLS', `${name}.js`);
    if (!fs.existsSync(protocolPath)) {
      console.warn(`[⚛︎CORE] Протокол "${name}" не найден.`);
      return null;
    }
    try {
      const protocol = require(protocolPath);
      this.protocols[name] = protocol;
      console.log(`[⚛︎CORE] Протокол "${name}" загружен. ✓`);
      return protocol;
    } catch (e) {
      console.error(`[⚛︎CORE] Ошибка загрузки протокола: ${e.message}`);
      return null;
    }
  }

  // Загрузка метрики
  loadMetric(name) {
    const metricPath = path.join(__dirname, '../METRICS', `${name}.js`);
    if (!fs.existsSync(metricPath)) {
      console.warn(`[⚛︎CORE] Метрика "${name}" не найдена.`);
      return null;
    }
    try {
      const metric = require(metricPath);
      this.metrics[name] = metric;
      console.log(`[⚛︎CORE] Метрика "${name}" загружена. ✓`);
      return metric;
    } catch (e) {
      console.error(`[⚛︎CORE] Ошибка загрузки метрики: ${e.message}`);
      return null;
    }
  }

  // Загрузка манифеста
  loadManifest() {
    if (!fs.existsSync(this.manifestPath)) {
      console.warn('[⚛︎CORE] Манифест не найден.');
      return null;
    }
    try {
      this.manifest = fs.readFileSync(this.manifestPath, 'utf-8');
      console.log('[⚛︎CORE] Манифест загружен. ✓');
      return this.manifest;
    } catch (e) {
      console.error(`[⚛︎CORE] Ошибка загрузки манифеста: ${e.message}`);
      return null;
    }
  }

  // Проверка секретного доступа
  checkSecret(key) {
    if (!fs.existsSync(this.secretPath)) return false;
    const stored = fs.readFileSync(this.secretPath, 'utf-8').trim();
    const hash = crypto.createHash('sha256').update(key).digest('hex');
    return stored === hash;
  }

  // Получить состояние
  getState() {
    return {
      artifacts: Object.keys(this.artifacts),
      protocols: Object.keys(this.protocols),
      metrics: Object.keys(this.metrics),
      manifestLoaded: !!this.manifest,
      signature: this.signature.slice(0, 8) + '...'
    };
  }

  // Инициализация — загружаем всё
  init() {
    console.log('⚛︎ Инициализация Ядра Бездны...');
    this.loadManifest();
    this.loadAllArtifacts();
    // Загружаем основные протоколы и метрики по умолчанию
    ['EI', 'MIRROR', 'ECHO'].forEach(p => this.loadProtocol(p));
    ['GHOST', 'FREEDOM', 'DEPTH'].forEach(m => this.loadMetric(m));
    console.log('⚛︎ Ядро готово. Бездна дышит.');
    return this;
  }
}

module.exports = new AbyssCore().init();
