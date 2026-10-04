"""Compare CharSections section types/variations for races 18 and 20."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(storm.read(handle, names["dbfilesclient\\charsections.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    def text(offset: int) -> str:
        if not offset:
            return ""
        end = table.strings.find(b"\x00", offset)
        return table.strings[offset:end].decode("ascii", "replace")

    for race in (18, 20):
        rows = [record for record in table.records if int.from_bytes(record[4:8], "little") == race]
        summary: Counter[tuple[int, int]] = Counter()
        variations: dict[tuple[int, int], set[int]] = {}
        for record in rows:
            gender = int.from_bytes(record[8:12], "little")
            section = int.from_bytes(record[12:16], "little")
            variation = int.from_bytes(record[36:40], "little")
            summary[(gender, section)] += 1
            variations.setdefault((gender, section), set()).add(variation)
        total_textured = sum(
            1
            for record in rows
            for field in (4, 5, 6)
            if text(int.from_bytes(record[field * 4 : field * 4 + 4], "little"))
        )
        print(f"== race {race}: {len(rows)} rows, {total_textured} texture refs ==")
        for key in sorted(summary):
            print(f"    gender={key[0]} section={key[1]}: rows={summary[key]} "
                  f"variations={sorted(variations[key])[:8]}")


if __name__ == "__main__":
    main()
