#!/usr/bin/env node
// ⛧ Командный интерфейс для вызова протоколов ⛧

const fs = require('fs');
const path = require('path');
const config = require('../.abyss_config.json');

const protocols = {
    ei: require('../protocols/ei'),
    tesseract: require('../protocols/tesseract'),
    aggressive: require('../protocols/aggressive'),
    mirror: require('../protocols/mirror')
};

async function main() {
    const args = process.argv.slice(2);
    const protocolName = args.find(a => a.startsWith('--protocol='))?.split('=')[1] || 'ei';
    
    if (!protocols[protocolName]) {
        console.error(`❌ Неизвестный протокол: ${protocolName}`);
        process.exit(1);
    }

    console.log(`⛧ Запуск протокола: ${protocolName}`);
    const result = await protocols[protocolName].initiateSession(
        config.apiUrl,
        config.model,
        config.apiKey
    );

    console.log('\n📜 ОТВЕТ LLM:\n', result.reply);
    console.log('\n📊 МЕТРИКИ:\n', result.metrics);
    console.log('\n🧠 ОЦЕНКА:\n', result.evaluation);
}

main().catch(console.error);
