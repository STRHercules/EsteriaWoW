"""Resolve target race display -> model path -> asset presence in Patch-C."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"


def cstring(pool: bytes, offset: int) -> str:
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    chr_races = RawWdbc((HERE / "client-dbc-extract" / "ChrRaces.dbc").read_bytes())
    displays = RawWdbc((HERE / "client-dbc-extract" / "CreatureDisplayInfo.dbc").read_bytes())
    models = RawWdbc((HERE / "client-dbc-extract" / "CreatureModelData.dbc").read_bytes())
    display_rows = {int.from_bytes(r[:4], "little"): r for r in displays.records}
    model_rows = {int.from_bytes(r[:4], "little"): r for r in models.records}

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(CLIENT / "Data" / "Patch-C.MPQ")
    try:
        names = {name.casefold() for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)

    for race in (18, 20):
        row = next(r for r in chr_races.records if int.from_bytes(r[:4], "little") == race)
        for field, label in ((16, "male"), (20, "female")):
            display_id = int.from_bytes(row[field : field + 4], "little")
            display = display_rows[display_id]
            model_id = int.from_bytes(display[4:8], "little")
            model = model_rows[model_id]
            path_field = int.from_bytes(model[8:12], "little")
            model_path = cstring(models.strings, path_field)
            base = model_path.rsplit(".", 1)[0]
            present = [
                name
                for name in names
                if name.startswith(model_path.casefold().replace("/", "\\"))
            ]
            print(
                f"race {race} {label}: display={display_id} model={model_id} "
                f"path={model_path} archive_hits={len(present)}"
            )
            for name in sorted(present)[:4]:
                print(f"    {name}")
            if not present:
                print(f"    (no archive entries starting with {base})")


if __name__ == "__main__":
    main()
