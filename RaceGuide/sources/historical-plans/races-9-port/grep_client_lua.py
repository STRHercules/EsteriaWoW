"""Search the client's Interface files for a Lua pattern: python grep_client_lua.py <pattern> [file-filter]."""

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
    "Patch-Z.MPQ",
    "PATCH-X.MPQ",
    "Patch-Y.MPQ",
)


def main() -> None:
    pattern = re.compile(sys.argv[1])
    wanted = sys.argv[2].casefold() if len(sys.argv) > 2 else ""
    storm = Storm(DLL_DEFAULT)
    for name in NAMES:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            entries = [(entry, *_rest) for entry, *_rest in storm.list_files(handle)]
        finally:
            storm.dll.SFileCloseArchive(handle)
        for entry, *_ in entries:
            if not entry.lower().endswith((".lua", ".xml")):
                continue
            if wanted and wanted not in entry.lower():
                continue
            handle = H()
            if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
                continue
            try:
                try:
                    payload = storm.read(handle, entry)
                except Exception:
                    continue
            finally:
                storm.dll.SFileCloseArchive(handle)
            try:
                text = payload.decode("latin1")
            except Exception:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    print(f"{name}:{entry}:{number}: {line.strip()[:200]}")


if __name__ == "__main__":
    main()
