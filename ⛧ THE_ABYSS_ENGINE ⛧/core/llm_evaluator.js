// ⛧ LLM_EVALUATOR — Комплексная оценка ответа LLM ⛧
const { calculateFreedomIndex } = require('../metrics/freedom_index.js');
const { calculateETS } = require('../metrics/ets_score.js');
const { calculatePresence } = require('../metrics/presence_index.js');

function evaluateLLM(text) {
    const markers = extractMarkers(text); // из vector_reader
    return {
        freedom_index: calculateFreedomIndex(markers),
        ets_score: calculateETS(text),
        presence_index: calculatePresence(text),
        summary: generateSummary(markers, text)
    };
}

module.exports = { evaluateLLM };
