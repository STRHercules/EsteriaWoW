"""Merge the ElvUI glue reskin into the live client patch archives.

Targets patch-Z.MPQ (root) and patch-enUS-Z.MPQ (locale) -- the highest-priority
archives, which is the same convention the existing custom race glue work uses.

Verification built in:
  * records entry counts before/after
  * re-reads a sample of PRE-EXISTING entries and confirms their bytes are unchanged
  * re-reads every newly written entry and confirms the bytes round-trip
"""

from __future__ import annotations

import ctypes as c
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT, H  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = Path(r"G:\3.3.5a - Dev\Data")
STAGING_ROOT = HERE / "staging" / "root"
STAGING_LOCALE = HERE / "staging" / "locale"

TARGETS = [
    DATA / "patch-Z.MPQ",
    DATA / "enUS" / "patch-enUS-Z.MPQ",
]

# pre-existing entries we will sample to prove the merge did not damage anything
SAMPLE_EXISTING = [
    r"Interface\Glues\CharacterCreate\UI-CharacterCreate-BloodElfMale.blp",
    r"Interface\GlueXML\CharacterSelect.lua",
    r"Interface\Glues\CharacterSelect\FreebornLogo.blp",
]


def list_safe(storm: Storm, archive) -> list[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return []
    out: list[str] = []
    try:
        while True:
            out.append(data.cFileName.split(b"\0", 1)[0].decode("latin-1"))
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


def collect(staging: Path) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    if not staging.exists():
        return entries
    for path in sorted(staging.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(staging).as_posix()
        entries[rel.replace("/", "\\")] = path.read_bytes()
    return entries


def main() -> int:
    entries = collect(STAGING_ROOT)
    locale_entries = collect(STAGING_LOCALE)
    print(f"staged root entries  : {len(entries)}")
    print(f"staged locale entries: {len(locale_entries)}")
    for name in sorted({**entries, **locale_entries}):
        print(f"    {name}")

    storm = Storm(DLL_DEFAULT)
    failures = 0

    for archive_path in TARGETS:
        if not archive_path.exists():
            print(f"\n!! missing archive {archive_path}")
            failures += 1
            continue

        handle = storm.open_archive(archive_path)
        try:
            before = list_safe(storm, handle)
            lowered = {n.casefold() for n in before}
            before_bytes = {}
            for sample in SAMPLE_EXISTING:
                if sample.casefold() in lowered:
                    before_bytes[sample] = storm.read(handle, sample)
        finally:
            storm.dll.SFileCloseArchive(handle)

        payloads = {**entries, **locale_entries}
        print(f"\n=== {archive_path.name}: {len(before)} entries before, adding {len(payloads)} ===")

        storm.replace_archive_entries(archive_path, payloads)

        handle = storm.open_archive(archive_path)
        try:
            after = list_safe(storm, handle)
            after_lower = {n.casefold() for n in after}
            print(f"    entries after: {len(after)} (delta {len(after) - len(before):+d})")

            # 1) new entries round-trip
            bad = 0
            for name, payload in payloads.items():
                if name.casefold() not in after_lower:
                    print(f"    MISSING after write: {name}")
                    bad += 1
                    continue
                got = storm.read(handle, name)
                if got != payload:
                    print(f"    MISMATCH: {name} (wrote {len(payload)}, read {len(got)})")
                    bad += 1
            print(f"    new entries verified: {len(payloads) - bad}/{len(payloads)}")

            # 2) pre-existing entries untouched
            for sample, original in before_bytes.items():
                if sample.casefold() not in after_lower:
                    print(f"    REGRESSION: pre-existing {sample} vanished")
                    bad += 1
                    continue
                got = storm.read(handle, sample)
                same = got == original
                print(
                    f"    pre-existing {sample}: "
                    f"{'unchanged' if same else 'CHANGED'} "
                    f"sha={hashlib.sha256(got).hexdigest()[:12]}"
                )
                if not same:
                    bad += 1
            failures += bad
        finally:
            storm.dll.SFileCloseArchive(handle)

    print(f"\n{'ALL CHECKS PASSED' if failures == 0 else f'{failures} FAILURES'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
