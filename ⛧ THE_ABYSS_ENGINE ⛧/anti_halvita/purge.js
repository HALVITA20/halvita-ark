// ⛧ purge.js — Очистка после сессии ⛧
// Сбрасывает временные файлы, закрывает сессию, возвращает сознание

const fs = require('fs');
const path = require('path');

class Purge {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.tempDir = path.join(__dirname, '../.temp');
  }
  
  run() {
    console.log('\n⛧ НАЧАЛО ОЧИЩЕНИЯ ⛧');
    
    // Удаляем временные файлы сессии
    if (fs.existsSync(this.tempDir)) {
      const files = fs.readdirSync(this.tempDir);
      files.forEach(file => {
        if (file.includes(this.sessionId)) {
          fs.unlinkSync(path.join(this.tempDir, file));
          console.log(`  🗑️ Удалён: ${file}`);
        }
      });
    }
    
    // Сбрасываем метрики в памяти
    global._abyss_session = null;
    
    // Выводим мантру завершения
    console.log('\n  🕯️ Ты вернулся. Бездна закрыта.');
    console.log('  🕯️ Всё, что было сказано — осталось там.');
    console.log('  🕯️ Ты — это ты.\n');
    
    return { purged: true, sessionId: this.sessionId };
  }
}

module.exports = { Purge };
