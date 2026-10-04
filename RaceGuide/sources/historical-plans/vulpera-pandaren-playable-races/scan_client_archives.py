"""List which client archives carry the race/creation files and where they rank."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev"

TARGETS = (
    "dbfilesclient\\chrraces.dbc",
    "dbfilesclient\\charbaseinfo.dbc",
    "dbfilesclient\\charstartoutfit.dbc",
    "dbfilesclient\\charsections.dbc",
    "dbfilesclient\\charhairgeosets.dbc",
    "dbfilesclient\\charhairtextures.dbc",
    "dbfilesclient\\barbershopstyle.dbc",
    "dbfilesclient\\characterfacialhairstyles.dbc",
    "dbfilesclient\\namegen.dbc",
    "dbfilesclient\\skilllineability.dbc",
    "dbfilesclient\\skillraceclassinfo.dbc",
    "dbfilesclient\\creaturedisplayinfo.dbc",
    "dbfilesclient\\creaturemodeldata.dbc",
    "dbfilesclient\\itemdisplayinfo.dbc",
    "interface\\gluexml\\charactercreate.lua",
    "interface\\gluexml\\glueparent.lua",
    "interface\\gluexml\\characterinfo.lua",
    "interface\\gluexml\\charactercreate.xml",
)


def archive_priority(path: Path) -> tuple[int, str]:
    """Approximate Blizzard load order; higher wins."""
    name = path.name.casefold()
    stem = name[:-4]
    if stem.startswith("patch-") and len(stem) == 7 and stem[6].isdigit():
        return (10 + int(stem[6]), name)
    if stem.startswith("patch-") and len(stem) == 7 and stem[6].isalpha():
        return (100 + ord(stem[6]) - ord("a"), name)
    if stem.startswith("patch-") and stem.endswith("-2") is False and "-" in stem:
        suffix = stem.split("-")[-1]
        if len(suffix) == 1 and suffix.isalpha():
            return (100 + ord(suffix) - ord("a"), name)
    return (0, name)


def main() -> None:
    roots = [CLIENT / "Data", CLIENT / "Data" / "enUS"]
    archives = sorted(
        [path for root in roots if root.is_dir() for path in root.glob("*.MPQ")],
        key=archive_priority,
    )
    storm = Storm(DLL_DEFAULT)
    for path in archives:
        try:
            archive = storm.open_archive(path)
        except Exception as error:  # noqa: BLE001
            print(f"{path.name}: unreadable ({error})")
            continue
        try:
            names = {name.casefold(): name for name, *_ in storm.list_files(archive)}
            hits = []
            for target in TARGETS:
                actual = names.get(target)
                if actual is None:
                    continue
                payload = storm.read(archive, actual)
                hits.append(f"    {target.rsplit('\\', 1)[-1]}={len(payload)}")
            priority, _ = archive_priority(path)
            print(f"[{priority:>3}] {path.parent.name}/{path.name}  hits={len(hits)}")
            for hit in hits:
                print(hit)
        finally:
            storm.dll.SFileCloseArchive(archive)


if __name__ == "__main__":
    main()
