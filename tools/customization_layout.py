"""Split extended creator controls around the preview; preserve both client archive layers."""

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from luaparser import ast
from lupa import LuaRuntime

import customization_label_repair as labels

p = labels.h.p
STAGE = Path("C:/Users/Zach/.codex/tmp/customization-layout")
KEY = p.GLUE_ROOT + "CharacterCreate.lua"
RELATIVES = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)
MARKER = "-- Esteria split customization columns:"


def patch(text):
    if MARKER in text:
        return text
    head, block = text.split("-- Esteria native appearance controls:", 1)
    old = "        local visibleRow=0;"
    replacement = '''        -- Esteria split customization columns: balance only selectable options.
        local optionCount=0;
        for i=1,29 do
            local _,count = CycleCharCustomization("EA_GET",i);
            if count and count>1 then optionCount=optionCount+1; end
        end
        local rowsPerColumn=math.max(1,math.ceil(optionCount/2));
        local rowSpacing=optionCount>22 and 28 or 36;
        local visibleRow=0;'''
    if block.count(old) != 1:
        raise ValueError("Extended picker row counter changed")
    block = block.replace(old, replacement, 1)
    block, changes = re.subn(
        r'            frame:SetPoint\("CENTER", parent, "CENTER",[^\n]*\);\n'
        r'            if CharacterCreate.selectedRaceID == 50 or CharacterCreate.selectedRaceID == 51 then\n'
        r'.*?            end\n(?=            local earthenChoiceText)',
        '''            local side=visibleRow>=rowsPerColumn and "TOPRIGHT" or "TOPLEFT";
            frame:SetPoint(side, CharacterCreateFrame, side, side=="TOPRIGHT" and -55 or 55,
                -110-(visibleRow%rowsPerColumn)*rowSpacing);
''', block, flags=re.S)
    if changes != 1:
        raise ValueError("Extended picker positioning changed")
    return head + "-- Esteria native appearance controls:" + block


def check(text):
    ast.parse(text)
    labels.check(text)
    lua = LuaRuntime()
    lua.execute('''
CharacterCreate={selectedRaceID=50};
CHAR_CUSTOMIZATION1_DESC="Skin Color"; CHAR_CUSTOMIZATION2_DESC="Face";
function widget()
    local w={shown=true};
    function w:GetParent() return parent; end
    function w:ClearAllPoints() self.point=nil; end
    function w:SetPoint(...) self.point={...}; end
    function w:SetID(id) self.id=id; end
    function w:IsShown() return self.shown; end
    function w:Show() self.shown=true; end
    function w:Hide() self.shown=false; end
    function w:SetText(text) self.text=text; end
    function w:SetScript(...) end
    return w;
end
parent=widget(); CharacterCreateFrame=widget();
for i=1,29 do
    _G["CharacterCustomizationButtonFrame"..i]=widget();
    _G["CharacterCustomizationButtonFrame"..i.."Text"]=widget();
end
for _,name in ipairs({"CharacterCreateRotateLeft","CharacterCreateRotateRight",
    "CharacterCreateRotateLeft30","CharacterCreateRotateRight30","CharacterCreateNameEdit"}) do
    _G[name]=widget();
end
function CreateFrame() return widget(); end
function CharacterCustomization_Left(id) clicked={id,-1}; end
function CharacterCustomization_Right(id) clicked={id,1}; end
function CharacterCreate_UpdateHairCustomization() end
counts={};
function CycleCharCustomization(command,index,delta)
    if command=="EA_GET" then return 0,counts[index],"Option"; end
    clicked={command,index,delta};
end
''')
    lua.execute(text[text.index("-- Esteria native appearance controls:"):])
    lua.execute('''
for _,race in ipairs({46,47,48,49,50,51,52,53}) do
    CharacterCreate.selectedRaceID=race;
    for _,total in ipairs({29,28,23,22,12,10,3,0}) do
        counts={}; for i=1,total do counts[i]=3; end
        if total==23 then counts[3]=1; end
        CharacterCustomizationButtonFrame1:Show();
        CharacterCreate_UpdateHairCustomization();
        local visible=total-(total==23 and 1 or 0);
        local rows=math.max(1,math.ceil(visible/2));
        local spacing=visible>22 and 28 or 36;
        local row=0;
        for i=1,29 do
            local frame=_G["CharacterCustomizationButtonFrame"..i];
            if counts[i] and counts[i]>1 then
                local side=row>=rows and "TOPRIGHT" or "TOPLEFT";
                assert(frame.shown and frame.point[1]==side and frame.point[2]==CharacterCreateFrame);
                assert(frame.point[3]==side and frame.point[4]==(side=="TOPRIGHT" and -55 or 55));
                assert(frame.point[5]==-110-(row%rows)*spacing);
                row=row+1;
            else assert(not frame.shown); end
        end
        assert(row==visible);
    end
    counts={}; for i=1,29 do counts[i]=3; end
    CharacterCustomizationButtonFrame1:Show();
    CharacterCustomization_Right(29);
    assert(clicked[1]=="EA_CYCLE" and clicked[2]==29 and clicked[3]==1);
    CharacterCustomization_Left(1);
    assert(clicked[1]=="EA_CYCLE" and clicked[2]==1 and clicked[3]==-1);
    CharacterCustomizationButtonFrame1:Hide();
    CharacterCreate_UpdateHairCustomization();
    for i=1,29 do assert(not _G["CharacterCustomizationButtonFrame"..i].shown); end
    CharacterCreate.selectedRaceID=11;
    CharacterCustomizationButtonFrame1:Show();
    CharacterCreate_UpdateHairCustomization();
    for i=1,5 do
        local point=_G["CharacterCustomizationButtonFrame"..i].point;
        assert(point[1]=="CENTER" and point[2]==parent and point[4]==900 and point[5]==200-i*50);
    end
    for i=6,29 do assert(not _G["CharacterCustomizationButtonFrame"..i].shown); end
end
''')
    return "PASS: balanced edge columns, hidden options, race switches, selector IDs and stock labels"


