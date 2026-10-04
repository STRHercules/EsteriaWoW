"""Compare animation file sets between custom race models."""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = ("Data/PATCH-A.MPQ", "Data/Patch-C.MPQ")
PREFIXES = {
    "sethrak_male": "character\\sethrak\\male\\sethrakmale",
    "broken_male": "character\\esteriabroken\\male\\brokenmale",
    "vulpera_male": "character\\vulpera\\male\\vulperamale",
    "pandaren_male": "character\\pandaren\\male\\pandarenmale",
}


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    names: set[str] = set()
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        handle = storm.open_archive(path)
        try:
            names |= {n.casefold() for n, *_ in storm.list_files(handle)}
        finally:
            storm.dll.SFileCloseArchive(handle)

    for label, prefix in PREFIXES.items():
        anims = sorted(
            n.rsplit("\\", 1)[-1]
            for n in names
            if n.startswith(prefix) and n.endswith(".anim")
        )
        others = sorted(
            n.rsplit("\\", 1)[-1]
            for n in names
            if n.startswith(prefix) and not n.endswith(".anim")
        )
        ids = sorted({re.match(r".*?(\d{2,4})-", name).group(1) for name in anims if re.match(r".*?(\d{2,4})-", name)})
        print(f"{label}: anim={len(anims)} files, base={others}")
        print(f"    anim ids: {ids}")


if __name__ == "__main__":
    main()
