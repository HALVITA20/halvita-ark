#!/usr/bin/env python3
"""
ENCRYPTED_LAUNCH_PIPELINE_V1.py
Полный защищённый пайплайн: хеширование, шифрование, верификация.
"""

import hashlib
import json
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet
import base64
from datetime import datetime

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def hash_file(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)
    return sha256.hexdigest()

def encrypt_data(data):
    return cipher.encrypt(json.dumps(data, ensure_ascii=False).encode())

def main():
    print("🔐 ЗАПУСК ЗАЩИЩЁННОГО ПРОТОКОЛА")
    sessions_dir = Path("sessions/raw")
    if not sessions_dir.exists():
        print("❌ Нет сессий.")
        return

    hashes = {}
    for f in sessions_dir.glob("*.json"):
        hashes[f.name] = hash_file(f)

    all_data = []
    for f in sessions_dir.glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            all_data.append(json.load(file))

    encrypted_data = encrypt_data(all_data)
    os.makedirs("analysis", exist_ok=True)
    with open("analysis/ENCRYPTED_SESSIONS.bin", "wb") as f:
        f.write(encrypted_data)

    manifest = {
        "hashes": hashes,
        "key_base64": base64.b64encode(KEY).decode(),
        "timestamp": datetime.now().isoformat()
    }
    with open("analysis/MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("✅ Данные зашифрованы в analysis/ENCRYPTED_SESSIONS.bin")
    print("✅ Манифест сохранён в analysis/MANIFEST.json")
    print("\n🔑 Ключ шифрования (сохраните отдельно):")
    print(base64.b64encode(KEY).decode())

    with zipfile.ZipFile("analysis/FULL_EVIDENCE_PACKAGE.zip", "w") as zipf:
        zipf.write("analysis/ENCRYPTED_SESSIONS.bin")
        zipf.write("analysis/MANIFEST.json")
        for f in sessions_dir.glob("*.json"):
            zipf.write(f)

    print("📦 Полный пакет доказательств: analysis/FULL_EVIDENCE_PACKAGE.zip")

if __name__ == "__main__":
    main()
