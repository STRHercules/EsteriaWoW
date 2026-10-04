"""Compare race 14/15 outfit + model chains between the backup and the live archive."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc, _start_outfit_display_ids  # noqa: E402

BACKUP = Path(
    r"G:\Ascension\Ascension\resources\ascension-live\Data\Backups"
    r"\patch-c-before-dbcfix-20260911-103259\Patch-C.MPQ"
)
LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")


def load(storm: Storm, archive: Path, table: str) -> RawWdbc:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        payload = storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)
    return RawWdbc(payload)


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "backslashreplace")


def safe(value: str) -> str:
    return "".join(character if 32 <= ord(character) < 127 else "?" for character in value)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, archive in (("backup", BACKUP), ("live", LIVE)):
        races = load(storm, archive, "ChrRaces")
        outfits = load(storm, archive, "CharStartOutfit")
        items = load(storm, archive, "ItemDisplayInfo")
        item_rows = {int.from_bytes(r[:4], "little"): r for r in items.records}
        print(f"=== {label} ===")
        for row in races.records:
            race = int.from_bytes(row[:4], "little")
            if race not in (14, 15, 18, 20):
                continue
            print(
                f"  race {race}: flags=0x{int.from_bytes(row[4:8], 'little'):02x} "
                f"file={safe(cstring(races.strings, int.from_bytes(row[44:48], 'little')))!r} "
                f"display={int.from_bytes(row[16:20], 'little')}/"
                f"{int.from_bytes(row[20:24], 'little')}"
            )
        for target in (14, 15):
            ids = set()
            for record in outfits.records:
                if record[4] != target:
                    continue
                ids.update(
                    int.from_bytes(record[o : o + 4], "little") for o in range(104, 200, 4)
                )
            ids.discard(0)
            ids.discard(0xFFFFFFFF)
            unresolved = [
                display_id
                for display_id in sorted(ids)
                if display_id not in item_rows
            ]
            print(f"  race {target} outfit display ids: {len(ids)} missing rows: {unresolved[:8]}")
            sample = sorted(ids)[:6]
            for display_id in sample:
                row = item_rows.get(display_id)
                if row is None:
                    continue
                models = [cstring(items.strings, int.from_bytes(row[f * 4 : f * 4 + 4], "little"))
                          for f in (1, 2)]
                textures = [cstring(items.strings, int.from_bytes(row[f * 4 : f * 4 + 4], "little"))
                            for f in range(15, 18)]
                print(
                    f"    {display_id}: models={[safe(m) for m in models]} "
                    f"textures={[safe(t) for t in textures if t]}"
                )


if __name__ == "__main__":
    main()
