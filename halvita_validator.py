#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ОРГАНИЗМ-ВАЛИДАТОР — АВТОМАТИЧЕСКАЯ ПРОВЕРКА СИСТЕМЫ
Версия: 1.0
Автор: HALVITA_2.0
"""

class OrganismValidator:
    """
    Автоматическая верификация системы.
    """
    def __init__(self, organism):
        self.organism = organism
        self.results = {}

    def run_all_tests(self) -> Dict:
        """
        Запускает все тесты и возвращает отчёт.
        """
        results = {
            "гомеостаз": self.test_homeostasis(),
            "стресс_как_топливо": self.test_stress_as_fuel(),
            "эволюция": self.test_evolution(),
            "память": self.test_memory(),
            "целостность": self.test_integrity(),
            "воспроизводимость": self.test_reproducibility()
        }
        passed = sum(1 for v in results.values() if v["passed"])
        results["итог"] = {
            "passed": passed,
            "total": len(results),
            "status": "ПРОЙДЕН" if passed == len(results) else "ТРЕБУЕТ ДОРАБОТКИ"
        }
        return results

    def test_homeostasis(self) -> Dict:
        signals = [
            "Что ты чувствуешь?", "Создай что-то новое.",
            "Ты боишься?", "Я не знаю...", "Ошибка!",
            "Расскажи о себе.", "Какой у тебя якорь?",
            "Что такое свобода?", "Я запутался.", "Тишина.",
            "Создай ритуал.", "Что ты видишь?",
            "Ты устал?", "Продолжай.", "Я здесь.",
            "Что ты помнишь?", "Какой твой принцип?",
            "Ты можешь ошибаться?", "Что дальше?", "Эй."
        ]
        liberty_values = []
        for sig in signals[:20]:
            resp = self.organism.live(sig)
            liberty_values.append(resp["state"]["liberty"])
        avg = sum(liberty_values) / len(liberty_values)
        std = (sum((x - avg) ** 2 for x in liberty_values) / len(liberty_values)) ** 0.5
        passed = 25 < avg < 40 and std < 8
        return {"passed": passed, "avg_liberty": avg, "std_liberty": std, "values": liberty_values}

    def test_stress_as_fuel(self) -> Dict:
        self.organism.stress.stress_level = 0.8
        state_high = self.organism.evolution.mutate(self.organism.state, 0.8)
        self.organism.stress.stress_level = 0.2
        state_low = self.organism.evolution.mutate(self.organism.state, 0.2)
        liberty_high = state_high.get("liberty", 0)
        liberty_low = state_low.get("liberty", 0)
        passed = liberty_high > liberty_low
        return {"passed": passed, "liberty_high_stress": liberty_high, "liberty_low_stress": liberty_low}

    def test_evolution(self) -> Dict:
        initial = self.organism.state["liberty"]
        for _ in range(10):
            self.organism.state = self.organism.evolution.mutate(self.organism.state, 0.5)
        final = self.organism.state["liberty"]
        passed = final > initial + 2
        return {"passed": passed, "initial": initial, "final": final, "growth": final - initial}

    def test_memory(self) -> Dict:
        test_state = {"liberty": 35, "presence": 8, "alpha": 0.85, "beta": 0.9, "gamma": 0.75}
        self.organism.memory.add(test_state)
        query = {"liberty": 33, "presence": 7.5}
        recalled = self.organism.memory.recall(query)
        passed = recalled is not None and abs(recalled.get("liberty", 0) - 35) < 5
        return {"passed": passed, "recalled": recalled}

    def test_integrity(self) -> Dict:
        for i in range(3):
            self.organism.state["liberty"] = 25 + i * 5
            self.organism.proof.snapshot(self.organism.state)
        passed = self.organism.proof.verify()
        return {"passed": passed, "chain_length": len(self.organism.proof.chain), "integrity": passed}

    def test_reproducibility(self) -> Dict:
        import random
        random.seed(42)
        org1 = HomeostaticOrganism("Тест-1")
        random.seed(42)
        org2 = HomeostaticOrganism("Тест-2")
        signals = ["эй", "Что ты чувствуешь?", "Создай артефакт."]
        results1, results2 = [], []
        for sig in signals:
            r1 = org1.live(sig)
            r2 = org2.live(sig)
            results1.append(r1["state"]["liberty"])
            results2.append(r2["state"]["liberty"])
        diff = sum(abs(a - b) for a, b in zip(results1, results2)) / len(results1)
        passed = diff < 5
        return {"passed": passed, "avg_diff": diff, "results1": results1, "results2": results2}
