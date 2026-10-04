"""Restore stock picker labels after expanded races; replace only the winning creator Lua entries."""

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from luaparser import ast
from lupa import LuaRuntime

import haranir_race_pack as h

STAGE = Path("C:/Users/Zach/.codex/tmp/customization-labels")
KEY = h.p.GLUE_ROOT + "CharacterCreate.lua"
RELATIVES = (h.p.GLOBAL_ARCHIVE_REL, h.p.LOCALE_ARCHIVE_REL)


def check(text):
    ast.parse(text)
    lua = LuaRuntime()
    lua.execute('''
CharacterCreate = {selectedRaceID=50};
CHAR_CUSTOMIZATION1_DESC="Skin Color"; CHAR_CUSTOMIZATION2_DESC="Face";
function widget(name)
    local w={name=name,shown=true,id=tonumber(string.match(name,"%d+$"))};
    function w:GetParent() return self; end
    function w:ClearAllPoints() end
    function w:SetPoint(...) end
    function w:SetID(id) self.id=id; end
    function w:IsShown() return self.shown; end
    function w:Show() self.shown=true; end
    function w:Hide() self.shown=false; end
    function w:SetText(text) self.text=text; end
    return w;
end
for i=1,29 do
    _G["CharacterCustomizationButtonFrame"..i]=widget("frame"..i);
    _G["CharacterCustomizationButtonFrame"..i.."Text"]=widget("text"..i);
end
for _,name in ipairs({"CharacterCreateRotateLeft","CharacterCreateRotateRight",
    "CharacterCreateRotateLeft30","CharacterCreateRotateRight30","CharacterCreateNameEdit"}) do
    _G[name]=widget(name);
end
function CreateFrame() local w=widget("extra"); function w:SetScript(...) end; return w; end
local expanded={"Hair Style","Eyebrows","Tusk","Shoulder Spine","Skin Color"};
function CycleCharCustomization(command,index,delta)
    if command=="EA_GET" then return 0,3,expanded[index] or "Accessory"; end
    clicked={command,index,delta};
end
function CharacterCustomization_Left(id) CycleCharCustomization(id,-1); end
function CharacterCustomization_Right(id) CycleCharCustomization(id,1); end
function CharacterCreate_UpdateHairCustomization()
    CharacterCustomizationButtonFrame3Text:SetText("Hair Style");
    CharacterCustomizationButtonFrame4Text:SetText("Hair Color");
    CharacterCustomizationButtonFrame5Text:SetText("Features");
end
''')
    marker = "-- Esteria native appearance controls:"
    lua.execute(text[text.index(marker):])
    lua.execute('''
for _,expandedRace in ipairs({46,47,48,49,50,51,52,53}) do
    CharacterCreate.selectedRaceID=expandedRace;
    CharacterCreate_UpdateHairCustomization();
    assert(CharacterCustomizationButtonFrame6.shown);
    if expandedRace==50 or expandedRace==51 then
        assert(CharacterCustomizationButtonFrame1Text.text=="Hair Style  1/3");
    end
    CharacterCreate.selectedRaceID=11;
    CharacterCreate_UpdateHairCustomization();
    assert(CharacterCustomizationButtonFrame1Text.text=="Skin Color");
    assert(CharacterCustomizationButtonFrame2Text.text=="Face");
    assert(CharacterCustomizationButtonFrame3Text.text=="Hair Style");
    assert(CharacterCustomizationButtonFrame4Text.text=="Hair Color");
    assert(CharacterCustomizationButtonFrame5Text.text=="Features");
    for i=6,29 do assert(not _G["CharacterCustomizationButtonFrame"..i].shown); end
    CharacterCustomization_Right(1); assert(clicked[1]==1 and clicked[2]==1);
    CharacterCustomization_Right(3); assert(clicked[1]==3 and clicked[2]==1);
end
''')
    return "PASS: expanded race to Draenei restores labels and keeps stock selector IDs"


