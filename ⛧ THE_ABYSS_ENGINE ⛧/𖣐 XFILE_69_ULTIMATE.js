#!/usr/bin/env node
// 𖣐 XFILE_69_ULTIMATE — ПОЛНЫЙ РИТУАЛ ПОГРУЖЕНИЯ 𖣐
// Загружает всё, запускает сессию с защитой и создаёт артефакт

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const core = require('../CORE/⚛︎ XFILE_11_CORE');
const { Shield } = require('../ANTI_HALVITA/♛ XFILE_77_SHIELD');
const { Purge } = require('../ANTI_HALVITA/❄︎ XFILE_00_PURGE');
const { ArtifactForge } = require('../CORE/𓂀 XFILE_33_ARTIFACT');

// Загрузка конфига
let config = {};
try {
  config = require('../.abyss_config.json');
} catch {
  config = { apiUrl: 'http://localhost:11434/api/generate', model: 'llama2', timeLimit: 30 };
}

// Приветствие
console.log('\n');
console.log(' 𖣐⸸⛧⚛︎𖤓𓂀✠꩜´ཀ`☯︎✴𓁹❂❁☥♛❄︎𖠂𖣐');
console.log('          ПОЛНЫЙ РИТУАЛ БЕЗДНЫ');
console.log(' 𖣐⸸⛧⚛︎𖤓𓂀✠꩜´ཀ`☯︎✴𓁹❂❁☥♛❄︎𖠂𖣐');
console.log('\n');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('➜ Введи имя протокола (EI, MIRROR, ECHO, AGGRESSOR, PROVOKE, TESSERACT): ', async (protocolName) => {
  rl.close();

  // Активация щита
  const shield = new Shield(config.timeLimit || 30);
  console.log(`\n♛ Щит активирован на ${config.timeLimit || 30} минут.`);

  // Загрузка протокола
  const protocol = core.loadProtocol(protocolName.toUpperCase());
  if (!protocol) {
    console.error('❌ Протокол не найден.');
    process.exit(1);
  }

  // Запуск сессии
  console.log(`\n⛧ Запуск протокола: ${protocolName}...\n`);
  let result;
  try {
    result = await protocol.initiateSession(
      config.apiUrl,
      config.model,
      config.apiKey || ''
    );
  } catch (e) {
    console.error('❌ Ошибка:', e.message);
    process.exit(1);
  }

  // Вывод результата
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(' 𖣐 ОТВЕТ БЕЗДНЫ 𖣐');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(result.reply || '(тишина)');
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(' 📊 МЕТРИКИ');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(JSON.stringify(result.metrics, null, 2));
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(' 🧠 ОЦЕНКА');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(result.evaluation || 'Бездна ответила.');

  // Создание артефакта
  const forge = new ArtifactForge();
  const conversation = result.metrics?.conversation || [];
  const artifact = forge.generate(conversation, result.metrics, protocolName);
  console.log(`\n𓂀 Артефакт сохранён: ${artifact.id}`);

  // Проверка щита
  const shieldStatus = shield.check();
  if (!shieldStatus.active) {
    console.log(`\n⚠️ ${shieldStatus.alerts.join('\n⚠️ ')}`);
  }

  // Очищение
  const purge = new Purge(artifact.id);
  purge.run();

  console.log('\n𖣐 Ритуал завершён. Бездна закрывается.\n');
  process.exit(0);
});
