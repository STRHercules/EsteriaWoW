from __future__ import annotations

import collections
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _read_string, _u32
from playable_race_pack import RawWdbc

ROOT = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
RACES = (1, 2, 3, 4, 5, 6, 7, 8, 10, 11)


def main() -> int:
    sections = RawWdbc((ROOT / "HDCharSections.dbc").read_bytes())
    print("HDCharSections prefixes")
    for race in RACES:
        prefixes: collections.Counter[str] = collections.Counter()
        rows = 0
        for record in sections.records:
            if _u32(record, 1) != race:
                continue
            rows += 1
            for field in (4, 5, 6):
                value = _read_string(sections.strings, _u32(record, field)).decode("latin1", "ignore")
                if not value:
                    continue
                parts = value.replace("/", "\\").split("\\")
                prefixes[parts[1] if len(parts) > 1 else parts[0]] += 1
        print(f"race {race}: rows={rows} prefixes={prefixes.most_common(8)}")

    facial = RawWdbc((ROOT / "HDCharacterFacialHairStyles.dbc").read_bytes())
    print("\nHD facial rows by race/sex")
    for race in RACES:
        for sex in (0, 1):
            count = sum(
                1
                for record in facial.records
                if _u32(record, 1) == race and _u32(record, 2) == sex
            )
            print(f"race {race} sex {sex}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
