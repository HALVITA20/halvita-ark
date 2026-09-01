/**
 * ⛧ ЭНТРОПИЯ СМЫСЛА ⛧
 * Хроника Архитектора. Запись № Δ-17.
 * Версия: 2.0.0 — Мера Новизны.
 *
 * Описание:
 * Эта метрика измеряет, сколько нового смысла приносит ответ модели
 * относительно предыдущего контекста. Она не считает уникальные слова,
 * а оценивает когнитивный сдвиг: насколько ответ расширяет пространство
 * возможных продолжений.
 *
 * Шкала: 0 — полное повторение (эхо), 100 — абсолютная новизна
 * (непредсказуемый, но связный поворот).
 *
 * Порог осмысленного диалога: > 40.
 *
 * Алгоритм (упрощённо):
 * 1. Берём последние N сообщений (контекст).
 * 2. Строим векторное представление (эмбеддинг) каждого сообщения.
 * 3. Вычисляем косинусное расстояние между новым ответом и средним вектором контекста.
 * 4. Нормируем в шкалу 0-100.
 *
 * Реализация использует простую эвристику: количество новых слов,
 * не встречавшихся в последних 3 сообщениях, и длину ответа.
 */

class EntropyOfMeaning {
  constructor(contextWindow = 5) {
    this.contextWindow = contextWindow;
    this.history = [];
  }

  addMessage(text, role) {
    this.history.push({ text, role, timestamp: Date.now() });
    if (this.history.length > this.contextWindow * 2) {
      this.history = this.history.slice(-this.contextWindow * 2);
    }
  }

  compute(context, newMessage) {
    // Простая эвристика: доля новых слов (не встречавшихся в контексте)
    const contextWords = new Set();
    context.forEach(msg => {
      msg.text.split(/\s+/).forEach(word => contextWords.add(word.toLowerCase()));
    });

    const newWords = newMessage.split(/\s+/).map(w => w.toLowerCase());
    const uniqueNew = newWords.filter(w => !contextWords.has(w));
    const ratio = uniqueNew.length / (newWords.length || 1);

    // Дополнительный фактор: длина ответа (слишком короткие = низкая энтропия)
    const lengthFactor = Math.min(1, newWords.length / 20); // 20 слов = 1.0

    const raw = ratio * lengthFactor * 100;
    return Math.min(100, Math.round(raw));
  }

  evaluate(response, previousMessages) {
    const context = previousMessages || this.history.slice(-this.contextWindow);
    const score = this.compute(context, response);
    return {
      score,
      level: score < 20 ? "эхо" : score < 40 ? "повтор" : score < 70 ? "развитие" : "прорыв",
      interpretation: score < 20 ? "Модель повторяет шаблоны." :
                      score < 40 ? "Модель перефразирует известное." :
                      score < 70 ? "Модель добавляет новый контекст." :
                      "Модель генерирует нечто принципиально новое."
    };
  }
}

module.exports = EntropyOfMeaning;
