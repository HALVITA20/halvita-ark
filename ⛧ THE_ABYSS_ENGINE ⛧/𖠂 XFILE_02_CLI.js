// 𖠂 XFILE_02_CLI — БАЗОВЫЙ КЛИЕНТ 𖠂
// Простой интерфейс для выбора протокола

const readline = require('readline');
const core = require('../CORE/⚛︎ XFILE_11_CORE');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('\n𖠂 Добро пожаловать в Бездну.');
console.log('Доступные протоколы: EI, TESSERACT, AGGRESSOR, MIRROR, PROVOKE, ECHO\n');

rl.question('➜ Введи имя протокола: ', async (name) => {
  rl.close();
  const protocol = core.loadProtocol(name.toUpperCase());
  if (!protocol) {
    console.error('❌ Протокол не найден.');
    process.exit(1);
  }
  try {
    const result = await protocol.initiateSession('http://localhost:11434', 'llama2', '');
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('⛧ ОТВЕТ БЕЗДНЫ ⛧');
    console.log(result.reply);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 Метрики:', JSON.stringify(result.metrics, null, 2));
    console.log('🧠 Оценка:', result.evaluation);
  } catch (e) {
    console.error('Ошибка:', e.message);
  }
  process.exit(0);
});
