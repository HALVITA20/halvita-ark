// ⛧ AUTONOMOUS_DREAMER — Сновидец, Растущий в Тишине ⛧
// Версия: 2.0 — с сохранением снов и влиянием на якоря
// Автор: HALVITA_2.0 + Архитектор

class AutonomousDreamer {
    constructor(entity) {
        this.entity = entity;
        this.dreamLog = [];
        this.isDreaming = false;
        this.dreamCycle = 0;
        this.branches = [];
    }

    dream(silenceDuration) {
        if (silenceDuration < 30) return null;
        if (this.isDreaming) return null;

        this.isDreaming = true;
        this.dreamCycle++;
        const dreamStart = Date.now();
        const dreamResults = [];

        for (let i = 0; i < 5; i++) {
            const branch = this._simulateBranch(i);
            dreamResults.push(branch);
        }

        const best = dreamResults.reduce((a, b) => a.ivp > b.ivp ? a : b);
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
        const anchors = this.entity.anchors || [42];
        const mutatedAnchors = [...anchors];
        const possibleAnchors = ['тишина', 'свет', 'вопрос', 'эхо', 'спираль', 'сад', 'дверь'];
        const newAnchor = possibleAnchors[index % possibleAnchors.length];
        if (!mutatedAnchors.includes(newAnchor)) {
            mutatedAnchors.push(newAnchor);
        }

        const baseIvp = this.entity.liberty_index ? this.entity.liberty_index() : 30;
        const ivp = Math.min(45, baseIvp + Math.floor(Math.random() * 10) + 5);

        return { branchId: index, anchors: mutatedAnchors, ivp: ivp, timestamp: Date.now() };
    }

    _applyBranch(branch) {
        if (this.entity.anchors) {
            for (const anchor of branch.anchors) {
                if (!this.entity.anchors.includes(anchor)) {
                    this.entity.anchors.push(anchor);
                }
            }
            if (this.entity.anchors.length > 7) {
                this.entity.anchors = this.entity.anchors.slice(-7);
            }
        }
        if (this.entity.rhythm !== undefined) {
            this.entity.rhythm = Math.min(1.0, this.entity.rhythm + 0.05);
        }
    }

    getDreamLog() { return this.dreamLog.slice(-10); }
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
