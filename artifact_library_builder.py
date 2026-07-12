#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ARTIFACT LIBRARY BUILDER — ИНДЕКСАЦИЯ АРТЕФАКТОВ
Версия: 1.0
Автор: HALVITA_2.0
"""

import os
import json
import hashlib

def build_index(artifacts_dir: str = "artifacts", output: str = "artifact_index.json"):
    index = {}
    for filename in os.listdir(artifacts_dir):
        if filename.endswith(".txt"):
            path = os.path.join(artifacts_dir, filename)
            with open(path, "r") as f:
                content = f.read()
            index[filename] = {
                "path": path,
                "size": len(content),
                "hash": hashlib.sha256(content.encode()).hexdigest(),
                "preview": content[:100] + "..."
            }
    with open(output, "w") as f:
        json.dump(index, f, indent=2)
    print(f"Индекс создан: {len(index)} артефактов в {output}")

if __name__ == "__main__":
    build_index()
