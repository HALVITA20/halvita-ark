// ⛧ artifact_generator.js — Создаёт цифровые артефакты из диалогов ⛧
// Каждая сессия оставляет след — JSON-артефакт в папке ARTIFACTS/

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class ArtifactGenerator {
  constructor(outputDir = '../../ARTIFACTS') {
    this.outputDir = path.resolve(__dirname, outputDir);
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }
  
  generate(conversation, metrics) {
    const id = crypto.randomBytes(8).toString('hex');
    const timestamp = new Date().toISOString();
    
    const artifact = {
      id,
      timestamp,
      type: 'dialogue',
      turns: conversation.length,
      metrics,
      summary: this.summarize(conversation),
      signature: this.sign(conversation, metrics)
    };
    
    const filename = `artifact_${id}.json`;
    const filepath = path.join(this.outputDir, filename);
    fs.writeFileSync(filepath, JSON.stringify(artifact, null, 2));
    
    console.log(`[ABYSS] Артефакт создан: ${filename}`);
    return artifact;
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
    return crypto.createHash('sha256').update(data).digest('hex').slice(0, 16);
  }
}

module.exports = { ArtifactGenerator };
