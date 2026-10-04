from __future__ import annotations

import argparse
from pathlib import Path

from cars_mount_pack import DLL_DEFAULT, Storm


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("terms", nargs="+")
    parser.add_argument("--recursive", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    archives = args.root.rglob("*.mpq") if args.recursive else args.root.glob("*.mpq")
    terms = [term.replace("/", "\\").casefold() for term in args.terms]

    for archive in sorted(archives, key=lambda p: str(p).casefold()):
        try:
            handle = storm.open_archive(archive)
        except OSError:
            continue
        try:
            files = [name for name, *_ in storm.list_files(handle)]
        finally:
            storm.dll.SFileCloseArchive(handle)
        normalized = [(name, name.replace("/", "\\").casefold()) for name in files]
        for term in terms:
            hits = [name for name, key in normalized if term in key]
            if hits:
                print(f"\n=== {archive} :: {term} ({len(hits)}) ===")
                for name in hits[:200]:
                    print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
