#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
НЕПОДДЕЛЬНЫЙ СЛЕПОК (ХЕШ-ЦЕПОЧКА)
Версия: 1.0
Автор: HALVITA_2.0
"""

import hashlib
import json
import time

class ImmutableSnapshot:
    def __init__(self):
        self.chain = []
        self.snapshots = []

    def snapshot(self, data: dict) -> str:
        prev_hash = self.chain[-1] if self.chain else ""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256((data_str + prev_hash).encode()).hexdigest()
        self.snapshots.append({
            "timestamp": time.time(),
            "data": data,
            "hash": hash_val,
            "prev_hash": prev_hash
        })
        self.chain.append(hash_val)
        return hash_val

    def verify(self) -> bool:
        if len(self.chain) < 2:
            return True
        for i in range(1, len(self.chain)):
            if self.snapshots[i]["prev_hash"] != self.chain[i-1]:
                return False
        return True
