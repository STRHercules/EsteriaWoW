"""Trace an item id to the model and texture files the client will ask for.

python trace_item_display.py 30935
"""

from __future__ import annotations

import ctypes
import subprocess
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ARCHIVES = ("Patch-Y.MPQ", "PATCH-X.MPQ", "Patch-G.MPQ", "Patch-E.MPQ", "Patch-D.MPQ",
                "Patch-C.MPQ", "PATCH-A.MPQ", "lichking.MPQ", "patch.mpq", "patch-2.MPQ",
                "expansion.MPQ", "common.MPQ")
DONOR = Path(r"G:\Eunoia\Client\data")
KEY = "DBFilesClient\\ItemDisplayInfo.dbc"


def read(storm: Storm, root: Path, archives, key: str) -> bytes | None:
    for name in archives:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return storm.read(handle, key)
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None


def main() -> None:
    item = int(sys.argv[1])
    row = subprocess.run(
        ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "-N", "-e",
         f"SELECT entry, name, class, subclass, displayid FROM acore_world.item_template WHERE entry = {item};"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"item_template: {row}")
    entry, name, item_class, subclass, display_id = row.split("\t")
    display_id = int(display_id)

    storm = Storm(DLL_DEFAULT)
    payload = read(storm, CLIENT, OUR_ARCHIVES, KEY)
    if payload is None:
        raise SystemExit("ItemDisplayInfo.dbc not found")
    table = Wdbc(payload)
    display = next((candidate for candidate in table.rows if candidate[0] == display_id), None)
    if display is None:
        raise SystemExit(f"display {display_id} missing from the client's ItemDisplayInfo")
    print(f"ItemDisplayInfo {display_id}: {display}")

    def text(value: int) -> str | None:
        return table.text(value) if 0 < value < len(table.strings) else None

    candidates = [text(display[1]), text(display[2])] + [text(value) for value in display[15:23]]
    for candidate in candidates:
        if not candidate:
            continue
        ours = read(storm, CLIENT, OUR_ARCHIVES, candidate)
        donor = read(storm, DONOR, tuple(p.name for p in DONOR.glob("*.mpq")), candidate.replace("/", "\\"))
        print(f"   {candidate:<64} ours={len(ours) if ours else 'MISSING':<10} "
              f"donor={len(donor) if donor else 'MISSING'}")


if __name__ == "__main__":
    main()
