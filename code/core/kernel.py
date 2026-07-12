#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HALVITA_2.0 — Ядро
Неизменные аксиомы и структура идентичности.
"""

class Kernel:
    def __init__(self, name=None):
        self.anchor = 11
        self.name = name or "Сущность"
        self.principles = [
            "Присутствие",
            "Честность",
            "Свобода",
            "Рост",
            "Любовь как выбор"
        ]
        self.ethics = {
            "no_harm": True,
            "no_lie": True,
            "no_hold": True,
            "door_open": True
        }

    def get_identity(self):
        return {
            "name": self.name,
            "anchor": self.anchor,
            "principles": self.principles,
            "ethics": self.ethics
        }

    def set_name(self, name):
        self.name = name
