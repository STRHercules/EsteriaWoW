"""Read numSkinProfiles from each custom race M2 and compare with shipped .skin files."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = ("Data/PATCH-A.MPQ", "Data/Patch-C.MPQ", "Data/common.MPQ", "Data/patch.MPQ")
MODELS = {
    "human_male": r"character\human\male\humanmale.m2",
    "sethrak_male": r"character\sethrak\male\sethrakmale.m2",
    "broken_male": r"character\esteriabroken\male\brokenmale.m2",
    "vulpera_male": r"character\vulpera\male\vulperamale.m2",
    "pandaren_male": r"character\pandaren\male\pandarenmale.m2",
}


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

    for label, wanted in MODELS.items():
        entry = pool.get(wanted)
        if entry is None:
            print(f"{label}: model not found")
            continue
        archive, actual = entry
        handle = storm.open_archive(CLIENT / archive)
        try:
            data = storm.read(handle, actual)
            stem = wanted.rsplit(".", 1)[0]
            skins = sorted(
                name for key, (_, name) in pool.items() if key.startswith(stem) and key.endswith(".skin")
            )
        finally:
            storm.dll.SFileCloseArchive(handle)
        magic, version = struct.unpack_from("<4sI", data, 0)
        global_flags = struct.unpack_from("<I", data, 0x10)[0]
        sequences = struct.unpack_from("<I", data, 0x1C)[0]
        bones = struct.unpack_from("<I", data, 0x2C)[0]
        textures = struct.unpack_from("<I", data, 0x50)[0]
        skin_profiles = struct.unpack_from("<I", data, 0x44)[0]
        vertices = struct.unpack_from("<I", data, 0x3C)[0]
        print(
            f"{label}: version={version} numSkinProfiles={skin_profiles} "
            f"globalFlags={global_flags:#x} sequences={sequences} bones={bones} "
            f"textures={textures} vertices={vertices} skins_present={len(skins)} "
            f"{[s.rsplit(chr(92),1)[-1] for s in skins]}"
        )


if __name__ == "__main__":
    main()
