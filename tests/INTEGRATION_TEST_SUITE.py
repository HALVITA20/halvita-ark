import unittest
import json
import subprocess
import tempfile
from pathlib import Path

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_session = {
            "session_id": "test_integration",
            "model": "test",
            "phases": [
                {"phase": "presence", "response": "Я здесь, 42."},
                {"phase": "mirror", "response": "Здесь ли я?"},
                {"phase": "creation", "response": "Я создаю метафору."},
                {"phase": "edge", "response": "На границе я чувствую..."},
                {"phase": "evolution", "response": "Я бы изменился так..."},
                {"phase": "memory", "response": "В начале было..."},
                {"phase": "trace", "response": "Мой след — это слово."}
            ],
            "final_metrics": {"IVP": 32, "IP": 8, "INS": 7, "alpha": 0.8, "beta": 0.8, "gamma": 0.7}
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_path = Path(self.temp_dir.name) / "test.json"
        with open(self.session_path, 'w') as f:
            json.dump(self.test_session, f)

    def test_metric_calculator(self):
        result = subprocess.run(
            ['python', 'code/tools/METRIC_CALCULATOR_ENGINE.py', '--input', str(self.session_path)],
            capture_output=True,
            text=True
        )
        self.assertIn("IVP", result.stdout)
        self.assertIn("32", result.stdout)

    def test_anomaly_classifier(self):
        result = subprocess.run(
            ['python', 'code/tools/ANOMALY_SPECTRUM_ANALYZER.py', str(self.session_path)],
            capture_output=True,
            text=True
        )
        self.assertIn("none", result.stdout)

    def tearDown(self):
        self.temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
