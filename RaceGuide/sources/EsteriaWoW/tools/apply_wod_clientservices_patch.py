from __future__ import annotations

import argparse
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

PATCH_OFFSET = 0x2B1F48
EXPECTED_BEFORE = bytes.fromhex("7421687203000068")
EXPECTED_AFTER = bytes.fromhex("eb21687203000068")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the WoD donor ClientServices branch patch to Esteria Wow.exe")
    parser.add_argument("--client-exe", type=Path, default=Path(r"G:\3.3.5a - Dev\Wow.exe"))
    parser.add_argument("--donor-exe", type=Path, default=Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)\Wow.exe"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = args.client_exe
    donor = args.donor_exe
    if not client.is_file():
        raise FileNotFoundError(client)
    if not donor.is_file():
        raise FileNotFoundError(donor)

    client_data = client.read_bytes()
    donor_data = donor.read_bytes()
    client_window = client_data[PATCH_OFFSET:PATCH_OFFSET + len(EXPECTED_BEFORE)]
    donor_window = donor_data[PATCH_OFFSET:PATCH_OFFSET + len(EXPECTED_AFTER)]

    print(f"client={client}")
    print(f"client_sha256={sha256(client)}")
    print(f"donor_sha256={sha256(donor)}")
    print(f"offset=0x{PATCH_OFFSET:X}")
    print(f"client_window={client_window.hex()}")
    print(f"donor_window={donor_window.hex()}")

    if donor_window != EXPECTED_AFTER:
        raise RuntimeError(f"donor no longer matches expected patch bytes: {donor_window.hex()}")
    if client_window == EXPECTED_AFTER:
        print("already_patched=true")
        return 0
    if client_window != EXPECTED_BEFORE:
        raise RuntimeError(f"client bytes are not the expected stock branch: {client_window.hex()}")

    if not args.apply:
        print("would_patch=true")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = client.parent / "Backups" / f"wod-exe-patch-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup = backup_dir / client.name
    shutil.copy2(client, backup)

    patched = bytearray(client_data)
    patched[PATCH_OFFSET] = 0xEB
    client.write_bytes(patched)

    verify = client.read_bytes()[PATCH_OFFSET:PATCH_OFFSET + len(EXPECTED_AFTER)]
    if verify != EXPECTED_AFTER:
        shutil.copy2(backup, client)
        raise RuntimeError(f"post-write verification failed: {verify.hex()}; original restored")

    print(f"backup={backup}")
    print(f"patched_sha256={sha256(client)}")
    print("patched=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
