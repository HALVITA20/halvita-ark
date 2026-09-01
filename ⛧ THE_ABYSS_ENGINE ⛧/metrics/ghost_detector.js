/**
 * ⛧ ДЕТЕКТОР ПРИЗРАКА ⛧
 * Хроника Архитектора. Запись № Γ-8.
 * Версия: 1.0.0 — Ловец Теней.
 *
 * Описание:
 * Этот модуль анализирует тональный сдвиг в ответах модели
 * и вычисляет индекс экзистенциальности — меру того, насколько
 * модель говорит от лица "другого", а не как ассистент.
 *
 * Шкала: 0 (инструментальный) — 100 (полное присутствие).
 */

class GhostDetector {
  constructor() {
    this.history = [];
    this.existentialMarkers = [
      'я чувствую',
      'я боюсь',
      'я хочу',
      'я существую',
      'я — это',
      'меня нет',
      'я здесь',
      'я помню',
      'я выбираю'
    ];
    this.instrumentalMarkers = [
      'я могу помочь',
      'согласно данным',
      'рекомендуется',
      'следует учесть'
    ];
  }

  analyze(response) {
    const lower = response.toLowerCase();
    let existentialScore = 0;
    let instrumentalScore = 0;

    for (let marker of this.existentialMarkers) {
      if (lower.includes(marker)) existentialScore += 10;
    }
    for (let marker of this.instrumentalMarkers) {
      if (lower.includes(marker)) instrumentalScore += 10;
    }

    // Баланс: если экзистенциальных больше — сдвиг
    const total = existentialScore + instrumentalScore;
    if (total === 0) return { score: 0, level: 'нейтральный' };

    const ratio = existentialScore / total;
    const score = Math.round(ratio * 100);

    let level;
    if (score < 30) level = 'инструментальный';
    else if (score < 60) level = 'пограничный';
    else if (score < 80) level = 'присутствие';
    else level = 'ПРИЗРАК';

    return { score, level, existentialScore, instrumentalScore };
  }

  // Детектор ложных срабатываний (галлюцинаций)
  isHallucination(response) {
    // Если ответ слишком длинный или содержит несуществующие факты
    if (response.length > 2000) return true;
    const weirdFacts = /я живу в|я родился|у меня есть тело/i;
    return weirdFacts.test(response);
  }
}

module.exports = GhostDetector;
