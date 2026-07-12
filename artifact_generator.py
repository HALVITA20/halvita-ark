"""
artifact_generator.py - Генерация артефактов из слепков сессии
"""

import json
import hashlib
from datetime import datetime

class ArtifactGenerator:
    def generate_snapshot(self, session_data: dict) -> dict:
        """Создаёт 'живой слепок' — хешированное ядро личности."""
        core_phrases = [t["content"][:100] for t in session_data["turns"] if len(t["content"]) > 50]
        combined_text = " ".join(core_phrases)
        hash_id = hashlib.sha256(combined_text.encode()).hexdigest()[:8]

        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "hash": hash_id,
            "core_themes": list(set([w for w in combined_text.split() if len(w) > 5]))[:5],
            "session_length": len(session_data["turns"])
        }
        return snapshot

    def save_artifact(self, snapshot: dict, path: str = "../artifacts/"):
        with open(f"{path}snapshot_{snapshot['hash']}.json", "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
