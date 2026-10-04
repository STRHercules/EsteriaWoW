"""Make helmets (and other head components) resolve for every custom race.

Wow.exe builds the model path in the item-component code at 0x732100:

    sprintf(buffer, "%s%s_%s%s.mdx", path, modelName, ChrRaces->ClientPrefix, sex)

`path` is `Item\\ObjectComponents\\Head\\` (0x9f6c0c), `modelName` comes from
`ItemDisplayInfo.ModelName`, and `ClientPrefix` is `ChrRaces` field 6 - the code
reads it as `[row + 0x18]`.  When the resulting file is absent the client draws its
white/blue missing-model cube.

Our port invented per-race prefixes (`Er`, `Nb`, `Ve`, `Lf`, `Za`, `Di`, `Kt`, `Il`)
that no archive supplies, which is why every ported race cubes its helm while race 14
(Broken, prefix `Bk`) renders fine - Patch-C ships a full `_Bk` model set.

The donor client solves it by pointing each race at a code it already ships a set for
(Eredar -> Draenei, Zandalari -> Troll, Void Elf/Illidari -> Blood Elf, ...); Pandaren
and Vulpera carry dedicated `_Pa`/`_Vu` sets.  Staging fills only the names the client
cannot already resolve - the donor's copy where it has one, otherwise a borrowed stock
model - so stock art is never overwritten.  `--stage-code` stages an extra code (for
experiments) without editing STAGE_CODES.

Usage:
    python fix_item_component_prefixes.py --dry-run
    python fix_item_component_prefixes.py
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import re
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
PATCH_Y = CLIENT / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
DONOR = Path(r"G:\Eunoia\Client\data")
CHRRACES = "DBFilesClient\\ChrRaces.dbc"
ITEM_DISPLAY_INFO = "DBFilesClient\\ItemDisplayInfo.dbc"
LISTFILE = "(listfile)"

# Low priority first; the last archive that holds a file wins.
DONOR_ORDER = ("common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq")
OUR_ORDER = ("common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ")

# race -> ClientPrefix, matching the donor's own ChrRaces rows.
PREFIXES = {
    14: "Bk",  # Broken - Patch-C already ships the whole _Bk set
    15: "Tr",  # Sethrak - no dedicated set; Troll is the closest body
    16: "Dr",  # Eredar        <- donor uses the Draenei set
    17: "Ni",  # Nightborne    <- donor uses the Night Elf set
    18: "Pa",  # Pandaren      <- dedicated donor set, staged below
    19: "Be",  # Void Elf      <- donor uses the Blood Elf set
    20: "Vu",  # Vulpera       <- dedicated donor set, staged below
    21: "Dr",  # Lightforged   <- donor uses the Draenei set
    22: "Tr",  # Zandalari     <- donor uses the Troll set
    23: "Dw",  # Dark Iron     <- donor uses the Dwarf set
    28: "Be",  # Dracthyr      <- donor uses the Blood Elf set
    29: "Ni",  # Kul Tiran     <- donor uses the Night Elf set
    30: "Be",  # Illidari (Horde)   <- donor uses the Blood Elf set
    31: "Ni",  # Illidari (Alliance)-> donor uses the Night Elf set
}
STAGE_CODES = ("Pa", "Vu")
FALLBACK_CODES = ("Hu", "Ni", "Be", "Or", "Ta")
HEAD = "Item\\ObjectComponents\\Head\\"


def open_archives(storm: Storm, root: Path, names) -> list[tuple[str, H]]:
    handles = []
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    return handles


def read(storm: Storm, handles, key: str) -> tuple[str | None, bytes | None]:
    for name, handle in reversed(handles):
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None, None


def list_names(storm: Storm, handles, prefix: str) -> list[str]:
    names = []
    for _name, handle in handles:
        try:
            listing = storm.list_files(handle)
        except Exception:
            continue
        names.extend(entry[0] for entry in listing if entry[0].lower().startswith(prefix))
    return names


def intern(pool: bytearray, text: str) -> int:
    encoded = text.encode("ascii")
    needle = b"\0" + encoded + b"\0"
    index = pool.find(needle)
    while index > 0:
        start = index + 1
        if pool.rfind(b"\0", 0, start) == index:
            return start
        index = pool.find(needle, index + 1)
    offset = len(pool)
    pool.extend(encoded + b"\0")
    return offset


def rebuild(table: Wdbc, rows: list[list[int]]) -> bytes:
    body = b"".join(struct.pack(f"<{table.fields}I", *(v & 0xFFFFFFFF for v in row))
                    for row in rows)
    return (struct.pack("<4s4I", b"WDBC", len(rows), table.fields, table.record_size,
                        len(table.strings))
            + body + bytes(table.strings))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", action="append", default=[], metavar="RACE=CODE",
                        help="override one race's ClientPrefix, repeatable")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-stage", action="store_true")
    parser.add_argument("--stage-code", action="append", default=[], metavar="CODE",
                        help="stage this code instead of STAGE_CODES (repeatable)")
    parser.add_argument("--force-stage", action="store_true",
                        help="re-stage names the client already resolves")
    args = parser.parse_args()
    for item in args.set:
        race, _sep, code = item.partition("=")
        PREFIXES[int(race)] = code
    stage_codes = tuple(args.stage_code) or STAGE_CODES

    storm = Storm(DLL_DEFAULT)
    ours = open_archives(storm, CLIENT, OUR_ORDER)
    donor = open_archives(storm, DONOR, DONOR_ORDER)
    patch_y = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0, ctypes.byref(patch_y)):
        raise SystemExit("cannot open Patch-Y")
    entries: dict[str, bytes] = {}
    try:
        payload = storm.read(patch_y, CHRRACES)
        table = Wdbc(payload)
        pool = bytearray(table.strings)
        rows = [list(row) for row in table.rows]
        print(f"{CHRRACES}: {len(rows)} rows, {table.fields} fields")
        changed = 0
        for row in rows:
            race = row[0]
            if race not in PREFIXES:
                continue
            old = table.text(row[6])
            new = PREFIXES[race]
            if old == new:
                continue
            row[6] = intern(pool, new)
            print(f"   race {race:>2}: prefix {old!r} -> {new!r}")
            changed += 1
        if not changed:
            print("   prefixes already correct")
        else:
            entries[CHRRACES] = (struct.pack("<4s4I", b"WDBC", len(rows), table.fields,
                                             table.record_size, len(pool))
                                 + b"".join(struct.pack(f"<{table.fields}I",
                                                        *(v & 0xFFFFFFFF for v in row))
                                            for row in rows)
                                 + bytes(pool))

        if not args.skip_stage:
            pattern = re.compile(r"_[A-Za-z]{2}[MF](\d\d)?\.(m2|skin|mdx)$", re.IGNORECASE)
            shipped: dict[str, str] = {}
            sources: dict[str, list[str]] = {}
            stems = set()
            for name in list_names(storm, ours, HEAD.lower()):
                tail = name[len(HEAD):]
                shipped.setdefault(tail.lower(), name)
                match = pattern.search(tail)
                if not match:
                    continue
                stem = tail[: match.start()]
                stems.add(stem)
                if tail.lower().endswith(".m2"):
                    sources.setdefault(stem.lower(), []).append(tail)
            print(f"head component stems our client already ships: {len(stems)}")

            def borrow(tail_stem: str, suffix: str) -> tuple[bytes | None, str | None]:
                """Any code/sex of the same stem, model and skin from one source."""
                for source in sources.get(tail_stem.lower(), ()):
                    model = read(storm, ours, f"{HEAD}{source}")
                    skin = read(storm, ours, f"{HEAD}{source[:-3]}00.skin")
                    if model[1] is None or skin[1] is None:
                        continue
                    if suffix.endswith(".skin"):
                        return skin[1], source
                    return model[1], source
                return None, None

            wanted: dict[str, str] = {}
            for stem in sorted(stems):
                for code in stage_codes:
                    for sex in ("M", "F"):
                        for suffix in (".m2", "00.skin"):
                            key = f"{HEAD}{stem}_{code}{sex}{suffix}"
                            wanted.setdefault(key.lower(), key)

            total = 0
            already = 0
            borrowed = []
            missing = []
            for key in sorted(wanted.values()):
                if not args.force_stage and read(storm, ours, key)[1] is not None:
                    already += 1
                    continue
                _source, blob = read(storm, donor, key)
                note = None
                if blob is None:
                    tail = key[len(HEAD):]
                    stem, _sep, rest = tail.rpartition("_")
                    for fallback in FALLBACK_CODES:
                        _source, blob = read(storm, ours, f"{HEAD}{stem}_{fallback}{rest[2:]}")
                        if blob is not None:
                            note = f"{stem}_{fallback}{rest[2:]}"
                            break
                if blob is None:
                    tail_stem, _sep, suffix = key[len(HEAD):].rpartition("_")
                    blob, source = borrow(tail_stem, suffix)
                    note = f"{source} (any code/sex)" if source else None
                if blob is None:
                    missing.append(key)
                    continue
                entries[key] = blob
                total += len(blob)
                if note:
                    borrowed.append((key, note))
            staged = len(entries) - (1 if CHRRACES in entries else 0)
            print(f"   staging {staged} files, {total / 1048576:.1f} MB; "
                  f"{already} already present, {len(borrowed)} borrowed, {len(missing)} unavailable")
            for key, note in borrowed[:6]:
                print(f"      ~ {key[len(HEAD):]} <- {note}")
            for key in missing[:10]:
                print(f"      ! {key[len(HEAD):]}")

        if args.dry_run:
            print("dry run - Patch-Y untouched")
            return

        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = BACKUP_ROOT / f"patch-y-before-item-component-prefixes-{stamp}"
        backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
        print(f"backup: {backup}")
    finally:
        storm.dll.SFileCloseArchive(patch_y)

    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), {len(entries)} entries written")

    handle = H()
    if storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0, ctypes.byref(handle)):
        try:
            check = Wdbc(storm.read(handle, CHRRACES))
            for row in check.rows:
                if row[0] in PREFIXES:
                    print(f"   verify race {row[0]:>2}: {check.text(row[6])!r}")
            for key in sorted(k for k in entries if k.lower().startswith(HEAD.lower()))[:3]:
                print(f"   verify {key}: {len(storm.read(handle, key)):,} bytes")
        finally:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
