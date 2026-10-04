"""List declared M2 sequences vs shipped .anim files for custom races."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/PATCH-A.MPQ",
    "Data/Patch-C.MPQ",
    "Data/common.MPQ",
    "Data/patch.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
)
MODELS = {
    "human_male": r"character\human\male\humanmale.m2",
    "sethrak_male": r"character\sethrak\male\sethrakmale.m2",
    "broken_male": r"character\esteriabroken\male\brokenmale.m2",
    "vulpera_male": r"character\vulpera\male\vulperamale.m2",
    "pandaren_male": r"character\pandaren\male\pandarenmale.m2",
}
EXTERNAL_FLAG = 0x20


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            for name, *_ in storm.list_files(handle):
                pool.setdefault(name.casefold(), (relative, name))
        finally:
            storm.dll.SFileCloseArchive(handle)
    known = set(pool)

    for label, wanted in MODELS.items():
        entry = pool.get(wanted)
        if entry is None:
            print(f"{label}: model missing")
            continue
        handle = storm.open_archive(CLIENT / entry[0])
        try:
            data = storm.read(handle, entry[1])
        finally:
            storm.dll.SFileCloseArchive(handle)
        count, offset = struct.unpack_from("<II", data, 0x1C)
        stem = wanted.rsplit(".", 1)[0]
        expected = []
        external = 0
        for index in range(count):
            base = offset + index * 68
            anim_id = struct.unpack_from("<H", data, base)[0]
            variation = struct.unpack_from("<H", data, base + 2)[0]
            flags = struct.unpack_from("<I", data, base + 12)[0]
            name = f"{stem}{anim_id:04d}-{variation:02d}.anim"
            expected.append(name)
            if flags & EXTERNAL_FLAG:
                external += 1
        present = [n for n in expected if n in known]
        missing = [n for n in expected if n not in known]
        print(
            f"{label}: sequences={count} external_flag={external} "
            f"anim_files_present={len(present)} anim_files_missing={len(missing)}"
        )
        for name in missing[:8]:
            print(f"      MISSING {name}")


if __name__ == "__main__":
    main()
