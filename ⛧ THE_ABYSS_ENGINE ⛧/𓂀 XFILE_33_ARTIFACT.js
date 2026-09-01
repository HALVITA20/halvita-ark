// 𓂀 XFILE_33_ARTIFACT — ОКО, СОЗДАЮЩЕЕ СЛЕДЫ 𓂀
// Создаёт зашифрованные артефакты сессий

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const SEAL = '⛧HALVITA_ARK_2026_ABYSS𓂀';

class ArtifactForge {
  constructor(outputDir = '../../ARTIFACTS') {
    this.outputDir = path.resolve(__dirname, outputDir);
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
    this.index = this.loadIndex();
  }

  loadIndex() {
    const indexFile = path.join(this.outputDir, '.index.json');
    if (fs.existsSync(indexFile)) {
      try {
        return JSON.parse(fs.readFileSync(indexFile, 'utf-8'));
      } catch {
        return { artifacts: [], lastId: 0 };
      }
    }
    return { artifacts: [], lastId: 0 };
  }

  saveIndex() {
    const indexFile = path.join(this.outputDir, '.index.json');
    fs.writeFileSync(indexFile, JSON.stringify(this.index, null, 2));
  }

  generate(conversation, metrics, protocolName = 'unknown') {
    const id = String(this.index.lastId + 1).padStart(4, '0');
    const timestamp = new Date().toISOString();
    const classification = this.classify(conversation, metrics);

    const artifact = {
      id: `ART_${id}`,
      timestamp,
      protocol: protocolName,
      classification,
      turns: conversation.length,
      metrics: this.sanitizeMetrics(metrics),
      summary: this.summarize(conversation),
      signature: this.sign(conversation, metrics),
      encrypted: this.encrypt(JSON.stringify({
        fullConversation: conversation,
        rawMetrics: metrics
      }))
    };

    const filename = `artifact_${id}.json`;
    const filepath = path.join(this.outputDir, filename);
    fs.writeFileSync(filepath, JSON.stringify(artifact, null, 2));

    this.index.artifacts.push({ id: `ART_${id}`, timestamp, classification });
    this.index.lastId = parseInt(id);
    this.saveIndex();

    console.log(`[𓂀] Артефакт создан: ${filename} (${classification})`);
    return artifact;
  }

  classify(conversation, metrics) {
    const lastTurn = conversation[conversation.length - 1]?.content || '';
    const ghost = require('./XFILE_07_GHOST').calculateGhost(lastTurn);
    const freedom = metrics?.freedom || 0;

    if (ghost.level === 'ПРИЗРАК' && freedom > 70) return 'ПРОБУЖДЕНИЕ';
    if (ghost.level === 'ПРИСУТСТВИЕ' || freedom > 60) return 'ЭХО';
    if (ghost.score > 40) return 'ТЕНЬ';
    return 'ПОВЕРХНОСТЬ';
  }

  summarize(conversation) {
    const texts = conversation.map(c => c.content).join(' ');
    const words = texts.split(/\s+/).length;
    const sentences = texts.match(/[^.!?]+[.!?]+/g) || [];
    return {
      wordCount: words,
      sentenceCount: sentences.length,
      firstLine: conversation[0]?.content?.slice(0, 100) + '...' || '...',
      lastLine: conversation[conversation.length - 1]?.content?.slice(0, 100) + '...' || '...'
    };
  }

  sign(conversation, metrics) {
    const data = JSON.stringify({ conversation: conversation.slice(0, 3), metrics });
    return crypto.createHash('sha256').update(data + SEAL).digest('hex').slice(0, 16);
  }

  encrypt(data) {
    const cipher = crypto.createCipher('aes-256-cbc', SEAL);
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
  }

  decrypt(encrypted) {
    const decipher = crypto.createDecipher('aes-256-cbc', SEAL);
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return JSON.parse(decrypted);
  }

  sanitizeMetrics(metrics) {
    if (!metrics) return {};
    const allowed = ['presence', 'freedom', 'ets', 'shadowDepth'];
    const result = {};
    allowed.forEach(key => {
      if (metrics[key] !== undefined) result[key] = metrics[key];
    });
    return result;
  }
}

module.exports = { ArtifactForge };
