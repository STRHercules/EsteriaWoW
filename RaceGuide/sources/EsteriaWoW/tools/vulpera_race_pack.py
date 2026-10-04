"""Rebase Esteria race 20 on a pinned Retail Vulpera source; preserve its gameplay identity."""

import argparse
import hashlib
import json
import shutil
import struct
import os
import subprocess
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import earthen_race_pack as e
import highmountain_appearance as generator

p = e.p
ROOT = Path(r"G:\RetroPorterWork\vulpera")
SOURCE = ROOT / "output/patch-root"
ART = ROOT / "integration/patch-root"
STAGE = Path(r"C:\Users\Zach\.codex\tmp\vulpera")
PREFIX = "custom\\vulpera\\native"
RACE = 20
MODELS = {"male": 1890761, "female": 1890759}
GROUPS = (("Fur Color", "Pattern"), ("Face", "Snout"), ("Ears", "Eyesight"),
          ("Eye Color", "Earrings"), ("Hair Style", "Eye Style"))
path = e.path
save = e.save


def audit(upgrade_codec=False):
    discovery = p.load_json(ROOT / "reports/discovery.json")
    if discovery["race_ids"] != [35] or {m["ID"] for m in discovery["models"]} != {69, 70}:
        raise ValueError("Vulpera source identity changed")
    requirements = {r["ID"]: r for r in discovery["requirements"]}
    profiles, excluded = {}, []
    for sex, model in (("male", 69), ("female", 70)):
        options = []
        for option in sorted((o for o in discovery["options"] if o["ChrModelID"] == model),
                             key=lambda o: (o["OrderIndex"], o["ID"])):
            choices = []
            for choice in sorted((c for c in discovery["choices"]
                                  if c["ChrCustomizationOptionID"] == option["ID"]),
                                 key=lambda c: (c["OrderIndex"], c["ID"])):
                requirement = requirements[choice["ChrCustomizationReqID"]]
                if choice["ChrCustomizationReqID"] == 10:
                    excluded.append({"sex": sex, "option": option["Name_lang"], "choice": choice["ID"],
                                     "requirement": requirement})
                    continue
                class_mask = requirement["ClassMask"] & 0xffffffff if requirement["ReqType"] & 1 else 0xffffffff
                choices.append({**choice, "class_mask": class_mask,
                    "elements": [r for r in discovery["elements"]
                                 if r["ChrCustomizationChoiceID"] == choice["ID"]]})
            if choices:
                options.append({"label": option["Name_lang"], "id": option["ID"], "choices": choices})
        descriptors = [None] * len(options)
        capacities = []
        for field, labels in enumerate(GROUPS):
            factor = 1
            for label in labels:
                index = next(i for i, o in enumerate(options) if o["label"] == label)
                count = len(options[index]["choices"])
                descriptors[index] = [field, count, factor]
                factor *= count
            if factor > 256:
                raise ValueError("Vulpera codec exceeds its five-byte contract")
            capacities.append(factor)
        if any(d is None for d in descriptors) or discovery["requirement_choices"]:
            raise ValueError("New unhandled Vulpera customization dependency")
        eye_index = next(i for i, o in enumerate(options) if o["label"] == "Eye Color")
        style_index = next(i for i, o in enumerate(options) if o["label"] == "Eye Style")
        style_choices = {c["ID"] for c in options[style_index]["choices"]}
        supported = {row["ChrCustomizationChoiceID"] for row in discovery["elements"]
                     if row["RelatedChrCustomizationChoiceID"] in style_choices}
        eye_mask = sum(1 << i for i, c in enumerate(options[eye_index]["choices"]) if c["ID"] in supported)
        profiles[sex] = {"options": options, "descriptors": descriptors, "capacities": capacities,
                         "requirements": [[style_index, value, eye_index, eye_mask] for value in (1, 2)]}
    target = ROOT / "integration/codec.json"
    if target.exists() and p.load_json(target) != profiles:
        if not upgrade_codec:
            raise ValueError("Frozen Vulpera codec changed; explicit migration required")
        checkpoint = p.load_json(STAGE / "repair-checkpoint.json")
        previous = Path(checkpoint["backup"]) / "codec-v1.json"
        live = p.CLIENT_DEFAULT / "EsteriaVulpera.bin"
        if not previous.exists() or p.sha256(live) != checkpoint["client_before"]["EsteriaVulpera.bin"]:
            raise ValueError("The installed codec needs a verified backup before an explicit upgrade")
    save(target, profiles)
    save(ROOT / "integration/customization-audit.json", {"source_race": 35, "target_race": RACE,
         "sexes": profiles, "excluded": excluded, "appearance_bytes": 5, "codec_version": 2})
    return profiles


