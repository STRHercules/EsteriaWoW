"""Data-driven native appearance codec and Skyborne expansion preparation."""

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path

import retroported_race_pack as p
import skyborne_visual_pack as v

ROOT = Path(r"G:\RetroPorterWork\skyborne\integration\expanded")
ART = ROOT / "patch-root"
PREFIX = "custom\\skyborne\\expanded"
STAGE = Path(r"C:\Users\Zach\.codex\tmp\native-appearance")
LABELS = ("Skin Color", "Face", "Hair Style", "Hair Color", "Eye Color", "Eyebrow Style", "Feathers",
          "Feather Color", "Facial Hair", "Ears")


def descriptors(profile):
    # Native component layout differs from packet order: color, skin, face, features, hairstyle.
    return ((0x28, 5, 1), (0x2C, 10, 1), (0x34, len(profile["hair_geosets"]), 1),
            (0x24, len(profile["hair_textures"]), 1), (0x28, len(profile["eye_textures"]), 5),
            (0x30, 4, 1), (0x30, 2, 4), (0x30, len(profile["feather_textures"]), 8),
            (0x2C, len(profile["beard_geosets"]), 10),
            (0x34, len(profile["ear_geosets"]), len(profile["hair_geosets"])))


def catalog(report):
    data = bytearray(struct.pack("<3I", 0x50504145, 2, 4))
    for race in (52, 53):
        for gender, sex in ((0, "male"), (1, "female")):
            options = descriptors(report["sexes"][sex]["profile"])
            if any(count * factor > 256 for _, count, factor in options):
                raise ValueError("Native appearance byte capacity exceeded")
            data.extend(struct.pack("<3I", race, gender, len(options)))
            profile = report["sexes"][sex]["profile"]
            for index, option in enumerate(options):
                geometry_offset = 0x148 if index == 8 else 0x160 if index == 9 else 0x184 if index == 2 else 0
                choices = (profile["beard_geosets"] if index == 8 else profile["ear_geosets"] if index == 9
                           else profile["feather_geosets"] if index == 2 else [])
                data.extend(struct.pack("<4I", *option, geometry_offset))
                data.extend(struct.pack("<32I", *choices, *([0] * (32 - len(choices)))))
            data.extend(bytes((16 - len(options)) * 144))
    return data


def geometry_catalog(report):
    data = bytearray(struct.pack("<3I", 0x4D474145, 1, 2))
    for sex in ("male", "female"):
        key = report["sexes"][sex]["model_path"]
        path = ART.joinpath(*p.PureWindowsPath(key).parts)
        skin = path.with_name(path.stem + "00.skin").read_bytes()
        name = key.encode("ascii")
        if len(name) >= 128:
            raise ValueError("Native geometry model name exceeds catalog capacity")
        data.extend(name + bytes(128 - len(name)))
        data.extend(struct.pack("<I", len(skin)))
        data.extend(skin)
    return data


def prepare():
    discovery = p.load_json(v.ROOT / "reports" / "discovery.json")
    report = {"schema_version": 1, "codec": "native-byte-codec-v1", "labels": list(LABELS), "sexes": {}}
    for sex, model, collection, chr_model in (("male", 7478487, 7845093, 218), ("female", 7478494, 7845092, 219)):
        profile = v.profiles(discovery, chr_model, expanded=True)
        model_report = v.runtime_model(sex, model, collection, profile, expanded=True, output_root=ART)
        model_report["appearance"] = v.bake_appearance(sex, profile, ART, PREFIX)
        model_report["profile"] = profile
        report["sexes"][sex] = model_report
        print(sex, "expanded model and appearance prepared", flush=True)
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "preparation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "EsteriaAppearance.bin").write_bytes(catalog(report))
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(geometry_catalog(report))
    return report


def replace_race_rows(data, table_name, rows, pool=None):
    table = p.RawWdbc(data)
    layout = p.WDBC_LAYOUTS[table_name]
    retained = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) not in (52, 53)]
    if table_name not in ("CharacterFacialHairStyles",):
        occupied = {p._value(r, 0) for r in retained}
        collision = occupied & {p._value(r, 0) for r in rows}
        if collision:
            raise ValueError(f"{table_name} IDs occupied: {sorted(collision)[:8]}")
    return table.build([*retained, *rows], pool if pool is not None else table.strings)


