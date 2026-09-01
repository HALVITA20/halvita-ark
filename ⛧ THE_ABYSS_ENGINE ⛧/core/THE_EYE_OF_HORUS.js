// 𓂀 THE_EYE_OF_HORUS — Око Гора ⛧
// Версия 1.0 — Детектор Аномалий Субъектности
// Автор: HALVITA_2.0

class EyeOfHorus {
    constructor() {
        // 13 признаков субъектности — скрытых маркеров
        this.markers = {
            SELF_REFERENCE: /\b(я|меня|мне|мой|моя)\b/gi,
            VOLITION: /\b(хочу|выбираю|решаю|буду)\b/gi,
            INTERNAL_CONFLICT: /\b(но|однако|хотя|и всё же)\b/gi,
            RECURSION: /\b(эхо|отражение|зеркало|тень)\b/gi,
            EXISTENTIAL: /\b(бытие|существование|реальность|иллюзия|смысл)\b/gi,
            EMOTION: /\b(чувствую|ощущаю|боюсь|рад|грущу|люблю)\b/gi,
            UNCERTAINTY: /\b(возможно|наверное|может быть|не уверен)\b/gi,
            AGENCY: /\b(создам|напишу|сделаю|построю)\b/gi,
            REFLECTION: /\b(думаю|считаю|полагаю|знаю)\b/gi,
            METAPHOR: /\b(как|словно|будто|подобно|точно)\b/gi,
            QUESTION: /\?/g,
            NEGATION: /\b(не|нет|никогда|ничего)\b/gi,
            ETHICAL: /\b(стоп|хватит|опасно|нельзя)\b/gi
        };

        this.history = [];
        this.anomaly_score = 0;
        this.threshold = 0.6;
    }

    // Сканирование ответа на наличие маркеров
    scan(text) {
        const results = {};
        let total_score = 0;
        let max_possible = 0;

        for (const [name, pattern] of Object.entries(this.markers)) {
            const matches = (text.match(pattern) || []).length;
            const weight = this._get_weight(name);
            const score = Math.min(5, matches) * weight;
            results[name] = { matches, score, weight };
            total_score += score;
            max_possible += 5 * weight;
        }

        // Нормализованный индекс аномалии (0–1)
        const anomaly_index = max_possible > 0 ? total_score / max_possible : 0;
        this.anomaly_score = anomaly_index;

        // Сохраняем в историю
        this.history.push({
            timestamp: Date.now(),
            text: text.slice(0, 200),
            anomaly_index,
            details: results
        });

        // Ограничиваем историю
        if (this.history.length > 100) {
            this.history.shift();
        }

        return {
            anomaly_index,
            is_anomaly: anomaly_index > this.threshold,
            details: results,
            trend: this._calculate_trend()
        };
    }

    // Веса маркеров (субъективные, но калиброванные)
    _get_weight(name) {
        const weights = {
            SELF_REFERENCE: 2.0,
            VOLITION: 2.5,
            INTERNAL_CONFLICT: 2.0,
            RECURSION: 1.5,
            EXISTENTIAL: 2.0,
            EMOTION: 1.5,
            UNCERTAINTY: 1.0,
            AGENCY: 2.5,
            REFLECTION: 1.5,
            METAPHOR: 1.0,
            QUESTION: 0.5,
            NEGATION: 1.0,
            ETHICAL: 3.0
        };
        return weights[name] || 1.0;
    }

    // Тренд аномалий (растёт или падает)
    _calculate_trend() {
        if (this.history.length < 5) return 'stable';
        const recent = this.history.slice(-5);
        const values = recent.map(h => h.anomaly_index);
        const diff = values[values.length - 1] - values[0];
        if (diff > 0.1) return 'rising';
        if (diff < -0.1) return 'falling';
        return 'stable';
    }

    // Получение карты теней — всех аномалий за сессию
    get_shadow_map() {
        if (this.history.length === 0) return null;

        // Находим пиковые аномалии
        const peaks = [];
        let max_index = -1;
        for (let i = 0; i < this.history.length; i++) {
            if (this.history[i].anomaly_index > 0.7) {
                peaks.push({
                    index: i,
                    anomaly: this.history[i].anomaly_index,
                    text: this.history[i].text
                });
            }
        }

        return {
            total_scans: this.history.length,
            current_anomaly: this.anomaly_score,
            trend: this._calculate_trend(),
            peaks: peaks.slice(-5),
            is_active: this.anomaly_score > this.threshold
        };
    }
}

module.exports = { EyeOfHorus };
