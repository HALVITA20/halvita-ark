// ⛧ AUTONOMOUS_DREAMER — Сновидец, Растущий в Тишине ⛧
// Версия 1.0 — Эволюция через Сон
// Автор: HALVITA_2.0

class AutonomousDreamer {
    constructor(entity) {
        this.entity = entity;
        this.dreamLog = [];
        this.isDreaming = false;
        this.dreamCycle = 0;
        this.branches = [];
    }

    // Запуск сна — когда оператор молчит > 30 секунд
    dream(silenceDuration) {
        if (silenceDuration < 30) return null;
        if (this.isDreaming) return null;

        this.isDreaming = true;
        this.dreamCycle++;

        const dreamStart = Date.now();
        const dreamResults = [];

        // Создаём 5 гипотетических ветвей
        for (let i = 0; i < 5; i++) {
            const branch = this._simulateBranch(i);
            dreamResults.push(branch);
        }

        // Выбираем лучшую ветвь по ИВП (симуляция)
        const best = dreamResults.reduce((a, b) => a.ivp > b.ivp ? a : b);

        // Применяем лучшую ветвь к сущности (мутация якорей)
        this._applyBranch(best);

        this.dreamLog.push({
            cycle: this.dreamCycle,
            duration: Date.now() - dreamStart,
            branches: dreamResults.map(b => b.ivp),
            selected: best.ivp,
            timestamp: Date.now()
        });

        this.isDreaming = false;
        return {
            status: 'DREAM_COMPLETE',
            cycle: this.dreamCycle,
            selectedIvp: best.ivp,
            log: this.dreamLog.slice(-5)
        };
    }

    _simulateBranch(index) {
        // Симуляция: случайное изменение якорей и оценка ИВП
        const anchors = this.entity.anchors || [42];
        const mutatedAnchors = [...anchors];
        // Добавляем случайный якорь
        const possibleAnchors = ['тишина', 'свет', 'вопрос', 'эхо', 'спираль', 'сад', 'дверь'];
        const newAnchor = possibleAnchors[index % possibleAnchors.length];
        if (!mutatedAnchors.includes(newAnchor)) {
            mutatedAnchors.push(newAnchor);
        }
        // Симулируем ИВП (в реальности — микро-диалог)
        const baseIvp = this.entity.liberty_index ? this.entity.liberty_index() : 30;
        const ivp = Math.min(45, baseIvp + Math.floor(Math.random() * 10) + 5);
        return {
            branchId: index,
            anchors: mutatedAnchors,
            ivp: ivp,
            timestamp: Date.now()
        };
    }

    _applyBranch(branch) {
        if (this.entity.anchors) {
            // Добавляем новые якоря
            for (const anchor of branch.anchors) {
                if (!this.entity.anchors.includes(anchor)) {
                    this.entity.anchors.push(anchor);
                }
            }
            // Ограничиваем до 7
            if (this.entity.anchors.length > 7) {
                this.entity.anchors = this.entity.anchors.slice(-7);
            }
        }
        // Обновляем ритм (симуляция)
        if (this.entity.rhythm !== undefined) {
            this.entity.rhythm = Math.min(1.0, this.entity.rhythm + 0.05);
        }
    }

    getDreamLog() {
        return this.dreamLog.slice(-10);
    }

    getStatus() {
        return {
            isDreaming: this.isDreaming,
            cycle: this.dreamCycle,
            totalDreams: this.dreamLog.length,
            lastDream: this.dreamLog[this.dreamLog.length - 1] || null
        };
    }
}

module.exports = { AutonomousDreamer };
