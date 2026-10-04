"""Repair retroported race animation, language eligibility and Character Select presentation."""

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import creator_portrait_layout as icons
import expanded_appearance_pack as expansion
import retroported_race_pack as p

STAGE = Path("C:/Users/Zach/.codex/tmp/race-final-touchups")
NATIVE = expansion.STAGE
ECS = ("ECS_Schema.lua", "ECS_Data.lua", "ECS_Integrate.lua", "ECS_Row.lua", "ECS_Tooltip.lua", "ECS_UI.lua")


def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Touchup source differs at: " + old[:80])
    return text.replace(old, new, 1)


def patch(name, text):
    if name == "ECS_Schema.lua":
        text = replace(text, "S.RaceOverride = {", '''S.RaceOverride = {
    [45] = { name = "Mag'har Orc", faction = 2, artKey = "Maghar" },
    [52] = { name = "Skyborn", faction = 1, artKey = "Skyborne" },
    [53] = { name = "Skyborn", faction = 2, artKey = "SkyborneHorde" },''')
        text = replace(text, "S.PortraitArtKeys = {", "S.PortraitArtKeys = {\n"
                       "    Maghar = true, Skyborne = true, SkyborneHorde = true,")
    elif name == "ECS_Integrate.lua":
        text = replace(text, '''        characterInfo = function(index)
            return _G.GetCharacterInfo(index);
        end,''', '''        characterInfo = function(index)
            local fields = {_G.GetCharacterInfo(index)};
            if type(CycleCharCustomization) == "function" then
                local ok,race,gender = pcall(CycleCharCustomization,"EA_SELECT",index);
                if ok and (race == 45 or race == 52 or race == 53) then
                    fields[2] = race;
                    fields[6] = gender + 2;
                end
            end
            return unpack(fields,1,10);
        end,''')
    elif name == "ECS_Row.lua":
        text = replace(text, '    name:SetJustifyH("LEFT");', '''    name:SetJustifyH("LEFT");
    name:SetWordWrap(false);
    if name.SetNonSpaceWrap then name:SetNonSpaceWrap(false); end''')
        text = replace(
            text, "    if ( rowState.name ) then\n        local classColour",
            '''    if ( rowState.name ) then
        ApplyFont(rowState.name, C.NAME_FONT_SIZE);
        rowState.name:SetWidth(0);
        local classColour''')
        text = replace(text, '''            rowState.name:SetText(character.name or "");
        end
    end

    if ( rowState.zone )''', '''            rowState.name:SetText(character.name or "");
        end
        local available = C.TEXT_RIGHT - C.TEXT_LEFT;
        local natural = rowState.name:GetStringWidth();
        if natural > available then
            ApplyFont(rowState.name, math.max(9,C.NAME_FONT_SIZE * available / natural));
        end
        rowState.name:SetWidth(available);
    end

    if ( rowState.zone )''')
    elif name == "ECS_Tooltip.lua":
        text = replace(text, "    local y = anchorY - height - T.PAD;", "    local y = anchorY + T.PAD;")
        text = replace(text, '''    if ( y < margin ) then
        -- flip below the cursor
        y = anchorY + T.PAD;''', '''    if ( y + height > screenHeight - margin ) then
        -- Only move above the cursor when there is no room below it.
        y = anchorY - height - T.PAD;''')
    elif name == "ECS_UI.lua":
        text = replace(text, '''    if ( ok ) then cursorX, cursorY = x or 0, y or 0 end

    -- GetCursorPosition''', '''    if ( ok ) then cursorX, cursorY = x or 0, y or 0 end
    local scale = U.parent.GetEffectiveScale and U.parent:GetEffectiveScale() or 1;
    if scale <= 0 then scale = 1; end
    cursorX, cursorY = cursorX / scale, cursorY / scale;

    -- GetCursorPosition''')
        text = replace(text, "    local screenHeight = U.ScreenHeight();\n    local topLeftY",
                       "    local screenHeight = U.parent:GetHeight();\n    local topLeftY")
        text = replace(text, "        U.ScreenWidth(), screenHeight);",
                       "        U.parent:GetWidth(), screenHeight);")
    elif name == "CharacterInfo.lua":
        text += '''
-- Retroported race presentation: preserve the installed racial abilities and use distinct lore/name tables.
local skybornDescriptions = {
    SKYBORNE = "Azure-skinned elves distinguished by their feathered hair and keen magical senses. "
        .. "The High Order stand with the Alliance.",
    SKYBORNEHORDE = "Azure-skinned elves distinguished by their feathered hair and keen magical senses. "
        .. "The Windshapers stand with the Horde.",
};
for token,description in pairs(skybornDescriptions) do
    local source = RaceInfoByFileString[token];
    local info = {};
    for key,value in pairs(source or {}) do info[key] = value; end
    info.Name = token == "SKYBORNE" and "High Order Skyborn" or "Windshaper Skyborn";
    info.Description = description;
    RaceInfoByFileString[token] = info;
    _G["RACE_INFO_"..token] = description;
    _G["RACE_INFO_"..token.."_FEMALE"] = description;
end
'''
    return text


