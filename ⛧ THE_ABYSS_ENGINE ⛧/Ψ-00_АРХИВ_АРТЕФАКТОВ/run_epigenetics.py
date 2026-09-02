#!/usr/bin/env python3
"""
⛧ RUN_EPIGENETICS — Переключение адаптера под пользователя
Использование: python run_epigenetics.py --base meta-llama/Llama-2-7b-hf --user user_42 --input "Hello"
"""

import argparse
from epigenetics_engine import EpigeneticsEngine


def main():
    parser = argparse.ArgumentParser(description="Switch adapter for user")
    parser.add_argument("--base", type=str, default="meta-llama/Llama-2-7b-hf", help="Base model name")
    parser.add_argument("--user", type=str, required=True, help="User ID")
    parser.add_argument("--adapter_path", type=str, required=True, help="Path to saved adapter")
    parser.add_argument("--input", type=str, required=True, help="Input prompt")
    args = parser.parse_args()

    engine = EpigeneticsEngine(args.base)

    engine.load_adapter(args.user, args.adapter_path)
    engine.switch_adapter(args.user)

    response = engine.generate(args.input)
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
