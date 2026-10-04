"""Confirm the retuned variants land where intended (world box vs the Vulpera skull)."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
HEAD = "Item\\ObjectComponents\\Head\\"
ITEMS = {"A": 50679, "B": 50713, "C": 51494, "D": 51825, "E": 50073, "F": 47688, "G": 47690}
ANCHOR = (-0.001, 0.0, 1.270)
SKULL = dict(x=(-0.327, 0.150), z=(1.051, 1.388))


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    try:
        display = Wdbc(storm.read(handle, "DBFilesClient\\ItemDisplayInfo.dbc"))
        lookup = {row[0]: row for row in display.rows}
        print(f"skull: x[{SKULL['x'][0]:+.3f},{SKULL['x'][1]:+.3f}] "
              f"z[{SKULL['z'][0]:+.3f},{SKULL['z'][1]:+.3f}]  anchor {ANCHOR}")
        for label, item in ITEMS.items():
            display_id = {"A": 64503, "B": 64429, "C": 65195, "D": 65160,
                          "E": 64427, "F": 61210, "G": 62159}[label]
            row = lookup[display_id]
            payload = storm.read(handle, f"{HEAD}HelmCal{label}_VuM.m2")
            low = struct.unpack_from("<3f", payload, 0xA0)
            high = struct.unpack_from("<3f", payload, 0xAC)
            world_x = (ANCHOR[0] + low[0], ANCHOR[0] + high[0])
            world_z = (ANCHOR[2] + low[2], ANCHOR[2] + high[2])
            print(f"  {label} (item {item}): x[{world_x[0]:+.3f},{world_x[1]:+.3f}] "
                  f"z[{world_z[0]:+.3f},{world_z[1]:+.3f}]  vis={row[13]}/{row[14]} "
                  f"model={display.text(row[1])}")
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
