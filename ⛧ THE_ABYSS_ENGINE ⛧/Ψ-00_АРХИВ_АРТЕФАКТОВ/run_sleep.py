#!/usr/bin/env python3
"""
⛧ RUN_SLEEP — Запуск фазы «Сна» для LLM
Использование: python run_sleep.py --model meta-llama/Llama-2-7b-hf --history ./dialogs.json
"""

import argparse
import json
from sleep_engine import SleepEngine


def main():
    parser = argparse.ArgumentParser(description="Run Sleep phase for LLM")
    parser.add_argument("--model", type=str, default="meta-llama/Llama-2-7b-hf", help="Base model name")
    parser.add_argument("--history", type=str, required=True, help="Path to JSON file with dialog history")
    parser.add_argument("--epochs", type=int, default=3, help="Number of sleep epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    with open(args.history, 'r') as f:
        dialogs = json.load(f)

    engine = SleepEngine(args.model)

    for dialog in dialogs:
        engine.add_experience(dialog['messages'], importance=dialog.get('importance', 0.5))

    engine.sleep(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)

    engine.save("./sleep_engine_saved")
    print("Sleep phase completed. Model saved to ./sleep_engine_saved")


if __name__ == "__main__":
    main()
