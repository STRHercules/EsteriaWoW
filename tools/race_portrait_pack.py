"""Convert the supplied race portrait PNGs into the BLP2 files this client loads.

Sources:  <Pictures>\\Portraits\\Alliance\\Charactercreate-races_<race>-<gender>[_alliance].png
          <Pictures>\\Portraits\\Horde\\Charactercreate-races_<race>-<gender>[_horde].png

Destinations, per race and gender:

  Interface\\CharacterFrame\\TemporaryPortrait-<Male|Female>-<ClientFileString>.blp
      The character-select and paper-doll portrait. The client builds this name from
      ChrRaces field 11 plus "Male"/"Female" (Wow.exe 0x006181C0), and a missing file is
      what draws the placeholder portrait on the character-select screen.

  the Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-... path the client's own
  RACE_ICON_TEXTURES table already points at (creation-screen race buttons).

Images are written as 64x64 BLP2 raw BGRA with 7 mips, byte-identical in format to the
client's existing race icons, with a circular alpha mask so the square source art sits
correctly in the round portrait frames.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm
from derive_playable_race_portraits import encode_portrait, validate_portrait
from playable_race_pack import RawWdbc


PORTRAIT_SIZE = 64
SUPERSAMPLE = 4
DEFAULT_SOURCE = Path(r"R:\Users\Zach\Pictures\Portraits")
CHARACTER_FRAME_ROOT = "Interface\\CharacterFrame\\"
CREATOR_ICON_ROOT = "Interface\\Glues\\CharacterCreate\\"
ICON_TEMPLATE_ENTRY = CREATOR_ICON_ROOT + "UI-CharacterCreate-HumanMale.blp"
RING_ENTRY = CREATOR_ICON_ROOT + "UI-CharacterCreate-GenderMale.blp"
RING_INNER_RADIUS = 28
ICON_ART_DIAMETER = 58
LUA_ENTRY = "Interface\\GlueXML\\CharacterCreate.lua"
RACE_ICON_TABLE = re.compile(r'\["([A-Z0-9_]+)"\]\s*=\s*"(Interface\\\\Glues\\\\CharacterCreate\\\\[^"]+)"')

# The pictures are named after the creator-screen race art; map those names onto the
# client's ChrRaces ClientFileString values.
RACE_ALIASES = {
    "undead": "scourge",
    "panda": "pandaren",
    "worgen2": "worgen",
    "kultiranhuman": "kultiran",
    "lightforged": "lightforgeddraenei",
    "dracthyrvisage": "dracthyr",
    "zandalaritroll": "zandalaritroll",
    "darkirondwarf": "darkirondwarf",
}

# Race keys that only exist for one faction of a shared picture name.
FACTION_RACE_KEYS = {("darkfallen", "horde"): "darkfallenhorde"}
# Art that should be flipped before conversion. The supplied Darkfallen portraits are used
# exactly as drawn: the two factions are already mirrored versions of each other, so adding a
# race here would put that faction's portrait back the wrong way round.
MIRRORED_RACES: frozenset[str] = frozenset()


def race_key(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", name.casefold())
    return RACE_ALIASES.get(normalized, normalized)


def circular_mask(size: int = PORTRAIT_SIZE, supersample: int = SUPERSAMPLE) -> Image.Image:
    big = Image.new("L", (size * supersample, size * supersample), 0)
    draw = ImageDraw.Draw(big)
    draw.ellipse((0, 0, size * supersample - 1, size * supersample - 1), fill=255)
    return big.resize((size, size), Image.Resampling.LANCZOS)


def portrait_bytes(source: Path, mask: Image.Image) -> bytes:
    with Image.open(source) as handle:
        image = handle.convert("RGBA")
    image = image.resize((PORTRAIT_SIZE, PORTRAIT_SIZE), Image.Resampling.LANCZOS)
    image.putalpha(mask)
    return image


def decode_client_blp(data: bytes) -> Image.Image:
    """Decode a client icon BLP, including the raw-BGRA variant PIL rejects."""
    if data[:4] == b"BLP2" and data[8:12] == bytes((3, 8, 8, 1)):
        width, height = struct.unpack("<2I", data[12:20])
        offsets = struct.unpack("<16I", data[20:84])
        base = data[offsets[0] : offsets[0] + width * height * 4]
        return Image.frombytes("RGBA", (width, height), base, "raw", "BGRA")
    return Image.open(io.BytesIO(data)).convert("RGBA")


def ring_layer(icon: Image.Image, inner_radius: int = RING_INNER_RADIUS) -> Image.Image:
    """Keep only the metal ring of an icon so it can frame other artwork."""
    size = icon.size[0]
    centre = size // 2
    inner = Image.new("L", (size * SUPERSAMPLE, size * SUPERSAMPLE), 255)
    ImageDraw.Draw(inner).ellipse(
        (
            SUPERSAMPLE * (centre - inner_radius),
            SUPERSAMPLE * (centre - inner_radius),
            SUPERSAMPLE * (centre + inner_radius) - 1,
            SUPERSAMPLE * (centre + inner_radius) - 1,
        ),
        fill=0,
    )
    inner = inner.resize((size, size), Image.Resampling.LANCZOS)
    ring = icon.copy()
    ring.putalpha(ImageChops.multiply(icon.getchannel("A"), inner))
    return ring


def compose_race_icon(art: Image.Image, ring: Image.Image, diameter: int = ICON_ART_DIAMETER) -> Image.Image:
    """Draw the race art inside the ring the gender buttons use."""
    canvas = Image.new("RGBA", (PORTRAIT_SIZE, PORTRAIT_SIZE), (0, 0, 0, 0))
    inner = art.resize((diameter, diameter), Image.Resampling.LANCZOS)
    offset = (PORTRAIT_SIZE - diameter) // 2
    canvas.paste(inner, (offset, offset), inner)
    canvas.alpha_composite(ring)
    return canvas


def read_icon_table(storm: Storm, archives: list[Path]) -> dict[str, str]:
    table: dict[str, str] = {}
    for archive in archives:
        handle = storm.open_archive(archive)
        try:
            names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
            entry = names.get(LUA_ENTRY.casefold())
            if entry is None:
                continue
            text = storm.read(handle, entry).decode("utf-8-sig", "replace")
        finally:
            storm.dll.SFileCloseArchive(handle)
        for key, path in RACE_ICON_TABLE.findall(text):
            table.setdefault(key, path.replace("\\\\", "\\"))
    return table


def discover_sources(root: Path) -> tuple[dict[tuple[str, str, str], Path], list[str]]:
    """Return {(race key, gender, faction): png} plus the unmapped file names."""
    found: dict[tuple[str, str, str], Path] = {}
    unmapped: list[str] = []
    pattern = re.compile(
        r"Charactercreate-races_(?P<race>.+?)-(?P<gender>male|female)\d*(?P<faction>_alliance|_horde)?$",
        re.IGNORECASE,
    )
    for path in sorted(root.rglob("*.png")):
        match = pattern.match(path.stem)
        if not match:
            unmapped.append(path.name)
            continue
        # The folder carries the faction when the file name does not (the Illidari art
        # sits in both folders without a suffix).
        folder = path.parent.name.casefold()
        faction = (match.group("faction") or "").lstrip("_").casefold()
        if not faction and folder in ("alliance", "horde"):
            faction = folder
        race = race_key(match.group("race"))
        race = FACTION_RACE_KEYS.get((race, faction), race)
        found[(race, match.group("gender").casefold(), faction)] = path
    return found, unmapped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--root-archive", type=Path, default=Path(r"G:\3.3.5a - Dev\Data\patch-Z.MPQ"))
    parser.add_argument(
        "--locale-archive",
        type=Path,
        default=Path(r"G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ"),
    )
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--archive",
        action="append",
        type=Path,
        default=None,
        help="extra archives to write (default: every archive that carries race-icon or portrait art)",
    )
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    archives = [args.root_archive, args.locale_archive]

    handle = storm.open_archive(args.root_archive)
    try:
        races = RawWdbc(storm.read(handle, "DBFilesClient\\ChrRaces.dbc"))
        template = storm.read(handle, ICON_TEMPLATE_ENTRY)
        ring = ring_layer(decode_client_blp(storm.read(handle, RING_ENTRY)))
    finally:
        storm.dll.SFileCloseArchive(handle)
    icon_table = read_icon_table(storm, archives)

    def field(row: bytes, index: int) -> int:
        return int.from_bytes(row[index * 4 : index * 4 + 4], "little")

    def string(row: bytes, index: int) -> str:
        offset = field(row, index)
        return races.strings[offset:].split(b"\0", 1)[0].decode("ascii", "replace") if offset else ""

    race_rows = {
        string(row, 11).casefold(): row
        for row in races.records
        if string(row, 11)
    }
    sources, unmapped = discover_sources(args.source)
    mask = circular_mask()

    portrait_entries: dict[str, bytes] = {}
    icon_entries: dict[str, bytes] = {}
    used: set[tuple[str, str, str]] = set()
    consumed: set[tuple[str, str, str]] = set()
    skipped: list[str] = []
    for key, path in sorted(sources.items()):
        race, gender, faction = key
        row = race_rows.get(race)
        if row is None:
            skipped.append(f"{path.name} (no ChrRaces ClientFileString {race!r})")
            continue
        file_string = string(row, 11)
        sex = "Male" if gender == "male" else "Female"
        image = portrait_bytes(path, mask)
        if race in MIRRORED_RACES:
            image = ImageOps.mirror(image)
        encoded = encode_portrait(image, template)
        validate_portrait(encoded, path)
        used.add(key)
        # The portrait name carries no faction, so the first faction variant wins.
        # The client builds this name itself (Wow.exe 0x006181C0) and may hand it to the
        # storage layer with or without an extension, so provide both spellings.
        portrait_stem = CHARACTER_FRAME_ROOT + f"TemporaryPortrait-{sex}-{file_string}"
        claimed = False
        for portrait_name in (portrait_stem, portrait_stem + ".blp"):
            claimed = claimed or portrait_name not in portrait_entries
            portrait_entries.setdefault(portrait_name, encoded)
        icon_path = icon_table.get(f"{file_string.upper()}_{sex.upper()}")
        if icon_path is None and faction != "all":
            icon_path = icon_table.get(f"{file_string.upper()}_{faction.upper()}_{sex.upper()}")
        if icon_path is not None:
            # The Lua table stores extension-less texture paths; the client appends .blp,
            # so the archive entry has to carry the extension.
            if not icon_path.casefold().endswith(".blp"):
                icon_path += ".blp"
            claimed = claimed or icon_path not in icon_entries
            icon_entries.setdefault(icon_path, encode_portrait(compose_race_icon(image, ring), template))
        if claimed:
            consumed.add(key)

    print(f"sources: {len(sources)} portraits found, {len(portrait_entries)} portrait files, "
          f"{len(icon_entries)} creator icons")
    unused = sorted(f"{path.name}" for key, path in sources.items() if key not in consumed)
    for name in unused:
        print(f"  duplicate faction variant, shared ClientFileString keeps the first: {name}")
    for name in unmapped:
        print(f"  unmatched file name: {name}")
    for name in skipped:
        print(f"  skipped: {name}")
    missing = [f"{string(row, 11)}" for row in races.records
               if string(row, 11) and (string(row, 11).casefold(), "male", "all") not in used
               and (string(row, 11).casefold(), "male", "alliance") not in used
               and (string(row, 11).casefold(), "male", "horde") not in used]
    print(f"  races without a supplied portrait: {sorted(set(missing))}")

    updates = dict(portrait_entries)
    updates.update(icon_entries)

    # Race art also lives in the other patch archives; write wherever a competing copy
    # exists so the client cannot fall back to older art from a lower archive.
    discovered = [args.root_archive, args.locale_archive]
    if args.archive:
        discovered.extend(args.archive)
    else:
        data_root = args.root_archive.parent
        for candidate in sorted(data_root.glob("*.MPQ")) + sorted((data_root / "enUS").glob("*.MPQ")):
            if candidate in discovered:
                continue
            try:
                handle = storm.open_archive(candidate)
            except OSError:
                continue
            try:
                holds_race_art = False
                for name in updates:
                    try:
                        storm.read(handle, name)
                    except (OSError, UnicodeDecodeError):
                        continue
                    holds_race_art = True
                    break
            finally:
                storm.dll.SFileCloseArchive(handle)
            if holds_race_art:
                discovered.append(candidate)

    for archive in discovered:
        handle = storm.open_archive(archive)
        try:
            existing = {name: storm.read(handle, name) for name in updates
                        if name.casefold() in {n.casefold() for n, *_ in storm.list_files(handle)}}
        finally:
            storm.dll.SFileCloseArchive(handle)
        changed = {name: payload for name, payload in updates.items()
                   if existing.get(name) != payload}
        print(f"{archive.name}: {len(changed)} of {len(updates)} entries to write")
        if not args.apply or not changed:
            continue
        assert args.backup_dir is not None, "--backup-dir is required with --apply"
        args.backup_dir.mkdir(parents=True, exist_ok=True)
        backup = args.backup_dir / archive.name
        if not backup.exists():
            shutil.copy2(archive, backup)
            print(f"  backed up -> {backup}")
        storm.replace_archive_entries(archive, changed)
        handle = storm.open_archive(archive)
        try:
            for name, payload in changed.items():
                readback = storm.read(handle, name)
                assert readback == payload, f"{archive.name}: readback mismatch for {name}"
        finally:
            storm.dll.SFileCloseArchive(handle)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        print(f"  verified {archive.name}: sha256={digest[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
