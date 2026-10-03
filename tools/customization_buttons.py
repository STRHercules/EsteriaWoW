"""Repair creator dice buttons and keep one centered pair of smooth rotation controls."""

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

from luaparser import ast
from lupa import LuaRuntime

import character_ui_pack as ui

STAGE = Path("C:/Users/Zach/.codex/tmp/customize-buttons")
FILES = ("CharacterCreate.lua", "CharacterCreate.xml")
MARKER = "-- Esteria creator dice and smooth rotation:"
ATLAS = r"Interface\Glues\CharacterCreate\charactercreate.blp"


def block(text, tag, name):
    start = text.index(f'<{tag} name="{name}"')
    end = text.index(f"</{tag}>", start) + len(tag) + 3
    return text[start:end]


def patch_lua(text):
    if MARKER in text:
        return text
    text = ui.replace(text, "function CharacterCreate_SetupCustomButtons()",
                      MARKER + " reuse the client atlas and native name generator.\n"
                      "function CharacterCreate_SetupCustomButtons()")
    text = ui.replace(text,
                      "{button = CharacterCreateRandomName, width = 30, height = 30}",
                      "{button = CharacterCreateRandomName, width = 30, height = 30},\n"
                      "        {button = CharacterCreateRandomLastName, width = 30, height = 30}")
    text = ui.replace(text, 'local texturePath = "Interface\\\\Buttons\\\\charactercreate.blp"',
                      'local texturePath = "Interface\\\\Glues\\\\CharacterCreate\\\\charactercreate"')
    for state in ("Normal", "Pushed"):
        suffix = "Up" if state == "Normal" else "Down"
        text = ui.replace(text, f'button:Set{state}Texture(texturePath.."-{suffix}")',
                          f"button:Set{state}Texture(texturePath)")
    text = ui.replace(text, "function CharacterCreate_RandomizeName()\n"
                      "    CharacterCreate_SetNameFields(GetRandomName());\nend",
                      "function CharacterCreate_RandomizeName(editBox)\n"
                      "    local field = editBox or CharacterCreateNameEdit;\n"
                      "    field:SetText(GetRandomName());\nend")
    text = re.sub(r"^(\s*)CharacterCreateRandomName:(Show|Hide)\(\);?$",
                  lambda m: m.group(0) + "\n" + m[1] + f"CharacterCreateRandomLastName:{m[2]}();",
                  text, flags=re.M)
    start = text.index("    local rotateButtons =", text.index("local function EA_REFRESH()"))
    end = text.index("    for i=6,29 do", start)
    text = text[:start] + text[end:]
    for direction in ("Left", "Right"):
        text = re.sub(rf"^ *CharacterCreateRotate{direction}30:(Show|Hide)\(\);\n", "", text, flags=re.M)
        pattern = rf"^function CharacterCreate_Rotate{direction}30\(\).*?^end\n\n"
        text, count = re.subn(pattern, "", text, flags=re.M | re.S)
        if count != 1:
            raise ValueError("Expected one incremented rotation function: " + direction)
    return text


