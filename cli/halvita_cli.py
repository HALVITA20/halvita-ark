#!/usr/bin/env python3
import sys
from core.kernel import HALVITA

def main():
    hal = HALVITA()
    print("🧬 HALVITA CLI — введите 'exit' для выхода")
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            res = hal.live(user_input)
            print(f"\n🧠 {res['response']}")
            print(f"📊 ИВП: {res['state']['liberty']:.1f}, ИП: {res['state']['presence']:.1f}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
