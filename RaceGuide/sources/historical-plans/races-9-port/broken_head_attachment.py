"""Head attachment record of the working donor-style races (Broken, Eredar, Pandaren)."""
from __future__ import annotations

import ctypes
import struct
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
MODELS = {
    "broken": "character\\esteriabroken\\male\\brokenmale.m2",
    "eredar": "character\\eredar\\male\\eredarmale.m2",
    "pandaren": "character\\pandaren\\male\\pandarenmale.m2",
    "vulpera": "character\\vulpera\\male\\vulperamale.m2",
}


def load(storm: Storm, key: str):
    for name in reversed(ORDER):
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return name, storm.read(handle, key)
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None, None


def find(payload: bytes, stride: int, minimum: int = 8):
    hits = []
    for offset in range(0, len(payload) - stride * minimum, 4):
        if struct.unpack_from("<I", payload, offset)[0] != 0:
            continue
        run = 1
        for index in range(1, 40):
            here = offset + index * stride
            if here + stride > len(payload):
                break
            if struct.unpack_from("<I", payload, here)[0] != index:
                break
            run += 1
        if run >= minimum:
            hits.append((offset, run, stride))
    return hits


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in MODELS.items():
        source, payload = load(storm, key)
        if payload is None:
            print(f"{label}: missing")
            continue
        print(f"== {label} [{source}] size={len(payload):,}")
        found_any = False
        for stride in (0x1C, 0x20, 0x24, 0x28, 0x2C, 0x30, 0x34):
            hits = find(payload, stride)
            if not hits:
                continue
            found_any = True
            for offset, run, stride_used in hits[:3]:
                record = offset + 11 * stride_used
                identifier, bone = struct.unpack_from("<IH", payload, record)
                pivot = struct.unpack_from("<3f", payload, record + 8)
                print(f"   stride {stride_used:#x} table {offset:#08x} ({run} ids): "
                      f"id {identifier} bone {bone} pivot=({pivot[0]:+.3f}, "
                      f"{pivot[1]:+.3f}, {pivot[2]:+.3f})")
        if not found_any:
            print("   no ordered attachment table at any stride")


if __name__ == "__main__":
    main()