def save(path, report):
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")


def prepare():
    storm = p.Storm(p.DLL_DEFAULT)
    sources = {relative: p._read_archive_entry(storm, p.CLIENT_DEFAULT / relative, KEY) for relative in RELATIVES}
    candidates = {relative: patch(data.decode()).encode() for relative, data in sources.items()}
    report = {"source_hashes": {}, "stage_hashes": {}}
    for data in candidates.values():
        report["check"] = check(data.decode())
    backup = Path("C:/Users/Zach/.codex/backups") / (
        "customization-layout-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    report["backup"] = str(backup)
    for relative in RELATIVES:
        live, copy = p.CLIENT_DEFAULT / relative, backup / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        before = p.sha256(live)
        shutil.copy2(live, copy)
        if p.sha256(copy) != before or p._read_archive_entry(storm, copy, KEY) != sources[relative]:
            raise ValueError("Backup differs from the merge base")
        report["source_hashes"][str(relative)] = before
    for relative in RELATIVES:
        target = STAGE / "pack" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup / relative, target)
        storm.replace_archive_entries(target, {KEY: candidates[relative]})
        if p._read_archive_entry(storm, target, KEY) != candidates[relative]:
            raise ValueError("Staged Lua readback differs")
        report["stage_hashes"][str(relative)] = p.sha256(target)
    save(STAGE / "build-report.json", report)
    save(backup / "build-report.json", report)
    return report


def install():
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing their loaded archives")
    report = p.load_json(STAGE / "build-report.json")
    backup = Path(report["backup"])
    for relative in RELATIVES:
        if p.sha256(p.CLIENT_DEFAULT / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Live archive changed since preparation")
        if p.sha256(backup / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Backup changed")
        if p.sha256(STAGE / "pack" / relative) != report["stage_hashes"][str(relative)]:
            raise ValueError("Stage changed")
    try:
        for relative in RELATIVES:
            live = p.CLIENT_DEFAULT / relative
            temporary = live.with_suffix(".MPQ.layout-next")
            shutil.copy2(STAGE / "pack" / relative, temporary)
            if p.sha256(temporary) != report["stage_hashes"][str(relative)]:
                raise ValueError("Install copy differs")
            os.replace(temporary, live)
        for relative in RELATIVES:
            if p.sha256(p.CLIENT_DEFAULT / relative) != report["stage_hashes"][str(relative)]:
                raise ValueError("Installed archive differs")
    except Exception:
        for relative in RELATIVES:
            shutil.copy2(backup / relative, p.CLIENT_DEFAULT / relative)
        raise
    import expanded_appearance_pack as native
    for relative in RELATIVES:
        shutil.copy2(p.CLIENT_DEFAULT / relative, labels.h.STAGE / "pack" / relative)
    for directory in (labels.h.STAGE, labels.h.e.STAGE, labels.h.e.h.STAGE, native.STAGE):
        receipt = directory / "last-install.json"
        if receipt.exists():
            data = p.load_json(receipt)
            data["installed_hashes"].update(report["stage_hashes"])
            data["latest_layout_backup"] = str(backup)
            save(receipt, data)
    source = p._read_archive_entry(p.Storm(p.DLL_DEFAULT), p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, KEY)
    labels.h.path(labels.h.ART, KEY).write_bytes(source)
    report["status"] = "installed_awaiting_live_layout_check"
    build_file = labels.h.STAGE / "build-report.json"
    if build_file.exists():
        build = p.load_json(build_file)
        build["stage_hashes"].update(report["stage_hashes"])
        save(build_file, build)
    acceptance_file = labels.h.ROOT / "integration/acceptance.json"
    if acceptance_file.exists():
        acceptance = p.load_json(acceptance_file)
        acceptance["installed_hashes"].update(report["stage_hashes"])
        acceptance["customization_layout"] = report
        save(acceptance_file, acceptance)
    save(STAGE / "last-install.json", report)
    save(backup / "install-report.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "prepare", "install"))
    args = parser.parse_args()
    if args.action == "check":
        source = p._read_archive_entry(p.Storm(p.DLL_DEFAULT), p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, KEY)
        result = check(patch(source.decode()))
    else:
        result = {"prepare": prepare, "install": install}[args.action]()
    print(json.dumps(result, indent=2))
