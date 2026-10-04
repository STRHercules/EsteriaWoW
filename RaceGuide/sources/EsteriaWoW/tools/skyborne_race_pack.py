"""Skyborne's curated race data, using the shared retroported-race installer."""

import copy
import hashlib
import json
import shutil
import struct
from pathlib import Path

from PIL import Image
from wotlkconv.blp.image import Image as BlpImage

import retroported_race_pack as p
import skyborne_visual_pack as visuals

RACES = (52, 53)


def append_rows(data, rows):
    table = p.RawWdbc(data)
    if any(len(row) != table.record_size for row in rows):
        raise ValueError("Incorrect added DBC row size")
    return table.build([*table.records, *rows])


def sections(data):
    table = p.RawWdbc(data)
    donor = {(p._value(r, 8), p._value(r, 12)): r for r in table.records
             if p._value(r, 4) == 10 and p._value(r, 32) == 0 and p._value(r, 36) == 0}
    kept = [r for r in table.records if p._value(r, 4) not in RACES]
    existing = {p._value(r, 0) for r in kept}
    pool = bytearray(table.strings)
    rows = []
    for race in RACES:
        row_id = 455000 + (race - 52) * 1000

        def add(gender, kind, style, color, paths):
            nonlocal row_id
            if row_id in existing:
                raise ValueError(f"CharSections ID {row_id} is occupied")
            template = donor.get((gender, kind), donor[(0, kind)])
            row = p._clone_strings("CharSections", table, template, pool)
            for field, value in ((0, row_id), (1, race), (2, gender),
                                 (7, 1 if kind == 1 else 17), (8, style), (9, color)):
                row = p._replace(row, field * 4, 4, value)
            for field in (4, 5, 6):
                row = p._set_string(row, field, pool, paths.get(field, ""))
            rows.append(row)
            row_id += 1

        report = p.load_json(visuals.ROOT / "integration" / "visual-preparation.json")
        for gender, sex in ((0, "male"), (1, "female")):
            root = f"{visuals.PREFIX}\\{sex}"
            for color in range(5):
                add(gender, 0, 0, color, {4: f"{root}\\body{color:02d}.blp"})
                add(gender, 4, 0, color, {4: f"{root}\\pelvis{color:02d}.blp",
                                        5: f"{root}\\torso{color:02d}.blp" if sex == "female" else ""})
            for face in range(4):
                for color in range(5):
                    add(gender, 1, face, color, {4: f"{root}\\facelower{face:02d}_{color:02d}.blp",
                                               5: f"{root}\\faceupper{face:02d}_{color:02d}.blp"})
            for style in range(4):
                for color, hair in enumerate(report["sexes"][sex]["profile"]["hair_textures"]):
                    add(gender, 3, style, color, {4: hair})
            for style in range(4):
                for color in range(8):
                    add(gender, 2, style, color, {4: f"{visuals.PREFIX}\\transparent_lower.blp"})
    return table.build([*kept, *rows], bytes(pool))


