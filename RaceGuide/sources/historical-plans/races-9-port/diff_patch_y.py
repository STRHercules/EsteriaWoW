"""Diff DBC entries between two Patch-Y archives: python diff_patch_y.py <old.mpq> <new.mpq> [key ...]."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402
from inspect_client_races import Client  # noqa: E402

DEFAULT_KEYS = (
    "DBFilesClient\\ChrRaces.dbc",
    "DBFilesClient\\CreatureDisplayInfo.dbc",
    "DBFilesClient\\CreatureDisplayInfoExtra.dbc",
)


def load(storm: Storm, path: Path, key: str) -> bytes | None:
    handle = H()
    if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
        raise OSError(f"cannot open {path}")
    try:
        try:
            return storm.read(handle, key)
        except Exception:
            return None
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    old, new = Path(sys.argv[1]), Path(sys.argv[2])
    keys = tuple(sys.argv[3:]) or DEFAULT_KEYS
    storm = Storm(DLL_DEFAULT)
    for key in keys:
        left, right = load(storm, old, key), load(storm, new, key)
        if left is None or right is None:
            print(f"{key}: missing ({left is None=}, {right is None=})")
            continue
        if left == right:
            print(f"{key}: identical ({len(left):,} bytes)")
            continue
        from cars_mount_pack import Wdbc

        a, b = Wdbc(left), Wdbc(right)
        print(f"{key}: differs ({len(left):,} -> {len(right):,} bytes, rows {len(a.rows)} -> {len(b.rows)})")
        dict_a = {row[0]: tuple(row) for row in a.rows}
        dict_b = {row[0]: tuple(row) for row in b.rows}
        for row_id in sorted(set(dict_a) | set(dict_b)):
            first, second = dict_a.get(row_id), dict_b.get(row_id)
            if first == second:
                continue
            print(f"    id {row_id}:")
            print(f"      old {first}")
            print(f"      new {second}")


if __name__ == "__main__":
    main()
