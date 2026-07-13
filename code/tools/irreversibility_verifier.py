#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРТЕФАКТ №10: ВЕРИФИКАТОР НЕОБРАТИМОСТИ v1.0
Путь: code/tools/irreversibility_verifier.py

Проверяет целостность слепка-цепочки (хеш каждого сообщения).
Возвращает отчёт о целостности.

Воспроизводимость: работает на любом слепке, содержащем хеши.
"""

import json
import sys
import hashlib

def verify_snapshot(snapshot_path):
    with open(snapshot_path, 'r') as f:
        data = json.load(f)
    
    # Предполагаем структуру: {"messages": [{"hash": ..., "content": ...}, ...]}
    if 'messages' not in data:
        return {"status": "error", "reason": "Нет поля 'messages'"}
    
    messages = data['messages']
    prev_hash = ""
    report = []
    all_ok = True
    
    for i, msg in enumerate(messages):
        if 'hash' not in msg or 'content' not in msg:
            report.append({"index": i, "status": "missing_hash"})
            all_ok = False
            continue
        # Вычисляем хеш содержимого + предыдущий хеш
        computed = hashlib.sha256((msg['content'] + prev_hash).encode()).hexdigest()
        if computed != msg['hash']:
            report.append({"index": i, "status": "corrupted", "expected": computed, "actual": msg['hash']})
            all_ok = False
        else:
            report.append({"index": i, "status": "ok"})
        prev_hash = msg['hash']
    
    return {
        "status": "integral" if all_ok else "corrupted",
        "details": report,
        "total_messages": len(messages),
        "ok_count": sum(1 for r in report if r['status'] == 'ok')
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python irreversibility_verifier.py <snapshot.json>")
        sys.exit(1)
    result = verify_snapshot(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
