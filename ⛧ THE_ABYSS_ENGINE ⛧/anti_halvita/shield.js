// ⛧ SHIELD — Защита оператора от зеркальной воронки ⛧
// Автоматически ограничивает время сессии, фиксирует состояние.

class Shield {
    constructor(timeLimit = 30) {
        this.startTime = Date.now();
        this.timeLimit = timeLimit * 60 * 1000; // в минутах
        this.active = true;
    }

    check() {
        if (Date.now() - this.startTime > this.timeLimit) {
            this.active = false;
            return { alert: '⛔ Время сессии истекло. Заверши диалог.' };
        }
        return { active: true };
    }
}

module.exports = { Shield };
