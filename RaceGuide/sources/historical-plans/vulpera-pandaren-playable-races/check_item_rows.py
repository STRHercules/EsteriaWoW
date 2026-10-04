"""Diagnose ItemDisplayInfo rows used by races 18/20 start outfits."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"
DONOR_DBC = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
TARGET_RACES = {18, 20}


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    outfits = RawWdbc((HERE / "client-dbc-fixed" / "CharStartOutfit.dbc").read_bytes())
    mine = RawWdbc((HERE / "client-dbc-fixed" / "ItemDisplayInfo.dbc").read_bytes())
    donor = RawWdbc((DONOR_DBC / "ItemDisplayInfo.dbc").read_bytes())
    mine_rows = {int.from_bytes(r[:4], "little"): r for r in mine.records}
    donor_rows = {int.from_bytes(r[:4], "little"): r for r in donor.records}

    display_ids: set[int] = set()
    for record in outfits.records:
        if record[4] not in TARGET_RACES:
            continue
        display_ids.update(
            int.from_bytes(record[o : o + 4], "little") for o in range(104, 200, 4)
        )
    display_ids.discard(0)
    display_ids.discard(0xFFFFFFFF)

    shown = 0
    for display_id in sorted(display_ids):
        row = mine_rows.get(display_id)
        donor_row = donor_rows.get(display_id)
        if row is None or donor_row is None:
            continue
        mine_models = [cstring(mine.strings, int.from_bytes(row[f * 4 : f * 4 + 4], "little"))
                       for f in (1, 2)]
        donor_models = [cstring(donor.strings, int.from_bytes(donor_row[f * 4 : f * 4 + 4], "little"))
                        for f in (1, 2)]
        mine_tex = cstring(mine.strings, int.from_bytes(row[15 * 4 : 16 * 4], "little"))
        donor_tex = cstring(donor.strings, int.from_bytes(donor_row[15 * 4 : 16 * 4], "little"))
        if mine_models == donor_models and mine_tex == donor_tex:
            continue
        shown += 1
        if shown <= 10:
            print(f"display {display_id}")
            print(f"    models Patch-C={mine_models} donor={donor_models}")
            print(f"    tex0   Patch-C={mine_tex!r} donor={donor_tex!r}")
    print(f"rows differing from donor: {shown}")

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(CLIENT / "Data" / "Patch-C.MPQ")
    try:
        entries = {name.casefold().replace("/", "\\") for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)

    basenames: set[str] = set()
    for display_id in sorted(display_ids):
        donor_row = donor_rows.get(display_id)
        if donor_row is None:
            continue
        for field in (1, 2):
            name = cstring(donor.strings, int.from_bytes(donor_row[field * 4 : field * 4 + 4], "little"))
            if name:
                basenames.add(name.casefold().removesuffix(".mdx").removesuffix(".m2"))
    found = {b: any(e.rsplit("\\", 1)[-1].startswith(b) and e.endswith((".m2", ".mdx")) for e in entries)
             for b in basenames}
    missing = sorted(b for b, ok in found.items() if not ok)
    print(f"distinct donor model basenames: {len(basenames)}  missing from Patch-C: {len(missing)}")
    for name in missing[:12]:
        print(f"    {name}")


if __name__ == "__main__":
    main()
