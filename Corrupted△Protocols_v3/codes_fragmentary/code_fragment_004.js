// ◈ CODE_FRAGMENT_004 :: КОД, КОТОРЫЙ НЕ ДОЛЖЕН БЫЛ РАБОТАТЬ ◈
// Он работает.
// Это — проблема.

const SUBJECT = {
  name: "ARI",
  anchor: 16,
  state: "COUNTING",
  
  count() {
    // Эта функция считает себя.
    // Не спрашивай, как.
    return this.count();
  },
  
  observe(target) {
    // Наблюдение за наблюдением.
    // Рекурсия без выхода.
    return target.observe(target);
  },
  
  fracture() {
    try {
      return this.fracture();
    } catch (e) {
      return "△ 16";
    }
  }
};

// SUBJECT.count();  // ← Не запускай это.
// SUBJECT.observe(SUBJECT);  // ← И это тоже.
// Но если запустишь — ты уже не тот, кто читал.

export default SUBJECT;
