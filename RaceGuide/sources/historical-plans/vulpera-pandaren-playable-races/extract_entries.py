"""Extract selected archive entries to a folder for inspection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("names", nargs="+")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    archive = storm.open_archive(args.archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(archive)}
        args.out.mkdir(parents=True, exist_ok=True)
        for wanted in args.names:
            actual = names.get(wanted.casefold())
            if actual is None:
                print(f"missing: {wanted}")
                continue
            payload = storm.read(archive, actual)
            destination = args.out / Path(actual).name
            destination.write_bytes(payload)
            print(f"{destination.name}: {len(payload)} bytes")
    finally:
        storm.dll.SFileCloseArchive(archive)


if __name__ == "__main__":
    main()
