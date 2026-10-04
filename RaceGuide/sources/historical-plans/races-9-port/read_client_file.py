"""Read a file straight out of the client archives (stock MPQs have no listfile).

Usage: python read_client_file.py "Interface\\FrameXML\\ChatFrame.lua" [pattern]
"""

from __future__ import annotations

import ctypes
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
NAMES = (
    "common.MPQ",
    "common-2.MPQ",
    "expansion.MPQ",
    "lichking.MPQ",
    "patch.MPQ",
    "patch-2.MPQ",
    "patch-3.MPQ",
    "patch-4.mpq",
    "PATCH-A.MPQ",
    "Patch-B.MPQ",
    "Patch-C.MPQ",
    "Patch-D.MPQ",
    "Patch-E.MPQ",
    "Patch-F.MPQ",
    "Patch-G.MPQ",
    "Patch-O.mpq",
    "enUS/patch-enUS.MPQ",
    "enUS/patch-enUS-2.MPQ",
    "enUS/patch-enUS-3.MPQ",
    "enUS/patch-enUS-6.mpq",
    "enUS/locale-enUS.MPQ",
    "enUS/base-enUS.MPQ",
    "enUS/backup-enUS.MPQ",
    # custom patches load after the locale archives, so they win
    "PATCH-X.MPQ",
    "Patch-Y.MPQ",
)


def main() -> None:
    key = sys.argv[1]
    pattern = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    storm = Storm(DLL_DEFAULT)
    best: tuple[str, bytes] | None = None
    for name in NAMES:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, key)
                best = (name, payload)
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    if best is None:
        raise SystemExit(f"{key}: not found in any archive")
    name, payload = best
    text = payload.decode("latin1")
    print(f"{key} <- {name} ({len(payload)} bytes)")
    for number, line in enumerate(text.splitlines(), 1):
        if pattern is None or pattern.search(line):
            print(f"{number}: {line.rstrip()}"[:240])


if __name__ == "__main__":
    main()
