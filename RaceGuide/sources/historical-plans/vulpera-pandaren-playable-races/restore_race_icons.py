"""Restore the per-race character-create icons into Patch-C.

A later step reverted both the icon files and the Lua table that wires them, so
every race except Pandaren and Vulpera fell back to the shared Races atlas.

Sources:
  pre-dxt5  (18:35 backup) - 30 uncompressed per-race icons (comp=3, 23016 B),
                             the same format the live Pandaren/Vulpera icons use
  post-dxt5 (18:58 backup) - the two HighElf icons, which only exist in DXT form
                           - the 32-entry RACE_ICON_TEXTURES table for the Lua
"""

from __future__ import annotations

import argparse
import datetime
import gc
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm

B = chr(92)
PRE = REPO / "3.3.5a - Dev" / "Backups" / "patch-c-before-dxt5-race-icons-20260911-183510" / "Patch-C.MPQ"
POST = REPO / "3.3.5a - Dev" / "Backups" / "patch-c-before-lossless-race-icons-20260911-185815" / "Patch-C.MPQ"
LIVE = REPO / "3.3.5a - Dev" / "Data" / "Patch-C.MPQ"
LUA = B.join(["Interface", "GlueXML", "CharacterCreate.lua"])
ICON_DIR = B.join(["Interface", "Glues", "CharacterCreate"])


def open_archive(p):
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(p)
    return storm, handle


def read_all(p, predicate):
    storm, handle = open_archive(p)
    try:
        out = {}
        for n, *_ in storm.list_files(handle):
            if predicate(n):
                out[n] = storm.read(handle, n)
        return out
    finally:
        storm.dll.SFileCloseArchive(handle)
        del storm
        gc.collect()


def icon_pred(n):
    leaf = n.rsplit(B, 1)[-1].casefold()
    return n.casefold().startswith("interface" + B + "glues" + B + "charactercreate" + B) and leaf.startswith("ui-charactercreate-") and leaf.endswith(".blp")


def lua_pred(n):
    return n.casefold() == LUA.casefold()


def extract_block(text, marker):
    start = text.index(marker)
    end = text.index("};", start) + 2
    return text[start:end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", type=Path, default=LIVE)
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "race-icons-fix")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pre_icons = read_all(PRE, icon_pred)
    post_icons = read_all(POST, icon_pred)
    live_icons = read_all(args.live, icon_pred)
    print(f"icons: pre-dxt5={len(pre_icons)}  post-dxt5={len(post_icons)}  live={len(live_icons)}")

    updates = {}
    for n in sorted(set(pre_icons) | set(post_icons)):
        leaf = n.rsplit(B, 1)[-1]
        if leaf in ("UI-CharacterCreate-Races.blp", "UI-CharacterCreate-RacesRound.blp"):
            continue   # this atlas already ships in PATCH-A
        if n in pre_icons:
            updates[n] = pre_icons[n]
        elif n in post_icons:
            updates[n] = post_icons[n]
    print(f"icons to write: {len(updates)}")

    live_lua = read_all(args.live, lua_pred)
    backup_lua = read_all(POST, lua_pred)
    live_key = next(iter(live_lua))
    backup_key = next(iter(backup_lua))
    live_text = live_lua[live_key].decode("utf-8", "replace")
    backup_text = backup_lua[backup_key].decode("utf-8", "replace")
    block = extract_block(backup_text, "RACE_ICON_TEXTURES = {")
    entries = block.count('["')
    print(f"RACE_ICON_TEXTURES in backup: {entries} entries")
    live_block = extract_block(live_text, "RACE_ICON_TEXTURES = {")
    print("RACE_ICON_TEXTURES in live  : %d entries" % live_block.count('["'))
    merged = live_text.replace(live_block, block)
    if merged == live_text:
        raise SystemExit("lua table replacement produced no change")
    updates[live_key] = merged.encode("utf-8")
    print(f"merged lua: {len(live_text)} -> {len(merged)} chars")

    staging = args.staging
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    staged = staging / args.live.name
    print("copying live archive (%.0f MB)" % (args.live.stat().st_size / 1e6))
    shutil.copy2(args.live, staged)
    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(staged, updates)
    del storm
    gc.collect()

    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        names = {n.casefold(): n for n, *_ in check.list_files(handle)}
        missing = [n for n in updates if n.casefold() not in names]
        if missing:
            raise SystemExit("VERIFY FAIL missing: %s" % missing[:5])
        txt = check.read(handle, names[live_key.casefold()]).decode("utf-8", "replace")
        got = extract_block(txt, "RACE_ICON_TEXTURES = {")
        if got.count('["') != entries:
            raise SystemExit("VERIFY FAIL lua table has %d entries" % got.count('["'))
        print("verify: %d icons present, RACE_ICON_TEXTURES has %d entries" % (len(updates) - 1, got.count('["')))
    finally:
        check.dll.SFileCloseArchive(handle)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = REPO / "3.3.5a - Dev" / "Backups" / ("patch-c-before-race-icon-restore-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / args.live.name
    shutil.copy2(args.live, backup)
    os.replace(staged, args.live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (args.live, args.live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
