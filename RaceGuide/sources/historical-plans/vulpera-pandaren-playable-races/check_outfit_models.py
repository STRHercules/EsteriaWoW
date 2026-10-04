"""Trace start-outfit item models for races 18/20 through ItemDisplayInfo."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"
TARGET_RACES = {18, 20}
MODEL_FIELDS = (1, 2)
TEXTURE_FIELDS = tuple(range(15, 23))


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    outfits = RawWdbc((HERE / "client-dbc-fixed" / "CharStartOutfit.dbc").read_bytes())
    displays = RawWdbc((HERE / "client-dbc-fixed" / "ItemDisplayInfo.dbc").read_bytes())
    rows = {int.from_bytes(r[:4], "little"): r for r in displays.records}

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(CLIENT / "Data" / "Patch-C.MPQ")
    try:
        names = {name.casefold() for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)

    display_ids: set[int] = set()
    for record in outfits.records:
        race = record[4]
        if race not in TARGET_RACES:
            continue
        display_ids.update(
            int.from_bytes(record[offset : offset + 4], "little")
            for offset in range(104, 200, 4)
        )
    display_ids.discard(0)
    print(f"race 18/20 start-outfit display ids: {len(display_ids)}")

    missing_rows = sorted(display_ids - set(rows))
    print(f"display ids without an ItemDisplayInfo row: {len(missing_rows)} {missing_rows[:12]}")

    bad_models: dict[str, list[int]] = {}
    bad_textures: dict[str, list[int]] = {}
    for display_id in sorted(display_ids & set(rows)):
        row = rows[display_id]
        for field in MODEL_FIELDS:
            path = cstring(displays.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if path and path.casefold().replace("/", "\\") not in names:
                bad_models.setdefault(path, []).append(display_id)
        for field in TEXTURE_FIELDS:
            path = cstring(displays.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if path and path.casefold().replace("/", "\\") not in names:
                bad_textures.setdefault(path, []).append(display_id)

    print(f"missing model files: {len(bad_models)} paths")
    for path, ids in sorted(bad_models.items())[:15]:
        print(f"    {path}  (displays {sorted(set(ids))[:6]})")
    print(f"missing texture files: {len(bad_textures)} paths")
    for path, ids in sorted(bad_textures.items())[:15]:
        print(f"    {path}  (displays {sorted(set(ids))[:6]})")


if __name__ == "__main__":
    main()
