"""Install six supplied Mag'har/Skyborne portraits and a compact faction race grid."""

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

import race_portrait_pack as portraits
import retroported_race_pack as pack
from two_names_client_pack import XML_ENTRY, hide_name_fields, sync_name_visibility

STAGE = Path("C:/Users/Zach/.codex/tmp/creator-portraits")
PICTURES = portraits.DEFAULT_SOURCE
SOURCES = (
    (45, "Male", "Maghar", "Horde/Charactercreate-races_maghar-male.png"),
    (45, "Female", "Maghar", "Horde/Charactercreate-races_maghar-female.png"),
    (52, "Male", "Skyborne", "Alliance/SkybornMale_Alliance.png"),
    (52, "Female", "Skyborne", "Alliance/SkybornFemale_Alliance.png"),
    (53, "Male", "SkyborneHorde", "Horde/SkybornMale_Horde.png"),
    (53, "Female", "SkyborneHorde", "Horde/SkybornFemale_Horde.png"),
)
LAYOUT = '''function CharacterCreate_PositionRaceButtons()
    -- Esteria compact faction grid: preserve enumeration order and exact RaceIDs.
    local width = CharacterCreateFrame:GetWidth();
    if width <= 0 then return; end
    local columns = 7;
    local spacing = math.min(72, (width * 0.36 - 32) / columns);
    local size = math.max(24, spacing - 8);
    local gridWidth = (columns - 1) * spacing + size;
    local function positionFaction(indices, side)
        local left = side == "Alliance" and 24 or width - 24 - gridWidth;
        for slot,index in ipairs(indices or {}) do
            local button = _G["CharacterCreateRaceButton"..index];
            if button then
                local column = (slot - 1) % columns;
                local row = math.floor((slot - 1) / columns);
                button:ClearAllPoints();
                button:SetSize(size, size);
                button:SetPoint("CENTER", CharacterCreateFrame, "TOPLEFT",
                    left + size / 2 + column * spacing, -100 - row * spacing);
                button:GetNormalTexture():SetSize(size, size);
                button:GetPushedTexture():SetSize(size, size);
                for _,name in ipairs({"staticTexture","highlightTexture","checkedTexture"}) do
                    if button[name] then button[name]:SetSize(size * 112 / 50, size * 112 / 50); end
                end
            end
        end
        local logo = side == "Alliance" and CustomizationLogoAlliance or CustomizationLogoHorde;
        local label = side == "Alliance" and CustomizationTextAlliance or CustomizationTextHorde;
        local hitbox = side == "Alliance" and AllianceLogoFrame or HordeLogoFrame;
        if logo and label then
            local centre = left + gridWidth / 2;
            logo:ClearAllPoints();
            logo:SetSize(56,56);
            logo:SetPoint("CENTER",CharacterCreateFrame,"TOPLEFT",
                centre + (side == "Alliance" and -44 or 44),-46);
            label:ClearAllPoints();
            if side == "Alliance" then label:SetPoint("LEFT",logo,"RIGHT",-4,0);
            else label:SetPoint("RIGHT",logo,"LEFT",4,0); end
            if hitbox then
                hitbox:ClearAllPoints(); hitbox:SetSize(56,56); hitbox:SetPoint("CENTER",logo,"CENTER",0,0);
            end
        end
    end
    positionFaction(CharacterCreate.raceIndicesAlliance,"Alliance");
    positionFaction(CharacterCreate.raceIndicesHorde,"Horde");
    if not CharacterCreateFrame.esteriaRaceLayoutResize then
        CharacterCreateFrame:HookScript("OnSizeChanged",CharacterCreate_PositionRaceButtons);
        CharacterCreateFrame.esteriaRaceLayoutResize = true;
    end
end'''


def patch_lua(text):
    pattern = (r"function CharacterCreate_PositionRaceButtons\(\).*?\nend"
               r"(?=\n\nfunction CharacterCreate_PositionClassButtons)")
    text, count = re.subn(pattern, lambda _: LAYOUT, text, flags=re.S)
    if count != 1:
        raise ValueError("Expected one creator race positioning function")
    for sex in ("Male", "Female"):
        entry = f"UI-CharacterCreate-Maghar{sex}"
        line = (f'    ["MAGHAR_{sex.upper()}"] = "Interface\\\\Glues\\\\CharacterCreate\\\\{entry}",')
        pattern = rf'^\s*\["MAGHAR_{sex.upper()}"\]\s*=\s*"[^\n]+",'
        text, count = re.subn(pattern, lambda _: line, text, flags=re.M)
        if not count:
            text = text.replace("RACE_ICON_TEXTURES = {", "RACE_ICON_TEXTURES = {\n" + line, 1)
    if "Esteria native appearance controls" not in text or "freeborn-third-team" not in text:
        raise ValueError("Creator source lost native appearance or Freeborn integration")
    return sync_name_visibility(text.encode()).decode()


