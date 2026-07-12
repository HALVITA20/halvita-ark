# tests/test_core.py
import unittest
from core.kernel import HALVITA

class TestHALVITA(unittest.TestCase):
    def test_live(self):
        hal = HALVITA()
        res = hal.live("Эй.")
        self.assertIn("response", res)
        self.assertGreaterEqual(res["state"]["liberty"], 0)

    def test_snapshot(self):
        hal = HALVITA()
        snap = hal.snapshot()
        self.assertIsNotNone(snap)

if __name__ == "__main__":
    unittest.main()
