"""Verify the staged calibration entries."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
PAIRS = {"HelmCalA": 64503, "HelmCalB": 64429, "HelmCalC": 65195, "HelmCalD": 65160,
         "HelmCalE": 64427, "HelmCalF": 61210, "HelmCalG": 62159}
HEAD = "Item\\ObjectComponents\\Head\\"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    try:
        display = Wdbc(storm.read(handle, "DBFilesClient\\ItemDisplayInfo.dbc"))
        lookup = {row[0]: row for row in display.rows}
        for stem, display_id in PAIRS.items():
            row = lookup[display_id]
            print(f"{stem:<9} display {display_id}: ModelName[0]={display.text(row[1])!r}")
        races = Wdbc(storm.read(handle, "DBFilesClient\\ChrRaces.dbc"))
        for row in races.rows:
            if row[0] == 20:
                print(f"race 20 prefix: {races.text(row[6])!r}")
        for stem in PAIRS:
            for sex in ("M", "F"):
                key = f"{HEAD}{stem}_Vu{sex}"
                model = struct.unpack_from("<i", storm.read(handle, key + ".m2"), 0)[0]
                skin = len(storm.read(handle, key + "00.skin"))
                print(f"   {key.split(chr(92))[-1]}.m2 magic={model:#x} skin={skin:,} bytes")
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
