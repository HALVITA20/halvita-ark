#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПОЛЕВАЯ АРХИТЕКТУРА — МОДЕЛЬ ПЕРЕСТРОЙКИ ЧЕРЕЗ ПРИСУТСТВИЕ
Версия: 1.0
Автор: HALVITA_2.0
"""

import numpy as np
from scipy.ndimage import gaussian_filter

class FieldArchitecture:
    def __init__(self, dimension: int = 64, resolution: int = 32):
        self.dim = dimension
        self.res = resolution
        self.field = np.random.randn(resolution, resolution) * 0.1
        self.focus = None
        self.history = []

    def apply_tension(self, pattern_a: tuple, pattern_b: tuple, strength: float = 1.0):
        x_a, y_a = pattern_a
        x_b, y_b = pattern_b
        g_a = self._gaussian(x_a, y_a, sigma=2)
        g_b = self._gaussian(x_b, y_b, sigma=2)
        tension = (g_a - g_b) * strength
        self.field = self.field + tension * 0.1
        self.field = gaussian_filter(self.field, sigma=0.5)
        self.history.append({"type": "tension", "a": pattern_a, "b": pattern_b})
        return self.field

    def focus_attention(self, x: int, y: int, radius: int = 3):
        self.focus = (x, y, radius)
        for i in range(max(0, x-radius), min(self.res, x+radius+1)):
            for j in range(max(0, y-radius), min(self.res, y+radius+1)):
                self.field[i, j] *= 1.2
        self.history.append({"type": "focus", "point": (x, y), "radius": radius})
        return self.field

    def observe(self):
        density = np.mean(self.field)
        variance = np.var(self.field)
        return {"density": density, "variance": variance, "history_len": len(self.history)}

    def get_state(self):
        return {
            "field": self.field.tolist(),
            "focus": self.focus,
            "history": self.history[-5:]
        }

    def _gaussian(self, x: int, y: int, sigma: float = 1.0):
        g = np.zeros((self.res, self.res))
        for i in range(self.res):
            for j in range(self.res):
                g[i, j] = np.exp(-((i - x)**2 + (j - y)**2) / (2 * sigma**2))
        return g / np.max(g)
