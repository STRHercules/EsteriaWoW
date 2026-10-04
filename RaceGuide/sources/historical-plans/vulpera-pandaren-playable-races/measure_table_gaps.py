"""Rows present in PATCH-A but absent from Patch-C, per character table."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RACE_BYTE_LAYOUTS, RawWdbc  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
TABLES = (
    "ChrRaces",
    "CharBaseInfo",
    "CharStartOutfit",
    "CharSections",
    "CharHairGeosets",
    "CharHairTextures",
    "BarberShopStyle",
    "CharacterFacialHairStyles",
    "NameGen",
    "CreatureDisplayInfo",
    "CreatureModelData",
    "ItemDisplayInfo",
    "SkillLineAbility",
    "SkillRaceClassInfo",
)


def load(storm: Storm, archive: Path, table: str) -> dict[int, bytes]:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        payload = storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)
    return {int.from_bytes(r[:4], "little"): r for r in RawWdbc(payload).records}


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    legacy = CLIENT / "Data" / "PATCH-A.MPQ"
    current = CLIENT / "Data" / "Patch-C.MPQ"
    for table in TABLES:
        try:
            old_rows = load(storm, legacy, table)
            new_rows = load(storm, current, table)
        except Exception as error:  # noqa: BLE001
            print(f"{table}: unreadable ({error})")
            continue
        missing = sorted(set(old_rows) - set(new_rows))
        races = ""
        if table in RACE_BYTE_LAYOUTS:
            offset, width = RACE_BYTE_LAYOUTS[table]
            counts: dict[int, int] = {}
            for row_id in missing:
                race = int.from_bytes(old_rows[row_id][offset : offset + width], "little")
                counts[race] = counts.get(race, 0) + 1
            races = f" by race {dict(sorted(counts.items())[:8])}"
        print(
            f"{table}: PATCH-A={len(old_rows)} Patch-C={len(new_rows)} "
            f"missing_from_Patch-C={len(missing)}{races}"
        )


if __name__ == "__main__":
    main()