def patch_xml(text):
    if 'name="CharacterCreateRandomLastName"' in text:
        return text
    first = block(text, "Button", "CharacterCreateRandomName")
    last = first.replace('name="CharacterCreateRandomName"', 'name="CharacterCreateRandomLastName"')
    last = last.replace('relativeTo="CharacterCreateNameEdit"', 'relativeTo="CharacterCreateLastNameEdit"')
    last = last.replace(' text="RANDOMIZE" hidden="true">',
                        '\n                        text="RANDOMIZE" hidden="true">')
    last = last.replace(' relativePoint="RIGHT" x="-30" y="35"/>',
                        '\n                                relativePoint="RIGHT" x="-30" y="35"/>')
    last = last.replace("CharacterCreate_RandomizeName();",
                        "CharacterCreate_RandomizeName(CharacterCreateLastNameEdit);")
    text = ui.replace(text, first, first + "\n                    " + last)
    appearance = block(text, "Button", "CharCreateRandomizeButton")
    updated = ui.replace(appearance, '<Anchor point="CENTER" x="280" y="-100"/>',
                         '<Anchor point="BOTTOM" relativeTo="CharacterCreateNameEdit"\n                                '
                         'relativePoint="TOP" x="110" y="42"/>')
    # The dice atlas stays the same for every class; panel recoloring would replace its icon.
    updated = re.sub(r"\s*<OnUpdate>.*?</OnUpdate>", "", updated, flags=re.S)
    text = ui.replace(text, appearance, updated)
    for direction, field, offset in (("Left", "CharacterCreateNameEdit", 88),
                                     ("Right", "CharacterCreateLastNameEdit", -88)):
        smooth = block(text, "Button", "CharacterCreateRotate" + direction)
        stepped = block(text, "Button", "CharacterCreateRotate" + direction + "30")
        updated = re.sub(r"<Anchor [^>]+/>",
                         f'<Anchor point="TOP" relativeTo="{field}"\n                                '
                         'relativePoint="BOTTOM" '
                         f'x="{offset}" y="-8"/>', smooth, count=1)
        for texture in ("NormalTexture", "PushedTexture"):
            pattern = rf"<{texture}\b[^>]*(?:/>|>.*?</{texture}>)"
            art = re.search(pattern, stepped, re.S).group(0)
            updated = re.sub(pattern, lambda _: art, updated, count=1, flags=re.S)
        text = ui.replace(text, smooth, updated)
        text = ui.replace(text, "                    " + stepped, "")
    text = re.sub(r'\n{3,}(?=                    <Button name="CharCreatePersonalizeButton")', "\n\n", text)
    return ui.replace(text, "                CharacterCreateRandomName:Show();\n", "")


