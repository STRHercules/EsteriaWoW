"""Which donor archive serves each Vulpera .anim file, and do they differ?"""
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
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq",
               "enUS\\locale-enUS.MPQ", "enUS\\base-enUS.MPQ", "enUS\\patch-enUS.MPQ",
               "enUS\\patch-enUS-2.MPQ", "enUS\\patch-enUS-3.MPQ",
               "enUS\\patch-enUS-4.MPQ", "enUS\\patch-enUS-5.MPQ"]
CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
KEYS = [
    "character\\vulpera\\male\\vulperamale0060-00.anim",
    "character\\vulpera\\male\\vulperamale0069-00.anim",
    "character\\vulpera\\female\\vulperafemale0060-00.anim",
    "character\\vulpera\\male\\vulperamale.m2",
]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, root, order in (("donor", DONOR, DONOR_ORDER), ("ours", CLIENT, OUR_ORDER)):
        print(f"=== {label}")
        handles = []
        for name in order:
            path = root / name
            if not path.is_file():
                continue
            handle = H()
            if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
                handles.append((name, handle))
        try:
            for key in KEYS:
                print(f"  {key.split(chr(92))[-1]}")
                for name, handle in handles:
                    try:
                        payload = storm.read(handle, key)
                    except Exception:
                        continue
                    digest = hashlib.sha1(payload).hexdigest()[:10]
                    print(f"     {name:<22} {len(payload):>9,} bytes  sha1={digest}")
        finally:
            for _name, handle in handles:
                storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
