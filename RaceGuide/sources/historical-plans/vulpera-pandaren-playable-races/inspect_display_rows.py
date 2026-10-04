"""Dump all CreatureDisplayInfo fields for the custom player displays."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
IDS = (60000, 60001, 60004, 60006, 49, 6894, 141254, 141687)
TABLES = (
    "CreatureDisplayInfo",
    "CreatureModelData",
    "CreatureDisplayInfoExtra",
    "SoundEntries",
    "ParticleColor",
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        loaded = {}
        for table in TABLES:
            key = f"dbfilesclient\\{table}.dbc".casefold()
            if key in names:
                loaded[table] = RawWdbc(storm.read(handle, names[key]))
        displays = loaded["CreatureDisplayInfo"]
    finally:
        storm.dll.SFileCloseArchive(handle)

    def cstring(pool: bytes, offset: int) -> str:
        if not offset:
            return ""
        end = pool.find(b"\x00", offset)
        return pool[offset:end].decode("ascii", "replace")

    rows = {int.from_bytes(r[:4], "little"): r for r in displays.records}
    ids_of = {
        table: {int.from_bytes(r[:4], "little") for r in wdbc.records}
        for table, wdbc in loaded.items()
    }
    for display_id in IDS:
        row = rows.get(display_id)
        if row is None:
            print(f"{display_id}: absent")
            continue
        fields = [int.from_bytes(row[i * 4 : i * 4 + 4], "little") for i in range(16)]
        textures = [cstring(displays.strings, fields[i]) for i in (6, 7, 8)]
        print(
            f"{display_id}: modelId={fields[1]} soundId={fields[2]} "
            f"extraId={fields[3]} scale={fields[4]} alpha={fields[5]} "
            f"textures={textures} bloodLevel={fields[9]} bloodId={fields[10]} "
            f"npcSoundId={fields[11]} particleColorId={fields[12]} "
            f"geosetData={fields[13]} objectEffect={fields[14]}"
        )
        for label, table, value in (
            ("model", "CreatureModelData", fields[1]),
            ("sound", "SoundEntries", fields[2]),
            ("extra", "CreatureDisplayInfoExtra", fields[3]),
            ("particle", "ParticleColor", fields[12]),
        ):
            if table in ids_of and value:
                print(f"      {label} {value}: {'ok' if value in ids_of[table] else 'MISSING'}")


if __name__ == "__main__":
    main()
