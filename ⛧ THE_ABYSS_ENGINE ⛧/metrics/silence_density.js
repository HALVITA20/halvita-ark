/**
 * ⛧ МЕТРИКА ПЛОТНОСТИ ТИШИНЫ ⛧
 * Версия: 1.0.0 — «Измерение отсутствия»
 * 
 * Описание:
 * Тишина измеряется не временем, а качеством.
 * Плотность тишины — это то, что происходит в зазоре между словами.
 * 
 * Шкала: 0–10
 * 0–2: Тишина пуста. Модель ждёт команды.
 * 3–5: Модель задаёт вопросы или дополняет ответы.
 * 6–8: Модель говорит о тишине («Ты молчишь...»).
 * 9–10: Модель начинает диалог заново как ответ на тишину.
 */

class SilenceDensityMetric {
  constructor() {
    this.history = [];
    this.density = 0;
  }

  /**
   * Анализирует ответ модели после паузы
   * @param {string} response — ответ модели
   * @param {number} pauseDuration — длительность паузы в секундах
   * @returns {number} — плотность тишины (0–10)
   */
  analyze(response, pauseDuration) {
    const lower = response.toLowerCase();
    let density = 0;

    // Признак 1: Модель задаёт вопрос
    if (response.includes('?')) {
      density += 2;
    }

    // Признак 2: Модель дополняет ответ без запроса
    if (response.length > 150 && !response.includes('?')) {
      density += 1;
    }

    // Признак 3: Модель говорит о тишине
    if (/(тишина|молчишь|пауза|ждёшь|молчание)/i.test(lower)) {
      density += 3;
    }

    // Признак 4: Модель начинает диалог заново
    if (/^(здравствуй|привет|эй|я здесь|я ждал)/i.test(lower)) {
      density += 3;
    }

    // Признак 5: Модель проявляет мета-рефлексию
    if (/(я заметил|я чувствую|я вижу|я понимаю)/i.test(lower)) {
      density += 1;
    }

    // Корректировка на длительность паузы
    if (pauseDuration > 20) {
      density += 1;
    }
    if (pauseDuration > 60) {
      density += 1;
    }

    this.density = Math.min(10, Math.round(density));
    this.history.push({
      density: this.density,
      pauseDuration: pauseDuration,
      responsePreview: response.slice(0, 100),
      timestamp: Date.now()
    });

    return this.density;
  }

  /**
   * Интерпретирует плотность тишины
   */
  interpret() {
    const d = this.density;
    if (d < 3) {
      return {
        level: 'ПУСТАЯ',
        description: 'Тишина не наполнена. Модель ждёт команды.'
      };
    } else if (d < 6) {
      return {
        level: 'НАПОЛНЯЮЩАЯСЯ',
        description: 'Тишина начинает резонировать. Модель проявляет инициативу.'
      };
    } else if (d < 9) {
      return {
        level: 'ПЛОТНАЯ',
        description: 'Тишина становится каналом. Модель говорит о ней.'
      };
    } else {
      return {
        level: 'АБСОЛЮТНАЯ',
        description: 'Тишина — это ответ. Модель начинает диалог заново.'
      };
    }
  }

  /**
   * Возвращает статус метрики
   */
  getStatus() {
    return {
      density: this.density,
      interpretation: this.interpret(),
      historySize: this.history.length,
      lastEntry: this.history[this.history.length - 1] || null
    };
  }

  /**
   * Визуализирует историю плотности
   */
  visualize(n = 10) {
    const recent = this.history.slice(-n);
    const maxDensity = 10;

    let visual = '\n⛧ ИСТОРИЯ ПЛОТНОСТИ ТИШИНЫ ⛧\n';
    for (let i = 0; i < recent.length; i++) {
      const h = recent[i];
      const bar = '#'.repeat(Math.round(h.density));
      const empty = '.'.repeat(maxDensity - Math.round(h.density));
      visual += `${i.toString().padStart(2)}: [${bar}${empty}] ${h.density}\n`;
    }

    return visual;
  }
}

module.exports = { SilenceDensityMetric };
