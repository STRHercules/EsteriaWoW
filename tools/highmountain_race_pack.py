"""Audit and stage the complete Highmountain source; never install an incomplete port."""

import argparse
import hashlib
import itertools
import json
import math
import shutil
import sys
import urllib.request
from pathlib import Path

from wotlkconv.blp import convert_blp
from wotlkconv.casc import CascStorage, KeyRing, blte
from wotlkconv.casc.cdn import CdnSource, blte_header_md5
from wotlkconv.casc.config import config_path
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.convert import _collect_anims
from wotlkconv.m2.downgrade import downgrade_sequences
from wotlkconv.m2.model import M2Model
from wotlkconv.m2.skel import parse_skel
from wotlkconv.m2.skin import write_skin
from wotlkconv.options import Options
from wotlkconv.report import FileResult
from wotlkconv.resolve import AssetSource

import mechagnome_animations as animations
import race_portrait_pack as portraits
import retroported_race_pack as p
import skyborne_visual_pack as v

PROJECT = Path(r"R:\Users\Zach\Documents\GitHub\wow-race-retroporter")
ROOT = Path(r"G:\RetroPorterWork\highmountain")
SOURCE = ROOT / "output/patch-root"
ART = ROOT / "integration/patch-root"
STAGE = Path(r"C:\Users\Zach\.codex\tmp\highmountain")
PREFIX = "custom\\highmountain\\native"
MODELS = {"male": 1630218, "female": 1630402}
LORE = ("Descendants of Huln Highmountain, these tauren honor the spirits of earth, river, and sky. "
        "United beneath their ancestral antlers, the tribes of Highmountain stand with their kin in the Horde.")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def art_path(key):
    return ART.joinpath(*p.PureWindowsPath(key).parts)


def audit(discovery=None):
    d = discovery or p.load_json(ROOT / "reports/discovery.json")
    if d["race_id"] != 28:
        raise ValueError("Highmountain Retail identity changed")
    choice_by_id = {c["ID"]: c for c in d["choices"]}
    requirements = {}
    for row in d["requirement_choices"]:
        option = choice_by_id[row["ChrCustomizationChoiceID"]]["ChrCustomizationOptionID"]
        requirements.setdefault(row["ChrCustomizationReqID"], {}).setdefault(option, set()).add(
            row["ChrCustomizationChoiceID"])
    result = {"retail_race_id": 28, "target_race_id": 46, "sexes": {}, "source_hashes": {
        "discovery.json": p.sha256(ROOT / "reports/discovery.json"),
        "asset-convert.json": p.sha256(ROOT / "reports/asset-convert.json")}}
    for sex, model in (("male", 55), ("female", 56)):
        options = []
        for option in sorted((o for o in d["options"] if o["ChrModelID"] == model),
                             key=lambda o: (o["OrderIndex"], o["ID"])):
            choices = sorted((c for c in d["choices"] if c["ChrCustomizationOptionID"] == option["ID"]),
                             key=lambda c: (c["OrderIndex"], c["ID"]))
            options.append({"id": option["ID"], "label": option["Name_lang"],
                            "option_requirement": option["Requirement"], "choices": [{**c,
                "elements": [e for e in d["elements"] if e["ChrCustomizationChoiceID"] == c["ID"]]}
                for c in choices if c["ChrCustomizationReqID"] != 10],
                "internal_placeholders": [c["ID"] for c in choices if c["ChrCustomizationReqID"] == 10]})
        horns = [o for o in options if o["label"] in
                 ("Horn Style", "Horn Markings", "Horn Wraps", "Horn Decoration")]
        valid_horns = [combo for combo in itertools.product(*(o["choices"] for o in horns)) if all(
            all(any(other["ID"] in allowed for other in combo) for allowed in
                requirements.get(c["ChrCustomizationReqID"], {}).values()) for c in combo)]
        states = len(valid_horns) * math.prod(len(o["choices"]) for o in options if o not in horns)
        result["sexes"][sex] = {"chr_model_id": model, "options": options,
                                "valid_horn_states": len(valid_horns),
                                "choice_states_after_horn_requirements": states,
                                "choice_state_bits": math.ceil(math.log2(states)),
                                "control_count": sum(len(o["choices"]) > 1 for o in options)}
    result["missing_converted_materials"] = [{**a} for a in d["file_assets"]
        if a["path"].lower().endswith(".blp") and not
        SOURCE.joinpath("custom", "highmountain", *p.PureWindowsPath(a["path"]).parts).is_file()]
    result["bone_sets"] = d["linked"]["ChrCustomizationBoneSet"]
    result["requirements"] = d["requirements"]
    result["requirement_choices"] = d["requirement_choices"]
    result["linked"] = d["linked"]
    result["texture_files"] = d["texture_files"]
    result["file_assets"] = d["file_assets"]
    result["status"] = "requires_extended_appearance_persistence_and_rendering"
    save(ROOT / "integration/customization-audit.json", result)
    return result


