"""Stop drawing the always-on circular border around character-create race icons.

CharacterCreateEnumerateRaces creates three textures per race button:

    staticTexture   always visible, IconBorder_F tinted by faction   <- remove
    highlightTexture hover only, alpha 0.5 ADD                       (keep)
    checkedTexture   selected only, IconBorderRace_H ADD             (keep)

The XML defines none of them, so hiding staticTexture right after creation is
enough. Class and gender buttons use the same pattern with IconBorder_F1 and are
deliberately left alone.
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
LIVE = REPO / "3.3.5a - Dev" / "Data" / "Patch-C.MPQ"
LUA = B.join(["Interface", "GlueXML", "CharacterCreate.lua"])

# the race-button block, identified by its IconBorder_F texture (class uses IconBorder_F1)
OLD = """        if not button.staticTexture then
            button.staticTexture = button:CreateTexture(button:GetName().."StaticTexture", "ARTWORK");
            button.staticTexture:SetTexture("Interface\\\\Glues\\\\CharacterCreate\\\\IconBorder_F");
            button.staticTexture:SetSize(112, 112);
            button.staticTexture:SetPoint("CENTER", 0, 0);
            button.staticTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        else
            button.staticTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        end
"""

NEW = """        if not button.staticTexture then
            button.staticTexture = button:CreateTexture(button:GetName().."StaticTexture", "ARTWORK");
            button.staticTexture:SetTexture("Interface\\\\Glues\\\\CharacterCreate\\\\IconBorder_F");
            button.staticTexture:SetSize(112, 112);
            button.staticTexture:SetPoint("CENTER", 0, 0);
            button.staticTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        else
            button.staticTexture:SetVertexColor(borderColor[1], borderColor[2], borderColor[3]);
        end
        button.staticTexture:Hide();
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", type=Path, default=LIVE)
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "race-border-fix")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.live)
    try:
        names = {n.casefold(): n for n, *_ in storm.list_files(handle)}
        key = names[LUA.casefold()]
        text = storm.read(handle, key).decode("utf-8", "replace")
    finally:
        storm.dll.SFileCloseArchive(handle)
        del storm
        gc.collect()

    hits = text.count(OLD)
    print("race-button staticTexture block occurrences: %d" % hits)
    if hits != 1:
        raise SystemExit("expected exactly one race-button block, found %d" % hits)
    if "button.staticTexture:Hide();" in text:
        raise SystemExit("lua already patched")
    merged = text.replace(OLD, NEW, 1)
    print("lua %d -> %d chars" % (len(text), len(merged)))

    staging = args.staging
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    staged = staging / args.live.name
    print("copying live archive (%.0f MB)" % (args.live.stat().st_size / 1e6))
    shutil.copy2(args.live, staged)
    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(staged, {key: merged.encode("utf-8")})
    del storm
    gc.collect()

    check = Storm(DLL_DEFAULT)
    h2 = check.open_archive(staged)
    try:
        n2 = {n.casefold(): n for n, *_ in check.list_files(h2)}
        got = check.read(h2, n2[LUA.casefold()]).decode("utf-8", "replace")
        if "button.staticTexture:Hide();" not in got:
            raise SystemExit("VERIFY FAIL: patch not present")
        if got.count("button.staticTexture:Hide();") != 1:
            raise SystemExit("VERIFY FAIL: unexpected hide count")
        if "IconBorderRace_H" not in got:
            raise SystemExit("VERIFY FAIL: selected-state ring was disturbed")
        print("verify: race border hidden, selected-state ring intact")
    finally:
        check.dll.SFileCloseArchive(h2)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = REPO / "3.3.5a - Dev" / "Backups" / ("patch-c-before-race-border-fix-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / args.live.name
    shutil.copy2(args.live, backup)
    os.replace(staged, args.live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (args.live, args.live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