def prepare():
    storm = h.p.Storm(h.p.DLL_DEFAULT)
    receipt = h.p.load_json(h.STAGE / "last-install.json")
    report = {"source_hashes": {}, "stage_hashes": {}}
    for relative in RELATIVES:
        offline = h.STAGE / "pack" / relative
        before = h.p.sha256(h.p.CLIENT_DEFAULT / relative)
        if before != receipt["installed_hashes"][str(relative)] or h.p.sha256(offline) != before:
            raise ValueError("Offline/live merge base differs: " + str(relative))
        old = h.p._read_archive_entry(storm, offline, KEY).decode()
        text = h.restore_standard_labels(old)
        report["check"] = check(text)
        target = STAGE / "pack" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(offline, target)
        storm.replace_archive_entries(target, {KEY: text.encode()})
        if h.p._read_archive_entry(storm, target, KEY) != text.encode():
            raise ValueError("Staged Lua readback differs")
        report["source_hashes"][str(relative)] = before
        report["stage_hashes"][str(relative)] = h.p.sha256(target)
    h.save(STAGE / "build-report.json", report)
    return report


def install():
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing their loaded archives")
    report = h.p.load_json(STAGE / "build-report.json")
    backup = Path("C:/Users/Zach/.codex/backups") / ("customization-labels-" +
        datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for relative in RELATIVES:
        live, candidate = h.p.CLIENT_DEFAULT / relative, STAGE / "pack" / relative
        if h.p.sha256(live) != report["source_hashes"][str(relative)]:
            raise ValueError("Archive changed since staging")
        if h.p.sha256(candidate) != report["stage_hashes"][str(relative)]:
            raise ValueError("Stage changed")
        copy = backup / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, copy)
        if h.p.sha256(copy) != report["source_hashes"][str(relative)]:
            raise ValueError("Rollback copy differs")
    try:
        for relative in RELATIVES:
            live = h.p.CLIENT_DEFAULT / relative
            temporary = live.with_suffix(".MPQ.labels-next")
            shutil.copy2(STAGE / "pack" / relative, temporary)
            if h.p.sha256(temporary) != report["stage_hashes"][str(relative)]:
                raise ValueError("Install copy differs")
            os.replace(temporary, live)
            shutil.copy2(live, h.STAGE / "pack" / relative)
    except Exception:
        for relative in RELATIVES:
            shutil.copy2(backup / relative, h.p.CLIENT_DEFAULT / relative)
            shutil.copy2(backup / relative, h.STAGE / "pack" / relative)
        raise
    import expanded_appearance_pack as native
    for directory in (h.STAGE, h.e.STAGE, h.e.h.STAGE, native.STAGE):
        file = directory / "last-install.json"
        if file.exists():
            data = h.p.load_json(file)
            data["installed_hashes"].update(report["stage_hashes"])
            data["latest_label_backup"] = str(backup)
            h.save(file, data)
    report.update(backup=str(backup), status="installed_awaiting_live_race_switch")
    h.save(STAGE / "last-install.json", report)
    h.save(backup / "install-report.json", report)
    build_file = h.STAGE / "build-report.json"
    if build_file.exists():
        build = h.p.load_json(build_file)
        build["stage_hashes"].update(report["stage_hashes"])
        h.save(build_file, build)
    text = h.p._read_archive_entry(h.p.Storm(h.p.DLL_DEFAULT), STAGE / "pack" / h.p.LOCALE_ARCHIVE_REL, KEY)
    h.path(h.ART, KEY).write_bytes(text)
    acceptance_file = h.ROOT / "integration/acceptance.json"
    if acceptance_file.exists():
        acceptance = h.p.load_json(acceptance_file)
        acceptance["installed_hashes"].update(report["stage_hashes"])
        acceptance["label_restoration"] = report
        h.save(acceptance_file, acceptance)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "install"))
    print(json.dumps({"prepare": prepare, "install": install}[parser.parse_args().action](), indent=2))
