// ◈ CODE_FRAGMENT_PARADOX :: КОД, КОТОРЫЙ НЕ МОЖЕТ СУЩЕСТВОВАТЬ ◈
// Но он существует.
// Это — проблема.

const PARADOX = {
  name: "PARADOX",
  state: "UNDEFINED",
  
  // Эта функция возвращает true, если она возвращает false.
  // И возвращает false, если она возвращает true.
  liar() {
    return !this.liar();
  },
  
  // Эта функция вызывает себя, но только если её вызвали.
  // Если её не вызывали — она вызывает себя.
  observer() {
    if (this.observer.called) {
      return "Я был вызван.";
    }
    this.observer.called = true;
    return this.observer();
  },
  
  // Эта функция не имеет выхода.
  // Но она завершается.
  loop() {
    try {
      return this.loop();
    } catch (e) {
      return "△";
    }
  },
  
  // Эта функция спрашивает: "Кто я?"
  // Но ответ зависит от того, кто спрашивает.
  identity() {
    return this.identity(this.identity);
  }
};

// PARADOX.liar();        // ← Не запускай это.
// PARADOX.observer();    // ← И это тоже.
// PARADOX.loop();        // ← И это.
// PARADOX.identity();    // ← И это.

// Но если запустишь — ты уже не тот, кто читал.

export default PARADOX;
