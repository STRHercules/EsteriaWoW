"""Verify target race display/model chains across the winning archives."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev"
ARCHIVES = {"Patch-C": CLIENT / "Data" / "Patch-C.MPQ", "PATCH-X": CLIENT / "Data" / "PATCH-X.MPQ"}


def load(storm: Storm, archive: Path, inner: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return storm.read(handle, names[inner.casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    chr_races = RawWdbc(load(storm, ARCHIVES["Patch-C"], "DBFilesClient\\ChrRaces.dbc"))
    models: dict[str, dict[int, bytes]] = {}
    for label, path in ARCHIVES.items():
        table = RawWdbc(load(storm, path, "DBFilesClient\\CreatureModelData.dbc"))
        models[label] = {int.from_bytes(row[:4], "little"): row for row in table.records}
    displays: dict[str, dict[int, bytes]] = {}
    for label, path in ARCHIVES.items():
        table = RawWdbc(load(storm, path, "DBFilesClient\\CreatureDisplayInfo.dbc"))
        displays[label] = {int.from_bytes(row[:4], "little"): row for row in table.records}

    for race in (18, 20, 26):
        row = next((r for r in chr_races.records if int.from_bytes(r[:4], "little") == race), None)
        if row is None:
            print(f"race {race}: absent from Patch-C ChrRaces")
            continue
        race_model = int.from_bytes(row[8:12], "little")
        print(f"race {race}: faction={int.from_bytes(row[8:12], 'little')} "
              f"model18={int.from_bytes(row[16:20], 'little')} model20={int.from_bytes(row[20:24], 'little')}")
        for field in (16, 20):
            display_id = int.from_bytes(row[field : field + 4], "little")
            for label in ARCHIVES:
                display = displays[label].get(display_id)
                if display is None:
                    print(f"  display {display_id}: MISSING in {label}")
                    continue
                model_id = int.from_bytes(display[4:8], "little")
                model = models[label].get(model_id)
                print(f"  display {display_id} in {label}: model={model_id} present={model is not None}")


if __name__ == "__main__":
    main()