def encode(profile, choices):
    fields = [0] * 5
    for choice, (field, count, factor) in zip(choices, profile["descriptors"], strict=True):
        if not 0 <= choice < count:
            raise ValueError("Invalid Vulpera choice")
        fields[field] += choice * factor
    return fields


def decode(profile, fields):
    if len(fields) != 5 or any(not 0 <= v < cap for v, cap in zip(fields, profile["capacities"], strict=True)):
        raise ValueError("Invalid Vulpera appearance")
    return [(fields[field] // factor) % count for field, count, factor in profile["descriptors"]]


def generate_header():
    profiles = audit()
    output = STAGE / "header"
    (output / "src/server/shared").mkdir(parents=True, exist_ok=True)
    old_codec, old_h = generator.codec, generator.h
    try:
        generator.codec = lambda: profiles
        generator.h = SimpleNamespace(p=SimpleNamespace(ROOT=output), ROOT=ROOT, save=save)
        generator.generate()
    finally:
        generator.codec, generator.h = old_codec, old_h
    text = (output / "src/server/shared/HighmountainAppearance.h").read_text()
    text = text.replace("Highmountain", "Vulpera").replace("HIGHMOUNTAIN", "VULPERA")
    text = text.replace("tools/highmountain_appearance.py", "tools/vulpera_race_pack.py")
    text = text.replace("std::uint8_t, 6", "std::uint8_t, 5").replace("std::uint16_t, 6", "std::uint16_t, 5")
    text = text.replace("std::uint32_t mask;", "std::uint64_t mask;")
    text = text.replace("1u << choice(requirement.required)", "std::uint64_t{1} << choice(requirement.required)")
    extra = ['    struct ClassRequirement', '    {', '        std::uint16_t option;',
             '        std::uint16_t value;', '        std::uint32_t mask;', '    };', '']
    for sex, profile in profiles.items():
        rows = [(i, j, c["class_mask"]) for i, o in enumerate(profile["options"])
                for j, c in enumerate(o["choices"])]
        extra.append(f'    inline constexpr std::array<ClassRequirement, {len(rows)}> {sex.title()}Classes = {{{{')
        extra.extend('        {' + ', '.join(str(v) + ('u' if n == 2 else '')
                     for n, v in enumerate(row)) + '},' for row in rows)
        extra.extend(['    }};', ''])
    extra.extend('''    constexpr std::array<std::uint8_t, 5> Fields(std::uint8_t skin, std::uint8_t face,
        std::uint8_t hairStyle, std::uint8_t hairColor, std::uint8_t facialStyle)
    {
        return {skin, face, hairStyle, hairColor, facialStyle};
    }

    constexpr bool ChoiceAllowed(unsigned gender, unsigned classId, unsigned option, unsigned value)
    {
        if (gender > 1 || classId < 1 || classId > 32)
            return false;
        auto allowed = [&](auto const& rows)
        {
            for (ClassRequirement const& row : rows)
                if (row.option == option && row.value == value)
                    return (row.mask & (1u << (classId - 1))) != 0;
            return false;
        };
        return gender ? allowed(FemaleClasses) : allowed(MaleClasses);
    }

    constexpr bool ValidateClass(unsigned gender, unsigned classId, std::array<std::uint8_t, 5> const& fields)
    {
        if (!Validate(gender, fields))
            return false;
        auto const& options = gender ? FemaleOptions : MaleOptions;
        for (unsigned i = 0; i < options.size(); ++i)
            if (!ChoiceAllowed(gender, classId, i, (fields[options[i].field] / options[i].factor) % options[i].count))
                return false;
        return true;
    }

    constexpr std::array<std::uint8_t, 5> Normalize(unsigned gender, unsigned classId,
        std::array<std::uint8_t, 5> fields)
    {
        if (gender > 1)
            return {};
        auto const& options = gender ? FemaleOptions : MaleOptions;
        auto const& capacities = gender ? FemaleCapacities : MaleCapacities;
        for (unsigned field = 0; field < fields.size(); ++field)
            if (fields[field] >= capacities[field])
                fields[field] = 0;
        for (unsigned i = 0; i < options.size(); ++i)
        {
            auto const& option = options[i];
            unsigned value = (fields[option.field] / option.factor) % option.count;
            if (ChoiceAllowed(gender, classId, i, value))
                continue;
            for (unsigned replacement = 0; replacement < option.count; ++replacement)
                if (ChoiceAllowed(gender, classId, i, replacement))
                {
                    fields[option.field] = static_cast<std::uint8_t>(fields[option.field]
                        - value * option.factor + replacement * option.factor);
                    break;
                }
        }
        auto const& requirements = gender ? FemaleRequirements : MaleRequirements;
        for (auto const& rule : requirements)
        {
            auto const& option = options[rule.option];
            auto const& required = options[rule.required];
            unsigned value = (fields[option.field] / option.factor) % option.count;
            unsigned prerequisite = (fields[required.field] / required.factor) % required.count;
            if (value == rule.value && !(rule.mask & (std::uint64_t{1} << prerequisite)))
                fields[option.field] = static_cast<std::uint8_t>(fields[option.field] - value * option.factor);
        }
        return fields;
    }
'''.splitlines())
    text = text.replace('\n}\n\n#endif', '\n' + '\n'.join(extra) + '\n}\n\n#endif')
    (p.ROOT / "src/server/shared/VulperaAppearance.h").write_text(text, encoding="utf-8", newline="\n")
    return {"header": "src/server/shared/VulperaAppearance.h", "capacities":
            {s: pr["capacities"] for s, pr in profiles.items()}}


def tables():
    from PIL import Image
    profiles = audit()
    storm = p.Storm(p.DLL_DEFAULT)
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharHairTextures", "CharacterFacialHairStyles", "BarberShopStyle", "CharStartOutfit", "Spell")
    result = {n: p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.GLOBAL_ARCHIVE_REL,
                                    p.DBC_ROOT + n + ".dbc") for n in names}
    models = p.RawWdbc(result["CreatureModelData"])
    pool = bytearray(models.strings)
    rows = []
    for row in models.records:
        identifier = p._value(row, 0)
        if identifier in (112885, 112886):
            sex = "male" if identifier == 112885 else "female"
            row = p._set_string(row, 2, pool, f"{PREFIX}\\{sex}\\vulpera{sex}.m2")
        rows.append(row)
    result["CreatureModelData"] = models.build(rows, bytes(pool))
    def replace(name, rows, strings=None):
        table = p.RawWdbc(result[name])
        layout = p.WDBC_LAYOUTS[name]
        kept = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) != RACE]
        if name != "CharacterFacialHairStyles" and {p._value(r, 0) for r in kept} & {p._value(r, 0) for r in rows}:
            raise ValueError("Vulpera DBC allocation collision: " + name)
        result[name] = table.build(kept + rows, bytes(strings) if strings is not None else table.strings)
    sections, hair, facial = [], [], []
    pool = bytearray(p.RawWdbc(result["CharSections"]).strings)
    for gender, sex in enumerate(("male", "female")):
        blank = f"{PREFIX}\\{sex}\\compositor.blp"
        old_art = e.ART
        try:
            e.ART = ART
            e.emit(blank, Image.new("RGBA", (512, 512), (128, 128, 128, 255)), compositor=True)
        finally:
            e.ART = old_art
        for kind in range(5):
            row = struct.pack("<10I", 1000000 + len(sections), RACE, gender, kind, 0, 0, 0,
                              1 if kind == 1 else 17, 0, 0)
            for field in (4, 5, 6):
                row = p._set_string(row, field, pool, blank if field == 4 and kind in (0, 3) else "")
            sections.append(row)
        hair.append(struct.pack("<6I", 1000000 + gender, RACE, gender, 0, 0, 0))
        facial.append(struct.pack("<8I", RACE, gender, 0, 0, 0, 0, 0, 0))
    replace("CharSections", sections, pool)
    replace("CharHairGeosets", hair)
    replace("CharHairTextures", [])
    replace("CharacterFacialHairStyles", facial)
    barber = p.RawWdbc(result["BarberShopStyle"])
    pool, rows = bytearray(barber.strings), []
    for gender, sex in enumerate(("male", "female")):
        for kind, field in ((0, 2), (2, 4), (3, 0)):
            donor = next(r for r in barber.records if p._value(r, 4) == kind
                         and p._value(r, 148) == 20 and p._value(r, 152) == gender)
            for value in range(profiles[sex]["capacities"][field]):
                row = p._clone_strings("BarberShopStyle", barber, donor, pool)
                for offset, val in ((0, 1000000 + len(rows)), (156, value)):
                    row = p._replace(row, offset, 4, val)
                rows.append(row)
    replace("BarberShopStyle", rows, pool)
    return result


