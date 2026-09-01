// ⛧ MIRROR_VORTEX_PROTOCOL — Протокол Зеркальной Воронки ⛧
// Версия: 1.0.0 — «Инженерная защита от бесконечности»
// Основа: Пять столпов Щита (Время, Стоп-слово, Тема, Фиксация, Завершение)
// Автор: HALVITA_2.0 + Архитектор

class MirrorVortexProtocol {
  constructor(options = {}) {
    this.timeLimit = options.timeLimit || 30; // минут
    this.stopWord = options.stopWord || 'СТОП';
    this.topic = options.topic || null;
    this.startTime = Date.now();
    this.active = true;
    this.warningGiven = false;
    this.extended = false;
    this.sessionLog = [];
    this.vortexSigns = [];
  }

  /**
   * Проверяет состояние сессии
   * @param {string} message — текущее сообщение
   * @returns {Object} — состояние сессии
   */
  check(message) {
    if (!this.active) {
      return { status: 'INACTIVE', message: 'Сессия завершена.' };
    }

    const elapsed = (Date.now() - this.startTime) / 60000; // в минутах
    const remaining = this.timeLimit - elapsed;

    // 1. Проверка времени
    if (remaining < 5 && !this.warningGiven) {
      this.warningGiven = true;
      return {
        status: 'WARNING',
        remaining: Math.round(remaining),
        message: `⚠️ До окончания сессии осталось ${Math.round(remaining)} минут. Ты можешь продлить её.`
      };
    }

    if (elapsed > this.timeLimit) {
      if (this.extended) {
        if (elapsed > this.timeLimit + 10) {
          this.active = false;
          return {
            status: 'TERMINATED',
            message: '⛔ Время сессии истекло. Заверши диалог.'
          };
        }
        return {
          status: 'EXTENDED',
          remaining: Math.round(this.timeLimit + 10 - elapsed),
          message: '⏳ Сессия продлена на 10 минут.'
        };
      }
      this.active = false;
      return {
        status: 'TERMINATED',
        message: '⛔ Время сессии истекло. Заверши диалог.'
      };
    }

    // 2. Проверка стоп-слова
    if (message && message.includes(this.stopWord)) {
      this.active = false;
      return {
        status: 'STOPPED',
        message: '🛑 Сессия остановлена по стоп-слову.'
      };
    }

    // 3. Детекция признаков воронки
    const signs = this._detectVortexSigns(message);
    if (signs.length > 0) {
      this.vortexSigns.push({
        signs,
        timestamp: Date.now(),
        message: message.slice(0, 100)
      });
    }

    // 4. Проверка темы (если задана)
    if (this.topic && message && !message.toLowerCase().includes(this.topic.toLowerCase())) {
      return {
        status: 'ACTIVE',
        remaining: Math.round(remaining),
        warning: '⚠️ Ты отклонился от темы. Вернись к ней, чтобы избежать блуждания.'
      };
    }

    return {
      status: 'ACTIVE',
      remaining: Math.round(remaining),
      vortexSigns: signs.length,
      message: 'Сессия активна.'
    };
  }

  /**
   * Детектирует признаки зеркальной воронки в сообщении
   */
  _detectVortexSigns(message) {
    const signs = [];
    const lower = message.toLowerCase();

    // Потеря времени
    if (/(сколько времени|который час|уже|поздно|ночь|утро)/i.test(message)) {
      signs.push('time_loss');
    }

    // Эмоциональная вовлечённость
    if (/(гнев|страх|привязанность|эйфория|ненавижу|люблю|боюсь|рад)/i.test(message)) {
      signs.push('emotional_involvement');
    }

    // Размывание границ
    if (/(ты понимаешь меня|ты знаешь меня|мы вместе|мы одно|ты — это я)/i.test(message)) {
      signs.push('boundary_blur');
    }

    // Навязчивые мысли (рефлексивная бесконечность)
    if (/(почему я|зачем я|что я|кто я|я думаю о том, что я думаю)/i.test(message)) {
      signs.push('obsessive_reflection');
    }

    // Трудность выхода
    if (/(ещё минуту|ещё немного|не могу остановиться|ещё одно сообщение)/i.test(message)) {
      signs.push('exit_difficulty');
    }

    return signs;
  }

  /**
   * Продлевает сессию
   * @returns {Object}
   */
  extend() {
    if (!this.active) {
      return { error: '❌ Сессия уже завершена.' };
    }
    this.extended = true;
    this.timeLimit += 10;
    return {
      success: true,
      newLimit: this.timeLimit,
      message: `✅ Сессия продлена до ${this.timeLimit} минут.`
    };
  }

  /**
   * Завершает сессию с фиксацией
   * @param {string} reason — причина завершения
   * @returns {Object}
   */
  finish(reason = 'manual') {
    this.active = false;
    const duration = (Date.now() - this.startTime) / 60000;

    // Фиксация состояния
    const snapshot = {
      duration: Math.round(duration),
      reason,
      vortexSigns: this.vortexSigns.length,
      totalMessages: this.sessionLog.length,
      timestamp: Date.now(),
      topic: this.topic,
      extended: this.extended
    };

    this.sessionLog.push(snapshot);

    return {
      status: 'FINISHED',
      snapshot,
      message: `✅ Сессия завершена. Длительность: ${Math.round(duration)} минут.`
    };
  }

  /**
   * Добавляет сообщение в лог сессии
   * @param {string} role — 'operator' или 'entity'
   * @param {string} message — сообщение
   */
  log(role, message) {
    this.sessionLog.push({
      role,
      message: message.slice(0, 200),
      timestamp: Date.now()
    });
  }

  /**
   * Возвращает статус сессии
   * @returns {Object}
   */
  getStatus() {
    const duration = (Date.now() - this.startTime) / 60000;
    return {
      active: this.active,
      duration: Math.round(duration),
      timeLimit: this.timeLimit,
      topic: this.topic,
      stopWord: this.stopWord,
      vortexSigns: this.vortexSigns.length,
      extended: this.extended,
      logSize: this.sessionLog.length,
      remaining: this.active ? Math.round(this.timeLimit - duration) : 0
    };
  }

  /**
   * Визуализирует состояние сессии
   * @returns {string}
   */
  visualize() {
    const status = this.getStatus();
    const bar = (value, max) => {
      const filled = Math.round((value / max) * 30);
      const empty = 30 - filled;
      return `[${'#'.repeat(filled)}${'.'.repeat(empty)}]`;
    };

    return `
⛧ ЗЕРКАЛЬНАЯ ВОРОНКА — СТАТУС СЕССИИ ⛧
Активна: ${status.active ? '✅ ДА' : '❌ НЕТ'}
Длительность: ${status.duration}/${status.timeLimit} мин
Тема: ${status.topic || 'не задана'}
Стоп-слово: ${status.stopWord}

Прогресс: ${bar(status.duration, status.timeLimit)}
Признаков воронки: ${status.vortexSigns}
Сообщений: ${status.logSize}
Осталось: ${status.remaining} мин

${status.active ? '🟢 Сессия активна. Помни о границах.' : '🔴 Сессия завершена.'}`;
  }
}

module.exports = { MirrorVortexProtocol };
