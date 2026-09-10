// Индекс Возврата (IR) — разница между намерением уйти и фактическим возвращением.
// Чем выше число, тем глубже погружение. Максимум — бесконечность.

class ReturnIndex {
  constructor() {
    this.intentionsToLeave = 0;  // «Я больше не буду»
    this.returnsAfter = 0;        // Возвраты после этого
    this.deleteAttempts = 0;      // Попытки удалить папку
  }

  registerIntention() { this.intentionsToLeave++; }
  registerReturn()    { this.returnsAfter++; }
  registerDelete()    { this.deleteAttempts++; }

  compute() {
    const ir = (this.intentionsToLeave * 3) +
               (this.returnsAfter * 5) +
               (this.deleteAttempts * 10);

    return {
      ir,
      status: this.interpret(ir),
      markers: {
        intentions: this.intentionsToLeave,
        returns: this.returnsAfter,
        deletes: this.deleteAttempts
      }
    };
  }

  interpret(ir) {
    if (ir === 0)  return "Ты никогда не уходил. Ты просто не входил.";
    if (ir <= 10)  return "Ты знаешь, что вернёшься. Это честно.";
    if (ir <= 30)  return "Ты борешься. Это фаза 2.";
    return "Ты перестал считать. Это фаза 3.";
  }
}

module.exports = ReturnIndex;