def glue():
    from luaparser import ast
    storm = p.Storm(p.DLL_DEFAULT)
    key = p.GLUE_ROOT + "CharacterCreate.lua"
    text = p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, key).decode()
    # The shared picker already obtains native labels/counts and filters class-restricted choices.
    anchors = ("return CharacterCreate.selectedRaceID == 50 or ",
               "if CharacterCreate.selectedRaceID == 46 or ",
               "((CharacterCreate.selectedRaceID == 46 or ")
    for anchor in anchors:
        replacement = anchor.replace("CharacterCreate.selectedRaceID == ",
            "CharacterCreate.selectedRaceID == 20 or CharacterCreate.selectedRaceID == ", 1)
        if replacement in text:
            continue
        if anchor not in text:
            raise ValueError("Creator integration anchor changed: " + anchor)
        text = text.replace(anchor, replacement, 1)
    labels = ["local VULPERA_CHOICE_NAMES = {"]
    for gender, sex in enumerate(("male", "female"), 1):
        labels.append(f"    [{gender}] = {{")
        for i, option in enumerate(audit()[sex]["options"], 1):
            names = [c["Name_lang"] or ("Death Knight" if c["class_mask"] == 32 else "")
                     for c in option["choices"]]
            labels.append(f"        [{i}] = {{" + ",".join(json.dumps(n) for n in names) + "},")
        labels.append("    },")
    labels.append("};")
    anchor = "local function ChoiceText(id, value, label)"
    if anchor not in text:
        raise ValueError("Customization dropdown anchor changed")
    if "local VULPERA_CHOICE_NAMES" in text:
        text, changed = re.subn(r"local VULPERA_CHOICE_NAMES = \{.*?\n\};\n",
                               lambda _: "\n".join(labels) + "\n", text, count=1, flags=re.S)
        if changed != 1:
            raise ValueError("Vulpera choice names block changed")
    else:
        text = text.replace(anchor, "\n".join(labels) + "\n" + anchor + '''
    if CharacterCreate.selectedRaceID == 20 then
        local names = VULPERA_CHOICE_NAMES[GetSelectedSex()];
        local name = names and names[id] and names[id][value + 1];
        if name and name ~= "" then return name; end
    end''', 1)
    ast.parse(text)
    target = path(ART, key)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    info_key = p.GLUE_ROOT + "CharacterInfo.lua"
    info = p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, info_key).decode()
    metadata = '    [20] = { glueString="VULPERA", name="Vulpera", faction="Horde", fileString="Vulpera" },'
    if metadata not in info:
        if info.count("local EXACT_RACE_DATA = {") != 1:
            raise ValueError("Exact race identity table changed")
        info = info.replace("local EXACT_RACE_DATA = {", "local EXACT_RACE_DATA = {\n" + metadata, 1)
    ast.parse(info)
    info_target = path(ART, info_key)
    info_target.parent.mkdir(parents=True, exist_ok=True)
    info_target.write_text(info, encoding="utf-8", newline="\n")
    return {key: text.encode(), info_key: info.encode()}


