"""For the helm the user tested, confirm every custom race's resolved files exist."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
HEAD = "Item\\ObjectComponents\\Head\\"
# race -> (name, ClientPrefix) as the client will read them now
RACES = {14: ("Broken", "Bk"), 15: ("Sethrak", "Tr"), 16: ("Eredar", "Dr"),
         17: ("Nightborne", "Ni"), 18: ("Pandaren", "Pa"), 19: ("Void Elf", "Be"),
         20: ("Vulpera", "Wo"), 21: ("Lightforged", "Dr"), 22: ("Zandalari", "Tr"),
         23: ("Dark Iron", "Dw"), 28: ("Dracthyr", "Be"), 29: ("Kul Tiran", "Ni"),
         30: ("Illidari H", "Be"), 31: ("Illidari A", "Ni")}
STEMS = ["Helm_Leather_B_06", "Helm_Cloth_A_01", "Helm_Plate_D_02"]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handles = []
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    try:
        for race, (label, prefix) in sorted(RACES.items()):
            parts = []
            for stem in STEMS:
                for sex in ("M", "F"):
                    for suffix in (".m2", "00.skin"):
                        key = f"{HEAD}{stem}_{prefix}{sex}{suffix}"
                        found = None
                        for archive, handle in reversed(handles):
                            try:
                                storm.read(handle, key)
                                found = archive
                                break
                            except Exception:
                                continue
                        parts.append("ok" if found else "MISSING")
            state = "all present" if all(p == "ok" for p in parts) else " ".join(parts)
            print(f"race {race:>2} {label:<12} prefix {prefix}: {state}")
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
