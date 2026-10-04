"""Resolve the custom-race display chain the way the live client does.

PATCH-X.MPQ loads after Patch-C.MPQ and ships its own CreatureDisplayInfo /
CreatureModelData, so those two tables come from PATCH-X while ChrRaces and
CreatureSoundData come from Patch-C. This script mirrors that priority and
fails loudly when a link is missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev" / "Data"
# later archives win, so read in load order and let the last hit overwrite
PRIORITY = (
    "common.MPQ",
    "patch.MPQ",
    "expansion.MPQ",
    "lichking.MPQ",
    "patch-2.MPQ",
    "patch-3.MPQ",
    "patch-4.mpq",
    "PATCH-A.MPQ",
    "Patch-B.MPQ",
    "Patch-C.MPQ",
    "Patch-F.MPQ",
    "Patch-O.mpq",
    "PATCH-X.MPQ",
)
# race -> (race name, expected model path fragment, glue display id, world display id)
# The player path in the world resolves UNIT_FIELD_DISPLAYID through a 16-bit
# value, so the id the server sends must be below 65536.
RACES = {
    18: ("Pandaren", "pandaren", 141687, 60004),
    20: ("Vulpera", "vulpera", 141254, 60006),
}


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for archive in PRIORITY:
        path = CLIENT / archive
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except OSError:
            continue
        try:
            for name, *_ in storm.list_files(handle):
                pool[name.casefold()] = (archive, name)
        finally:
            storm.dll.SFileCloseArchive(handle)

    def table(relative: str) -> RawWdbc:
        archive, name = pool[relative.casefold()]
        handle = storm.open_archive(CLIENT / archive)
        try:
            return RawWdbc(storm.read(handle, name))
        finally:
            storm.dll.SFileCloseArchive(handle)

    def indexed(raw: RawWdbc) -> dict[int, list[int]]:
        return {
            int.from_bytes(record[:4], "little"): [
                int.from_bytes(record[i * 4 : i * 4 + 4], "little")
                for i in range(raw.fields)
            ]
            for record in raw.records
        }

    chr_races = indexed(table("DBFilesClient\\ChrRaces.dbc"))
    displays = indexed(table("DBFilesClient\\CreatureDisplayInfo.dbc"))
    models = indexed(table("DBFilesClient\\CreatureModelData.dbc"))
    sounds = indexed(table("DBFilesClient\\CreatureSoundData.dbc"))

    def string_of(raw: RawWdbc, offset: int) -> str:
        if not offset:
            return ""
        end = raw.strings.find(b"\x00", offset)
        return raw.strings[offset:end].decode("utf-8", "replace")

    model_data = table("DBFilesClient\\CreatureModelData.dbc")
    failures = 0
    for race, (name, fragment, glue_display, world_display) in RACES.items():
        row = chr_races.get(race)
        if row is None:
            print(f"{name} (race {race}): missing from ChrRaces")
            failures += 1
            continue
        for (field, gender, expected) in ((4, "male", glue_display), (5, "female", glue_display + 1)):
            display_id = row[field]
            display = displays.get(display_id)
            if display is None:
                print(f"{name} {gender}: display {display_id} missing from live CreatureDisplayInfo")
                failures += 1
                continue
            model = models.get(display[1])
            if model is None:
                print(f"{name} {gender}: model {display[1]} missing from live CreatureModelData")
                failures += 1
                continue
            path = string_of(model_data, model[2])
            asset = pool.get(path.casefold().replace(".mdx", ".m2"))
            sound_ok = model[13] == 0 or model[13] in sounds
            print(
                f"{name} {gender}: glue display {display_id} -> model {display[1]} "
                f"-> {path} asset={'ok' if asset else 'MISSING'} "
                f"soundKit={model[13]} {'ok' if sound_ok else 'MISSING'}"
            )
            if asset is None or not sound_ok or display_id != expected:
                failures += 1

        for gender, world_id in (("male", world_display), ("female", world_display + 1)):
            display = displays.get(world_id)
            if world_id >= 0x10000 or display is None:
                print(f"{name} {gender}: world display {world_id} unusable (16-bit path)")
                failures += 1
                continue
            model = models.get(display[1])
            path = string_of(model_data, model[2]) if model else ""
            ok = model is not None and fragment in path.casefold()
            print(
                f"{name} {gender}: world display {world_id} -> model {display[1]} -> {path} "
                f"{'ok' if ok else 'WRONG MODEL'}"
            )
            if not ok:
                failures += 1
    print("chain failures:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
