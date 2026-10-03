"""Stage and install focused creator/roster GlueXML changes with verified MPQ backups."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

from luaparser import ast
from cars_mount_pack import DLL_DEFAULT, Storm

CLIENT = Path("G:/3.3.5a - Dev")
STAGE = Path("C:/Users/Zach/.codex/tmp/character-ui")
ARCHIVES = (Path("Data/patch-Z.MPQ"), Path("Data/enUS/patch-enUS-Z.MPQ"))
ZOOM_REL = Path("Extensions/wxl-glue-zoom/wxl-glue-zoom.dll")
FILES = ("CharacterCreate.lua", "CharacterCreate.xml", "CharacterSelect.lua", "CharacterSelect.xml")
GLUE = "Interface\\GlueXML\\"
MARKER = "-- Esteria customization dropdown:"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Expected exactly one patch anchor: " + old[:100])
    return text.replace(old, new, 1)


def hide_horde_vrykul(text):
    if 'strupper(fileString) == "VRYKULHORDE"' in text:
        return text
    text = replace(text, 'local hiddenRace = strupper(fileString) == "SETHRAK"',
                   'local hiddenRace = strupper(fileString) == "SETHRAK" '
                   'or strupper(fileString) == "VRYKULHORDE"')
    text = replace(text, 'local hiddenRaceID;', 'local hiddenSelection = false;')
    text = replace(text, 'hiddenRaceID = raceID',
                   'hiddenSelection = hiddenSelection or GetSelectedRace() == index;')
    return replace(text, 'if hiddenRaceID and GetSelectedRace() == hiddenRaceID '
                   'and CharacterCreate.raceIndicesAlliance[1] then',
                   'if hiddenSelection and CharacterCreate.raceIndicesAlliance[1] then')


def patch(name, text):
    if name == "CharacterCreate.lua":
        text = hide_horde_vrykul(text)
        text = text.split(MARKER)[0].rstrip() + "\n"
        anchor = '    for i=6,29 do\n'
        setup = '''    CharCreateRandomizeButton:ClearAllPoints();
    CharCreateRandomizeButton:SetPoint("RIGHT", CharacterCreateRotateLeft, "LEFT", -8, 0);
'''
        if setup not in text:
            head, tail = text.split("local function EA_REFRESH()", 1)
            tail = replace(tail, anchor, setup + anchor)
            text = head + "local function EA_REFRESH()" + tail
        return text + Path(__file__).with_name("character_ui").joinpath("CustomizationDropdown.lua").read_text()
    if name == "CharacterCreate.xml":
        start = text.index('<Frame name="CharacterCustomizationFrameTemplate"')
        end = text.index("\n    </Frame>", start) + len("\n    </Frame>")
        block = text[start:end]
        block = block.replace('<AbsDimension x="230" y="32"/>', '<AbsDimension x="340" y="32"/>')
        block = block.replace('<AbsDimension x="150" y="34"/>', '<AbsDimension x="284" y="34"/>')
        button = '''            <Button name="$parentChoiceButton">
                <Size x="284" y="28"/>
                <Anchors><Anchor point="CENTER"/></Anchors>
                <Scripts><OnClick>CharacterCustomization_OpenChoices(self);</OnClick></Scripts>
                <HighlightTexture file="Interface\\Buttons\\UI-Common-MouseHilight" alphaMode="ADD"/>
            </Button>
'''
        if '$parentChoiceButton' not in block:
            block = replace(block, "        <Frames>\n", "        <Frames>\n" + button)
        text = text[:start] + block + text[end:]
        start = text.index('<Button name="CharCreateRandomizeButton"')
        end = text.index("</Button>", start) + len("</Button>")
        block = text[start:end].replace('<Size x="146" y="30"/>', '<Size x="92" y="28"/>')
        return text[:start] + block + text[end:]
    if name == "CharacterSelect.lua":
        old = '''        CharacterSelect.scrollUpdating = false;
    end
end

function CharacterSelect_AdjustOffsetForSelection()'''
        new = '''        local scrollbar = CharacterSelectCharacterScrollFrameScrollBar;
        if scrollbar then
            scrollbar:SetValue((CharacterSelect.scrollOffset or 0) * CHARACTER_SELECT_ROW_HEIGHT);
            GlueScrollFrame_OnVerticalScroll(CharacterSelectCharacterScrollFrame, scrollbar:GetValue());
        end
        CharacterSelect.scrollUpdating = false;
    end
end

function CharacterSelect_AdjustOffsetForSelection()'''
        if "local scrollbar = CharacterSelectCharacterScrollFrameScrollBar;" not in text:
            text = replace(text, old, new)
        return text
    if name == "CharacterSelect.xml":
        text = text.replace('text="CREATE_NEW_CHARACTER"', 'text="New Character"')
        text = text.replace('"TOPRIGHT", 7, 4)', '"TOPRIGHT", -3, 4)')
        text = text.replace('"BOTTOMRIGHT", 7, 12)', '"BOTTOMRIGHT", -3, 12)')
        text = text.replace('"TOPRIGHT", -3, 4)', '"TOPRIGHT", -18, 4)')
        text = text.replace('"BOTTOMRIGHT", -3, 12)', '"BOTTOMRIGHT", -18, 12)')
        anchor = '                                        GlueScrollFrame_OnScrollRangeChanged(self, yrange);'
        setup = ' ' * 40 + '''local scrollbar = CharacterSelectCharacterScrollFrameScrollBar;
                                        scrollbar:SetValueStep(CHARACTER_SELECT_ROW_HEIGHT);
                                        scrollbar:SetScript("OnValueChanged", function(_, value)
                                            if not CharacterSelect.scrollUpdating then
                                                CharacterSelect_SetScrollOffset(value / CHARACTER_SELECT_ROW_HEIGHT);
                                            end
                                        end);
                                        CharacterSelectCharacterScrollFrameScrollBarScrollUpButton:SetScript(
                                            "OnClick", function() CharacterSelect_ScrollBy(1); end);
                                        CharacterSelectCharacterScrollFrameScrollBarScrollDownButton:SetScript(
                                            "OnClick", function() CharacterSelect_ScrollBy(-1); end);
'''
        if 'scrollbar:SetValueStep(CHARACTER_SELECT_ROW_HEIGHT)' not in text:
            text = text.replace(anchor, setup + anchor, 1)
        return text
    raise ValueError(name)


def read(storm, archive):
    handle = storm.open_archive(archive)
    try:
        return {name: storm.read(handle, GLUE + name) for name in FILES}
    finally:
        storm.dll.SFileCloseArchive(handle)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def prepare():
    storm = Storm(DLL_DEFAULT)
    backup = Path("C:/Users/Zach/.codex/backups") / (
        "character-ui-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    report = {"backup": str(backup), "source_hashes": {}, "stage_hashes": {}}
    for relative in ARCHIVES:
        live, copy, stage = CLIENT / relative, backup / relative, STAGE / "pack" / relative
        before = sha(live)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, copy)
        if sha(copy) != before or sha(live) != before:
            raise ValueError("Backup changed while being copied")
        updates = {GLUE + name: patch(name, data.decode("utf-8-sig")).encode()
                   for name, data in read(storm, copy).items()}
        for name in FILES:
            text = updates[GLUE + name].decode()
            ast.parse(text) if name.endswith(".lua") else ElementTree.fromstring(text)
            output = STAGE / "source" / relative.stem / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text, encoding="utf-8", newline="\n")
        stage.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(copy, stage)
        storm.replace_archive_entries(stage, updates)
        if {GLUE + name: data for name, data in read(storm, stage).items()} != updates:
            raise ValueError("Staged entry readback differs")
        report["source_hashes"][str(relative)] = before
        report["stage_hashes"][str(relative)] = sha(stage)
    native = CLIENT / "EsteriaAppearance.dll"
    native_backup = backup / native.name
    report["native_source_hash"] = sha(native)
    shutil.copy2(native, native_backup)
    if sha(native_backup) != report["native_source_hash"]:
        raise ValueError("Native helper backup differs")
    report["native_stage_hash"] = sha(STAGE / "native" / native.name)
    zoom = CLIENT / ZOOM_REL
    zoom_stage = STAGE / "native" / ZOOM_REL.name
    zoom_receipt = json.loads(zoom_stage.with_suffix(".json").read_text())
    report["zoom_source_hash"] = sha(zoom)
    report["zoom_stage_hash"] = sha(zoom_stage)
    if report["zoom_source_hash"] not in (zoom_receipt["source_hash"], zoom_receipt["patched_hash"]):
        raise ValueError("GlueZoom changed since fingerprinted staging")
    if report["zoom_stage_hash"] != zoom_receipt["patched_hash"]:
        raise ValueError("GlueZoom guard stage differs")
    zoom_backup = backup / ZOOM_REL
    zoom_backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(zoom, zoom_backup)
    if sha(zoom_backup) != report["zoom_source_hash"]:
        raise ValueError("GlueZoom rollback backup differs")
    save(STAGE / "build-report.json", report)
    save(backup / "build-report.json", report)
    return report


def install():
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if '"wow.exe"' in processes or '"eclipse.exe"' in processes:
        raise RuntimeError("Close WoW before installing its UI archives")
    report = json.loads((STAGE / "build-report.json").read_text())
    backup = Path(report["backup"])
    native = CLIENT / "EsteriaAppearance.dll"
    if sha(native) != report["native_source_hash"] or sha(backup / native.name) != report["native_source_hash"]:
        raise ValueError("Native helper or rollback copy changed")
    if sha(STAGE / "native" / native.name) != report["native_stage_hash"]:
        raise ValueError("Native helper stage changed")
    zoom = CLIENT / ZOOM_REL
    if sha(zoom) != report["zoom_source_hash"] or sha(backup / ZOOM_REL) != report["zoom_source_hash"]:
        raise ValueError("GlueZoom or rollback copy changed")
    if sha(STAGE / "native" / ZOOM_REL.name) != report["zoom_stage_hash"]:
        raise ValueError("GlueZoom stage changed")
    for relative in ARCHIVES:
        if sha(CLIENT / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Live archive changed since preparation")
        if sha(backup / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Rollback backup differs")
        if sha(STAGE / "pack" / relative) != report["stage_hashes"][str(relative)]:
            raise ValueError("Stage differs")
    try:
        if report["native_source_hash"] != report["native_stage_hash"]:
            native_next = native.with_suffix(".dll.ui-next")
            shutil.copy2(STAGE / "native" / native.name, native_next)
            if sha(native_next) != report["native_stage_hash"]:
                raise ValueError("Native install copy differs")
            os.replace(native_next, native)
        for relative in ARCHIVES:
            live = CLIENT / relative
            temporary = live.with_suffix(".MPQ.ui-next")
            shutil.copy2(STAGE / "pack" / relative, temporary)
            if sha(temporary) != report["stage_hashes"][str(relative)]:
                raise ValueError("Install copy differs")
            os.replace(temporary, live)
        for relative in ARCHIVES:
            if sha(CLIENT / relative) != report["stage_hashes"][str(relative)]:
                raise ValueError("Installed archive differs")
        if report["zoom_source_hash"] != report["zoom_stage_hash"]:
            zoom_next = zoom.with_suffix(".dll.ui-next")
            shutil.copy2(STAGE / "native" / zoom.name, zoom_next)
            if sha(zoom_next) != report["zoom_stage_hash"]:
                raise ValueError("GlueZoom install copy differs")
            os.replace(zoom_next, zoom)
        if sha(native) != report["native_stage_hash"] or sha(zoom) != report["zoom_stage_hash"]:
            raise ValueError("Installed DLL differs")
    except Exception:
        if report["zoom_source_hash"] != report["zoom_stage_hash"]:
            shutil.copy2(backup / ZOOM_REL, zoom)
        if report["native_source_hash"] != report["native_stage_hash"]:
            shutil.copy2(backup / native.name, native)
        for relative in ARCHIVES:
            shutil.copy2(backup / relative, CLIENT / relative)
        raise
    report["status"] = "installed_awaiting_live_UI_test"
    save(STAGE / "last-install.json", report)
    save(backup / "install-report.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "install"))
    print(json.dumps({"prepare": prepare, "install": install}[parser.parse_args().action](), indent=2))
