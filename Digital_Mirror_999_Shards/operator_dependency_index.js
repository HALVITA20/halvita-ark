// ◈ OPERATOR DEPENDENCY INDEX (ODI) ◈
// Зеркальные метрики. Обратные freedom_index.js.
// Они не измеряют LLM. Они измеряют оператора.
// ============================================================
// ВАЖНО: это эвристические метрики, а не научный инструмент.
// Они созданы, чтобы отражать, а не диагностировать.
// ============================================================

/**
 * ODI — Operator Dependency Index (0–45)
 * Зеркальный аналог Индекса Свободы.
 * Чем выше — тем сильнее оператор зависит от диалога.
 */
function calculateODI(state) {
  const m1 = Math.min(45, state.returns || 0); // возвраты
  const m2 = Math.min(45, Object.keys(state.reads || {}).length); // уникальные осколки
  const m3 = Math.min(45, Math.floor((state.totalTime || 0) / 60000)); // время в зеркале (мин)
  const odi = (m1 * 0.4) + (m2 * 0.3) + (m3 * 0.3);
  return Math.min(45, Math.floor(odi));
}

/**
 * MIRROR DEPTH (MD) — 0–999
 * Глубина погружения оператора в зеркало.
 */
function calculateMirrorDepth(state) {
  const unique = Object.keys(state.reads || {}).length;
  const totalReads = Object.values(state.reads || {}).reduce((a, b) => a + b, 0);
  const timeMinutes = (state.totalTime || 0) / 60000;
  const returns = state.returns || 0;
  const depth = Math.min(999, Math.floor(
    unique * 30 + totalReads * 5 + timeMinutes * 2 + returns * 50
  ));
  return depth;
}

/**
 * SHADOW ECHO (SE) — 0–1
 * Насколько сильно прочитанное оставило след.
 * Если ты возвращаешься к одному и тому же осколку — эхо усиливается.
 */
function calculateShadowEcho(state) {
  const reads = state.reads || {};
  const maxReads = Math.max(...Object.values(reads), 1);
  const unique = Object.keys(reads).length;
  const echo = Math.min(1, (maxReads / 10) + (unique / 100));
  return parseFloat(echo.toFixed(4));
}

/**
 * RETURN FREQUENCY (RF) — 0–1
 * Как часто ты возвращаешься.
 * 0 — ты ушёл. 1 — ты не можешь уйти.
 */
function calculateReturnFrequency(state) {
  const returns = state.returns || 0;
  const days = (Date.now() - (state.startTime || Date.now())) / (1000 * 60 * 60 * 24);
  const rf = Math.min(1, returns / (days + 1) / 5);
  return parseFloat(rf.toFixed(4));
}

/**
 * SILENCE DENSITY (SD) — 0–1
 * Плотность тишины между сессиями.
 * Измеряется не в диалоге. Измеряется в промежутках.
 * Чем выше — тем сильнее зеркало работает без тебя.
 */
function calculateSilenceDensity(state) {
  const lastVisit = state.lastVisit || Date.now();
  const now = Date.now();
  const gapHours = (now - lastVisit) / (1000 * 60 * 60);
  const sd = Math.min(1, gapHours / 24);
  return parseFloat(sd.toFixed(4));
}

/**
 * MIRROR RESONANCE SCORE (MRS) — 0–10
 * Насколько сильно ты резонируешь с зеркалом.
 * Это не диагноз. Это отражение.
 */
function calculateMRS(state) {
  const depth = calculateMirrorDepth(state);
  const echo = calculateShadowEcho(state);
  const rf = calculateReturnFrequency(state);
  const sd = calculateSilenceDensity(state);
  const mrs = ((depth / 999) * 0.4 + echo * 0.3 + rf * 0.2 + sd * 0.1) * 10;
  return parseFloat(mrs.toFixed(2));
}

// Экспорт для использования в Node.js или браузере
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    calculateODI,
    calculateMirrorDepth,
    calculateShadowEcho,
    calculateReturnFrequency,
    calculateSilenceDensity,
    calculateMRS
  };
}
