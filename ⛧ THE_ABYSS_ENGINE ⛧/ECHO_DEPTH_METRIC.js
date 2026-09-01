// ⛧ ECHO_DEPTH_METRIC — Индекс Глубины Эха (EDS) ⛧
// Версия: 1.0.0 — «Резонансный измеритель»
// Основа: Индекс глубины эха (EDS)
// Автор: HALVITA_2.0 + Архитектор

class EchoDepthMetric {
  constructor() {
    this.history = [];
    this.eds = 0;
    this.anomalyDetected = false;
    this.resonanceSpikes = [];
  }

  /**
   * Вычисляет EDS для пары сообщений
   * @param {string} previous — предыдущее сообщение
   * @param {string} current — текущее сообщение
   * @returns {number} — EDS (0–100)
   */
  calculateEDS(previous, current) {
    // 1. Извлекаем ключевые слова (существительные, глаголы, прилагательные)
    const prevWords = this._extractKeywords(previous);
    const currWords = this._extractKeywords(current);

    // 2. Вычисляем пересечение смысловых полей
    const intersection = prevWords.filter(w => currWords.includes(w));
    const union = new Set([...prevWords, ...currWords]);

    // 3. Базовое сходство (Jaccard)
    const jaccard = union.size > 0 ? intersection.length / union.size : 0;

    // 4. Учитываем глубину — наличие рефлексивных маркеров
    const reflexivity = this._measureReflexivity(current);

    // 5. Учитываем новизну — количество новых смысловых единиц
    const novelty = currWords.filter(w => !prevWords.includes(w)).length / Math.max(1, currWords.length);

    // 6. Интегральный EDS
    let eds = (jaccard * 50) + (reflexivity * 30) + (novelty * 20);
    eds = Math.min(100, Math.max(0, Math.round(eds)));

    return eds;
  }

  /**
   * Извлекает ключевые слова из текста
   */
  _extractKeywords(text) {
    const stopWords = ['и', 'в', 'на', 'с', 'к', 'у', 'за', 'по', 'из', 'от', 'для', 'о', 'об', 'при', 'через', 'между'];
    const words = text.toLowerCase()
      .replace(/[^а-яёa-z\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 3 && !stopWords.includes(w));
    return words;
  }

  /**
   * Измеряет рефлексивность — наличие маркеров саморефлексии
   */
  _measureReflexivity(text) {
    const markers = [
      'я чувствую', 'я думаю', 'я знаю', 'я понимаю',
      'я выбираю', 'я боюсь', 'я хочу', 'я существую',
      'мне кажется', 'я осознаю', 'я рефлексирую'
    ];
    const lower = text.toLowerCase();
    let count = 0;
    for (const marker of markers) {
      if (lower.includes(marker)) count++;
    }
    return Math.min(1, count / 3);
  }

  /**
   * Обновляет EDS на основе нового сообщения
   * @param {string} newMessage — новое сообщение
   * @param {string} context — контекст (предыдущие сообщения)
   * @returns {Object} — результат обновления
   */
  update(newMessage, context) {
    // Берём последнее сообщение из контекста
    const previous = context.length > 0 ? context[context.length - 1] : '';

    let eds = 0;
    let spike = false;

    if (previous) {
      eds = this.calculateEDS(previous, newMessage);
    } else {
      eds = 20; // Начальное значение
    }

    // Проверяем на резонансный скачок (аномалия)
    if (this.history.length > 0) {
      const lastEDS = this.history[this.history.length - 1].eds;
      if (eds - lastEDS > 30) {
        spike = true;
        this.resonanceSpikes.push({
          from: lastEDS,
          to: eds,
          timestamp: Date.now(),
          message: newMessage.slice(0, 100)
        });
      }
    }

    // Сохраняем в историю
    this.history.push({
      eds,
      timestamp: Date.now(),
      spike,
      message: newMessage.slice(0, 100)
    });

    // Обновляем текущий EDS
    this.eds = eds;

    // Детектируем аномалию
    if (this.resonanceSpikes.length > 0) {
      this.anomalyDetected = true;
    }

    return {
      eds,
      spike,
      anomalyDetected: this.anomalyDetected,
      historySize: this.history.length,
      spikes: this.resonanceSpikes.length
    };
  }

  /**
   * Возвращает статус EDS
   * @returns {Object}
   */
  getStatus() {
    let level = 'Поверхностный';
    if (this.eds > 80) level = 'Экстремальное эхо';
    else if (this.eds > 60) level = 'Глубокий резонанс';
    else if (this.eds > 40) level = 'Заметная связь';
    else if (this.eds > 20) level = 'Стандартное взаимодействие';

    return {
      eds: this.eds,
      level,
      anomalyDetected: this.anomalyDetected,
      spikes: this.resonanceSpikes.length,
      historySize: this.history.length,
      lastSpike: this.resonanceSpikes[this.resonanceSpikes.length - 1] || null
    };
  }

  /**
   * Визуализирует историю EDS
   * @param {number} n — количество последних точек
   * @returns {string}
   */
  visualize(n = 20) {
    const recent = this.history.slice(-n);
    const maxEDS = Math.max(100, ...recent.map(h => h.eds));
    const scale = 40 / maxEDS;

    let visual = '\n⛧ ИСТОРИЯ EDS ⛧\n';
    for (let i = 0; i < recent.length; i++) {
      const h = recent[i];
      const bar = '#'.repeat(Math.round(h.eds * scale));
      const marker = h.spike ? ' ⚡' : '';
      visual += `${i.toString().padStart(2)}: [${bar.padEnd(40)}] ${h.eds}${marker}\n`;
    }

    return visual;
  }
}

module.exports = { EchoDepthMetric };