def table_data(client, manifest, allocation):
    if manifest["appearance"].get("mode") == "native-byte-codec-v1":
        raise ValueError("Skyborne uses native appearance; build with tools/expanded_appearance_pack.py")
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharHairTextures", "CharacterFacialHairStyles", "BarberShopStyle", "CharBaseInfo",
             "CharStartOutfit", "NameGen", "Spell")
    result = {name: p._full_table(client / "Data", name)[0] for name in names}
    for name in ("CreatureModelData", "CreatureDisplayInfo"):
        result[name] = p._merge_model_table(name, result[name], manifest, allocation)
    result["CharSections"] = sections(result["CharSections"])
    offsets = {"CharStartOutfit": 0, "NameGen": 0, "CharHairTextures": 0}
    for race in RACES:
        one = copy.deepcopy(manifest)
        one["race_ids"] = [race]
        one["source_race_id"] = manifest["source_races"][str(race)]
        one["name"] = manifest["names"][str(race)]
        result["ChrRaces"] = p._merge_chr_races(result["ChrRaces"], one, allocation)
        result["CharBaseInfo"] = p._build_char_base_info(result["CharBaseInfo"], one)
        for name, builder in (("CharStartOutfit", p._build_char_start_outfit), ("NameGen", p._clone_namegen),
                              ("CharHairTextures", lambda data, m, a: p._clone_race_rows(name, data, m, a))):
            local = copy.deepcopy(allocation)
            start, end = local["race_allocations"]["skyborne"][name]
            local["race_allocations"]["skyborne"][name] = [start + offsets[name], end]
            if name == "NameGen":
                one["source_race_id"] = 10
            count = len(p._table_rows_for_race(result[name], name, one["source_race_id"]))
            result[name] = builder(result[name], one, local)
            offsets[name] += count

    races = p.RawWdbc(result["ChrRaces"])
    pool = bytearray(races.strings)
    records = []
    for row in races.records:
        if p._value(row, 0) in RACES:
            row = p._set_string(row, 66, pool, "SKYBORNE_FEATURES")
            row = p._set_string(row, 67, pool, "SKYBORNE_FEATURES")
        records.append(row)
    result["ChrRaces"] = races.build(records, bytes(pool))

    hair_table = p.RawWdbc(result["CharHairGeosets"])
    hair = [r for r in hair_table.records if p._value(r, 4) not in RACES]
    ids = {p._value(r, 0) for r in hair}
    for index, (race, gender, style) in enumerate((r, g, s) for r in RACES for g in range(2) for s in range(4)):
        row_id = 450500 + index
        if row_id in ids:
            raise ValueError("Skyborne hair ID collision")
        hair.append(struct.pack("<6I", row_id, race, gender, style, style + 1, 0))
    result["CharHairGeosets"] = hair_table.build(hair)
    facial = p.RawWdbc(result["CharacterFacialHairStyles"])
    rows = [r for r in facial.records if p._value(r, 0) not in RACES]
    # Beard, horns, eyebrows, feathers, ordinary eye-glow group.
    presets = ((0, 0, 1, 0, 2), (0, 0, 1, 1, 2), (0, 0, 2, 0, 2), (0, 0, 2, 1, 2))
    for race in RACES:
        for gender in range(2):
            for style, values in enumerate(presets):
                values = (0, *values[1:]) if gender else values
                rows.append(struct.pack("<8I", race, gender, style, *values))
    result["CharacterFacialHairStyles"] = facial.build(rows)
    # Native barber types: hair style, facial feature, skin. Hair color is a numeric slider.
    barber = p.RawWdbc(result["BarberShopStyle"])
    retained = [r for r in barber.records if p._value(r, 148) not in RACES]
    taken = {p._value(r, 0) for r in retained}
    pool = bytearray(barber.strings)
    next_id = 450500
    for race in RACES:
        for gender in range(2):
            for kind, count in ((0, 4), (2, 4), (3, 5)):
                templates = [r for r in barber.records
                             if p._value(r, 148) == 10 and p._value(r, 152) == gender
                             and p._value(r, 4) == kind]
                template = templates[0] if templates else next(
                    r for r in barber.records if p._value(r, 4) == kind)
                for style in range(count):
                    if next_id in taken:
                        raise ValueError("Skyborne barber ID collision")
                    row = p._clone_strings("BarberShopStyle", barber, template, pool)
                    for offset, value in ((0, next_id), (148, race), (152, gender), (156, style)):
                        row = p._replace(row, offset, 4, value)
                    retained.append(row)
                    next_id += 1
    result["BarberShopStyle"] = barber.build(retained, bytes(pool))
    return result


def transparent_overlay():
    image = BlpImage(256, 128, bytearray(256 * 128 * 4))
    levels = image.mip_chain(levels=8)
    return p.Blp.from_images(levels, compression=1, alpha_type=8, alpha_size=8,
                             palette=[0] * 256, payloads=[bytes(m.width * m.height * 2) for m in levels]).serialize()