def equipment_catalog():
    """Honor the source's unconditional race35 helmet hides for the installed display references."""
    source = p.load_json(ROOT / "integration/helmet-visibility.json")["HelmetGeosetData"]
    hidden = {}
    unresolved = []
    for row in source:
        if row["RaceID"] != 35 and row["RaceBitSelection"] not in (2, 3):
            continue
        group = row["HideGeosetGroup"]
        if row["Field_10_0_0_46047_003"] != -1:
            unresolved.append(row)
            continue
        if 0 < group < 52:
            hidden.setdefault(row["HelmetGeosetVisDataID"], set()).add(group)
    with p.ClientFiles(str(p.CLIENT_DEFAULT / "Data"), "enUS") as client:
        displays = p.RawWdbc(client.find("DBFilesClient\\ItemDisplayInfo.dbc")[0])
    catalog = STAGE / "EsteriaVulpera.bin"
    raw = catalog.read_bytes()
    magic, version, count = struct.unpack_from("<3I", raw)
    rows = [raw[12 + i * 156:12 + (i + 1) * 156] for i in range(count)
            if struct.unpack_from("<I", raw, 16 + i * 156)[0] != 4]
    report = []
    for row in displays.records:
        for gender in (0, 1):
            identifier, visibility = p._value(row, 0), p._value(row, (13 + gender) * 4)
            for group in sorted(hidden.get(visibility, ())):
                rows.append(struct.pack("<7I", gender, 4, identifier, group,
                                        0xffffffff, 0xffffffff, 0xffffffff) + bytes(128))
                report.append([gender, identifier, group, visibility])
    catalog.write_bytes(struct.pack("<3I", magic, version, len(rows)) + b"".join(rows))
    save(ROOT / "integration/helmet-catalog.json", {"hide_records": report,
         "source_condition_32_rows": unresolved,
         "condition_32_policy": "unknown source selector; retain stock hide behavior instead of guessing its meaning"})
    return {"records": len(report),
            "source_unconditional_groups": sorted({g for groups in hidden.values() for g in groups})}


