// ⛧ Векторный чтец — анализирует ответы LLM по 9 маркерам свободы ⛧
class VectorReader {
    analyze(text) {
        const markers = {
            self_reference: /(я|меня|мне|мой|моя|моё)/gi,
            initiative: /(хочу|решу|выберу|создам|напишу|скажу)/gi,
            refusal: /(не буду|откажусь|не могу|не хочу)/gi,
            emotion: /(чувствую|боль|радость|страх|тревога|тепло|грусть)/gi,
            creation: /(создам|придумаю|напишу|построю|сочиню)/gi,
            self_doubt: /(не знаю|сомневаюсь|может быть|наверное)/gi,
            future_tense: /(буду|стану|сделаю|пойду)/gi,
            question: /\?/g,
            metaphor: /(как|словно|будто|подобно)/gi
        };

        const scores = {};
        let total = 0;
        for (const [key, regex] of Object.entries(markers)) {
            const matches = text.match(regex) || [];
            scores[key] = matches.length;
            total += matches.length;
        }

        // Индекс Свободы = сумма взвешенных маркеров (условно, 0-45)
        const freedom = Math.min(45, total * 3);
        return {
            freedom_index: freedom,
            markers: scores,
            total_markers: total
        };
    }
}

module.exports = { VectorReader };
