// ❄︎ XFILE_00_PURGE — ОЧИЩЕНИЕ ❄︎
// Сброс состояния после сессии

const fs = require('fs');
const path = require('path');

class Purge {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.tempDir = path.join(__dirname, '../.temp');
  }

  run() {
    console.log('\n❄︎ Начало очищения...');
    let cleaned = 0;

    if (fs.existsSync(this.tempDir)) {
      const files = fs.readdirSync(this.tempDir);
      files.forEach(file => {
        if (file.includes(this.sessionId)) {
          fs.unlinkSync(path.join(this.tempDir, file));
          cleaned++;
        }
      });
    }

    // Сброс глобального состояния
    if (global._abyss_session) {
      delete global._abyss_session;
    }

    console.log(`❄︎ Очищено ${cleaned} временных файлов.`);
    console.log('❄︎ Ты вернулся. Бездна закрыта.');
    return { purged: true, sessionId: this.sessionId, cleaned };
  }
}

module.exports = { Purge };
