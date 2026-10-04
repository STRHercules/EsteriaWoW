"""Print id/flags/faction/displays/filestring for every ChrRaces row of a client install."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

ORDER = (
    "common.MPQ",
    "common-2.MPQ",
    "expansion.MPQ",
    "lichking.MPQ",
    "patch.MPQ",
    "patch-2.MPQ",
    "patch-3.MPQ",
    "patch-4.mpq",
)
KEY = "DBFilesClient\\ChrRaces.dbc"


def main() -> None:
    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else r"G:\3.3.5a\Data")
    storm = Storm(DLL_DEFAULT)
    payload = None
    source = None
    for name in ORDER:
        path = data_dir / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            payload = storm.read(handle, KEY)
            source = name
        except Exception:
            continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    if payload is None:
        raise SystemExit(f"{KEY}: not found under {data_dir}")
    table = Wdbc(payload)
    print(f"{KEY} <- {source}: rows={len(table.rows)} fields={table.fields}")
    for row in table.rows:
        print(f"  race {row[0]:>3}: flags={row[1]:<3} ({row[1]:#x}) faction={row[2]:<6} "
              f"expl={row[3]:<6} displays={row[4]}/{row[5]} lang={row[7]} "
              f"file={table.text(row[11])!r} cinematic={row[12]} alliance={row[13]}")


if __name__ == "__main__":
    main()
