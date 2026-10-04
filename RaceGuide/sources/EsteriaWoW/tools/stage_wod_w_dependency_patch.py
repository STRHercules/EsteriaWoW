"""Stage or remove the donor WoD patch-w archive as a lower-priority dependency patch.

This preserves the donor MPQ's internal filename hashes, including anonymous
entries that cannot be recovered from its listfile.  The live Esteria patch-Z
remains higher priority and therefore continues to win for the 12,701 X assets
already verified byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)\Data\patch-w.mpq")
TARGET = Path(r"G:\3.3.5a - Dev\Data\patch-T.MPQ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("apply", "remove", "status"))
    args = parser.parse_args()

    if args.action == "status":
        print(f"donor_exists={DONOR.is_file()}")
        print(f"target_exists={TARGET.is_file()}")
        if DONOR.is_file():
            print(f"donor_sha256={sha256(DONOR)}")
        if TARGET.is_file():
            print(f"target_sha256={sha256(TARGET)}")
        return 0

    if args.action == "remove":
        if TARGET.exists():
            TARGET.unlink()
            print(f"removed {TARGET}")
        else:
            print(f"already absent {TARGET}")
        return 0

    if not DONOR.is_file():
        raise SystemExit(f"donor archive missing: {DONOR}")
    donor_hash = sha256(DONOR)
    if TARGET.exists():
        target_hash = sha256(TARGET)
        if target_hash == donor_hash:
            print(f"already staged {TARGET}")
            print(f"sha256={target_hash}")
            return 0
        raise SystemExit(f"refusing to overwrite existing unrelated archive: {TARGET}")

    shutil.copy2(DONOR, TARGET)
    target_hash = sha256(TARGET)
    if target_hash != donor_hash:
        TARGET.unlink(missing_ok=True)
        raise SystemExit("copied archive hash mismatch; removed staged target")

    print(f"staged {TARGET}")
    print(f"size={TARGET.stat().st_size}")
    print(f"sha256={target_hash}")
    print("patch-Z remains higher priority; this archive only supplies lower-priority donor W content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