def glue_entries(client):
    storm = p.Storm(p.DLL_DEFAULT)
    archive = client / p.LOCALE_ARCHIVE_REL
    result = {}
    for name in ("CharacterInfo.lua", "CharacterCreate.lua", "GlueStrings.lua", "GlueParent.lua"):
        text = p._read_archive_entry(storm, archive, p.GLUE_ROOT + name).decode("utf-8")
        if name == "CharacterInfo.lua":
            entries = (
                '    [52] = { glueString = "SKYBORNE", name = "High Order Skyborne", faction = "Alliance", '
                'fileString = "Skyborne" },\n'
                '    [53] = { glueString = "SKYBORNEHORDE", name = "Windshaper Skyborne", faction = "Horde", '
                'fileString = "SkyborneHorde" },\n'
            )
            if "[52] = { glueString" not in text:
                text = text.replace("local EXACT_RACE_DATA = {\n", "local EXACT_RACE_DATA = {\n" + entries, 1)
            if "    SKYBORNE = bloodElfInfo," not in text:
                text = text.replace("    BLOODELF = bloodElfInfo,", "    BLOODELF = bloodElfInfo,\n"
                                    "    SKYBORNE = bloodElfInfo,\n    SKYBORNEHORDE = bloodElfInfo,", 1)
            anchor = "    local currentLocale = GetLocale()"
            extra = """    for _, raceData in pairs(EXACT_RACE_DATA) do
        if raceData.name == raceName then
            RACE_NAME_CACHE[raceName] = raceData.faction
            return raceData.faction
        end
    end

"""
            if "if raceData.name == raceName then" not in text:
                text = text.replace(anchor, extra + anchor, 1)
        elif name == "CharacterCreate.lua":
            label = '    CharacterCustomizationButtonFrame5Text:SetText(_G["FACIAL_HAIR_"..GetFacialHairCustomization()]);'
            if "-- Skyborne legacy labels" not in text:
                text = text.replace(label, label + '''
    -- Skyborne legacy labels
    if CharacterCreate.selectedRaceID == 52 or CharacterCreate.selectedRaceID == 53 then
        CharacterCustomizationButtonFrame3Text:SetText("Hair Style");
        CharacterCustomizationButtonFrame4Text:SetText("Hair Color");
        CharacterCustomizationButtonFrame5Text:SetText("Features");
    end''', 1)
            if '["SKYBORNE_MALE"]' not in text:
                text = text.replace("RACE_ICON_TEXTURES = {", "RACE_ICON_TEXTURES = {\n" + "\n".join(
                    f'    ["{token}_{sex.upper()}"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
                    f'UI-CharacterCreate-{file_string}{sex}",'
                    for token, file_string in (("SKYBORNE", "Skyborne"), ("SKYBORNEHORDE", "SkyborneHorde"))
                    for sex in ("Male", "Female")), 1)
                text = text.replace('        ["MAGHAR"] = "ORC",',
                                    '        ["MAGHAR"] = "ORC",\n        ["SKYBORNE"] = "HUMAN",\n'
                                    '        ["SKYBORNEHORDE"] = "ORC",', 1)
        elif name == "GlueStrings.lua":
            if 'FACIAL_HAIR_SKYBORNE_FEATURES = "Features";' not in text:
                text += '\nFACIAL_HAIR_SKYBORNE_FEATURES = "Features";\n'
            if '\nSKYBORNE = "' not in text:
                for token, label in (("SKYBORNE", "High Order Skyborne"), ("SKYBORNEHORDE", "Windshaper Skyborne")):
                    text += f'\n{token} = "{label}";\n{token}_MALE = {token};\n{token}_FEMALE = {token};\n'
                    text += f'RACE_INFO_{token} = "{label}";\nRACE_INFO_{token}_FEMALE = RACE_INFO_{token};\n'
        else:
            text = text.replace('        ["HIGHELF"] = true,',
                                '        ["HIGHELF"] = true,\n        ["SKYBORNE"] = true,', 1)
            text = text.replace('        ["BLOODELF"] = true,',
                                '        ["BLOODELF"] = true,\n        ["SKYBORNEHORDE"] = true,', 1)
        result[p.GLUE_ROOT + name] = text.encode("utf-8")
    return result