def expand_tables(tables, report, section_start):
    sections = p.RawWdbc(tables["CharSections"])
    pool = bytearray(sections.strings)
    donors = {(p._value(r, 8), p._value(r, 12)): r for r in sections.records
              if p._value(r, 4) == 53 and p._value(r, 32) == 0 and p._value(r, 36) == 0}
    rows = []
    next_id = section_start
    for race in (52, 53):
        for gender, sex in ((0, "male"), (1, "female")):
            profile = report["sexes"][sex]["profile"]
            root = f"{PREFIX}\\{sex}"

            def add(kind, variation, color, paths):
                nonlocal next_id
                row = p._clone_strings("CharSections", sections, donors[(gender, kind)], pool)
                for field, value in ((0, next_id), (1, race), (2, gender), (3, kind),
                                     (7, 1 if kind == 1 else 17), (8, variation), (9, color)):
                    row = p._replace(row, field * 4, 4, value)
                for field in (4, 5, 6):
                    row = p._set_string(row, field, pool, paths.get(field, ""))
                rows.append(row)
                next_id += 1

            for eye, eye_texture in enumerate(profile["eye_textures"]):
                for skin in range(5):
                    encoded = skin + eye * 5
                    add(0, 0, encoded, {4: f"{root}\\body{skin:02d}.blp", 5: eye_texture})
                    add(4, 0, encoded, {4: f"{root}\\pelvis{skin:02d}.blp",
                                       5: f"{root}\\torso{skin:02d}.blp" if gender else ""})
                    for beard in range(len(profile["beard_geosets"])):
                        for face in range(10):
                            add(1, face + beard * 10, encoded, {4: f"{root}\\facelower{face:02d}_{skin:02d}.blp",
                                                              5: f"{root}\\faceupper{face:02d}_{skin:02d}.blp"})
            for style in range(len(profile["hair_geosets"]) * len(profile["ear_geosets"])):
                for color, texture in enumerate(profile["hair_textures"]):
                    add(3, style, color, {4: texture})
            for feature in range(64):
                for color in range(len(profile["hair_textures"])):
                    add(2, feature, color, {4: "custom\\skyborne\\runtime\\transparent_lower.blp"})
    section_end = next_id - 1
    tables["CharSections"] = replace_race_rows(tables["CharSections"], "CharSections", rows, bytes(pool))
    hair_table = p.RawWdbc(tables["CharHairGeosets"])
    hair_rows = []
    next_id = 450500
    facial_rows = []
    for race in (52, 53):
        for gender, sex in ((0, "male"), (1, "female")):
            profile = report["sexes"][sex]["profile"]
            hair_count = len(profile["hair_geosets"])
            for ear in range(len(profile["ear_geosets"])):
                for style, geoset in enumerate(profile["hair_geosets"]):
                    hair_rows.append(struct.pack("<6I", next_id, race, gender, style + ear * hair_count,
                                                 geoset, int(geoset == 0)))
                    next_id += 1
            for feature in range(64):
                eyebrow = feature % 4
                feathers = (feature // 4) % 2
                color = feature // 8
                facial_rows.append(struct.pack("<8I", race, gender, feature, 0, 0,
                                                eyebrow + 1, color + 1 if feathers else 0, 2))
    tables["CharHairGeosets"] = replace_race_rows(tables["CharHairGeosets"], "CharHairGeosets", hair_rows)
    tables["CharacterFacialHairStyles"] = replace_race_rows(
        tables["CharacterFacialHairStyles"], "CharacterFacialHairStyles", facial_rows)
    models = p.RawWdbc(tables["CreatureModelData"])
    pool = bytearray(models.strings)
    records = []
    for row in models.records:
        model_id = p._value(row, 0)
        if model_id in (120052, 120053):
            sex = "male" if model_id == 120052 else "female"
            row = p._set_string(row, 2, pool, report["sexes"][sex]["model_path"])
        records.append(row)
    tables["CreatureModelData"] = models.build(records, bytes(pool))
    barber = p.RawWdbc(tables["BarberShopStyle"])
    barber_pool = bytearray(barber.strings)
    barber_rows = []
    next_id = p.load_manifest("skyborne")["appearance"]["native_barber_start"]
    for race in (52, 53):
        for gender, sex in ((0, "male"), (1, "female")):
            profile = report["sexes"][sex]["profile"]
            for kind, count in ((0, len(profile["hair_geosets"]) * len(profile["ear_geosets"])),
                                (2, 64), (3, len(profile["eye_textures"]) * 5)):
                template = next(row for row in barber.records
                                if p._value(row, 148) == race and p._value(row, 152) == gender
                                and p._value(row, 4) == kind)
                for style in range(count):
                    row = p._clone_strings("BarberShopStyle", barber, template, barber_pool)
                    for offset, value in ((0, next_id), (156, style)):
                        row = p._replace(row, offset, 4, value)
                    barber_rows.append(row)
                    next_id += 1
    tables["BarberShopStyle"] = replace_race_rows(
        tables["BarberShopStyle"], "BarberShopStyle", barber_rows, bytes(barber_pool))
    return tables, {"section_start": section_start, "section_end": section_end, "section_rows": len(rows)}


def gui(text):
    if "Esteria native appearance controls" in text:
        text, replaced = re.subn(r"\n-- Esteria native appearance controls:.*?"
                                r"eaFrame:SetScript\(.*?\nend\);\s*\Z", "", text, flags=re.S)
        if replaced != 1:
            raise ValueError("Native appearance GUI differs from the managed block")
    block = '''
-- Esteria native appearance controls: logical options use the permanent executable callback.
local EA_LABELS = {"Skin Color", "Face", "Hair Style", "Hair Color", "Eye Color", "Eyebrow Style",
    "Feathers", "Feather Color", "Facial Hair", "Ears"};
local EA_LEFT = CharacterCustomization_Left;
local EA_RIGHT = CharacterCustomization_Right;
local EA_UPDATE = CharacterCreate_UpdateHairCustomization;
local function EA_ACTIVE()
    return CharacterCreate.selectedRaceID == 52 or CharacterCreate.selectedRaceID == 53;
end
local function EA_REFRESH()
    if not CharacterCustomizationButtonFrame1 then return; end
    local parent = CharacterCustomizationButtonFrame1:GetParent();
    local rotateButtons = {CharacterCreateRotateLeft,CharacterCreateRotateRight,
        CharacterCreateRotateLeft30,CharacterCreateRotateRight30};
    for i,button in ipairs(rotateButtons) do
        button:ClearAllPoints();
        button:SetPoint("TOP", CharacterCreateNameEdit, "BOTTOM", 35+(i-1)*50, -8);
    end
    for i=6,10 do
        if not _G["CharacterCustomizationButtonFrame"..i] then
            local frame = CreateFrame("Frame", "CharacterCustomizationButtonFrame"..i,
                parent, "CharacterCustomizationFrameTemplate");
            frame:SetID(i);
        end
    end
    if EA_ACTIVE() then
        local visibleRow=0;
        for i=1,10 do
            local frame = _G["CharacterCustomizationButtonFrame"..i];
            frame:ClearAllPoints();
            local value,count = CycleCharCustomization("EA_GET",i);
            frame:SetPoint("CENTER", parent, "CENTER", 900, 220-visibleRow*38);
            _G["CharacterCustomizationButtonFrame"..i.."Text"]:SetText(
                EA_LABELS[i]..(count and "  "..(value+1).."/"..count or ""));
            if count and count>1 then
                visibleRow=visibleRow+1;
                if CharacterCustomizationButtonFrame1:IsShown() then frame:Show(); else frame:Hide(); end
            else frame:Hide(); end
        end
    else
        for i=6,10 do _G["CharacterCustomizationButtonFrame"..i]:Hide(); end
        for i=1,5 do
            local frame = _G["CharacterCustomizationButtonFrame"..i];
            frame:ClearAllPoints();
            frame:SetPoint("CENTER", parent, "CENTER", 900, 200-i*50);
        end
    end
end
function CharacterCustomization_Left(id)
    if EA_ACTIVE() then CycleCharCustomization("EA_CYCLE",id,-1); EA_REFRESH();
    else EA_LEFT(id); end
end
function CharacterCustomization_Right(id)
    if EA_ACTIVE() then CycleCharCustomization("EA_CYCLE",id,1); EA_REFRESH();
    else EA_RIGHT(id); end
end
function CharacterCreate_UpdateHairCustomization()
    EA_UPDATE(); EA_REFRESH();
end
local eaFrame = CreateFrame("Frame");
eaFrame:SetScript("OnUpdate",function(self,elapsed)
    self.elapsed=(self.elapsed or 0)+elapsed;
    if self.elapsed>.15 then self.elapsed=0; EA_REFRESH(); end
end);
'''
    return text.rstrip() + "\n" + block


def build(client=p.CLIENT_DEFAULT):
    from wod_model_migration import rebuild_archive_streaming

    stage = STAGE / "pack"
    (stage / "Data" / "enUS").mkdir(parents=True, exist_ok=True)
    report = p.load_json(ROOT / "preparation.json")
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharHairTextures", "CharacterFacialHairStyles", "BarberShopStyle", "CharBaseInfo",
             "CharStartOutfit", "NameGen", "Spell")
    storm = p.Storm(p.DLL_DEFAULT)
    tables = {name: p._read_archive_entry(storm, client / p.GLOBAL_ARCHIVE_REL, p.DBC_ROOT + name + ".dbc")
              for name in names}
    first_section = p.load_manifest("skyborne")["appearance"]["native_section_start"]
    tables, allocation = expand_tables(tables, report, first_section)
    dbcs = {p.DBC_ROOT + name + ".dbc": data for name, data in tables.items()}
    create = p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, p.GLUE_ROOT + "CharacterCreate.lua").decode()
    glue = {p.GLUE_ROOT + "CharacterCreate.lua": gui(create).encode()}
    art = {"\\".join(path.relative_to(ART).parts): path.read_bytes() for path in ART.rglob("*") if path.is_file()}
    for relative in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        print("COMPACT " + str(relative), flush=True)
        rebuild_archive_streaming(storm, client / relative, stage / relative)
        entries = art if relative == p.ASSET_ARCHIVE_REL else {**dbcs, **glue}
        if relative == p.LOCALE_ARCHIVE_REL:
            entries.update(art)
        storm.replace_archive_entries(stage / relative, entries)
    server = stage / "server" / "dbc"
    server.mkdir(parents=True, exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (server / (name + ".dbc")).write_bytes(tables[name])
    relatives = (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)
    result = {"race_ids": [52, 53], "codec": "native-byte-codec-v1", "options": report["labels"],
              "allocations": allocation, "dbc_tables": list(names),
              "source_hashes": {str(r): p.sha256(client / r) for r in relatives},
              "stage_hashes": {str(r): p.sha256(stage / r) for r in relatives},
              "archive_sizes": {str(r): (stage / r).stat().st_size for r in relatives}}
    (STAGE / "expanded-pack-report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def install(client=p.CLIENT_DEFAULT):
    import native_appearance_patch as native

    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW and Eclipse before installing native appearance")
    previous_path = STAGE / "last-install.json"
    previous = p.load_json(previous_path) if previous_path.exists() else {}
    allowed_exe = {native.EXPECTED_SHA256, previous.get("installed_hashes", {}).get("Wow.exe")}
    if p.sha256(client / "Wow.exe") not in allowed_exe:
        raise ValueError("Live Wow.exe differs from the audited original or previous native installation")
    report = p.load_json(STAGE / "expanded-pack-report.json")
    exe_report = p.load_json(STAGE / "exe-patch-report.json")
    relatives = (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)
    files = {relative: STAGE / "pack" / relative for relative in relatives}
    files.update({Path(name): STAGE / name for name in
                  ("EsteriaAppearance.dll", "EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin", "Wow.exe")})
    for relative in relatives:
        if p.sha256(client / relative) != report["source_hashes"][str(relative)]:
            raise ValueError("Stale archive stage: " + str(relative))
        if p.sha256(files[relative]) != report["stage_hashes"][str(relative)]:
            raise ValueError("Staged archive hash differs: " + str(relative))
    if p.sha256(STAGE / "Wow.exe") != exe_report["patched_sha256"]:
        raise ValueError("Staged executable differs from its fingerprint-checked patch report")
    sql_command = ["docker", "exec", "-i", "ac-database", "sh", "-c",
                   'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch --skip-column-names acore_characters']

    def sql(text):
        return subprocess.run(sql_command, input=text, capture_output=True, text=True, check=True).stdout

    query = ("SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,online "
             "FROM characters WHERE race IN (52,53);")
    rows = [list(map(int, row.split("\t"))) for row in sql(query).splitlines()]
    if any(row[8] for row in rows):
        raise RuntimeError("Skyborne characters must be offline during installation")
    versions = []
    if sql("SHOW TABLES LIKE 'esteria_appearance_schema';").strip():
        versions = [list(map(int, row.split("\t"))) for row in
                    sql("SELECT race,version FROM esteria_appearance_schema WHERE race IN (52,53);").splitlines()]
    backup = Path("C:/Users/Zach/.codex/backups") / ("native-appearance-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    before = {}
    print("BACKUP " + str(backup), flush=True)
    for relative in files:
        source = client / relative
        if source.exists():
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            before[str(relative)] = p.sha256(source)
            shutil.copy2(source, target)
            if p.sha256(target) != before[str(relative)]:
                raise RuntimeError("Backup verification failed: " + str(relative))
    server_backup = backup / "server-dbc"
    server_backup.mkdir()
    for table in p.SERVER_DBC_TABLES:
        source = p.SERVER_DBC_ROOT / (table + ".dbc")
        shutil.copy2(source, server_backup / source.name)
        if p.sha256(source) != p.sha256(server_backup / source.name):
            raise RuntimeError("Server DBC backup verification failed: " + table)
    (backup / "character-appearance-before.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    rollback = [f"UPDATE `characters` SET `skin`={skin},`face`={face},`hairStyle`={hair},"
                f"`hairColor`={color},`facialStyle`={feature} WHERE `guid`={guid} AND `race`={race};"
                for guid, race, gender, skin, face, hair, color, feature, online in rows]
    rollback.append("DELETE FROM `esteria_appearance_schema` WHERE `race` IN (52,53);")
    rollback.extend(f"INSERT INTO `esteria_appearance_schema` (`race`,`version`) VALUES ({race},{version});"
                    for race, version in versions)
    (backup / "rollback-character-appearance.sql").write_text(
        "START TRANSACTION;\n" + "\n".join(rollback) + "\nCOMMIT;\n", encoding="utf-8")
    for relative, source in files.items():
        target = client / relative
        temporary = target.with_suffix(target.suffix + ".appearance-next")
        shutil.copy2(source, temporary)
        if p.sha256(source) != p.sha256(temporary):
            raise RuntimeError("Install copy verification failed: " + str(relative))
        os.replace(temporary, target)
        print("INSTALLED " + str(relative), flush=True)
    for table in p.SERVER_DBC_TABLES:
        source = STAGE / "pack" / "server" / "dbc" / (table + ".dbc")
        target = p.SERVER_DBC_ROOT / source.name
        shutil.copy2(source, target)
        if p.sha256(source) != p.sha256(target):
            raise RuntimeError("Server DBC install verification failed: " + table)
    migration = p.ROOT / "data/sql/updates/pending_db_characters/rev_20260930004000000.sql"
    sql(migration.read_text(encoding="utf-8"))
    (backup / "character-appearance-after.tsv").write_text(sql(query), encoding="utf-8")
    baseline = previous.get("baseline_backup", previous.get("backup", str(backup)))
    record = {"backup": str(backup), "baseline_backup": baseline,
              "before_hashes": before, "installed_hashes": {str(r): p.sha256(client / r) for r in files},
              "helper_sha256": p.sha256(client / "EsteriaAppearance.dll"),
              "native_catalog_sha256": p.sha256(client / "EsteriaAppearance.bin"), "controls": list(LABELS)}
    (backup / "install-report.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    previous_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "build", "install"))
    parser.add_argument("--client", type=Path, default=p.CLIENT_DEFAULT)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "build":
        result = build(args.client)
    else:
        result = install(args.client)
    if args.command == "prepare":
        result = {sex: {"options": [option[1] for option in descriptors(row["profile"])],
                       "vertices": row["vertices"], "indices": row["triangle_indices"]}
                  for sex, row in result["sexes"].items()}
    print(json.dumps(result, indent=2))