def check(lua_text, xml_text):
    ast.parse(lua_text)
    root = ElementTree.fromstring(xml_text)
    assert patch_lua(lua_text) == lua_text and patch_xml(xml_text) == xml_text
    assert not re.search(r"CharacterCreate(?:_)?Rotate(?:Left|Right)30", lua_text + xml_text)
    ns = {"ui": "http://www.blizzard.com/wow/ui/"}
    buttons = {node.attrib["name"]: node for node in root.findall(".//ui:Button", ns)}
    appearance = buttons["CharCreateRandomizeButton"]
    assert appearance.find("ui:Scripts/ui:OnUpdate", ns) is None
    points = []
    for direction, centre in (("Left", -110), ("Right", 110)):
        node = buttons["CharacterCreateRotate" + direction]
        anchor = node.find("ui:Anchors/ui:Anchor", ns)
        assert anchor.attrib["point"] == "TOP" and anchor.attrib["relativePoint"] == "BOTTOM"
        assert anchor.attrib["y"] == "-8"
        points.append(centre + int(anchor.attrib["x"]))
        assert node.find("ui:Scripts/ui:OnUpdate", ns).text.strip() == (
            "CharacterCreateRotate" + direction + "_OnUpdate(self);")
        for state in ("Normal", "Pushed"):
            assert node.find(f"ui:{state}Texture", ns).attrib["file"] == ATLAS[:-4]
    assert points == [-22, 22]
    lua = LuaRuntime()
    lua.execute('''
function widget()
    local w={shown=false,text="",state="NORMAL"};
    function w:Show() self.shown=true; end
    function w:Hide() self.shown=false; end
    function w:SetText(text) self.text=text; end
    function w:GetText() return self.text; end
    function w:SetSize(x,y) self.width=x; self.height=y; end
    function w:GetFontString() return self; end
    function w:GetButtonState() return self.state; end
    function w:SetTexCoord(...) self.coords={...}; end
    function w:SetBlendMode(mode) self.blend=mode; end
    for _,kind in ipairs({"Normal","Pushed","Highlight"}) do
        w["Set"..kind.."Texture"]=function(self,path) self[kind]=widget(); self[kind].path=path; end;
        w["Get"..kind.."Texture"]=function(self) return self[kind]; end;
    end
    return w;
end
CharacterCreate={personalizationMode=false}; NUM_CHAR_CUSTOMIZATIONS=5;
for _,name in ipairs({"CharacterCreateRaceButtonsContainer","CharacterCreateClassButtonsContainer",
    "CharacterCreateGenderButtonsContainer","CustomizationLogoAlliance","CustomizationTextAlliance",
    "CustomizationLogoHorde","CustomizationTextHorde","CharacterCreateRotateLeft","CharacterCreateRotateRight",
    "CharCreatePersonalizeButton","CharCreateOkayButton","CharCreateRandomizeButton","CharacterCreateNameEdit",
    "CharacterCreateLastNameEdit","CharacterCreateRandomName","CharacterCreateRandomLastName"}) do
    _G[name]=widget();
end
for i=1,5 do _G["CharacterCustomizationButtonFrame"..i]=widget(); end
function PlaySound() end
function CharacterCreate_UpdateHairCustomization() end
function GetRandomName() return randomName; end
function GetCharacterCreateFacing() return facing or 0; end
function SetCharacterCreateFacing(value) facing=value; end
function RandomizeCharCustomization() randomized="stock"; end
function CycleCharCustomization(command) randomized=command; end
CHARACTER_FACING_INCREMENT=2;
''')
    for name in ("SetupCustomButtons", "TogglePersonalization", "ResetState", "RandomizeName", "Randomize"):
        function = re.search(rf"^function CharacterCreate_{name}\([^\n]*\).*?^end", lua_text, re.M | re.S)
        lua.execute(function.group(0))
    for direction in ("Left", "Right"):
        function = re.search(rf"^function CharacterCreateRotate{direction}_OnUpdate\(self\).*?^end",
                             lua_text, re.M | re.S)
        lua.execute(function.group(0))
    lua.execute('''
CharacterCreate_SetupCustomButtons();
for _,button in ipairs({CharCreateRandomizeButton,CharacterCreateRandomName,CharacterCreateRandomLastName}) do
    assert(button.Normal.path=="Interface\\\\Glues\\\\CharacterCreate\\\\charactercreate");
    assert(button.Pushed.path==button.Normal.path);
    assert(button.Normal.coords[1]==0.261230469 and button.Pushed.coords[1]==0.223144531);
    assert(button.width==(button==CharCreateRandomizeButton and 36 or 30));
end
for race=1,54 do
    CharacterCreate.selectedRaceID=race;
    CharacterCreate_TogglePersonalization();
    for _,button in ipairs({CharCreateRandomizeButton,CharacterCreateRandomName,CharacterCreateRandomLastName,
        CharacterCreateNameEdit,CharacterCreateLastNameEdit,CharacterCreateRotateLeft,CharacterCreateRotateRight}) do
        assert(button.shown);
    end
    CharacterCreate_Randomize(); assert(randomized=="stock" or randomized=="EA_RANDOM");
    CharacterCreate_TogglePersonalization();
    assert(not CharacterCreateRandomName.shown and not CharacterCreateRandomLastName.shown);
    CharacterCreate_TogglePersonalization(); CharacterCreate_ResetState();
    assert(not CharacterCreateRandomName.shown and not CharacterCreateRandomLastName.shown);
end
CharacterCreateNameEdit:SetText("First"); CharacterCreateLastNameEdit:SetText("Last");
randomName="Newfirst"; CharacterCreate_RandomizeName();
assert(CharacterCreateNameEdit.text=="Newfirst" and CharacterCreateLastNameEdit.text=="Last");
randomName="Newlast"; CharacterCreate_RandomizeName(CharacterCreateLastNameEdit);
assert(CharacterCreateNameEdit.text=="Newfirst" and CharacterCreateLastNameEdit.text=="Newlast");
CharacterCreateRotateLeft.state="PUSHED"; CharacterCreateRotateLeft_OnUpdate(CharacterCreateRotateLeft);
assert(facing==-2);
CharacterCreateRotateLeft.state="NORMAL"; CharacterCreateRotateLeft_OnUpdate(CharacterCreateRotateLeft);
assert(facing==-2);
CharacterCreateRotateRight.state="PUSHED"; CharacterCreateRotateRight_OnUpdate(CharacterCreateRotateRight);
assert(facing==0);
''')
    for name in ("CharacterCreateRandomName", "CharacterCreateRandomLastName", "CharCreateRandomizeButton"):
        lua.execute(buttons[name].find("ui:Scripts/ui:OnClick", ns).text)
    assert lua.globals().CharacterCreateNameEdit.text == "Newlast"
    assert lua.globals().CharacterCreateLastNameEdit.text == "Newlast"
    return "PASS: dice textures, independent names, centered smooth rotation, customize/reset visibility"


