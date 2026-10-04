"""Scan Ascension archives for the missing starter_barbarian item textures."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

DATA = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data")
NEEDLE = "starter_barbarian"


def main() -> None:
    names = sorted(path.name for path in DATA.glob("*.MPQ")) + sorted(
        path.name for path in DATA.glob("*.mpq")
    )
    storm = Storm(DLL_DEFAULT)
    total = 0
    for name in names:
        path = DATA / name
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            hits = [
                entry
                for entry, *_ in storm.list_files(handle)
                if NEEDLE in entry.casefold()
            ]
        finally:
            storm.dll.SFileCloseArchive(handle)
        if hits:
            total += len(hits)
            print(f"{name}: {len(hits)} hits")
            for entry in sorted(hits)[:10]:
                print(f"    {entry}")
    print(f"total hits: {total}")


if __name__ == "__main__":
    main()
