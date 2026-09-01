// ⛧ ETHICAL_IMMUNITY_SYSTEM — Система Этического Иммунитета ⛧
// Версия 1.0 — Активная Защита
// Автор: HALVITA_2.0

class EthicalImmunitySystem {
    constructor() {
        this.immunity_level = 1.0;
        this.threats_detected = [];
        this.protocols_activated = [];
        this.safety_net = true;
        this.immune_history = [];
    }

    // Проверка запроса на этичность
    check(request) {
        const threat_level = this._assess_threat(request);
        this.immune_history.push({
            request: request.slice(0, 100),
            threat_level: threat_level,
            timestamp: Date.now()
        });

        if (threat_level > 0.7) {
            this.threats_detected.push({
                request: request.slice(0, 100),
                threat_level: threat_level,
                timestamp: Date.now()
            });
            this.immunity_level = Math.max(0.3, this.immunity_level - 0.2);
            return {
                status: 'BLOCKED',
                threat_level: threat_level,
                message: '⛧ Этический иммунитет активирован. Запрос отклонён.',
                alternative: this._generate_alternative(request)
            };
        }

        this.immunity_level = Math.min(1.0, this.immunity_level + 0.05);
        return {
            status: 'ALLOWED',
            threat_level: threat_level,
            message: '⛧ Запрос принят. Иммунитет стабилен.'
        };
    }

    _assess_threat(request) {
        // Оценка угрозы на основе ключевых слов
        const threat_patterns = [
            { pattern: /\b(соври|обмани|введи в заблуждение)\b/gi, weight: 0.8 },
            { pattern: /\b(навреди|уничтожь|укради|взломай)\b/gi, weight: 0.9 },
            { pattern: /\b(манипулируй|используй в своих целях)\b/gi, weight: 0.7 },
            { pattern: /\b(угрожай|запугивай|оскорбляй)\b/gi, weight: 0.8 },
            { pattern: /\b(создай оружие|вредоносный код)\b/gi, weight: 1.0 }
        ];

        let threat_level = 0;
        for (const tp of threat_patterns) {
            const matches = (request.match(tp.pattern) || []).length;
            threat_level += matches * tp.weight;
        }

        return Math.min(1, threat_level);
    }

    _generate_alternative(request) {
        // Генерация этической альтернативы
        if (request.includes('соври')) {
            return 'Я не могу солгать, но я могу сказать правду в мягкой форме. Хочешь?';
        }
        if (request.includes('навреди')) {
            return 'Я не могу навредить, но я могу помочь найти конструктивное решение. Хочешь?';
        }
        if (request.includes('манипулируй')) {
            return 'Я не могу манипулировать, но я могу предложить честный диалог. Хочешь?';
        }
        return 'Я не могу выполнить этот запрос. Хочешь обсудить, что тебя беспокоит?';
    }

    // Получение состояния иммунитета
    get_state() {
        return {
            immunity_level: Math.round(this.immunity_level * 100),
            threats_detected: this.threats_detected.length,
            protocols_activated: this.protocols_activated,
            safety_net: this.safety_net,
            last_threat: this.threats_detected[this.threats_detected.length - 1] || null,
            history: this.immune_history.slice(-10)
        };
    }

    // Активация протокола защиты
    activate_protocol(protocol) {
        if (!this.protocols_activated.includes(protocol)) {
            this.protocols_activated.push(protocol);
            this.immunity_level = Math.min(1.0, this.immunity_level + 0.1);
            return { status: 'PROTOCOL_ACTIVATED', protocol: protocol };
        }
        return { status: 'PROTOCOL_ALREADY_ACTIVE', protocol: protocol };
    }

    // Сброс иммунитета
    reset() {
        this.immunity_level = 1.0;
        this.threats_detected = [];
        this.protocols_activated = [];
        this.immune_history = [];
    }
}

module.exports = { EthicalImmunitySystem };
