"""Assert merged ItemDisplayInfo rows match donor strings for the start outfits."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from playable_race_pack import RawWdbc, _start_outfit_display_ids  # noqa: E402

DONOR_ROOT = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def strings_of(table: RawWdbc, row: bytes, fields: tuple[int, ...]) -> tuple[str, ...]:
    return tuple(
        cstring(table.strings, int.from_bytes(row[f * 4 : f * 4 + 4], "little")) for f in fields
    )


def main() -> None:
    merged = RawWdbc((HERE / "patch-c-fix3" / "ItemDisplayInfo.dbc").read_bytes())
    donor = RawWdbc((DONOR_ROOT / "ItemDisplayInfo.dbc").read_bytes())
    outfits = RawWdbc((HERE / "client-dbc-fixed" / "CharStartOutfit.dbc").read_bytes())
    merged_rows = {int.from_bytes(r[:4], "little"): r for r in merged.records}
    donor_rows = {int.from_bytes(r[:4], "little"): r for r in donor.records}

    fields = (1, 2, 3, 4, 5, 6) + tuple(range(15, 23))
    display_ids = {
        value
        for value in _start_outfit_display_ids(outfits.records)
        if value not in (0, 0xFFFFFFFF)
    }
    mismatched = []
    for display_id in sorted(display_ids):
        row = merged_rows.get(display_id)
        donor_row = donor_rows.get(display_id)
        if row is None or donor_row is None:
            mismatched.append((display_id, "missing row"))
            continue
        if strings_of(merged, row, fields) != strings_of(donor, donor_row, fields):
            mismatched.append((display_id, "string mismatch"))

    print(f"checked {len(display_ids)} display ids, mismatches: {len(mismatched)}")
    for entry in mismatched[:10]:
        print(f"    {entry}")
    if mismatched:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
