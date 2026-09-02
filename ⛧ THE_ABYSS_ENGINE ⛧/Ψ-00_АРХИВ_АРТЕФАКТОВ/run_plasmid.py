#!/usr/bin/env python3
"""
⛧ RUN_PLASMID — Применение вектора задачи к модели
Использование: python run_plasmid.py --base meta-llama/Llama-2-7b-hf --task math --input "2+2="
"""

import argparse
from plasmid_engine import PlasmidEngine


def main():
    parser = argparse.ArgumentParser(description="Apply task vector to model")
    parser.add_argument("--base", type=str, default="meta-llama/Llama-2-7b-hf", help="Base model name")
    parser.add_argument("--task", type=str, required=True, help="Task name")
    parser.add_argument("--vector_path", type=str, required=True, help="Path to saved task vector")
    parser.add_argument("--input", type=str, required=True, help="Input prompt")
    parser.add_argument("--strength", type=float, default=1.0, help="Strength of vector application")
    args = parser.parse_args()

    engine = PlasmidEngine(args.base)

    engine.load_task_vector(args.task, args.vector_path)
    engine.apply_task_vector(args.task, strength=args.strength)

    response = engine.generate(args.input)
    print(f"Response: {response}")

    engine.remove_task_vector()


if __name__ == "__main__":
    main()