def build(client):
    manifest = p.load_manifest("skyborne")
    allocation = p.load_json(p.ALLOCATION_PATH)
    tables = table_data(client, manifest, allocation)
    assets = p._asset_entries(manifest)
    for path in visuals.OUTPUT.rglob("*"):
        if path.is_file():
            assets[str(pack_path(path.relative_to(visuals.OUTPUT)))] = path.read_bytes()
    assets[f"{visuals.PREFIX}\\transparent_lower.blp"] = transparent_overlay()
    storm = p.Storm(p.DLL_DEFAULT)
    old_assets = storm.open_archive(client / p.ASSET_ARCHIVE_REL)
    try:
        # Patch-R also owns Mag'har. Preserve every existing entry when adding this race.
        for name, *_ in storm.list_files(old_assets):
            if (name.casefold() not in ("(listfile)", "(attributes)")
                    and not name.casefold().startswith("custom\\skyborne\\")):
                assets[name] = storm.read(old_assets, name)
    finally:
        storm.dll.SFileCloseArchive(old_assets)
    template = p._effective_file(client / "Data", r"Interface\CharacterFrame\TemporaryPortrait-Male-BloodElf.blp")[0]
    visuals_report = p.load_json(visuals.ROOT / "integration" / "visual-preparation.json")
    for sex in ("male", "female"):
        source = visuals.path_for(visuals_report["sexes"][sex]["profile"]["skins"][0]["faces"][0])
        decoded = p.Blp.parse(source.read_bytes()).decode_level(0)
        image = Image.frombytes("RGBA", (decoded.width, decoded.height), bytes(decoded.data)).resize((64, 64))
        encoded = p.encode_portrait(image, template)
        for file_string in manifest["client_file_strings"].values():
            assets[f"{p.CHARACTER_FRAME_ROOT}TemporaryPortrait-{sex.title()}-{file_string}.blp"] = encoded
            assets[f"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-{file_string}{sex.title()}.blp"] = encoded
    root = p._build_root("skyborne")
    (root / "Data" / "enUS").mkdir(parents=True, exist_ok=True)
    dbcs = {p.DBC_ROOT + name + ".dbc": data for name, data in tables.items()}
    glue = glue_entries(client)
    for relative in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL):
        shutil.copy2(client / relative, root / relative)
        storm.replace_archive_entries(root / relative, {**dbcs, **glue})
    storm.create_archive(root / p.ASSET_ARCHIVE_REL, assets)
    storm.replace_archive_entries(root / p.LOCALE_ARCHIVE_REL, assets)
    server = root / "server" / "dbc"
    server.mkdir(parents=True, exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (server / (name + ".dbc")).write_bytes(tables[name])
    report = {"slug": "skyborne", "race_ids": list(RACES), "dbc_tables": list(tables),
              "client_source_hashes": {str(r): p.sha256(client / r)
                                       for r in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)},
              "staged_hashes": {str(r): p.sha256(root / r)
                                for r in (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)}}
    report_path = root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return p.BuildPaths(root, root / p.GLOBAL_ARCHIVE_REL, root / p.ASSET_ARCHIVE_REL,
                        root / p.LOCALE_ARCHIVE_REL, server, report_path)


def pack_path(relative):
    return p.PureWindowsPath(*relative.parts)


def validate(client, paths):
    if p.load_manifest("skyborne")["appearance"].get("mode") == "native-byte-codec-v1":
        raise ValueError("Curated Skyborne packs cannot replace native appearance; use the native installer")
    storm = p.Storm(p.DLL_DEFAULT)
    report = p.load_json(paths.report)
    for name in report["dbc_tables"]:
        key = p.DBC_ROOT + name + ".dbc"
        a = p._read_archive_entry(storm, paths.global_archive, key)
        b = p._read_archive_entry(storm, paths.locale_archive, key)
        if a != b:
            raise ValueError(f"Skyborne global/locale mismatch: {name}")
        if name in p.SERVER_DBC_TABLES and a != (paths.server_dbc_dir / (name + ".dbc")).read_bytes():
            raise ValueError(f"Skyborne server DBC mismatch: {name}")
    sections_table = p.RawWdbc(p._read_archive_entry(storm, paths.global_archive, p.DBC_ROOT + "CharSections.dbc"))
    handle = storm.open_archive(paths.asset_archive)
    try:
        for race in RACES:
            rows = [r for r in sections_table.records if p._value(r, 4) == race]
            if len(rows) != 188:
                raise ValueError(f"Race {race} has {len(rows)} appearance rows instead of 188")
            for row in rows:
                for field in (4, 5, 6):
                    name = p._string(sections_table.strings, p._value(row, field * 4)).decode()
                    if name:
                        data = storm.read(handle, name)
                        if p._value(row, 12) != 3:
                            blp = p.Blp.parse(data, name)
                            if blp.compression != 1:
                                raise ValueError(f"Non-indexed compositor texture: {name}")
    finally:
        storm.dll.SFileCloseArchive(handle)
    return {"race_ids": list(RACES), "charsections_per_race": 188,
            "staged_hashes": {str(r): p.sha256(paths.root / r)
                              for r in (p.GLOBAL_ARCHIVE_REL, p.ASSET_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL)}}
