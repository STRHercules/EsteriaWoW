"""Verify the deployed reskin end-to-end, driven by the staging tree.

Checks:
  1. every staged entry resolves from a -Z archive (highest load order)
  2. every staged BLP decodes and contains no stock crimson red
     (ElvUI accent orange is allowed and reported separately)
  3. GlueFontStyles.xml contains no gold colour definitions
  4. sampled pre-existing entries are byte-identical to the backups
"""

from __future__ import annotations

import ctypes as c
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402
from blp import decode_blp, describe_blp  # noqa: E402
from resolve_glue import load_order, DATA  # noqa: E402

HERE = Path(__file__).resolve().parent
STAGING = HERE / "staging"

SAMPLE_EXISTING = [
    r"Interface\Glues\CharacterCreate\UI-CharacterCreate-BloodElfMale.blp",
    r"Interface\GlueXML\CharacterSelect.lua",
    r"Interface\Glues\CharacterSelect\FreebornLogo.blp",
]

GOLD_PATTERNS = [
    r'r="1\.0"\s+g="0\.78"',
    r'r="1\.0"\s+g="0\.82"',
    r'r=1\.0,\s*g=0\.82',
    r'r="1\.0"\s+g="0\.96"',
]


def list_safe(storm, archive) -> set[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return set()
    out: set[str] = set()
    try:
        while True:
            out.add(data.cFileName.split(b"\0", 1)[0].decode("latin-1").casefold())
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


def staged_entries() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in sorted(STAGING.rglob("*")):
        if path.is_file():
            rel = path.relative_to(STAGING).as_posix()
            parts = rel.split("/", 1)
            logical = parts[1] if len(parts) > 1 else parts[0]
            out[logical.replace("/", "\\")] = path
    return out


def main() -> int:
    entries = staged_entries()
    print(f"staged entries: {len(entries)}\n")

    storm = Storm(DLL_DEFAULT)
    available = []
    handles = {}
    for rel in load_order():
        path = DATA / rel
        if not path.exists():
            continue
        try:
            handle = storm.open_archive(path)
        except OSError:
            continue
        handles[rel] = handle
        available.append((rel, list_safe(storm, handle)))

    failures = 0

    # ---- 1. load-order winners ----
    print("=== 1. load-order winner per staged entry ===")
    winners: dict[str, str] = {}
    for logical in sorted(entries, key=str.casefold):
        key = logical.casefold()
        holders = [rel for rel, names in available if key in names]
        winner = holders[-1] if holders else None
        winners[logical] = winner
        if winner is None or not winner.casefold().endswith("-z.mpq"):
            print(f"  BAD  {logical} -> {winner}")
            failures += 1
    print(f"  {len(entries) - failures}/{len(entries)} resolve from a -Z archive")

    # ---- 2. colour audit on every texture ----
    print("\n=== 2. colour audit (crimson = failure, accent = intended) ===")
    crimson, accent, neutral = [], [], []
    for logical, path in sorted(entries.items(), key=lambda kv: kv[0].casefold()):
        if not logical.casefold().endswith(".blp"):
            continue
        winner = winners.get(logical)
        if not winner:
            continue
        data = storm.read(handles[winner], logical)
        image = decode_blp(data).convert("RGBA")
        visible = [p for p in image.get_flattened_data() if p[3] > 8]
        if not visible:
            print(f"  EMPTY {logical}")
            failures += 1
            continue
        n = len(visible)
        r = sum(p[0] for p in visible) / n
        g = sum(p[1] for p in visible) / n
        b = sum(p[2] for p in visible) / n
        ratio_g = g / max(r, 1.0)
        ratio_b = b / max(r, 1.0)
        is_crimson = r > 90 and ratio_g < 0.35 and ratio_b < 0.35
        is_accent = r > 90 and 0.35 <= ratio_g <= 0.65 and ratio_b < 0.35
        if is_crimson:
            crimson.append((logical, r, g, b))
            failures += 1
        elif is_accent:
            accent.append((logical, r, g, b))
        else:
            neutral.append((logical, r, g, b))

    for logical, r, g, b in crimson:
        print(f"  CRIMSON {logical} mean=({r:.1f},{g:.1f},{b:.1f})")
    for logical, r, g, b in accent:
        print(f"  accent  {logical:58s} mean=({r:.0f},{g:.0f},{b:.0f})")
    print(f"  neutral={len(neutral)}  accent={len(accent)}  crimson={len(crimson)}")

    # ---- 3. gold text ----
    print("\n=== 3. gold text audit ===")
    target = r"Interface\GlueXML\GlueFontStyles.xml"
    winner = winners.get(target)
    if not winner:
        print("  GlueFontStyles.xml not staged!")
        failures += 1
    else:
        text = storm.read(handles[winner], target).decode("utf-8", "replace")
        found = [m.group(0) for p in GOLD_PATTERNS for m in re.finditer(p, text)]
        if found:
            print(f"  GOLD REMAINS: {found[:5]}")
            failures += 1
        else:
            match = re.search(r"NORMAL_FONT_COLOR = [^;]+", text)
            print(f"  no gold definitions; {match.group(0) if match else '?'}")

    # ---- 4b. ElvUI geometry audit: sharp corners + translucency ----
    print("\n=== 4b. geometry audit (sharp corners + backdropfade alpha) ===")
    # (path, panel rect or None, expected alpha)
    GEOMETRY = [
        (r"Interface\Glues\Common\Glue-Panel-Button-Up.blp", (0, 0, 592, 192), 0.80),
        (r"Interface\Glues\Common\Glue-Panel-Button-Down.blp", (0, 0, 592, 192), 0.85),
        (r"Interface\Glues\Common\Glue-Panel-Button-Up-Blue.blp", (0, 0, 592, 192), 0.80),
        (r"Interface\Glues\Common\Glue-Panel-Button-Disabled.blp", (0, 0, 148, 48), 0.60),
        (r"Interface\Tooltips\UI-Tooltip-Background.blp", None, 0.80),
        (r"Interface\DialogFrame\UI-DialogBox-Background.blp", None, 0.80),
    ]
    for logical, rect, expected in GEOMETRY:
        winner = winners.get(logical)
        if not winner:
            print(f"  MISSING {logical}")
            failures += 1
            continue
        image = decode_blp(storm.read(handles[winner], logical)).convert("RGBA")
        alpha = image.getchannel("A")
        if rect:
            x0, y0, x1, y1 = rect
            # Exact corners must be COVERED (the stock art was transparent there --
            # that transparency is what produced the rounded look). The fill, probed
            # safely inside the 1px-equivalent rim, must match backdropfade alpha.
            corners = {
                "TL": alpha.getpixel((x0, y0)),
                "TR": alpha.getpixel((x1 - 1, y0)),
                "BL": alpha.getpixel((x0, y1 - 1)),
                "BR": alpha.getpixel((x1 - 1, y1 - 1)),
            }
            fill = alpha.getpixel((x0 + 8, y0 + 8))
            target = round(expected * 255)
            sharp = all(v >= 250 for v in corners.values())
            fill_ok = abs(fill - target) <= 14
            translucent = fill < 250
            ok = sharp and fill_ok and translucent
            if not ok:
                failures += 1
            print(
                f"  [{'OK ' if ok else 'BAD'}] {Path(logical).name:44s} "
                f"corners={list(corners.values())} fill={fill} (target {target}) "
                f"sharp={sharp} translucent={translucent}"
            )
        else:
            cx, cy = image.width // 2, image.height // 2
            fill = alpha.getpixel((cx, cy))
            target = round(expected * 255)
            ok = fill < 250 and abs(fill - target) <= 14
            if not ok:
                failures += 1
            print(
                f"  [{'OK ' if ok else 'BAD'}] {Path(logical).name:44s} "
                f"fill={fill} (target {target}) translucent={fill < 250}"
            )

    # ---- 4. pre-existing entries untouched ----
    print("\n=== 4. pre-existing entries vs backup ===")
    backups = sorted(
        (Path(r"G:\3.3.5a - Dev\Backups")).glob("elvui-glue-reskin-*/patch-enUS-Z.MPQ")
    )
    if not backups:
        print("  no backup archive found; skipping")
    else:
        backup = backups[-1]
        print(f"  baseline: {backup.parent.name}")
        bh = storm.open_archive(backup)
        wh = handles.get(f"enUS\\patch-enUS-Z.MPQ")
        try:
            for sample in SAMPLE_EXISTING:
                try:
                    old = storm.read(bh, sample)
                except OSError:
                    continue
                new = storm.read(wh, sample)
                same = old == new
                if not same:
                    failures += 1
                print(
                    f"  [{'same' if same else 'DIFF'}] {sample} "
                    f"sha={hashlib.sha256(new).hexdigest()[:12]}"
                )
        finally:
            storm.dll.SFileCloseArchive(bh)

    for handle in handles.values():
        storm.dll.SFileCloseArchive(handle)

    print(f"\n{'VERIFIED OK — objective met' if failures == 0 else f'{failures} PROBLEMS'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