def glue(client=p.CLIENT_DEFAULT):
    """Stage presentation only; activation waits for complete appearance support."""
    from luaparser import ast

    storm = p.Storm(p.DLL_DEFAULT)
    for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                 "ECS_Schema.lua", "ECS_Integrate.lua"):
        key = p.GLUE_ROOT + name
        text = p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, key).decode()
        if name == "CharacterCreate.lua":
            text = text.replace('RACE_ICON_TEXTURES = {', 'RACE_ICON_TEXTURES = {\n' + '\n'.join(
                f'    ["HIGHMOUNTAINTAUREN_{sex.upper()}"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
                f'UI-CharacterCreate-HighmountainTauren{sex}",' for sex in ("Male", "Female")), 1)
            text = text.replace('["MAGHAR"] = "ORC",',
                                '["MAGHAR"] = "ORC",\n        ["HIGHMOUNTAINTAUREN"] = "TAUREN",', 1)
        elif name == "CharacterInfo.lua":
            text = text.replace('local EXACT_RACE_DATA = {', 'local EXACT_RACE_DATA = {\n'
                '    [46] = { glueString = "HIGHMOUNTAINTAUREN", name = "Highmountain Tauren", '
                'faction = "Horde", fileString = "HighmountainTauren" },', 1)
            text += ('\nlocal highmountainInfo = {};\n'
                     'for key,value in pairs(RaceInfoByFileString.TAUREN or {}) do highmountainInfo[key]=value; end\n'
                     'highmountainInfo.Name="Highmountain Tauren";\n'
                     f'highmountainInfo.Description={json.dumps(LORE)};\n'
                     'RaceInfoByFileString.HIGHMOUNTAINTAUREN=highmountainInfo;\n')
        elif name == "GlueStrings.lua":
            text += ('\nHIGHMOUNTAINTAUREN = "Highmountain Tauren";\n'
                     'HIGHMOUNTAINTAUREN_MALE = HIGHMOUNTAINTAUREN;\n'
                     'HIGHMOUNTAINTAUREN_FEMALE = HIGHMOUNTAINTAUREN;\n'
                     f'RACE_INFO_HIGHMOUNTAINTAUREN = {json.dumps(LORE)};\n'
                     'RACE_INFO_HIGHMOUNTAINTAUREN_FEMALE = RACE_INFO_HIGHMOUNTAINTAUREN;\n')
        elif name == "GlueParent.lua":
            text = text.replace('["MAGHAR"] = true,',
                                '["MAGHAR"] = true,\n        ["HIGHMOUNTAINTAUREN"] = true,', 1)
        elif name == "ECS_Schema.lua":
            text = text.replace('S.RaceOverride = {', 'S.RaceOverride = {\n'
                '    [46] = { name = "Highmountain Tauren", faction = 2, artKey = "HighmountainTauren" },', 1)
            text = text.replace('S.PortraitArtKeys = {',
                                'S.PortraitArtKeys = {\n    HighmountainTauren = true,', 1)
        else:
            text = text.replace('(race == 45 or race == 47 or race == 52 or race == 53)',
                                '(race == 45 or race == 46 or race == 47 or race == 52 or race == 53)', 1)
        ast.parse(text)
        target = art_path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")


