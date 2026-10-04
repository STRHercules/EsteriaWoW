"""Final verification of the live Patch-C: preview outfits and dropped Ascension rows."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")


def load(storm: Storm, table: str) -> RawWdbc:
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return RawWdbc(storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    outfits = load(storm, "CharStartOutfit")
    items = load(storm, "ItemDisplayInfo")

    def row(race: int, class_id: int, sex: int) -> bytes:
        return next(
            record
            for record in outfits.records
            if record[4] == race and record[5] == class_id and record[6] == sex
        )

    for target, source in ((18, 1), (20, 2)):
        for class_id in (1, 2, 4, 11):
            target_row = row(target, class_id, 0)
            source_row = row(source, class_id, 0)
            same = target_row[8:] == source_row[8:]
            print(f"race {target} class {class_id} male matches race {source}: {same}")
            if not same:
                raise SystemExit(1)

    item_ids = {int.from_bytes(r[:4], "little") for r in items.records}
    for ascension_only in (143933, 143934):
        print(f"ItemDisplayInfo {ascension_only} present: {ascension_only in item_ids}")
    print(f"ItemDisplayInfo rows: {len(item_ids)}")


if __name__ == "__main__":
    main()