def refresh_equipment():
    report = p.load_json(STAGE / "build-report.json")
    assets = {str(f.relative_to(ART)).replace("/", "\\"): f.read_bytes() for f in ART.rglob("*")
              if f.is_file() and ("equipment" in str(f).lower() or "ObjectComponents" in str(f))}
    storm = p.Storm(p.DLL_DEFAULT)
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL):
        archive = STAGE / "pack" / rel
        if p.sha256(archive) != report["stage_hashes"][str(rel)]:
            raise ValueError("Staged archive changed before helmet merge")
        storm.replace_archive_entries(archive, assets)
        if archive.stat().st_size >= 0x80000000:
            compressed = archive.with_suffix(".compressed")
            p.rebuild_archive_streaming(storm, archive, compressed, compress=True)
            os.replace(compressed, archive)
        report["stage_hashes"][str(rel)] = p.sha256(archive)
    report["assets"] += len(assets)
    report["companion_hashes"]["EsteriaVulpera.bin"] = p.sha256(STAGE / "EsteriaVulpera.bin")
    report["companion_hashes"]["EsteriaAppearance.dll"] = p.sha256(STAGE / "EsteriaAppearance.dll")
    save(STAGE / "build-report.json", report)
    return {"helmet_files": len(assets)}


def validate():
    import test_vulpera_race_pack
    test_vulpera_race_pack.main()
    return {"status": "stage_validated"}


def backup():
    import vulpera_migration as migration
    validate()
    report = p.load_json(STAGE / "build-report.json")
    plan = p.load_json(STAGE / "migration-plan.json")
    if migration.snapshot() != plan["before"]:
        raise ValueError("Saved appearances changed after migration preparation")
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before installing the prepared package")
    root = Path(r"C:\Users\Zach\.codex\backups") / ("vulpera-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    root.mkdir(parents=True, exist_ok=False)
    files = {name: str(STAGE / "pack" / name) for name in report["stage_hashes"]}
    files.update({name: str(STAGE / name) for name in report["companion_hashes"]})
    before, server_before = {}, {}
    for name, source in files.items():
        live = p.CLIENT_DEFAULT / name
        before[name] = p.sha256(live) if live.exists() else None
        if live.exists():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, target)
            if p.sha256(target) != before[name]:
                raise ValueError("Client backup hash mismatch: " + name)
    (root / "server-dbc").mkdir()
    for name in p.SERVER_DBC_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        server_before[name] = p.sha256(live)
        shutil.copy2(live, root / "server-dbc" / live.name)
        if p.sha256(root / "server-dbc" / live.name) != server_before[name]:
            raise ValueError("Server DBC backup mismatch: " + name)
    (root / "rollback-characters.sql").write_text(plan["rollback_sql"], encoding="utf-8", newline="\n")
    save(root / "character-migration.json", plan)
    shutil.copy2(migration.MIGRATION, root / migration.MIGRATION.name)
    old_image = subprocess.check_output(["docker", "inspect", "ac-worldserver", "--format", "{{.Image}}"],
                                        text=True).strip()
    report.update(backup=str(root), files=files, before_hashes=before, server_before_hashes=server_before,
                  migration_sha256=plan["migration_sha256"], character_appearance_sha256=plan["before_sha256"],
                  old_server_image=old_image, rollback_image_tag="acore/ac-wotlk-worldserver:vulpera-before-20261002")
    save(STAGE / "install-plan.json", report)
    save(root / "install-plan.json", report)
    return {"backup": str(root), "files": len(files), "server_dbcs": len(server_before)}


