from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _read_string, _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm
from wod_model_migration import archive_names

CLIENT = Path(r"G:\3.3.5a - Dev")
ARCHIVES = [
    CLIENT / "Data" / "PATCH-A.MPQ",
    CLIENT / "Data" / "Patch-C.MPQ",
    CLIENT / "Data" / "Patch-Y.MPQ",
    CLIENT / "Data" / "patch-Z.MPQ",
    CLIENT / "Data" / "enUS" / "patch-enUS-Z.MPQ",
]
STOCK_RACES = {1, 2, 3, 4, 5, 6, 7, 8, 10, 11}
WATCH_DISPLAYS = (49, 50, 55, 56, 141284, 141285, 141673, 141674, 49000, 49001, 49006, 49007)
WATCH_MODELS = (49, 50, 55, 56, 112887, 112888, 112915, 112916)


def read_table(storm: Storm, archive: Path, table_name: str):
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        actual = names.get(f"dbfilesclient\\{table_name.lower()}.dbc")
        if actual is None:
            return None
        return _table(storm.read(handle, actual), table_name)
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    for archive in ARCHIVES:
        if not archive.exists():
            continue
        print(f"\n### {archive}")
        races = read_table(storm, archive, "ChrRaces")
        if races is not None:
            pairs = [
                (_u32(row, 0), _u32(row, 4), _u32(row, 5))
                for row in races.records
                if _u32(row, 0) in STOCK_RACES
            ]
            print("ChrRaces stock pairs:", pairs)
        else:
            print("ChrRaces: missing")

        displays = read_table(storm, archive, "CreatureDisplayInfo")
        if displays is not None:
            by_id = {_u32(row, 0): row for row in displays.records}
            print("CreatureDisplayInfo watched rows:")
            for display_id in WATCH_DISPLAYS:
                row = by_id.get(display_id)
                if row is None:
                    continue
                tex = []
                for field in range(6, 10):
                    try:
                        tex.append(_read_string(displays.strings, _u32(row, field)).decode("latin1"))
                    except Exception as exc:
                        tex.append(f"<ERR:{exc}>")
                print(
                    f"  {display_id}: model={_u32(row, 1)} extra={_u32(row, 3)} "
                    f"tex={tex}"
                )
        else:
            print("CreatureDisplayInfo: missing")

        models = read_table(storm, archive, "CreatureModelData")
        if models is not None:
            by_id = {_u32(row, 0): row for row in models.records}
            print("CreatureModelData watched rows:")
            for model_id in WATCH_MODELS:
                row = by_id.get(model_id)
                if row is None:
                    continue
                try:
                    path = _read_string(models.strings, _u32(row, 2)).decode("latin1")
                except Exception as exc:
                    path = f"<ERR:{exc}>"
                print(f"  {model_id}: path={path}")
        else:
            print("CreatureModelData: missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
