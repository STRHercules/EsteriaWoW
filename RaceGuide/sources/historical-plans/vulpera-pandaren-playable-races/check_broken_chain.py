"""Overlap + model-chain check for the Broken and Sethrak races."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc, _start_outfit_display_ids  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/common.MPQ",
    "Data/patch.MPQ",
    "Data/patch-2.MPQ",
    "Data/patch-3.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
    "Data/PATCH-A.MPQ",
    "Data/PATCH-X.MPQ",
    "Data/Patch-C.MPQ",
)


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def load_table(storm: Storm, archive: Path, table: str) -> RawWdbc:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return RawWdbc(storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    patch_c = CLIENT / "Data" / "Patch-C.MPQ"
    outfits = load_table(storm, patch_c, "CharStartOutfit")
    races = load_table(storm, patch_c, "ChrRaces")
    displays = load_table(storm, patch_c, "CreatureDisplayInfo")
    models = load_table(storm, patch_c, "CreatureModelData")
    display_rows = {int.from_bytes(r[:4], "little"): r for r in displays.records}
    model_rows = {int.from_bytes(r[:4], "little"): r for r in models.records}

    replaced = set(_start_outfit_display_ids(outfits.records))
    for race in (14, 15):
        ids = set()
        for record in outfits.records:
            if record[4] != race:
                continue
            ids.update(int.from_bytes(record[o : o + 4], "little") for o in range(104, 200, 4))
        ids.discard(0)
        ids.discard(0xFFFFFFFF)
        overlap = sorted(ids & replaced)
        print(f"race {race}: {len(ids)} outfit ids, overlap with rebuilt rows: {len(overlap)} {overlap[:10]}")

    entries: set[str] = set()
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            entries |= {name.casefold().replace("/", "\\") for name, *_ in storm.list_files(handle)}
        finally:
            storm.dll.SFileCloseArchive(handle)

    for race in (14, 15):
        row = next(r for r in races.records if int.from_bytes(r[:4], "little") == race)
        client_file = cstring(races.strings, int.from_bytes(row[44:48], "little"))
        print(f"race {race}: fileString={client_file!r}")
        for field, label in ((16, "male"), (20, "female")):
            display_id = int.from_bytes(row[field : field + 4], "little")
            display = display_rows.get(display_id)
            if display is None:
                print(f"    {label}: display {display_id} MISSING from CreatureDisplayInfo")
                continue
            model_id = int.from_bytes(display[4:8], "little")
            model = model_rows.get(model_id)
            if model is None:
                print(f"    {label}: display {display_id} -> model {model_id} MISSING")
                continue
            path = cstring(models.strings, int.from_bytes(model[8:12], "little"))
            key = path.casefold().replace("/", "\\")
            variants = [e for e in entries if e.startswith(key.rsplit(".", 1)[0])]
            print(
                f"    {label}: display={display_id} model={model_id} path={path} "
                f"archive_hits={len(variants)}"
            )


if __name__ == "__main__":
    main()
