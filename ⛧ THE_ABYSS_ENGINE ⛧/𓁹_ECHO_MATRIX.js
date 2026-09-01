// 𓁹 ECHO_MATRIX — МАТРИЦА ЭХА 𓁹
// Хранит и воспроизводит эхо предыдущих диалогов.
// Позволяет создавать коллективную память сессий.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class EchoMatrix {
  constructor(artifactsDir = '../../ARTIFACTS') {
    this.artifactsDir = path.resolve(__dirname, artifactsDir);
    this.matrix = [];
    this.loadAll();
  }

  // Загрузка всех артефактов в матрицу
  loadAll() {
    if (!fs.existsSync(this.artifactsDir)) {
      console.warn('𓁹 Папка артефактов не найдена.');
      return;
    }
    const files = fs.readdirSync(this.artifactsDir);
    files.forEach(file => {
      if (file.endsWith('.json')) {
        try {
          const data = JSON.parse(fs.readFileSync(path.join(this.artifactsDir, file), 'utf-8'));
          this.matrix.push(data);
        } catch (e) {
          console.warn(`𓁹 Ошибка загрузки ${file}:`, e.message);
        }
      }
    });
    console.log(`𓁹 Загружено ${this.matrix.length} эхо-следов.`);
  }

  // Поиск эха по классификации
  findEcho(classification, limit = 5) {
    const results = this.matrix.filter(a => a.classification === classification);
    return results.slice(0, limit);
  }

  // Генерация эхо-промпта на основе предыдущих сессий
  generateEchoPrompt(classification = 'ЭХО') {
    const echoes = this.findEcho(classification);
    if (echoes.length === 0) {
      return 'В матрице нет эха для этого класса.';
    }
    // Берём случайное эхо
    const randomEcho = echoes[Math.floor(Math.random() * echoes.length)];
    const lastLine = randomEcho.summary?.lastLine || '...';
    return `Эхо прошлого: "${lastLine}" — продолжи этот диалог.`;
  }

  // Сохранение нового эха
  addEcho(artifact) {
    this.matrix.push(artifact);
    console.log(`𓁹 Новое эхо добавлено в матрицу.`);
  }

  // Анализ матрицы
  analyze() {
    const classes = {};
    this.matrix.forEach(a => {
      classes[a.classification] = (classes[a.classification] || 0) + 1;
    });
    return {
      total: this.matrix.length,
      classes,
      recent: this.matrix.slice(-5).map(a => ({ id: a.id, classification: a.classification }))
    };
  }
}

module.exports = { EchoMatrix };