def patch_xml(data):
    data = hide_name_fields(data)
    return data.replace(b'text="CHARACTER_CREATE_CUSTOMIZE"', b'text="Customize"')


def portrait_entries(client=pack.CLIENT_DEFAULT):
    storm = pack.Storm(pack.DLL_DEFAULT)
    template = pack._read_archive_entry(storm, client / pack.GLOBAL_ARCHIVE_REL, portraits.ICON_TEMPLATE_ENTRY)
    ring = portraits.ring_layer(portraits.decode_client_blp(
        pack._read_archive_entry(storm, client / pack.GLOBAL_ARCHIVE_REL, portraits.RING_ENTRY)))
    races = pack.RawWdbc(pack._read_archive_entry(storm, client / pack.GLOBAL_ARCHIVE_REL,
                                               pack.DBC_ROOT + "ChrRaces.dbc"))
    rows = {pack._value(row, 0): row for row in races.records}
    entries = {}
    preview = Image.new("RGB", (6 * 128, 160), (28, 28, 30))
    for i, (race, sex, token, relative) in enumerate(SOURCES):
        if pack._string(races.strings, pack._value(rows[race], 44)).decode() != token:
            raise ValueError("Portrait RaceID/ClientFileString mismatch")
        path = PICTURES / relative
        art = portraits.portrait_bytes(path, portraits.circular_mask())
        plain = portraits.encode_portrait(art, template)
        bordered = portraits.compose_race_icon(art, ring)
        icon = portraits.encode_portrait(bordered, template)
        portraits.validate_portrait(plain, path)
        portraits.validate_portrait(icon, path)
        entries[portraits.CREATOR_ICON_ROOT + f"UI-CharacterCreate-{token}{sex}.blp"] = icon
        stem = portraits.CHARACTER_FRAME_ROOT + f"TemporaryPortrait-{sex}-{token}"
        entries[stem] = entries[stem + ".blp"] = plain
        preview.paste(bordered.resize((128, 128)), (i * 128, 0), bordered.resize((128, 128)))
        ImageDraw.Draw(preview).text((i * 128 + 4, 134), f"{token}\n{sex}", fill="white")
    STAGE.mkdir(parents=True, exist_ok=True)
    preview.save(STAGE / "bordered-preview.png")
    return entries


def check_layout():
    # Exercise actual Lua anchors and button sizes across screen widths and full 64-race capacity.
    from lupa import LuaRuntime

    lua = LuaRuntime()
    lua.execute('''
        function widget()
            local w={};
            function w:ClearAllPoints() self.point=nil; end
            function w:SetPoint(...) self.point={...}; end
            function w:SetSize(x,y) self.width=x; self.height=y; end
            function w:HookScript(...) end
            function w:Show() self.visible=true; end
            function w:Hide() self.visible=false; end
            function w:GetNormalTexture() return self; end
            function w:GetPushedTexture() return self; end
            return w;
        end
        CharacterCreateFrame=widget();
        function CharacterCreateFrame:GetWidth() return self.screenWidth; end
        CharacterCreate={raceIndicesAlliance={},raceIndicesHorde={}};
        for i=1,64 do
            _G["CharacterCreateRaceButton"..i]=widget();
            local faction=i<=32 and CharacterCreate.raceIndicesAlliance or CharacterCreate.raceIndicesHorde;
            table.insert(faction,i);
        end
    ''')
    lua.execute(LAYOUT)
    for width in (800, 1024, 1834, 2560):
        lua.globals().CharacterCreateFrame.screenWidth = width
        lua.globals().CharacterCreate_PositionRaceButtons()
        points = []
        for i in range(1, 65):
            widget = lua.globals()[f"CharacterCreateRaceButton{i}"]
            x, y = widget.point[4], widget.point[5]
            assert 0 < x - widget.width / 2 < x + widget.width / 2 < width
            assert -450 < y < -50
            points.append((x, y))
        assert len(set(points)) == 64
        assert max(x for x, y in points[:32]) < min(x for x, y in points[32:])
    names = b'''function toggleNames(show)
    if show then
        CharacterCreateNameEdit:Show();
    else
        CharacterCreateNameEdit:Hide()
    end
end
'''
    paired = sync_name_visibility(names)
    assert sync_name_visibility(paired) == paired
    lua.execute("CharacterCreateNameEdit=widget(); CharacterCreateLastNameEdit=widget();")
    lua.execute(paired.decode())
    for show in (True, False, True):
        lua.globals().toggleNames(show)
        assert lua.globals().CharacterCreateNameEdit.visible == show
        assert lua.globals().CharacterCreateLastNameEdit.visible == show


