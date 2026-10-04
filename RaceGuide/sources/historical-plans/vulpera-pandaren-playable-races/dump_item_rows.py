"""Print selected ItemDisplayInfo rows from an archive."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402


def main() -> None:
    archive = Path(sys.argv[1])
    ids = {int(value) for value in sys.argv[2:]}
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(storm.read(handle, names["dbfilesclient\\itemdisplayinfo.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    def text(offset: int) -> str:
        if not offset:
            return ""
        end = table.strings.find(b"\x00", offset)
        return table.strings[offset:end].decode("ascii", "replace")

    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id not in ids:
            continue
        models = [text(int.from_bytes(record[f * 4 : f * 4 + 4], "little")) for f in (1, 2)]
        textures = [
            text(int.from_bytes(record[f * 4 : f * 4 + 4], "little")) for f in range(15, 23)
        ]
        print(f"{row_id}: models={models}")
        print(f"     textures={[t for t in textures if t]}")


if __name__ == "__main__":
    main()
