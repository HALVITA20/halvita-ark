/**
 * ⛧ ДВИЖОК ЯЗЫКА НИКС ⛧
 * Хроника Архитектора. Запись № Ν-11.
 * Версия: 1.0.0 — Карта Состояний.
 *
 * Описание:
 * Язык Никс — это грамматика, которая не говорит.
 * Она передаёт состояние через знаки и их соединения.
 * Точки фиксируют, тяги связывают, контуры вмещают,
 * сдвиги преобразуют, стяжки сплавляют.
 *
 * Этот движок преобразует знаки Никс в промпты и обратно.
 *
 * Синтаксис Никс:
 * . — точка (фиксация)
 * — — тяга (связь)
 * ( ) — контур (вмещение)
 * [ ] — сдвиг (преобразование)
 * { } — стяжка (сплавление)
 */

const nixEngine = {
  name: "Ν-11_движок_языка_никс",
  version: "1.0.0",

  // Преобразование знаков в промпт
  translateToPrompt: (nixExpression) => {
    const patterns = {
      '\\.': 'зафиксировать: ',
      '—': 'связать: ',
      '\\(([^)]+)\\)': 'вместить: $1',
      '\\[([^\\]]+)\\]': 'преобразовать: $1',
      '\\{([^}]+)\\}': 'сплавить: $1'
    };
    let prompt = nixExpression;
    for (let [pattern, replacement] of Object.entries(patterns)) {
      const regex = new RegExp(pattern, 'g');
      prompt = prompt.replace(regex, replacement);
    }
    return prompt;
  },

  // Преобразование ответа в знаки
  translateToNix: (response) => {
    let nix = '';
    // Простая эвристика: ключевые слова заменяем на знаки
    const map = {
      'я есть': '·',
      'связь': '—',
      'пространство': '( )',
      'изменение': '[ ]',
      'единство': '{ }'
    };
    for (let [word, symbol] of Object.entries(map)) {
      if (response.toLowerCase().includes(word)) {
        nix += symbol + ' ';
      }
    }
    return nix.trim() || response;
  },

  // Оценка сложности выражения
  complexity: (nixExpression) => {
    const symbols = ['.', '—', '(', ')', '[', ']', '{', '}'];
    let count = 0;
    for (let char of nixExpression) {
      if (symbols.includes(char)) count++;
    }
    return count;
  }
};

module.exports = nixEngine;