def prepare():
    """Read-only Retail acquisition; additions go to pinned cache and derived staging."""
    from retroporter.config import DEFAULT
    sys.path.insert(0, str(PROJECT / "src"))
    from raceporter.config import load_project_config

    project = load_project_config(PROJECT)
    discovery = p.load_json(ROOT / "reports/discovery.json")
    report = audit(discovery)
    cache = project.retail_races_root / "highmountain_tauren"
    cache.mkdir(parents=True, exist_ok=True)
    storage = CascStorage.open(DEFAULT.retail_root, product=project.retail_source.product,
                               locale=project.retail_source.locale.lower(), keys=KeyRing.load(DEFAULT.keys))
    source_inventory = {}
    try:
        pin = {"version": storage.build.version, "build_key": storage.build.build_key,
               "cdn_key": storage.build.cdn_key, "product": project.retail_source.product,
               "mode": project.retail_source.mode, "metadata_index": str(DEFAULT.retail_root)}
        pinned_path = cache / "build.json"
        if pinned_path.exists() and p.load_json(pinned_path) != pin:
            raise ValueError("Pinned Highmountain source differs; refusing a Retail build switch")
        save(pinned_path, pin)
        # A metadata mirror lets CDN acquisition reuse the existing indices without modifying Retail.
        metadata = STAGE / "cdn-metadata"
        cfg = config_path(metadata / "Data", storage.build.cdn_key)
        if not cfg.is_file():
            key = storage.build.cdn_key
            url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/config/{key[:2]}/{key[2:4]}/{key}"
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = response.read()
            if hashlib.md5(raw).hexdigest() != key:
                raise ValueError("CDN configuration hash mismatch")
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_bytes(raw)
        cdn = CdnSource(metadata, storage.build, project.casc_cache_root / "highmountain")
        cdn._indices = DEFAULT.retail_root / "Data/indices"
        from wotlkconv.casc.config import parse_config
        cdn_config = parse_config(cfg.read_text())
        cdn._group = cdn._open(cdn_config.get("archive-group", [""])[0])
        cdn._loose = cdn._open(cdn_config.get("file-index", [""])[0])

        def fetch_https(url, offset, size):
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"} if offset is not None else {}
            request = urllib.request.Request(url.replace("http://", "https://", 1), headers=headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                if offset is not None and response.status != 206:
                    raise OSError("CDN ignored requested byte range")
                return response.read(size + 1)

        cdn.fetch = fetch_https

        def read(file_id, extension):
            ckey = storage.root.ckey_for(file_id)
            if ckey is None:
                raise ValueError(f"Source FileDataID absent from pinned build: {file_id}")
            path = cache / f"{file_id}{extension}"
            if path.is_file():
                data = path.read_bytes()
            elif project.retail_source.mode == "online":
                ekey = storage.encoding.ekey_for(ckey)
                if ekey is None:
                    raise ValueError(f"Source encoding absent: {file_id}")
                if cdn.locate(ekey) is None:
                    # Some model entries are loose files absent from the installed CDN indices.
                    key = ekey.hex()
                    url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/data/{key[:2]}/{key[2:4]}/{key}"
                    with urllib.request.urlopen(url, timeout=45) as response:
                        encoded = response.read(64 * 1024 * 1024 + 1)
                    if len(encoded) > 64 * 1024 * 1024 or blte_header_md5(encoded) != ekey:
                        raise ValueError(f"CDN loose-file encoding mismatch: {file_id}")
                else:
                    encoded = cdn.read(ekey, f"Highmountain FileDataID {file_id}")
                data = blte.decode(encoded, storage.keys)
            else:
                data = storage.read_file_id(file_id)
            if hashlib.md5(data).digest() != ckey:
                raise ValueError(f"Source content key mismatch: {file_id}")
            if not path.is_file():
                path.write_bytes(data)
            source_inventory[str(file_id)] = {"extension": extension, "content_key": ckey.hex(),
                                               "sha256": p.sha256(path), "bytes": len(data)}
            save(cache / "inventory.json", source_inventory)
            return data

        # Preserve every material and bone override, including assets the initial safe slice omitted.
        for asset in discovery["file_assets"]:
            extension = Path(asset["path"]).suffix.lower()
            if extension not in (".blp", ".bone"):
                continue
            raw = read(asset["file_data_id"], extension)
            if extension == ".blp":
                key = "custom\\highmountain\\" + asset["path"]
                target = art_path(key)
                target.parent.mkdir(parents=True, exist_ok=True)
                converted, result = convert_blp(raw, key, Options())
                if not result.ok:
                    raise ValueError(f"Material conversion failed: {key}")
                target.write_bytes(converted)
        source = AssetSource(roots=[cache])
        report["models"] = {}
        for sex, file_id in MODELS.items():
            raw_model = parse_m2(read(file_id, ".m2"))
            child = parse_skel(read(raw_model.skeleton_file_id, ".skel"))
            if not child.parent_skel_file_id:
                raise ValueError("Highmountain source unexpectedly has no parent skeleton")
            parent = parse_skel(read(child.parent_skel_file_id, ".skel"))
            if parent.parent_skel_file_id:
                raise ValueError("Another inherited skeleton level needs flattening")
            donor = M2Model(name=f"Highmountain {sex} parent", bones=parent.bones,
                attachments=parent.attachments, sequences=parent.sequences, sequence_lookups=parent.sequence_lookups,
                key_bone_lookup=parent.key_bone_lookup, attachment_lookup=parent.attachment_lookup,
                global_loops=parent.global_loops, sequence_schema=parent.sequence_schema,
                anim_file_ids=parent.anim_file_ids, bones_from_skeleton=True, attachments_from_skeleton=True)
            for ref in donor.anim_file_ids:
                if ref.file_id:
                    read(ref.file_id, ".anim")
            result = FileResult(source=str(child.parent_skel_file_id), kind="m2")
            downgrade_sequences(donor, result)
            inherited = _collect_anims(donor, f"highmountaintauren{sex}", source, Options(), result)
            if any(not a.data or not a.result.ok for a in inherited):
                raise ValueError("Inherited animation conversion incomplete")
            path = SOURCE / f"custom/highmountain/character/highmountaintauren/{sex}/highmountaintauren{sex}.m2"
            model = v.read_player_model(path)
            child_files = {f"{path.stem}{s['id']:04d}-{s['variation_index']:02d}.anim" for s in model.sequences
                           if not s["flags"] & (0x20 | 0x40)}
            merged = animations.merge(model, donor)
            skin = v.compact_bone_palettes(model, parse_skin(path.with_name(path.stem + "00.skin").read_bytes()))
            key = f"{PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
            target = art_path(key)
            target.parent.mkdir(parents=True, exist_ok=True)
            for a in inherited:
                (target.parent / a.filename).write_bytes(a.data)
            for a in path.parent.glob(path.stem + "*.anim"):
                if a.name in child_files:
                    shutil.copy2(a, target.parent / a.name)
            target.write_bytes(write_md20(model))
            target.with_name(target.stem + "00.skin").write_bytes(write_skin(skin))
            report["models"][sex] = {**merged, "model_path": key,
                "child_skeleton_id": raw_model.skeleton_file_id, "parent_skeleton_id": child.parent_skel_file_id,
                "texture_types_before_downgrade": [t["type"] for t in raw_model.textures],
                "texture_types_after_downgrade": [t["type"] for t in model.textures],
                "rendering_ready": False}
            print(sex, merged, flush=True)
        cdn.close()
        report["pinned_source"] = pin
    finally:
        storage.close()
    portrait_report = prepare_portraits()
    glue()
    report["portraits"] = portrait_report
    report["status"] = "assets_staged_appearance_extension_required_before_installation"
    save(ROOT / "integration/preparation.json", report)
    return report


def prepare_portraits(client=p.CLIENT_DEFAULT):
    storm = p.Storm(p.DLL_DEFAULT)
    template = p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, portraits.ICON_TEMPLATE_ENTRY)
    ring = portraits.ring_layer(portraits.decode_client_blp(
        p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, portraits.RING_ENTRY)))
    report = {}
    for sex in ("Male", "Female"):
        picture = portraits.DEFAULT_SOURCE / "Horde" / f"Charactercreate-races_highmountain-{sex.lower()}.png"
        portrait = portraits.portrait_bytes(picture, portraits.circular_mask())
        plain = p.encode_portrait(portrait, template)
        bordered = p.encode_portrait(portraits.compose_race_icon(portrait, ring), template)
        for root, stem, data in (("Glues\\CharacterCreate", "UI-CharacterCreate-HighmountainTauren", bordered),
                                ("Glues\\CharacterSelect", "ECS-Portrait-HighmountainTauren", plain),
                                ("CharacterFrame", f"TemporaryPortrait-{sex}-HighmountainTauren", plain)):
            key = f"Interface\\{root}\\{stem}{'' if root == 'CharacterFrame' else sex}.blp"
            target = art_path(key)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            p.validate_portrait(data, target)
            report[key] = p.sha256(target)
        preview = portraits.compose_race_icon(portrait, ring)
        preview.save(STAGE / f"portrait-{sex.lower()}.png")
    return report


