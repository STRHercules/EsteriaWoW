"""Report which client archives contain the winning GlueXML character-creation files.

Determines the exact set of archives a Freeborn GlueXML patch must touch, and whether any
higher-priority archive overrides patch-Z.mpq.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

DATA = Path(r"G:\3.3.5a - Dev\Data")

ENTRIES = (
    "Interface\\GlueXML\\CharacterCreate.lua",
    "Interface\\GlueXML\\CharacterCreate.xml",
)

ARCHIVES = (
    "PATCH-A.MPQ",
    "Patch-B.MPQ",
    "Patch-C.MPQ",
    "Patch-D.MPQ",
    "Patch-E.MPQ",
    "Patch-F.MPQ",
    "Patch-G.MPQ",
    "Patch-Housing.MPQ",
    "Patch-O.mpq",
    "PATCH-V.mpq",
    "PATCH-X.MPQ",
    "Patch-Y.MPQ",
    "patch-K.mpq",
    "patch-Z.mpq",
    "locale-enUS.MPQ",
    "patch-enUS-2.MPQ",
    "patch-enUS-3.MPQ",
    "patch-enUS-5.MPQ",
    "patch-enUS-6.mpq",
    "patch-enUS-Z.MPQ",
)


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    for name in ARCHIVES:
        path = DATA / name
        if not path.is_file():
            print(f"{name}: MISSING")
            continue
        try:
            handle = storm.open_archive(path)
        except Exception as error:  # noqa: BLE001
            print(f"{name}: OPEN FAILED {error}")
            continue
        present = set()
        try:
            for entry in ENTRIES:
                try:
                    storm.read(handle, entry)
                except Exception:  # noqa: BLE001 - absent entry, any failure means "not here"
                    continue
                present.add(entry)
        finally:
            storm.dll.SFileCloseArchive(handle)
        hits = [entry for entry in ENTRIES if entry in present]
        print(f"{name}: {', '.join(Path(h).name for h in hits) if hits else '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
