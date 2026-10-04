"""Do the borrowed-fallback names actually exist in our archives?"""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
KEYS = [
    "Item\\ObjectComponents\\Head\\Helm_Eyepatch_A_02_BeM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Eyepatch_A_02_HeM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Goggles_B_04_DwM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2",
]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for name in sorted(p.name for p in CLIENT.glob("*.MPQ")) + sorted(
            p.name for p in CLIENT.glob("*.mpq")):
        path = CLIENT / name
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            for key in KEYS:
                try:
                    payload = storm.read(handle, key)
                    print(f"{name}: {key.split(chr(92))[-1]} -> {len(payload):,} bytes")
                except Exception:
                    pass
        finally:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