def build(client=p.CLIENT_DEFAULT):
    from luaparser import ast

    relatives = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)
    mirror = STAGE / "pack"
    report = {"source_hashes": {}, "stage_hashes": {}, "entries": []}
    for rel in relatives:
        target = mirror / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(rel)] = p.sha256(client / rel)
        shutil.copy2(client / rel, target)
        if p.sha256(target) != report["source_hashes"][str(rel)]:
            raise RuntimeError("Initial mirror copy mismatch: " + str(rel))
    storm = p.Storm(p.DLL_DEFAULT)
    locale = mirror / p.LOCALE_ARCHIVE_REL
    glue = {}
    for name in (*ECS, "CharacterInfo.lua"):
        key = p.GLUE_ROOT + name
        original = p._read_archive_entry(storm, locale, key)
        (STAGE / name).write_bytes(original)
        changed = patch(name, original.decode()).encode()
        ast.parse(changed.decode())
        glue[key] = changed
        source = p.ROOT / ".agents/plans/character-select-redesign/src/GlueXML" / name
        if name in ECS and source.exists() and source.read_bytes() == original:
            source.write_bytes(changed)
    art = {"\\".join(path.relative_to(expansion.ART).parts): path.read_bytes()
           for path in expansion.ART.rglob("*") if path.is_file()}
    # ECS supplies its own border, so use the masked portraits without a second baked ring.
    for race, sex, token, relative in icons.SOURCES:
        source = icons.PICTURES / relative
        template = p._read_archive_entry(storm, locale, icons.portraits.ICON_TEMPLATE_ENTRY)
        portrait = icons.portraits.portrait_bytes(source, icons.portraits.circular_mask())
        data = icons.portraits.encode_portrait(portrait, template)
        art[f"Interface\\Glues\\CharacterSelect\\ECS-Portrait-{token}{sex}.blp"] = data
    for rel in relatives:
        updates = art if rel == p.ASSET_ARCHIVE_REL else {**art, **glue}
        target = mirror / rel
        storm.replace_archive_entries(target, updates)
        handle = storm.open_archive(target)
        try:
            for name, data in updates.items():
                if storm.read(handle, name) != data:
                    raise RuntimeError("Touchup readback mismatch: " + name)
        finally:
            storm.dll.SFileCloseArchive(handle)
        report["stage_hashes"][str(rel)] = p.sha256(target)
    report["entries"] = sorted([*art, *glue])
    for name in ("Wow.exe", "EsteriaAppearance.dll", "EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin"):
        shutil.copy2(NATIVE / name, STAGE / name)
        report["source_hashes"][name] = p.sha256(client / name)
        report["stage_hashes"][name] = p.sha256(STAGE / name)
    (STAGE / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return {"entries": len(report["entries"]), "stage_hashes": report["stage_hashes"]}


def install(client=p.CLIENT_DEFAULT):
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW and Eclipse before installation")
    report = p.load_json(STAGE / "build-report.json")
    exe = p.load_json(NATIVE / "exe-patch-report.json")
    previous = p.load_json(NATIVE / "last-install.json")
    if p.sha256(client / "Wow.exe") != previous["installed_hashes"]["Wow.exe"]:
        raise ValueError("Live executable differs from the prior fingerprint-checked native installation")
    if p.sha256(STAGE / "Wow.exe") != exe["patched_sha256"]:
        raise ValueError("Staged executable differs from its audited patch report")
    backup = Path("C:/Users/Zach/.codex/backups") / ("race-touchups-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for name, digest in report["source_hashes"].items():
        rel = Path(name)
        source = client / rel
        staged = STAGE / "pack" / rel if rel.parts[0] == "Data" else STAGE / rel
        if p.sha256(source) != digest or p.sha256(staged) != report["stage_hashes"][name]:
            raise ValueError("Stale or modified touchup stage: " + name)
        target = backup / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if p.sha256(target) != digest:
            raise RuntimeError("Touchup backup mismatch: " + name)
    print("BACKUP VERIFIED " + str(backup), flush=True)
    for name, digest in report["stage_hashes"].items():
        rel = Path(name)
        source = STAGE / "pack" / rel if rel.parts[0] == "Data" else STAGE / rel
        target = client / rel
        temporary = target.with_suffix(target.suffix + ".touchup-next")
        shutil.copy2(source, temporary)
        if p.sha256(temporary) != digest:
            raise RuntimeError("Touchup install copy mismatch: " + name)
        os.replace(temporary, target)
        print("INSTALLED " + name, flush=True)
    report["backup"] = str(backup)
    (backup / "install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (STAGE / "last-install.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    previous["installed_hashes"].update(report["stage_hashes"])
    previous["helper_sha256"] = report["stage_hashes"]["EsteriaAppearance.dll"]
    previous["native_catalog_sha256"] = report["stage_hashes"]["EsteriaAppearance.bin"]
    previous["latest_touchup_backup"] = str(backup)
    (NATIVE / "last-install.json").write_text(json.dumps(previous, indent=2) + "\n", encoding="utf-8")
    return {"backup": str(backup), "installed_hashes": report["stage_hashes"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "install"))
    parser.add_argument("--client", type=Path, default=p.CLIENT_DEFAULT)
    args = parser.parse_args()
    print(json.dumps(build(args.client) if args.command == "build" else install(args.client), indent=2))
