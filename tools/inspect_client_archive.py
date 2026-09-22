"""Read-only StormLib inspector for the active WotLK client archives."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--match", default="")
    parser.add_argument("--extract", nargs="*", default=[])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    args = parser.parse_args()

    storm = Storm(args.stormlib)
    handle = storm.open_archive(args.archive)
    try:
        for name in sorted((name for name, *_ in storm.list_files(handle)), key=str.casefold):
            if args.match.casefold() in name.casefold():
                print(name)
        for wanted in args.extract:
            payload = storm.read(handle, wanted)
            args.out.mkdir(parents=True, exist_ok=True)
            target = args.out / Path(wanted.replace("\\", "/")).name
            target.write_bytes(payload)
            print(f"extracted {wanted} -> {target} ({len(payload)} bytes)")
    finally:
        storm.dll.SFileCloseArchive(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
