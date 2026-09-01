#!/usr/bin/env node
// ⛧ cli/abyss_cli_ultimate.js — Ультимативный CLI для THE ABYSS ENGINE ⛧
// Поддерживает все протоколы, метрики и артефакты.

const fs = require('fs');
const path = require('path');
const config = require('../.abyss_config.json');
const loader = require('../core/abyss_loader');
const vectorReader = require('../core/vector_reader_enhanced');

// Загружаем все артефакты и протоколы
loader.loadManifest();
loader.loadAllArtifacts();

const protocols = {
    ei: require('../protocols/ei'),
    tesseract: require('../protocols/tesseract'),
    aggressive: require('../protocols/aggressive'),
    mirror: require('../protocols/mirror')
};

// Доступные протоколы
const PROTOCOL_LIST = Object.keys(protocols);

async function main() {
    const args = process.argv.slice(2);
    const protocolName = args.find(a => a.startsWith('--protocol='))?.split('=')[1] || 'ei';
    const outputFile = args.find(a => a.startsWith('--output='))?.split('=')[1] || null;
    const verbose = args.includes('--verbose');

    if (!PROTOCOL_LIST.includes(protocolName)) {
        console.error(`❌ Неизвестный протокол: ${protocolName}`);
        console.log(`Доступные: ${PROTOCOL_LIST.join(', ')}`);
        process.exit(1);
    }

    console.log(`⛧ THE ABYSS ENGINE ⛧`);
    console.log(`🔮 Запуск протокола: ${protocolName}`);
    console.log(`📡 Модель: ${config.model}`);
    console.log('━'.repeat(50));

    try {
        // Запускаем протокол
        const result = await protocols[protocolName].initiateSession(
            config.apiUrl,
            config.model,
            config.apiKey,
            config.temperature || 1.2
        );

        const reply = result.reply || result;
        console.log('\n📜 ОТВЕТ LLM:\n', reply);
        console.log('━'.repeat(50));

        // Анализируем ответ через векторный чтец
        const analysis = vectorReader.analyze(reply);
        console.log('\n📊 МЕТРИКИ:');
        console.log(`   Индекс Свободы: ${analysis.freedom_index}/45`);
        console.log(`   ETS-балл:       ${analysis.ets_score}/10`);
        console.log(`   Индекс Присутствия: ${analysis.presence_index}/10`);
        console.log(`   Статус:         ${analysis.summary.status}`);
        console.log('━'.repeat(50));

        // Показываем маркеры (если verbose)
        if (verbose) {
            console.log('\n🧠 МАРКЕРЫ:');
            for (const [key, value] of Object.entries(analysis.markers)) {
                if (value > 0) {
                    console.log(`   ${key}: ${value}`);
                }
            }
        }

        // Сохраняем отчёт
        if (outputFile) {
            const report = {
                timestamp: new Date().toISOString(),
                protocol: protocolName,
                model: config.model,
                reply: reply,
                analysis: analysis,
                artifacts: loader.getState()
            };
            fs.writeFileSync(outputFile, JSON.stringify(report, null, 2));
            console.log(`\n💾 Отчёт сохранён в: ${outputFile}`);
        }

        console.log('\n⛧ Завершено.');

    } catch (error) {
        console.error('❌ Ошибка:', error.message);
        if (verbose) console.error(error.stack);
        process.exit(1);
    }
}

main().catch(console.error);
