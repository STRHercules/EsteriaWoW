from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _read_string, _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm
from wod_model_migration import archive_names

BACKUP = Path(r"G:\3.3.5a - Dev\Backups\ascension-hd-replacement-20260928-020737\patch-enUS-Z.MPQ")
LIVE = Path(r"G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ")
ASCENSION = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")

DISPLAY_IDS = {
    141284, 141285, 141286, 141287, 141669, 141670, 141671, 141672, 141673, 141674,
    141675, 141676, 141677, 141678, 141679, 141680, 141681, 141682, 141683, 141684,
}
MODEL_IDS = {
    112887, 112888, 112889, 112890, 112911, 112912, 112913, 112914, 112915, 112916,
    112917, 112918, 112919, 112920, 112921, 112922, 112923, 112924, 112925, 112926,
}


def archive_table(storm: Storm, archive: Path, table_name: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        return storm.read(handle, names[(f"DBFilesClient\\{table_name}.dbc").casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)


def dump_rows(label: str, data: bytes, table_name: str, wanted: set[int]) -> None:
    table = _table(data, table_name)
    counts = Counter(_u32(row, 0) for row in table.records)
    print(f"\n{label} {table_name}: total_rows={len(table.records)} duplicates={sum(1 for n in counts.values() if n > 1)}")
    for row_id in sorted(wanted):
        rows = [row for row in table.records if _u32(row, 0) == row_id]
        if not rows:
            continue
        for idx, row in enumerate(rows):
            values = [_u32(row, field) for field in range(min(table.fields, 8))]
            suffix = ""
            if table_name == "CreatureModelData":
                path_off = _u32(row, 2)
                if path_off:
                    suffix = " path=" + _read_string(table.strings, path_off).decode("utf-8", "replace")
            print(f"  id={row_id} occurrence={idx + 1}/{len(rows)} values={values}{suffix}")


def dump_chr_races(label: str, data: bytes) -> None:
    table = _table(data, "ChrRaces")
    print(f"\n{label} ChrRaces stock display pairs")
    for race in (1, 2, 3, 4, 5, 6, 7, 8, 10, 11):
        rows = [row for row in table.records if _u32(row, 0) == race]
        print(f"  race={race} count={len(rows)} pairs={[( _u32(r,4), _u32(r,5)) for r in rows]}")


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    ascension = {name: (ASCENSION / f"{name}.dbc").read_bytes() for name in ("ChrRaces", "CreatureDisplayInfo", "CreatureModelData")}
    backup = {name: archive_table(storm, BACKUP, name) for name in ("ChrRaces", "CreatureDisplayInfo", "CreatureModelData")}
    live = {name: archive_table(storm, LIVE, name) for name in ("ChrRaces", "CreatureDisplayInfo", "CreatureModelData")}

    dump_chr_races("BACKUP", backup["ChrRaces"])
    dump_chr_races("LIVE", live["ChrRaces"])
    dump_chr_races("ASCENSION", ascension["ChrRaces"])

    for table_name, wanted in (("CreatureDisplayInfo", DISPLAY_IDS), ("CreatureModelData", MODEL_IDS)):
        dump_rows("BACKUP", backup[table_name], table_name, wanted)
        dump_rows("LIVE", live[table_name], table_name, wanted)
        dump_rows("ASCENSION", ascension[table_name], table_name, wanted)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
