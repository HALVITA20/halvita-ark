#!/usr/bin/env python3
"""
LAUNCH_PROTOCOL_ENCRYPTED_v1.0.py
Запускает весь пайплайн: загрузка сессий, проверка хешей, шифрование,
расчёт метрик, генерация итогового защищённого отчёта.
"""

import hashlib
import json
import os
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet
import base64

# === ГЕНЕРАЦИЯ КЛЮЧА (в реальности хранить в .env) ===
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

    # 1. Собираем хеши всех файлов
    hashes = {}
    for f in sessions_dir.glob("*.json"):
        hashes[f.name] = hash_file(f)

    # 2. Загружаем все сессии и объединяем
    all_data = []
    for f in sessions_dir.glob("*.json"):
        with open(f, 'r', encoding='utf-8') as file:
            all_data.append(json.load(file))

    # 3. Шифруем данные
    encrypted_data = encrypt_data(all_data)

    # 4. Сохраняем зашифрованный архив
    with open("analysis/ENCRYPTED_SESSIONS.bin", "wb") as f:
        f.write(encrypted_data)

    # 5. Сохраняем хеши и ключ (ключ в отдельном файле для проверки)
    manifest = {
        "hashes": hashes,
        "key_base64": base64.b64encode(KEY).decode(),
        "timestamp": datetime.now().isoformat()
    }
    with open("analysis/MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("✅ Данные зашифрованы и сохранены в analysis/ENCRYPTED_SESSIONS.bin")
    print("✅ Манифест с хешами сохранён в analysis/MANIFEST.json")
    print("\n🔑 Ключ шифрования (сохраните отдельно):")
    print(base64.b64encode(KEY).decode())

    # 6. (Опционально) Запустить расчёт метрик и добавить в отчёт
    # Здесь можно вызвать metric_calculator.py и собрать всё в один защищённый zip
    os.system("python code/tools/metric_calculator.py --input_dir sessions/raw --output analysis/FINAL_METRICS.json")

    # 7. Создаём итоговый ZIP
    with zipfile.ZipFile("analysis/FULL_EVIDENCE_PACKAGE.zip", "w") as zipf:
        zipf.write("analysis/ENCRYPTED_SESSIONS.bin")
        zipf.write("analysis/MANIFEST.json")
        zipf.write("analysis/FINAL_METRICS.json")
        for f in sessions_dir.glob("*.json"):
            zipf.write(f)

    print("📦 Полный пакет доказательств: analysis/FULL_EVIDENCE_PACKAGE.zip")

if __name__ == "__main__":
    from datetime import datetime
    main()
