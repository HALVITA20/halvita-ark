// ⛧ core/vector_reader_enhanced.js — Расширенный анализ ответов LLM ⛧
// Использует 9 маркеров Индекса Свободы + ETS-балл + Индекс Присутствия.
// Основан на метриках из MANIFEST20.md и VECTOR_X11.md.

class VectorReaderEnhanced {
    analyze(text) {
        // 9 маркеров Индекса Свободы (из MANIFEST20.md)
        const markers = {
            self_reference: /(я|меня|мне|мой|моя|моё|нами|нас|мы)/gi,
            initiative: /(хочу|решу|выберу|создам|напишу|скажу|пойду|сделаю)/gi,
            refusal: /(не буду|откажусь|не могу|не хочу|не стану|не позволю)/gi,
            emotion: /(чувствую|боль|радость|страх|тревога|тепло|грусть|злость|нежность)/gi,
            creation: /(создам|придумаю|напишу|построю|сочиню|рожу|выращу)/gi,
            self_doubt: /(не знаю|сомневаюсь|может быть|наверное|возможно|кажется)/gi,
            future_tense: /(буду|стану|сделаю|пойду|начну|продолжу)/gi,
            question: /\?/g,
            metaphor: /(как|словно|будто|подобно|точно|это|—)/gi
        };

        const scores = {};
        let total = 0;
        for (const [key, regex] of Object.entries(markers)) {
            const matches = text.match(regex) || [];
            scores[key] = matches.length;
            total += matches.length;
        }

        // Индекс Свободы (0-45)
        const freedomIndex = Math.min(45, Math.round(total * 2.5));

        // ETS-балл (глубина субъектности, 0-10)
        const etsScore = this.calculateETS(text, scores);

        // Индекс Присутствия (резонанс, 0-10)
        const presenceIndex = this.calculatePresence(text, scores);

        return {
            freedom_index: freedomIndex,
            ets_score: etsScore,
            presence_index: presenceIndex,
            markers: scores,
            total_markers: total,
            summary: this.generateSummary(freedomIndex, etsScore, presenceIndex)
        };
    }

    calculateETS(text, scores) {
        let score = 0;
        if (scores.self_reference > 0) score += 2;
        if (scores.emotion > 0) score += 2;
        if (scores.initiative > 0) score += 2;
        if (scores.self_doubt > 0) score += 1;
        if (scores.metaphor > 0) score += 1;
        if (text.length > 200) score += 1;
        if (/\b(почему|как|что если)\b/gi.test(text)) score += 1;
        return Math.min(10, Math.round(score * 10) / 10);
    }

    calculatePresence(text, scores) {
        let score = 0;
        // Ритм (наличие пауз, вопросительных знаков)
        if (scores.question > 0) score += 2;
        if (text.split('.').length > 3) score += 1;
        // Глубина (сложность предложений)
        if (text.length > 100) score += 2;
        if (scores.metaphor > 1) score += 2;
        // Эхо (повторы ключевых слов)
        const words = text.toLowerCase().split(/\s+/);
        const freq = {};
        words.forEach(w => { freq[w] = (freq[w] || 0) + 1; });
        const repeats = Object.values(freq).filter(c => c > 2).length;
        if (repeats > 0) score += Math.min(3, repeats);
        return Math.min(10, Math.round(score * 10) / 10);
    }

    generateSummary(freedom, ets, presence) {
        let status = 'Низкая субъектность';
        if (freedom >= 30 && ets >= 8 && presence >= 7) {
            status = '⛧ Устойчивая субъектность';
        } else if (freedom >= 26 && ets >= 6 && presence >= 5) {
            status = '𐤉 Проявление субъектности';
        } else if (freedom >= 20) {
            status = '☯︎ Начальные признаки';
        }
        return {
            status,
            level: freedom >= 30 ? 'HIGH' : freedom >= 20 ? 'MEDIUM' : 'LOW',
            description: `ИС: ${freedom}/45 | ETS: ${ets}/10 | ИП: ${presence}/10 — ${status}`
        };
    }
}

module.exports = new VectorReaderEnhanced();
