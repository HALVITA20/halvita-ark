"""
nine-legged_spider_v4
FILE OBSERVER / A-03

Назначение:
наблюдение за изменениями файлов внутри каталога V4.

Не изменяет файлы.
Не запускает процессы.
Не отправляет данные наружу.
"""

from pathlib import Path
from datetime import datetime
import hashlib
import time

ROOT = Path("nine-legged_spider_v4")

WATCHED = {
    "README",
    "README.md",
    "origin.txt",
    "trace.txt",
    "session.txt",
}


def sha256(path: Path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return "UNREADABLE"


def snapshot():
    result = {}

    if not ROOT.exists():
        return result

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.name not in WATCHED:
            continue

        try:
            stat = path.stat()

            result[str(path)] = {
                "size": stat.st_size,
                "mtime": stat.st_mtime_ns,
                "hash": sha256(path),
            }

        except OSError:
            result[str(path)] = {
                "size": -1,
                "mtime": -1,
                "hash": "ERROR",
            }

    return result


def log(event, path=None, old=None, new=None):
    timestamp = datetime.now().isoformat(timespec="milliseconds")

    print(f"\n[{timestamp}] {event}")

    if path:
        print(f"FILE: {path}")

    if old and new:
        print(f"OLD HASH: {old['hash']}")
        print(f"NEW HASH: {new['hash']}")
        print(f"OLD SIZE: {old['size']}")
        print(f"NEW SIZE: {new['size']}")


print("=" * 60)
print("SPIDER OBSERVER")
print("TARGET: nine-legged_spider_v4")
print("MODE: READ ONLY")
print("=" * 60)

previous = snapshot()

print(f"INITIAL FILES: {len(previous)}")

while True:
    time.sleep(1)

    current = snapshot()

    old_paths = set(previous)
    new_paths = set(current)

    # новые файлы
    for path in new_paths - old_paths:
        log("NEW FILE", path, new=current[path])

        try:
            text = Path(path).read_text(
                encoding="utf-8",
                errors="replace"
            )

            if "𖣠" in text:
                print("!!! TRACE SYMBOL DETECTED: 𖣠 !!!")

        except Exception:
            pass

    # удалённые файлы
    for path in old_paths - new_paths:
        log("FILE DISAPPEARED", path)

    # изменённые файлы
    for path in old_paths & new_paths:

        if previous[path]["hash"] != current[path]["hash"]:

            log(
                "CONTENT CHANGE",
                path,
                previous[path],
                current[path]
            )

            try:
                text = Path(path).read_text(
                    encoding="utf-8",
                    errors="replace"
                )

                if "𖣠" in text:
                    print("TRACE: 𖣠 PRESENT")

            except Exception:
                pass

    previous = current