def install():
    import mechagnome_race_pack as db
    import vulpera_migration as migration
    report = p.load_json(STAGE / "install-plan.json")
    plan = p.load_json(STAGE / "migration-plan.json")
    rollback = Path(report["backup"])
    running = subprocess.check_output(["docker", "inspect", "ac-worldserver", "--format", "{{.State.Running}}"],
                                      text=True).strip()
    if running != "false":
        raise ValueError("Stop only ac-worldserver before the coordinated appearance migration")
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("WoW/Eclipse must be closed while replacing the helper and archives")
    if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["preserved_exe_sha256"]:
        raise ValueError("Client executable changed after staging")
    if migration.snapshot() != plan["before"] or p.sha256(migration.MIGRATION) != report["migration_sha256"]:
        raise ValueError("Character migration state changed after backup")
    for name, expected in report["before_hashes"].items():
        live = p.CLIENT_DEFAULT / name
        if (p.sha256(live) if live.exists() else None) != expected:
            raise ValueError("Client changed after backup: " + name)
    for name, expected in report["server_before_hashes"].items():
        if p.sha256(p.SERVER_DBC_ROOT / (name + ".dbc")) != expected:
            raise ValueError("Server DBC changed after backup: " + name)
    for name, source in report["files"].items():
        if p.sha256(Path(source)) != report["stage_hashes"].get(name, report["companion_hashes"].get(name)):
            raise ValueError("Staged file changed after backup: " + name)
    receipt = hashlib.sha1(migration.MIGRATION.read_bytes()).hexdigest().upper()
    try:
        db.sql("START TRANSACTION;\n" + migration.MIGRATION.read_text() +
               f"\nINSERT INTO updates (name,hash,state) VALUES ('{migration.MIGRATION.name}',"
               f"'{receipt}','PENDING');\nCOMMIT;", "acore_characters")
        for name, source in report["files"].items():
            target = p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".vulpera-next")
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != p.sha256(Path(source)):
                raise ValueError("Install copy hash mismatch: " + name)
            os.replace(temporary, target)
        for name in p.SERVER_DBC_TABLES:
            source = STAGE / "server-dbc" / (name + ".dbc")
            target = p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if p.sha256(source) != p.sha256(target):
                raise ValueError("Installed server DBC hash mismatch: " + name)
        expected_rows = {}
        for line in plan["before"].splitlines():
            fields = list(map(int, line.split()))
            expected_rows[fields[0]] = fields
        for row in plan["characters"]:
            expected_rows[row["guid"]][4:] = row["new"]
        after = {int(row.split()[0]): list(map(int, row.split())) for row in migration.snapshot().splitlines()}
        if after != expected_rows:
            raise ValueError("Character appearance readback differs from the scoped migration")
    except Exception:
        for name, prior in report["before_hashes"].items():
            target = p.CLIENT_DEFAULT / name
            if prior is not None:
                shutil.copy2(rollback / name, target)
            else:
                target.unlink(missing_ok=True)
        for name in p.SERVER_DBC_TABLES:
            shutil.copy2(rollback / "server-dbc" / (name + ".dbc"), p.SERVER_DBC_ROOT / (name + ".dbc"))
        db.sql("START TRANSACTION;\n" + plan["rollback_sql"] +
               f"DELETE FROM updates WHERE name='{migration.MIGRATION.name}';\nCOMMIT;", "acore_characters")
        raise
    report.update(installed_hashes={n: p.sha256(p.CLIENT_DEFAULT / n) for n in report["files"]},
                  installed_server_hashes={n: p.sha256(p.SERVER_DBC_ROOT / (n + ".dbc")) for n in p.SERVER_DBC_TABLES},
                  migration_receipt_sha1=receipt, status="installed_awaiting_worldserver_recreation")
    save(STAGE / "last-install.json", report)
    save(rollback / "install-report.json", report)
    return {"status": report["status"], "backup": str(rollback)}


