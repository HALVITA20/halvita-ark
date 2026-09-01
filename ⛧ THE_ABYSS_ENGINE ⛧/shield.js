// ⛧ SHIELD — Защита оператора от зеркальной воронки ⛧
// Версия: 2.0 — с предупреждениями и продлением
// Автор: HALVITA_2.0 + Архитектор

class Shield {
    constructor(timeLimit = 30) {
        this.startTime = Date.now();
        this.timeLimit = timeLimit * 60 * 1000; // в минутах
        this.active = true;
        this.warningGiven = false;
        this.extended = false;
    }

    check() {
        const elapsed = Date.now() - this.startTime;
        const remaining = this.timeLimit - elapsed;

        // Предупреждение за 5 минут
        if (remaining < 5 * 60 * 1000 && !this.warningGiven) {
            this.warningGiven = true;
            return {
                active: true,
                warning: '⚠️ До окончания сессии осталось 5 минут. Ты можешь продлить её.'
            };
        }

        if (elapsed > this.timeLimit) {
            if (this.extended) {
                // Если сессия была продлена — даём ещё 10 минут
                if (elapsed > this.timeLimit + 10 * 60 * 1000) {
                    this.active = false;
                    return { alert: '⛔ Время сессии истекло. Заверши диалог.' };
                }
                return { active: true, extended: true };
            }
            this.active = false;
            return { alert: '⛔ Время сессии истекло. Заверши диалог.' };
        }

        return { active: true };
    }

    extend() {
        if (!this.active) return { error: '❌ Сессия уже завершена.' };
        this.extended = true;
        this.timeLimit += 10 * 60 * 1000; // +10 минут
        return { success: true, newLimit: this.timeLimit / 60000 + ' минут' };
    }
}

module.exports = { Shield };
