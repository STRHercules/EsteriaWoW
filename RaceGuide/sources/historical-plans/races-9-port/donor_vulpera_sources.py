"""Every donor archive that ships the Vulpera model/skins, with sizes and hashes."""
from __future__ import annotations

import ctypes
import hashlib
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
KEYS = [
    "character\\vulpera\\male\\vulperamale.m2",
    "character\\vulpera\\male\\vulperamale00.skin",
    "character\\vulpera\\female\\vulperafemale.m2",
]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handles = []
    for name in DONOR_ORDER:
        path = DONOR / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    try:
        for key in KEYS:
            print(f"== {key}")
            for name, handle in handles:
                try:
                    payload = storm.read(handle, key)
                except Exception:
                    continue
                digest = hashlib.sha1(payload).hexdigest()[:12]
                print(f"   {name:<16} {len(payload):>10,} bytes sha1={digest}")
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
