"""Deploy the Esteria Character Select payload into the live client archives.

Adds, into BOTH patch-Z.MPQ and patch-enUS-Z.MPQ (the contract test reads both):

    Interface\\GlueXML\\ECS_*.lua              the ECS modules
    Interface\\GlueXML\\CharacterSelect.lua    with the keydown + scroll fixes
    Interface\\GlueXML\\GlueXML.toc            with the ECS load order
    Interface\\Glues\\CharacterSelect\\ECS-*.blp    portraits and row art
    vanilla panel/Glue button textures restored from locale-enUS.MPQ
    extended GlueFontStyles.xml plus the CharacterCreate tooltip font merged in

Backs up both archives first, then verifies: every new entry round-trips byte for
byte, and sampled pre-existing entries are untouched.

The client MUST be closed - a running game holds these archives open.

Usage:
    python .agents/plans/character-select-redesign/tools/deploy.py --client-data "G:\\BearCave\\Data"
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
REPO = PLAN.parents[2]

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents" / "plans" / "elvui-glue-reskin"))
from cars_mount_pack import Storm, DLL_DEFAULT  # noqa: E402
from blp import decode_blp, encode_blp_bgra  # noqa: E402

CLIENT_DATA_DEFAULT = Path(r"G:\3.3.5a - Dev\Data")

SRC_GLUE = PLAN / "src" / "GlueXML"
SRC_TEX = PLAN / "textures"

# These were replaced by flat ElvUI-style BLPs in the target patch archives. Put
# the original client textures back above those overrides so the stock Glue button
# and panel templates render their native artwork again.
VANILLA_UI_ASSETS = (
    r"Interface\Buttons\UI-Panel-Button-Disabled-Down.blp",
    r"Interface\Buttons\UI-Panel-Button-Disabled.blp",
    r"Interface\Buttons\UI-Panel-Button-Down.blp",
    r"Interface\Buttons\UI-Panel-Button-Highlight.blp",
    r"Interface\Buttons\UI-Panel-Button-Up.blp",
    r"Interface\Buttons\UI-Panel-MinimizeButton-Down.blp",
    r"Interface\Buttons\UI-Panel-MinimizeButton-Highlight.blp",
    r"Interface\Buttons\UI-Panel-MinimizeButton-Up.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Disabled.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Down-Blue.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Down.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Glow.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Highlight-Blue.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Highlight.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Up-Blue.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Up.blp",
    r"Interface\Glues\Common\Glue-Tooltip-Background.blp",
    r"Interface\Tooltips\UI-Tooltip-Background.blp",
    r"Interface\Tooltips\UI-Tooltip-Border.blp",
)
BLUE_GLUE_BUTTON_TEXTURES = {
    r"Interface\Glues\Common\Glue-Panel-Button-Up.blp":
        r"Interface\Glues\Common\Glue-Panel-Button-Up-Blue.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Down.blp":
        r"Interface\Glues\Common\Glue-Panel-Button-Down-Blue.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Highlight.blp":
        r"Interface\Glues\Common\Glue-Panel-Button-Highlight-Blue.blp",
}
EXTENDED_UI_XML = (r"Interface\GlueXML\GlueFontStyles.xml",)
STOCK_CHARACTER_SELECT_TEXTURES = (
    r"Interface\Glues\CharacterSelect\128redbuttonpart2.blp",
)
BLUE_DELETE_ATLAS = r"Interface\Glues\CharacterSelect\ECS-Delete-Button-Blue.blp"
CHARACTER_CREATE_TOOLTIP_FONT = (
    b'\t<Font name="CharacterCreateTooltipFont" inherits="SystemFont_Outline_Med2" virtual="true">\r\n'
    b'\t\t<Color r="1.0" g="1.0" b="1.0"/>\r\n'
    b'\t</Font>\r\n'
)

# Pre-existing entries sampled to prove the in-place add damaged nothing.
SAMPLE_EXISTING = [
    r"Interface\GlueXML\CharacterCreate.lua",
    r"Interface\Glues\CharacterCreate\UI-CharacterCreate-BloodElfMale.blp",
    r"Interface\Glues\CharacterSelect\FreebornLogo.blp",
]


def make_blue_delete_atlas(source: bytes) -> bytes:
    """Tint red atlas pixels WotLK-blue while preserving gold icon details/alpha."""
    image = decode_blp(source).convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha and red >= 32 and red > green * 1.7 and red > blue * 1.5:
                hue, saturation, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
                if saturation >= 0.35 and (hue <= 0.08 or hue >= 0.96):
                    blue_rgb = colorsys.hsv_to_rgb(0.60, saturation, value)
                    pixels[x, y] = tuple(int(channel * 255 + 0.5) for channel in blue_rgb) + (alpha,)
    return encode_blp_bgra(image)


def collect_payload(locale_archive: Path, stock_archive: Path, extended_ui_archive: Path) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}

    for name in ("CharacterSelect.lua", "GlueXML.toc"):
        path = SRC_GLUE / name
        entries[rf"Interface\GlueXML\{name}"] = path.read_bytes()

    ecs = sorted(p for p in SRC_GLUE.glob("ECS_*.lua"))
    for path in ecs:
        entries[rf"Interface\GlueXML\{path.name}"] = path.read_bytes()

    textures = sorted(SRC_TEX.glob("ECS-*.blp"))
    for path in textures:
        entries[rf"Interface\Glues\CharacterSelect\{path.name}"] = path.read_bytes()

    vanilla = Storm(DLL_DEFAULT)
    archive = vanilla.open_archive(locale_archive)
    try:
        for name in VANILLA_UI_ASSETS:
            entries[name] = vanilla.read(archive, name)
    finally:
        vanilla.dll.SFileCloseArchive(archive)
    for destination, source in BLUE_GLUE_BUTTON_TEXTURES.items():
        entries[destination] = entries[source]

    stock_archive_reader = Storm(DLL_DEFAULT)
    archive = stock_archive_reader.open_archive(stock_archive)
    try:
        for name in STOCK_CHARACTER_SELECT_TEXTURES:
            source = stock_archive_reader.read(archive, name)
            entries[name] = source
            entries[BLUE_DELETE_ATLAS] = make_blue_delete_atlas(source)
    finally:
        stock_archive_reader.dll.SFileCloseArchive(archive)

    extended = Storm(DLL_DEFAULT)
    archive = extended.open_archive(extended_ui_archive)
    try:
        for name in EXTENDED_UI_XML:
            payload = extended.read(archive, name)
            if name == r"Interface\GlueXML\GlueFontStyles.xml":
                declaration = b'<Font name="CharacterCreateTooltipFont"'
                if declaration not in payload:
                    if b"</Ui>" not in payload:
                        raise ValueError(f"cannot merge CharacterCreate font into {name}")
                    payload = payload.replace(
                        b"</Ui>", CHARACTER_CREATE_TOOLTIP_FONT + b"</Ui>", 1
                    )
                required_fonts = (b"GlueFontNormal", b"OptionsFontLeft", declaration)
                for required in required_fonts:
                    if required not in payload:
                        raise ValueError(f"required Glue font missing from {name}: {required!r}")
            entries[name] = payload
    finally:
        extended.dll.SFileCloseArchive(archive)

    print(f"payload: {len(ecs)} ECS lua, 2 patched glue files, {len(textures)} ECS textures, "
          f"{len(VANILLA_UI_ASSETS)} restored vanilla UI textures, "
          f"{len(STOCK_CHARACTER_SELECT_TEXTURES)} stock character-select textures, "
          f"{len(STOCK_CHARACTER_SELECT_TEXTURES)} blue-tinted Delete textures and "
          f"{len(EXTENDED_UI_XML)} extended UI font files")
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-data", type=Path, default=CLIENT_DATA_DEFAULT,
        help="client Data directory containing patch-Z.MPQ and enUS/patch-enUS-Z.MPQ")
    parser.add_argument("--backup-root", type=Path,
        help="directory for pre-deploy archive backups (default: sibling Backups folder)")
    parser.add_argument("--dry-run", action="store_true", help="list the payload without touching archives")
    args = parser.parse_args(argv)

    client_data = args.client_data
    targets = [
        client_data / "patch-Z.MPQ",
        client_data / "enUS" / "patch-enUS-Z.MPQ",
    ]
    locale_archive = client_data / "enUS" / "locale-enUS.MPQ"
    stock_archive = client_data / "patch-A.MPQ"
    extended_ui_archive = client_data / "enUS" / "patch-enUS.MPQ"
    backup_root = args.backup_root or client_data.parent / "Backups"

    if args.dry_run:
        entries = collect_payload(locale_archive, stock_archive, extended_ui_archive)
        for name in sorted(entries):
            print(f"  {name}  ({len(entries[name])} bytes)")
        total = sum(len(v) for v in entries.values())
        print(f"\ntotal: {len(entries)} entries, {total / 1024:.0f} KB")
        return 0

    entries = collect_payload(locale_archive, stock_archive, extended_ui_archive)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_root / f"character-select-ecs-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    print(f"backup: {backup}")
    for target in targets:
        if target.exists():
            shutil.copy2(target, backup / target.name)
            print(f"  copied {target.name} ({target.stat().st_size / 1024 / 1024:.0f} MB)")

    storm = Storm(DLL_DEFAULT)
    failures = 0

    for target in targets:
        if not target.exists():
            print(f"!! missing archive {target}")
            failures += 1
            continue

        handle = storm.open_archive(target)
        try:
            samples: dict[str, bytes] = {}
            for sample in SAMPLE_EXISTING:
                try:
                    samples[sample] = storm.read(handle, sample)
                except OSError:
                    pass
        finally:
            storm.dll.SFileCloseArchive(handle)

        print(f"\n=== {target.name} ===")
        storm.replace_archive_entries(target, entries)

        handle = storm.open_archive(target)
        try:
            bad = 0
            for name, payload in entries.items():
                try:
                    got = storm.read(handle, name)
                except OSError as exc:
                    print(f"  MISSING after write: {name} ({exc})")
                    bad += 1
                    continue
                if got != payload:
                    print(f"  MISMATCH: {name} (wrote {len(payload)}, read {len(got)})")
                    bad += 1
            print(f"  new entries verified: {len(entries) - bad}/{len(entries)}")

            for name, original in samples.items():
                try:
                    got = storm.read(handle, name)
                except OSError:
                    print(f"  REGRESSION: {name} vanished")
                    bad += 1
                    continue
                same = got == original
                print(f"  pre-existing {name}: {'unchanged' if same else 'CHANGED'} "
                      f"sha={hashlib.sha256(got).hexdigest()[:12]}")
                if not same:
                    bad += 1
            failures += bad
        finally:
            storm.dll.SFileCloseArchive(handle)

    print(f"\n{'DEPLOY VERIFIED' if failures == 0 else str(failures) + ' PROBLEMS'}")
    if failures == 0:
        print(f"Backup kept at: {backup}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
