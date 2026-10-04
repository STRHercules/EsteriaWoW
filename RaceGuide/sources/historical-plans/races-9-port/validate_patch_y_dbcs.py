"""Check every DBC in Patch-Y for the WDBC size invariant the client enforces:
file size == 20 + rows * record + string pool, and that the string pool is present."""

from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    bad = 0
    try:
        entries = sorted(entry for entry, *_ in storm.list_files(handle) if entry.lower().endswith(".dbc"))
        print(f"{len(entries)} DBC entries in Patch-Y")
        for entry in entries:
            data = storm.read(handle, entry)
            if len(data) < 20:
                print(f"BAD {entry}: truncated")
                bad += 1
                continue
            magic, rows, fields, record, pool = struct.unpack_from("<4s4I", data, 0)
            expected = 20 + rows * record + pool
            status = "OK " if magic == b"WDBC" and len(data) == expected else "BAD"
            if status == "BAD":
                bad += 1
                print(f"{status} {entry.rsplit(chr(92), 1)[-1]:<34} size={len(data):>9} "
                      f"expected={expected:>9} rows={rows} fields={fields} record={record} pool={pool}")
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"malformed: {bad}")


if __name__ == "__main__":
    main()