def candidates(storm, archive):
    source = ui.read(storm, archive)
    updated = dict(source)
    for name, patch in zip(FILES, (patch_lua, patch_xml)):
        updated[name] = patch(source[name].decode("utf-8-sig")).encode()
    check(updated[FILES[0]].decode(), updated[FILES[1]].decode())
    return source, updated


def prepare():
    storm = ui.Storm(ui.DLL_DEFAULT)
    backup = Path("C:/Users/Zach/.codex/backups") / (
        "customize-buttons-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    report = {"backup": str(backup), "source_hashes": {}, "stage_hashes": {}}
    for relative in ui.ARCHIVES:
        live, copy, target = ui.CLIENT / relative, backup / relative, STAGE / "pack" / relative
        source, updated = candidates(storm, live)
        before = ui.sha(live)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, copy)
        if ui.sha(copy) != before or ui.sha(live) != before or ui.read(storm, copy) != source:
            raise ValueError("Backup differs from the merge base")
        for name in FILES:
            output = STAGE / "patched" / relative.stem / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(updated[name])
            output.with_suffix(output.suffix + ".diff").write_text("".join(difflib.unified_diff(
                source[name].decode().splitlines(True), updated[name].decode().splitlines(True),
                fromfile="live/" + name, tofile="patched/" + name)), encoding="utf-8", newline="\n")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(copy, target)
        storm.replace_archive_entries(target, {ui.GLUE + name: updated[name] for name in FILES})
        if ui.read(storm, target) != updated:
            raise ValueError("Staged creator readback differs or roster files changed")
        report["source_hashes"][str(relative)] = before
        report["stage_hashes"][str(relative)] = ui.sha(target)
    report["check"] = check(updated[FILES[0]].decode(), updated[FILES[1]].decode())
    ui.save(STAGE / "build-report.json", report)
    ui.save(backup / "build-report.json", report)
    return report


def install():
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if '"wow.exe"' in processes or '"eclipse.exe"' in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing their loaded UI archives")
    report = json.loads((STAGE / "build-report.json").read_text())
    backup = Path(report["backup"])
    for relative in ui.ARCHIVES:
        if ui.sha(ui.CLIENT / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Live archive changed since preparation")
        if ui.sha(backup / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Rollback backup differs")
        if ui.sha(STAGE / "pack" / relative) != report["stage_hashes"][str(relative)]:
            raise ValueError("Staged archive changed")
    try:
        for relative in ui.ARCHIVES:
            live = ui.CLIENT / relative
            temporary = live.with_suffix(".MPQ.buttons-next")
            shutil.copy2(STAGE / "pack" / relative, temporary)
            if ui.sha(temporary) != report["stage_hashes"][str(relative)]:
                raise ValueError("Install copy differs")
            os.replace(temporary, live)
        for relative in ui.ARCHIVES:
            if ui.sha(ui.CLIENT / relative) != report["stage_hashes"][str(relative)]:
                raise ValueError("Installed archive differs")
            _, updated = candidates(ui.Storm(ui.DLL_DEFAULT), ui.CLIENT / relative)
    except Exception:
        for relative in ui.ARCHIVES:
            shutil.copy2(backup / relative, ui.CLIENT / relative)
        raise
    report["status"] = "installed_awaiting_live_customize_screen_test"
    ui.save(STAGE / "last-install.json", report)
    ui.save(backup / "install-report.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "prepare", "install"))
    action = parser.parse_args().action
    if action == "check":
        for relative in ui.ARCHIVES:
            _, updated = candidates(ui.Storm(ui.DLL_DEFAULT), ui.CLIENT / relative)
        result = check(updated[FILES[0]].decode(), updated[FILES[1]].decode())
    else:
        result = {"prepare": prepare, "install": install}[action]()
    print(json.dumps(result, indent=2))
