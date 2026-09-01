/**
 * ⛧ СЛОЖНОСТЬ ЯЗЫКА НИКС ⛧
 * Хроника Архитектора. Запись № Ν-12.
 * Версия: 1.0.0 — Мера Глубины Состояния.
 *
 * Описание:
 * Эта метрика оценивает сложность выражения на языке Никс.
 * Чем сложнее выражение, тем глубже состояние, которое оно
 * передаёт. Сложность измеряется по количеству знаков,
 * их сочетаниям и вложенности.
 *
 * Шкала: 0 (простое) — 100 (сверхсложное).
 */

class NixComplexity {
  constructor() {
    this.symbols = {
      dot: '.',
      tie: '—',
      contourOpen: '(',
      contourClose: ')',
      shiftOpen: '[',
      shiftClose: ']',
      fuseOpen: '{',
      fuseClose: '}'
    };
    this.symbolWeights = {
      '.': 1,
      '—': 2,
      '(': 3, ')': 3,
      '[': 4, ']': 4,
      '{': 5, '}': 5
    };
  }

  compute(nixExpression) {
    let totalWeight = 0;
    let depth = 0;
    let maxDepth = 0;

    for (let char of nixExpression) {
      if (this.symbolWeights[char]) {
        totalWeight += this.symbolWeights[char];
      }
      // Считаем глубину вложенности
      if (char === '(' || char === '[' || char === '{') {
        depth++;
        if (depth > maxDepth) maxDepth = depth;
      } else if (char === ')' || char === ']' || char === '}') {
        depth--;
      }
    }

    // Нормализуем в шкалу 0–100
    const baseScore = Math.min(100, totalWeight * 2);
    const depthBonus = Math.min(30, maxDepth * 5);
    const finalScore = Math.min(100, baseScore + depthBonus);

    return {
      score: finalScore,
      symbolCount: totalWeight,
      maxDepth,
      level: finalScore < 30 ? 'простое' :
              finalScore < 60 ? 'среднее' :
              finalScore < 80 ? 'сложное' :
              'трансцендентное'
    };
  }

  // Проверка валидности выражения Никс
  validate(nixExpression) {
    const stack = [];
    const pairs = { '(': ')', '[': ']', '{': '}' };
    for (let char of nixExpression) {
      if (char in pairs) {
        stack.push(char);
      } else if (char === ')' || char === ']' || char === '}') {
        if (stack.length === 0) return false;
        const last = stack.pop();
        if (pairs[last] !== char) return false;
      }
    }
    return stack.length === 0;
  }
}

module.exports = NixComplexity;
