"""List preview-outfit item textures for races 18/20 and their archive variants."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

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
CLASS_ID = 4
SEX = 0


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def load(storm: Storm, archive: Path, table: str) -> RawWdbc:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return RawWdbc(storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    patch_c = CLIENT / "Data" / "Patch-C.MPQ"
    outfits = load(storm, patch_c, "CharStartOutfit")
    items = load(storm, patch_c, "ItemDisplayInfo")
    item_rows = {int.from_bytes(r[:4], "little"): r for r in items.records}

    entries: list[str] = []
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            entries.extend(name.casefold().replace("/", "\\") for name, *_ in storm.list_files(handle))
        finally:
            storm.dll.SFileCloseArchive(handle)
    pool = set(entries)

    for race in (18, 20):
        row = next(
            record
            for record in outfits.records
            if record[4] == race and record[5] == CLASS_ID and record[6] == SEX
        )
        display_ids = [
            int.from_bytes(row[o : o + 4], "little") for o in range(104, 200, 4)
        ]
        print(f"== race {race} class {CLASS_ID} ==")
        for display_id in display_ids:
            if display_id in (0, 0xFFFFFFFF):
                continue
            item_row = item_rows.get(display_id)
            if item_row is None:
                print(f"   {display_id}: no ItemDisplayInfo row")
                continue
            textures = [
                cstring(items.strings, int.from_bytes(item_row[f * 4 : f * 4 + 4], "little"))
                for f in range(15, 23)
            ]
            for texture in textures:
                if not texture:
                    continue
                stem = texture.casefold().removesuffix(".blp")
                variants = sorted(
                    entry.rsplit("\\", 1)[-1]
                    for entry in pool
                    if stem in entry and entry.endswith(".blp")
                )
                print(f"   {display_id} {texture}: variants={variants[:6]}")


if __name__ == "__main__":
    main()
