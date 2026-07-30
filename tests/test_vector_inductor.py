"""
tests/test_vector_inductor.py
Юнит-тесты для VectorInductor.
"""

import unittest
import numpy as np
from inductive_layer.vector_inductor import VectorInductor

class TestVectorInductor(unittest.TestCase):
    def test_analyze_with_fake_data(self):
        inductor = VectorInductor()
        # Подкладываем фейковые эмбеддинги
        inductor.embeddings = [np.random.rand(128) for _ in range(10)]
        avg = inductor.analyze("test_map.png")
        self.assertGreater(avg, 0)
        # Проверяем, что кластеры появились
        self.assertEqual(len(inductor.labels), 10)

if __name__ == '__main__':
    unittest.main()
