"""Finish the Eredar player-model conversion by copying the port's edits from the Lightforged.

The donor's Eredar player model and the donor's Lightforged model are the same mesh (23,816,416
vs 23,816,432 bytes, identical header arrays and identical texture-replace tables). Our shipped
Lightforged renders correctly because the port edited it; this finds those edits by diffing the
two Lightforged copies and replays them onto the Eredar, matching each difference to its array
entry through the file's own header offsets (the Eredar is 16 bytes shorter, so raw offsets do
not line up).
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq",
                  "Patch-6.mpq", "Patch-7.mpq")
CLIENT = REPO / "3.3.5a - Dev/Data"
PATCH_D = CLIENT / "Patch-D.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
LF_DONOR = r"character\lightforgeddraenei\male\lightforgeddraeneimale.m2"
LF_OURS = r"character\LightforgedDraenei\Male\LightforgedDraeneiMale.m2"
EREDAR_OURS = r"Character\Eredar\Male\EredarMale.m2"
EREDAR_DONOR = r"character\eredar\male\race_eredarmale.m2"


def open_archives(storm: Storm, root: Path, names: tuple[str, ...]) -> list:
    handles = []
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append(handle)
    return handles


def read(storm: Storm, handles: list, key: str) -> bytes | None:
    for handle in handles:
        try:
            return storm.read(handle, key)
        except Exception:
            continue
    return None


def arrays(data: bytes) -> list[tuple[int, int, int]]:
    """(count, offset, header_offset) for every plausible array descriptor in the header."""
    found = []
    for header_offset in range(0x40, 0x120, 4):
        count, offset = struct.unpack_from("<II", data, header_offset)
        if 0 < count < 200000 and 0 < offset < len(data) and offset + 4 <= len(data):
            found.append((count, offset, header_offset))
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    ours = open_archives(storm, CLIENT, ("Patch-Y.MPQ", "PATCH-X.MPQ", "Patch-G.MPQ", "Patch-E.MPQ", "Patch-D.MPQ"))
    donor = open_archives(storm, DONOR, DONOR_ARCHIVES)
    try:
        lf_donor = read(storm, donor, LF_DONOR)
        lf_ours = read(storm, ours, LF_OURS)
        ered = read(storm, ours, EREDAR_OURS)
        if not all((lf_donor, lf_ours, ered)):
            raise SystemExit(f"missing input (donor lf={bool(lf_donor)}, ours lf={bool(lf_ours)}, eredar={bool(ered)})")
        print(f"donor lightforged {len(lf_donor):,}   ours lightforged {len(lf_ours):,}   eredar {len(ered):,}")
        if len(lf_donor) != len(lf_ours):
            raise SystemExit("lightforged copies differ in size; cannot diff directly")

        differences = [index for index in range(len(lf_donor)) if lf_donor[index] != lf_ours[index]]
        runs: list[tuple[int, int]] = []
        for index in differences:
            if runs and index == runs[-1][1] + 1:
                runs[-1] = (runs[-1][0], index)
            else:
                runs.append((index, index))
        print(f"byte differences: {len(differences)} in {len(runs)} runs")
        for start, end in runs[:40]:
            print(f"   {start:#x}..{end:#x}: donor={lf_donor[start:end+1].hex()} ours={lf_ours[start:end+1].hex()}")

        # Map each run to the array entry it belongs to, using our lightforged header offsets,
        # then write the same value into the Eredar's matching entry.
        patched = bytearray(ered)
        ered_arrays = arrays(ered)
        applied = 0
        for start, end in runs:
            size = end - start + 1
            target_array = None
            for count, offset, header_offset in arrays(lf_ours):
                stride = None
                for candidate in (4, 8, 20, 24, 28, 32, 40, 44, 48, 56, 88):
                    if count * candidate and offset + count * candidate > len(lf_ours):
                        continue
                    index, remainder = divmod(start - offset, candidate)
                    if 0 <= index < count and remainder + size <= candidate:
                        stride, entry_index = candidate, index
                        break
                if stride:
                    target_array = (count, offset, header_offset)
                    break
            if target_array is None:
                print(f"   ! run {start:#x} not inside any known array - skipped")
                continue
            _, _, header_offset = target_array
            ered_count, ered_offset = struct.unpack_from("<II", ered, header_offset)
            if ered_count != target_array[0]:
                print(f"   ! array at {header_offset:#x} has {ered_count} vs {target_array[0]} entries - skipped")
                continue
            for candidate in (4, 8, 20, 24, 28, 32, 40, 44, 48, 56, 88):
                index, remainder = divmod(start - target_array[1], candidate)
                if 0 <= index < ered_count and remainder + size <= candidate:
                    dest = ered_offset + index * candidate + remainder
                    patched[dest : dest + size] = lf_ours[start : end + 1]
                    applied += 1
                    break
        print(f"edits replayed onto the Eredar: {applied}/{len(runs)}")
        if args.dry_run:
            print("dry run - Patch-D untouched")
            return
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = BACKUP_ROOT / f"patch-d-before-eredar-conversion-{stamp}"
        backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PATCH_D, backup / "Patch-D.MPQ")
        storm.replace_archive_entries(PATCH_D, {EREDAR_OURS: bytes(patched)})
        print(f"Patch-D updated ({PATCH_D.stat().st_size:,} bytes), backup {backup}")
    finally:
        for handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