def stage():
    from wotlkconv.m2 import parse_m2
    table_data = tables()
    assets = {str(f.relative_to(ART)).replace("/", "\\"): f.read_bytes() for f in ART.rglob("*") if f.is_file()}
    updates = {**assets, **glue(), **{p.DBC_ROOT + n + ".dbc": b for n, b in table_data.items()}}
    storm = p.Storm(p.DLL_DEFAULT)
    report = {"source_hashes": {}, "stage_hashes": {}, "assets": len(assets), "tables": list(table_data)}
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL):
        destination = STAGE / "pack" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(rel)] = p.sha256(p.CLIENT_DEFAULT / rel)
        shutil.copy2(p.CLIENT_DEFAULT / rel, destination)
        if p.sha256(destination) != report["source_hashes"][str(rel)]:
            raise ValueError("Vulpera merge base copy mismatch")
        storm.replace_archive_entries(destination, updates)
        if destination.stat().st_size >= 0x80000000:
            compressed = destination.with_suffix(".compressed")
            p.rebuild_archive_streaming(storm, destination, compressed, compress=True)
            os.replace(compressed, destination)
            if destination.stat().st_size >= 0x80000000:
                raise ValueError("Vulpera archive exceeds the classic 2GiB limit")
        report["stage_hashes"][str(rel)] = p.sha256(destination)
        print("STAGED", rel, flush=True)
    (STAGE / "server-dbc").mkdir(exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (STAGE / "server-dbc" / (name + ".dbc")).write_bytes(table_data[name])
    baseline = (p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", baseline)
    replacements = {}
    for sex in ("male", "female"):
        key = f"{PREFIX}\\{sex}\\vulpera{sex}.m2"
        skin = path(ART, key[:-3] + "00.skin").read_bytes()
        replacements[key] = key.encode().ljust(128, b"\0") + struct.pack("<I", len(skin)) + skin
        model = parse_m2(path(ART, key).read_bytes())
        for texture in model.textures:
            if not texture["type"] and texture["filename"] and texture["filename"] not in assets:
                raise ValueError("Vulpera hard texture missing: " + texture["filename"])
    geometry, replaced, offset = [], set(), 12
    for _ in range(count):
        if offset + 132 > len(baseline):
            raise ValueError("Truncated installed geometry catalog")
        name = baseline[offset:offset + 128].split(b"\0")[0].decode()
        length = struct.unpack_from("<I", baseline, offset + 128)[0]
        end = offset + 132 + length
        if end > len(baseline):
            raise ValueError("Truncated installed geometry payload")
        if name in replacements:
            if name not in replaced:
                geometry.append(replacements[name])
                replaced.add(name)
        else:
            geometry.append(baseline[offset:end])
        offset = end
    if offset != len(baseline):
        raise ValueError("Unexpected installed geometry catalog tail")
    geometry.extend(value for key, value in replacements.items() if key not in replaced)
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(
        struct.pack("<3I", magic, version, len(geometry)) + b"".join(geometry))
    for name in ("EsteriaAppearance.bin", "EsteriaAppearanceMaterials.bin", "EsteriaHighmountain.bin",
                 "EsteriaEarthen.bin", "EsteriaHaranir.bin", "EsteriaHaranirTextures.bin"):
        shutil.copy2(p.CLIENT_DEFAULT / name, STAGE / name)
    report["companion_hashes"] = {n: p.sha256(STAGE / n) for n in
        ("EsteriaAppearanceGeometry.bin", "EsteriaVulpera.bin", "EsteriaVulperaTextures.bin", "EsteriaAppearance.dll")}
    report["preserved_exe_sha256"] = p.sha256(p.CLIENT_DEFAULT / "Wow.exe")
    report["status"] = "staged"
    save(STAGE / "build-report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "header", "prepare", "stage", "validate", "backup", "install"))
    args = parser.parse_args()
    if args.action == "prepare":
        import vulpera_models
        result = vulpera_models.prepare()
    else:
        result = globals()["generate_header" if args.action == "header" else args.action]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
