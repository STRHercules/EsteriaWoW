"""Dump DBFilesClient\\Languages.dbc (it lives in the locale MPQ, not Data\\*.MPQ)."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

DATA = REPO / "3.3.5a - Dev/Data"
ARCHIVES = (
    "enUS/locale-enUS.MPQ",
    "enUS/base-enUS.MPQ",
    "enUS/patch-enUS.MPQ",
    "enUS/patch-enUS-2.MPQ",
    "enUS/patch-enUS-3.MPQ",
    "enUS/patch-enUS-6.mpq",
)
KEY = "DBFilesClient\\Languages.dbc"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for name in ARCHIVES:
        path = DATA / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, KEY)
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
        table = Wdbc(payload)
        print(f"{KEY} <- {name}: rows={len(table.rows)} fields={table.fields} record={table.record_size}")
        for row in table.rows:
            extras = " ".join(repr(table.text(value)) for value in row[2:] if value < len(table.strings) and value)
            print(f"  id {row[0]:>3} name={table.text(row[1])!r} {extras}")
        return
    raise SystemExit(f"{KEY}: not found")


if __name__ == "__main__":
    main()
