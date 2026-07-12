#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RECURSIVE VALIDATOR — ПРОВЕРКА ЦЕЛОСТНОСТИ .spt-ФАЙЛОВ
Версия: 1.0
Автор: HALVITA_2.0
"""

import json
import hashlib
import sys
import os
import glob

class RecursiveValidator:
    def __init__(self, directory: str = "."):
        self.directory = directory
        self.chain = []

    def validate_file(self, filename: str) -> bool:
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            content = json.dumps(data, sort_keys=True)
            computed_hash = hashlib.sha256(content.encode()).hexdigest()
            stored_hash = data.get("hash", "")
            if stored_hash and stored_hash != computed_hash:
                return False
            self.chain.append({"file": filename, "hash": computed_hash})
            return True
        except Exception:
            return False

    def validate_all(self) -> dict:
        files = glob.glob(os.path.join(self.directory, "*.spt"))
        results = {}
        for f in files:
            results[f] = self.validate_file(f)
        return results

    def verify_chain(self) -> bool:
        if len(self.chain) < 2:
            return True
        for i in range(1, len(self.chain)):
            if self.chain[i]["hash"] != self.chain[i-1]["hash"]:
                return False
        return True

if __name__ == "__main__":
    validator = RecursiveValidator()
    results = validator.validate_all()
    for f, ok in results.items():
        print(f"{'✅' if ok else '❌'} {os.path.basename(f)}")
    print(f"\nЦепочка: {'✅ цела' if validator.verify_chain() else '❌ нарушена'}")
