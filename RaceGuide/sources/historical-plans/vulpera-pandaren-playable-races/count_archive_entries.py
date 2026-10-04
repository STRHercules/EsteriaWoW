"""Compare entry counts between two archives."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for path in sys.argv[1:]:
        handle = storm.open_archive(Path(path))
        try:
            names = [name for name, *_ in storm.list_files(handle)]
        finally:
            storm.dll.SFileCloseArchive(handle)
        print(f"{Path(path).name}: {len(names)} entries")


if __name__ == "__main__":
    main()
