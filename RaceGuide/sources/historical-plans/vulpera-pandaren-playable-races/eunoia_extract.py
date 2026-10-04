"""Read files out of Eunoia's client archives with StormLib in read-only mode.

The running client holds the MPQs open exclusively, but MPQ_OPEN_READ_ONLY
still opens them for shared reading.
"""

from __future__ import annotations

import ctypes as c
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, U  # noqa: E402

CLIENT = Path(r"G:\Eunoia\Client")
MPQ_OPEN_READ_ONLY = 0x00000100

# Blizzard load order: base patches, then locale patches, then custom patches.
ORDER = [
    "common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq",
    "patch.mpq", "patch-2.mpq", "patch-3.mpq",
    "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq", "Patch-7.mpq",
    "Patch-8.mpq", "Patch-9.mpq",
    "patch-I.mpq", "patch-m.mpq", "patch-x.mpq", "patch-y.mpq", "patch-z.mpq",
    "enUS/locale-enus.mpq", "enUS/backup-enus.mpq", "enUS/base-enus.mpq",
    "enUS/patch-enus.mpq", "enUS/patch-enus-2.mpq", "enUS/patch-enus-3.mpq",
    "enUS/patch-enus-4.mpq", "enUS/patch-enus-5.mpq",
]


class Reader:
    def __init__(self) -> None:
        self.storm = Storm(DLL_DEFAULT)

    def open(self, relative: str):
        handle = H()
        flags = MPQ_OPEN_READ_ONLY
        if not self.storm.dll.SFileOpenArchive(str(CLIENT / "data" / relative), 0, flags, c.byref(handle)):
            raise OSError(f"open failed {relative}: {c.get_last_error()}")
        return handle

    def read(self, relative: str, name: str) -> bytes | None:
        archive = self.open(relative)
        try:
            return self.storm.read(archive, name)
        except Exception:  # noqa: BLE001
            return None
        finally:
            self.storm.dll.SFileCloseArchive(archive)

    def read_best(self, name: str) -> tuple[str, bytes] | None:
        found: tuple[str, bytes] | None = None
        for relative in ORDER:
            path = CLIENT / "data" / relative
            if not path.exists():
                continue
            try:
                payload = self.read(relative, name)
            except Exception:  # noqa: BLE001
                continue
            if payload:
                found = (relative, payload)
        return found


def main() -> None:
    reader = Reader()
    targets = [
        "DBFilesClient\\ChrRaces.dbc",
        "DBFilesClient\\CharSections.dbc",
        "DBFilesClient\\CharBaseInfo.dbc",
        "DBFilesClient\\CreatureDisplayInfo.dbc",
        "DBFilesClient\\CreatureModelData.dbc",
        "DBFilesClient\\CharHairGeosets.dbc",
        "DBFilesClient\\CharHairTextures.dbc",
        "DBFilesClient\\CharacterFacialHairStyles.dbc",
        "Interface\\GlueXML\\CharacterCreate.lua",
    ]
    destination = REPO / ".agents/plans/vulpera-pandaren-playable-races/eunoia-dbc"
    destination.mkdir(parents=True, exist_ok=True)
    for name in targets:
        result = reader.read_best(name)
        if result is None:
            print(f"{name}: not found in any archive")
            continue
        relative, payload = result
        out = destination / Path(name).name
        out.write_bytes(payload)
        print(f"{name}: {len(payload):,} bytes from {relative} -> {out.name}")


if __name__ == "__main__":
    main()