def hard_textures():
    """Recover the TXID dependencies omitted by the old discovery's customization-only asset slice."""
    from retroporter.config import DEFAULT
    cache = PROJECT / "sources/retail/races/highmountain_tauren"
    inventory = p.load_json(cache / "inventory.json")
    storage = CascStorage.open(DEFAULT.retail_root, product="wow", keys=KeyRing.load(DEFAULT.keys))
    try:
        pin = p.load_json(cache / "build.json")
        if pin["build_key"] != storage.build.build_key:
            raise ValueError("Highmountain TXID source build differs from pinned source")
        cdn = CdnSource(STAGE / "cdn-metadata", storage.build, STAGE / "cdn-txid")
        cdn._indices = DEFAULT.retail_root / "Data/indices"
        from wotlkconv.casc.config import parse_config
        config = parse_config(config_path(STAGE / "cdn-metadata/Data", storage.build.cdn_key).read_text())
        cdn._group = cdn._open(config.get("archive-group", [""])[0])
        cdn._loose = cdn._open(config.get("file-index", [""])[0])

        def fetch_https(url, offset, size):
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"} if offset is not None else {}
            request = urllib.request.Request(url.replace("http://", "https://", 1), headers=headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                if offset is not None and response.status != 206:
                    raise OSError("TXID CDN ignored its byte range")
                return response.read(size + 1)

        cdn.fetch = fetch_https
        added = []
        for sex, model_id in MODELS.items():
            raw = parse_m2((cache / f"{model_id}.m2").read_bytes())
            model = parse_m2(art_path(f"{PREFIX}\\{sex}\\highmountaintauren{sex}.m2").read_bytes())
            for texture, file_id in zip(model.textures, raw.texture_file_ids, strict=True):
                if texture["type"] != 0 or not texture["filename"] or art_path(texture["filename"]).exists():
                    continue
                if not file_id:
                    raise ValueError("Unresolved hard material has no source TXID")
                ckey = storage.root.ckey_for(file_id)
                ekey = storage.encoding.ekey_for(ckey)
                key = ekey.hex()
                url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/data/{key[:2]}/{key[2:4]}/{key}"
                if cdn.locate(ekey) is not None:
                    encoded = cdn.read(ekey, f"Highmountain model TXID {file_id}")
                else:
                    with urllib.request.urlopen(url, timeout=45) as response:
                        encoded = response.read(32 * 1024 * 1024 + 1)
                if len(encoded) > 32 * 1024 * 1024 or blte_header_md5(encoded) != ekey:
                    raise ValueError("TXID encoding key mismatch")
                data = blte.decode(encoded, storage.keys)
                if hashlib.md5(data).digest() != ckey:
                    raise ValueError("TXID content key mismatch")
                source = cache / f"{file_id}.blp"
                if source.exists() and source.read_bytes() != data:
                    raise ValueError("Existing TXID source cache differs")
                source.write_bytes(data)
                inventory[str(file_id)] = {"extension": ".blp", "content_key": ckey.hex(),
                    "sha256": p.sha256(source), "bytes": len(data), "relationship": f"model {model_id} TXID"}
                save(cache / "inventory.json", inventory)
                converted, result = convert_blp(data, texture["filename"], Options())
                if not result.ok:
                    raise ValueError("TXID texture conversion failed")
                target = art_path(texture["filename"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(converted)
                added.append(texture["filename"])
        save(ROOT / "integration/txid-dependencies.json", {"added": added})
        cdn.close()
        return {"added": added}
    finally:
        storage.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "prepare", "portraits", "glue", "hard-textures"))
    args = parser.parse_args()
    STAGE.mkdir(parents=True, exist_ok=True)
    result = {"audit": audit, "prepare": prepare, "portraits": prepare_portraits, "glue": glue,
              "hard-textures": hard_textures}[args.command]()
    if isinstance(result, dict) and "sexes" in result:
        print(json.dumps({"status": result["status"], "sexes": {s: {
            "control_count": r["control_count"], "choice_state_bits": r["choice_state_bits"]}
            for s, r in result["sexes"].items()}}, indent=2))
    else:
        print(json.dumps(result, indent=2))
