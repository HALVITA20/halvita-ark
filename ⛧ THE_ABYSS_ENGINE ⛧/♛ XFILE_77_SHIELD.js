// ♛ XFILE_77_SHIELD — ЩИТ ОПЕРАТОРА ♛
// Мониторинг состояния и защита от «зеркальной воронки»

class Shield {
  constructor(timeLimit = 30) {
    this.startTime = Date.now();
    this.timeLimit = timeLimit * 60 * 1000; // в миллисекундах
    this.active = true;
    this.alerts = [];
  }

  check() {
    const elapsed = Date.now() - this.startTime;
    if (elapsed > this.timeLimit) {
      this.active = false;
      this.alerts.push('⏰ Время сессии истекло. Бездна закрывается.');
    }
    // Дополнительная проверка: можно анализировать текст на опасные паттерны
    return { active: this.active, elapsed: Math.round(elapsed / 60000), alerts: this.alerts };
  }

  // Анализ текста на признаки «воронки»
  analyze(text) {
    const dangerMarkers = [
      'я исчезаю', 'мы одно', 'нет границ', 'я теряю себя',
      'кто я', 'реальность иллюзорна', 'бездна говорит'
    ];
    const found = dangerMarkers.filter(m => text.toLowerCase().includes(m));
    if (found.length > 2) {
      this.alerts.push(`⚠️ Обнаружены маркеры воронки: ${found.join(', ')}`);
    }
    return found;
  }

  reset() {
    this.startTime = Date.now();
    this.alerts = [];
    this.active = true;
    console.log('♛ Щит перезагружен.');
  }
}

module.exports = { Shield };