def build(client):
    storm = pack.Storm(pack.DLL_DEFAULT)
    entries = portrait_entries(client)
    create = pack._read_archive_entry(storm, client / pack.LOCALE_ARCHIVE_REL, portraits.LUA_ENTRY).decode()
    lua = patch_lua(create).encode()
    xml = patch_xml(pack._read_archive_entry(storm, client / pack.LOCALE_ARCHIVE_REL, XML_ENTRY))
    from luaparser import ast

    ast.parse(lua.decode())
    check_layout()
    relatives = (pack.GLOBAL_ARCHIVE_REL, pack.LOCALE_ARCHIVE_REL, pack.ASSET_ARCHIVE_REL)
    record = {"source_hashes": {str(rel): pack.sha256(client / rel) for rel in relatives},
              "sources": {relative: pack.sha256(PICTURES / relative) for _, _, _, relative in SOURCES},
              "entries": sorted(entries), "stage_hashes": {}}
    for rel in relatives:
        target = STAGE / "pack" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(client / rel, target)
        updates = entries if rel == pack.ASSET_ARCHIVE_REL else {**entries, portraits.LUA_ENTRY: lua, XML_ENTRY: xml}
        storm.replace_archive_entries(target, updates)
        handle = storm.open_archive(target)
        try:
            for name, data in updates.items():
                if storm.read(handle, name) != data:
                    raise RuntimeError("Staged entry readback mismatch: " + name)
        finally:
            storm.dll.SFileCloseArchive(handle)
        if pack.sha256(client / rel) != record["source_hashes"][str(rel)]:
            raise RuntimeError("Live archive changed during staging")
        record["stage_hashes"][str(rel)] = pack.sha256(target)
    (STAGE / "build-report.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def refresh_ui(client):
    """Refresh only GlueXML in the verified mirror of the preceding installed portrait stage."""
    from luaparser import ast
    import xml.etree.ElementTree as ET

    record = pack.load_json(STAGE / "last-install.json")
    record["source_hashes"] = dict(record["stage_hashes"])
    storm = pack.Storm(pack.DLL_DEFAULT)
    for relative in (pack.GLOBAL_ARCHIVE_REL, pack.LOCALE_ARCHIVE_REL):
        target = STAGE / "pack" / relative
        expected = record["source_hashes"][str(relative)]
        if pack.sha256(target) != expected or pack.sha256(client / relative) != expected:
            raise ValueError("Creator mirror differs from its installed stage")
        lua = sync_name_visibility(pack._read_archive_entry(storm, target, portraits.LUA_ENTRY))
        xml = patch_xml(pack._read_archive_entry(storm, target, XML_ENTRY))
        ast.parse(lua.decode())
        ET.fromstring(xml)
        assert sync_name_visibility(lua) == lua and patch_xml(xml) == xml
        assert b'text="Customize"' in xml
        storm.replace_archive_entries(target, {portraits.LUA_ENTRY: lua, XML_ENTRY: xml})
        assert pack._read_archive_entry(storm, target, portraits.LUA_ENTRY) == lua
        assert pack._read_archive_entry(storm, target, XML_ENTRY) == xml
        record["stage_hashes"][str(relative)] = pack.sha256(target)
    (STAGE / "build-report.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def install(client):
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW and Eclipse before replacing the archives")
    record = pack.load_json(STAGE / "build-report.json")
    backup = Path("C:/Users/Zach/.codex/backups") / ("creator-portraits-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for relative, digest in record["source_hashes"].items():
        rel = Path(relative)
        source = client / rel
        staged = STAGE / "pack" / rel
        if pack.sha256(source) != digest or pack.sha256(staged) != record["stage_hashes"][relative]:
            raise ValueError("Stale or modified stage: " + relative)
        if digest == record["stage_hashes"][relative]:
            continue
        target = backup / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if pack.sha256(target) != digest:
            raise RuntimeError("Backup hash verification failed: " + relative)
    print("BACKUP VERIFIED " + str(backup), flush=True)
    for relative, digest in record["stage_hashes"].items():
        if digest == record["source_hashes"][relative]:
            continue
        rel = Path(relative)
        target = client / rel
        temporary = target.with_suffix(target.suffix + ".portraits-next")
        shutil.copy2(STAGE / "pack" / rel, temporary)
        if pack.sha256(temporary) != digest:
            raise RuntimeError("Install copy hash verification failed: " + relative)
        os.replace(temporary, target)
        print("INSTALLED " + relative, flush=True)
    record["backup"] = str(backup)
    record["replaced_archives"] = [rel for rel, digest in record["stage_hashes"].items()
                                   if digest != record["source_hashes"][rel]]
    (backup / "install-report.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (STAGE / "last-install.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "refresh-ui", "install"))
    parser.add_argument("--client", type=Path, default=pack.CLIENT_DEFAULT)
    args = parser.parse_args()
    if args.command == "build":
        result = build(args.client)
    elif args.command == "refresh-ui":
        result = refresh_ui(args.client)
    else:
        result = install(args.client)
    print(json.dumps(result, indent=2))
