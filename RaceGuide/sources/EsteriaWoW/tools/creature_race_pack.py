"""Port the requested Retail NPC race assets without changing installed client/server files."""

import argparse
import copy
from collections import deque
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path, PureWindowsPath
import shutil
import struct
import sys
import os
import subprocess
from datetime import datetime
import urllib.request

from retroporter.config import DEFAULT
from retroporter.discovery import discover_race
from retroporter.races import RaceSpec
from retroporter.wotlk import load_db2
from wotlkconv.casc import CascStorage, KeyRing, blte
from wotlkconv.casc.cdn import CdnSource, blte_header_md5
from wotlkconv.casc.config import BuildInfo, config_path, parse_config
from wotlkconv.chunks import ChunkReader
from wotlkconv.listfile import Listfile
from wotlkconv.blp import convert_blp
from wotlkconv.m2 import convert_m2, parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin
from wotlkconv.options import Options
from wotlkconv.resolve import AssetSource

import retroported_race_pack as p
from PIL import Image

PROJECT = Path(r"R:\Users\Zach\Documents\GitHub\wow-race-retroporter")
WORK = DEFAULT.work_root
STAGE = Path(r"C:\Users\Zach\.codex\tmp\creature-races")
SEED = WORK / "vulpera"
SPECS = {
    "naga": {"retail": 13, "name": "Naga", "file_string": "Naga_", "targets": [54],
             "factions": ["horde"], "genders": [0, 1], "hide_helm": True, "hide_feet": True},
    "tuskarr": {"retail": 17, "name": "Tuskarr", "file_string": "Tuskarr", "targets": [55],
                "factions": ["alliance"], "genders": [0], "hide_helm": True, "hide_feet": False},
    "vrykul": {"retail": 16, "name": "Vrykul", "file_string": "Vrykul", "targets": [56, 57],
               "factions": ["alliance", "horde"], "genders": [0], "hide_helm": True, "hide_feet": False,
               "display_scale": 0.55},
    "thinhuman": {"retail": 33, "name": "Forgotten", "file_string": "ThinHuman", "targets": [58, 59],
                  "factions": ["alliance", "horde"], "genders": [0], "hide_helm": False, "hide_feet": False},
}
CANDIDATES = {"tuskarr": (4039115, 4039116), "vrykul": (126397, 1339502)}
LABELS = ("Skin Color", "Face", "Hair Style", "Hair Color", "Facial Hair")
MIGRATION = p.ROOT / 'data/sql/updates/pending_db_world/rev_20261002230000000.sql'
MODEL_IDS = {'naga': (120057, 120058), 'tuskarr': (120059,), 'vrykul': (120060,), 'thinhuman': (120061,)}
DISPLAY_IDS = {'naga': (60048, 60049), 'tuskarr': (60050,), 'vrykul': (60051,), 'thinhuman': (60052,)}
FORGOTTEN_GLUE = '''
-- Forgotten presentation: keep the donor's shared Human tables intact.
for _, token in ipairs({"THINHUMAN", "THINHUMANHORDE"}) do
    local info = RaceInfoByFileString[token];
    info.Description = (info.Description or ""):gsub("[Hh]umanity", "the Forgotten")
        :gsub("[Hh]umans?", "Forgotten");
    for key, value in pairs(info) do
        if type(value) == "table" and value.name then
            local spell = {};
            for field, part in pairs(value) do spell[field] = part; end
            spell.name = spell.name:gsub("[Hh]umans?", "Forgotten");
            info[key] = spell;
        end
    end
end
'''


def token(slug, faction):
    name = {'naga': 'Naga', 'tuskarr': 'Tuskarr', 'vrykul': 'Vrykul', 'thinhuman': 'ThinHuman'}[slug]
    return name + ('Horde' if faction == 'horde' else '')


def donor_race(slug, faction):
    return 10 if slug == 'naga' else 3 if slug == 'tuskarr' else 1 if faction == 'alliance' else 2


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def immutable(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing to replace pinned source: " + str(path))
    else:
        path.write_bytes(data)


def references(data, skeleton=False):
    if data.startswith(b"MD20"):
        return []
    reader = ChunkReader(data, reverse=False) if skeleton else ChunkReader.auto(
        data, {"MD21", "SFID", "AFID", "BFID", "SKID", "TXID"})
    result = []
    for chunk in reader:
        if chunk.name in ("SFID", "BFID", "SKID", "TXID"):
            result.extend((row[0], chunk.name) for row in struct.iter_unpack("<I", chunk.data))
        elif chunk.name == "AFID":
            result.extend((row[2], "AFID") for row in struct.iter_unpack("<HHI", chunk.data))
        elif chunk.name == "SKPD" and len(chunk.data) >= 12:
            result.append((struct.unpack_from("<I", chunk.data, 8)[0], "SKPD"))
    return [(file_id, role) for file_id, role in result if file_id]


class Source:
    """The existing CDN range reader plus a content-verified, immutable FileDataID cache."""

    def __init__(self):
        sys.path.insert(0, str(PROJECT / "src"))
        from raceporter.config import load_project_config
        self.project = load_project_config(PROJECT)
        self.storage = CascStorage.open(DEFAULT.retail_root, product=self.project.retail_source.product,
            locale=self.project.retail_source.locale.lower(), keys=KeyRing.load(DEFAULT.keys))
        self.pin = asdict(self.storage.build)
        expected = p.load_json(SEED / "reports/source-pin.json")
        for key in ("product", "version", "build_key", "cdn_key"):
            if self.pin[key] != expected[key]:
                self.storage.close()
                raise ValueError("Retail source differs from the pinned previous ports: " + key)
        self.listfile = Listfile.load(DEFAULT.listfile)
        metadata = STAGE / "cdn-metadata"
        config = config_path(metadata / "Data", self.storage.build.cdn_key)
        if not config.exists():
            key = self.storage.build.cdn_key
            url = f"https://us.cdn.blizzard.com/{self.storage.build.cdn_path}/config/{key[:2]}/{key[2:4]}/{key}"
            data = urllib.request.urlopen(url, timeout=45).read()
            if hashlib.md5(data).hexdigest() != key:
                raise ValueError("CDN configuration hash differs")
            immutable(config, data)
        self.cdn = CdnSource(metadata, self.storage.build, self.project.casc_cache_root / "creature-races",
                             self.https)
        self.cdn._indices = DEFAULT.retail_root / "Data/indices"
        values = parse_config(config.read_text())
        self.cdn._group = self.cdn._open(values.get("archive-group", [""])[0])
        self.cdn._loose = self.cdn._open(values.get("file-index", [""])[0])

    @staticmethod
    def https(url, offset, size):
        headers = {"Range": f"bytes={offset}-{offset + size - 1}"} if offset is not None else {}
        request = urllib.request.Request(url.replace("http://", "https://", 1), headers=headers)
        with urllib.request.urlopen(request, timeout=45) as response:
            if offset is not None and response.status != 206:
                raise OSError("CDN ignored the requested byte range")
            return response.read(size + 1)

    def read(self, file_id, destination, database=False):
        ckey = self.storage.root.ckey_for(file_id)
        if not ckey:
            raise ValueError(f"FileDataID {file_id} is absent from the pinned build")
        if destination.exists():
            data = destination.read_bytes()
        elif self.project.retail_source.mode == "local":
            data = self.storage.read_file_id(file_id, zero_encrypted=database)
        else:
            ekey = self.storage.encoding.ekey_for(ckey)
            if not ekey:
                raise ValueError(f"Missing encoding for FileDataID {file_id}")
            if self.cdn.locate(ekey) is not None:
                encoded = self.cdn.read(ekey, f"FileDataID {file_id}")
            else:
                key = ekey.hex()
                url = f"https://us.cdn.blizzard.com/{self.storage.build.cdn_path}/data/{key[:2]}/{key[2:4]}/{key}"
                encoded = urllib.request.urlopen(url, timeout=45).read(64 * 1024 * 1024 + 1)
            if len(encoded) > 64 * 1024 * 1024 or blte_header_md5(encoded) != ekey:
                raise ValueError(f"Encoding hash/size differs: {file_id}")
            data = blte.decode(encoded, self.storage.keys, zero_missing=database)
        if not database and hashlib.md5(data).digest() != ckey:
            raise ValueError(f"Content key differs: {file_id}")
        immutable(destination, data)
        return data

    def close(self):
        self.cdn.close()
        self.storage.close()
        build = BuildInfo.load(DEFAULT.retail_root, self.project.retail_source.product)
        if any(getattr(build, k) != self.pin[k] for k in ("version", "build_key", "cdn_key")):
            raise ValueError("Retail build changed while exporting")


def discover(slugs):
    source = Source()
    try:
        shared = STAGE / "retail-db2/dbfilesclient"
        shared.mkdir(parents=True, exist_ok=True)
        for original in (SEED / "retail-db2/dbfilesclient").glob("*.db2"):
            immutable(shared / original.name, original.read_bytes())
        for name in ("creaturedisplayinfo", "creaturemodeldata"):
            source.read(source.listfile.id_for(f"dbfilesclient/{name}.db2"), shared / f"{name}.db2", True)
        result = {}
        for slug in slugs:
            spec = SPECS[slug]
            root = WORK / slug
            immutable(root / "reports/source-pin.json", (json.dumps(source.pin, indent=2) + "\n").encode())
            for original in shared.glob("*.db2"):
                immutable(root / "retail-db2/dbfilesclient" / original.name, original.read_bytes())
            discovery = discover_race(DEFAULT, RaceSpec(slug, spec["file_string"], spec["name"], (), (),
                retail_race_ids=(spec["retail"],)))
            model_ids = {r["ChrModelID"] for r in discovery["model_links"] if r["Sex"] in spec["genders"]}
            discovery["selected_models"] = [r for r in discovery["models"] if r["ID"] in model_ids]
            save(root / "reports/discovery.json", discovery)
            result[slug] = {"models": discovery["selected_models"],
                           "creature_models": discovery["creature_model_rows"],
                           "options": len(discovery["options"]), "choices": len(discovery["choices"])}
            print("DISCOVERED", slug, json.dumps(result[slug]), flush=True)
        return result
    finally:
        source.close()


def acquire(slugs, candidates=False):
    source = Source()
    try:
        for slug in slugs:
            root = WORK / slug
            discovery = p.load_json(root / "reports/discovery.json")
            if p.load_json(root / "reports/source-pin.json") != source.pin:
                raise ValueError("Pinned discovery differs from the active source: " + slug)
            displays = {r["ID"]: r for r in discovery["display_rows"]}
            models = {r["ID"]: r for r in discovery["creature_model_rows"]}
            cores = {m["Sex"]: models[displays[m["DisplayID"]]["ModelID"]]["FileDataID"]
                     for m in discovery["selected_models"]}
            selected = set(discovery["file_data_ids"]) | set(cores.values())
            if candidates:
                selected.update(CANDIDATES.get(slug, ()))
            pending = deque((fid, "") for fid in sorted(selected))
            seen, edges, inventory = set(), [], {}
            raw = PROJECT / "sources/retail/races" / slug
            immutable(raw / "build.json", (json.dumps(source.pin, indent=2) + "\n").encode())
            while pending:
                file_id, hint = pending.popleft()
                if file_id in seen:
                    continue
                seen.add(file_id)
                name = source.listfile.path_for(file_id)
                extension = PureWindowsPath(name).suffix if name else hint or ".bin"
                if hint and extension == ".bin":
                    extension = hint
                data = source.read(file_id, raw / f"{file_id}{extension}")
                record = {"file_data_id": file_id, "logical_name": name, "path": str(raw / f"{file_id}{extension}"),
                          "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                          "content_key": source.storage.root.ckey_for(file_id).hex()}
                inventory[str(file_id)] = record
                if extension.lower() in (".m2", ".skel"):
                    for dependency, role in references(data, extension.lower() == ".skel"):
                        edges.append({"owner": file_id, "dependency": dependency, "role": role})
                        suffix = {"TXID": ".blp", "SFID": ".skin", "AFID": ".anim", "BFID": ".bone",
                                  "SKID": ".skel", "SKPD": ".skel"}[role]
                        pending.append((dependency, suffix))
                save(raw / "inventory.json", inventory)
                if len(seen) % 25 == 0:
                    print("EXPORTED", slug, len(seen), "pending", len(pending), flush=True)
            layouts = {m["CharComponentTextureLayoutID"] for m in discovery["selected_models"]}
            model_ids = {m["ID"] for m in discovery["selected_models"]}
            layout_report = {}
            for table in ("CharComponentTextureLayouts", "CharComponentTextureSections", "ChrModelMaterial",
                          "ChrModelTextureLayer"):
                layout_report[table] = [{"_row_id": i, **r} for i, r in load_db2(DEFAULT, slug, table)
                    if table == "CharComponentTextureLayouts" and r.get("ID", i) in layouts
                    or r.get("CharComponentTextureLayoutID") in layouts
                    or r.get("CharComponentTextureLayoutsID") in layouts or r.get("ChrModelID") in model_ids]
            save(root / "reports/texture-layouts.json", layout_report)
            save(root / "reports/source-inventory.json", {"pin": source.pin, "core_models": cores,
                "assets": inventory, "dependencies": edges, "status": "source_graph_complete"})
            print("SOURCE COMPLETE", slug, cores, len(inventory), flush=True)
    finally:
        source.close()


def convert(slugs):
    listfile = Listfile.load(DEFAULT.listfile)
    for slug in slugs:
        root = WORK / slug
        inventory = p.load_json(root / "reports/source-inventory.json")
        raw = PROJECT / "sources/retail/races" / slug
        source = AssetSource(listfile=listfile, roots=[raw])
        destination = root / "output/patch-root"
        report = {"source_pin": inventory["pin"], "models": {}, "textures": {}, "files": {}}
        options = Options(path_prefix=f"custom\\{slug}", strict_limits=True)

        def write(key, data):
            target = destination.joinpath(*PureWindowsPath(key).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            report["files"][key] = hashlib.sha256(data).hexdigest()

        for file_id, asset in inventory["assets"].items():
            data = Path(asset["path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != asset["sha256"]:
                raise ValueError("Immutable source changed: " + asset["path"])
            name = asset["logical_name"]
            suffix = Path(asset["path"]).suffix.lower()
            key = f"custom\\{slug}\\{name}" if name else f"custom\\{slug}\\files\\{file_id}{suffix}"
            if suffix == ".blp":
                converted, result = convert_blp(data, name or file_id + ".blp", options)
                if not result.ok or not converted:
                    raise ValueError("Texture conversion failed: " + json.dumps(result.as_dict()))
                write(key, converted)
                report["textures"][file_id] = {"path": key, "result": result.as_dict()}
            elif suffix == ".m2":
                source_name = (name or str(file_id) + ".m2").replace("\\", "/")
                converted, result, companions = convert_m2(data, source_name, options, listfile, source)
                report["models"][file_id] = {"path": key, "result": result.as_dict(),
                    "companions": [a.result.as_dict() for a in companions]}
                if not result.ok or not converted or any(not a.result.ok or not a.data for a in companions):
                    save(root / "reports/asset-convert.json", report)
                    raise ValueError("Model/companion conversion failed: " + str(file_id))
                write(key, converted)
                parent = PureWindowsPath(key).parent
                for companion in companions:
                    write(str(parent / companion.filename), companion.data)
                source_model = parse_m2(data)
                target_model = parse_m2(converted)
                first_skin = next(a for a in companions if a.filename.lower().endswith("00.skin"))
                target_skin = parse_skin(first_skin.data)
                source_skin = parse_skin(source.by_file_id(source_model.skin_file_ids[0], ".skin"))
                geosets = sorted({struct.unpack_from("<H", row)[0] for row in target_skin.submeshes})
                original = {struct.unpack_from("<H", row)[0] for row in source_skin.submeshes}
                if not original.issubset(geosets):
                    raise ValueError("Conversion removed authored geosets: " + str(sorted(original - set(geosets))))
                report["models"][file_id].update(source_vertices=source_model.vertex_count,
                    vertices=target_model.vertex_count, skin_vertices=len(target_skin.vertices),
                    sequences=len(target_model.sequences), events=len(target_model.events), geosets=geosets,
                    attachments=[a["id"] for a in target_model.attachments],
                    texture_types=[t["type"] for t in target_model.textures])
                print("CONVERTED", slug, file_id, target_model.vertex_count, "geosets", geosets, flush=True)
        report["status"] = "assets_converted_awaiting_playable_integration"
        save(root / "reports/asset-convert.json", report)


def profiles(slug):
    discovery = p.load_json(WORK / slug / "reports/discovery.json")
    result = {}
    for model in discovery["models"]:
        if model["Sex"] not in SPECS[slug]["genders"]:
            continue
        by_label = {o["Name_lang"]: o for o in discovery["options"] if o["ChrModelID"] == model["ID"]}
        options = []
        for field, label in enumerate(LABELS):
            source = by_label.get(label)
            choices = sorted((c for c in discovery["choices"] if source
                              and c["ChrCustomizationOptionID"] == source["ID"]),
                             key=lambda c: (c["OrderIndex"], c["ID"]))
            options.append({"label": label, "id": source["ID"] if source else None, "field": field,
                            "count": max(1, len(choices)), "factor": 1, "choices": choices})
        result[str(model["Sex"])] = {"options": options, "capacities": [o["count"] for o in options]}
    return result


def header():
    lines = ['// Generated from the pinned Retail NPC customization graph by tools/creature_race_pack.py.',
             '#ifndef ACORE_CREATURE_APPEARANCE_H', '#define ACORE_CREATURE_APPEARANCE_H', '',
             '#include <array>', '#include <cstdint>', '', 'namespace CreatureAppearance', '{',
             '    struct Option', '    {', '        unsigned field;', '        unsigned count;',
             '        unsigned factor;', '    };', '']
    for slug, spec in SPECS.items():
        for gender, profile in profiles(slug).items():
            name = slug.title() + ('Male' if gender == '0' else 'Female')
            lines.extend([f'    inline constexpr std::array<Option, 5> {name} = {{{{',
                *[f'        {{{i}, {n}, 1}},' for i, n in enumerate(profile['capacities'])], '    }};', ''])
    lines.extend(['    constexpr bool Uses(unsigned race)', '    {', '        return race >= 54 && race <= 59;',
                  '    }', '', '    constexpr bool GenderAllowed(unsigned race, unsigned gender)', '    {',
                  '        return Uses(race) && (gender == 0 || (race == 54 && gender == 1));', '    }', '',
                  '    constexpr std::array<Option, 5> const& Options(unsigned race, unsigned gender)', '    {',
                  '        switch (race)', '        {'])
    for slug, spec in SPECS.items():
        for race in spec['targets']:
            lines.append(f'            case {race}:')
        if len(spec['genders']) == 2:
            lines.append(f'                return gender ? {slug.title()}Female : {slug.title()}Male;')
        else:
            lines.append(f'                return {slug.title()}Male;')
    lines.extend(['            default:', '                return NagaMale;', '        }', '    }', '',
        '    constexpr bool Validate(unsigned race, unsigned gender, std::array<std::uint8_t, 5> const& fields)',
        '    {', '        if (!GenderAllowed(race, gender))', '            return false;',
        '        auto const& options = Options(race, gender);',
        '        for (unsigned i = 0; i < fields.size(); ++i)',
        '            if (fields[i] >= options[i].count)', '                return false;',
        '        return true;', '    }', '}', '', '#endif', ''])
    target = p.ROOT / 'src/server/shared/CreatureAppearance.h'
    target.write_text('\n'.join(lines), encoding='utf-8', newline='\n')


def prepare(slugs):
    import earthen_race_pack as e
    from haranir_race_pack import lznt1
    from vulpera_models import split_atlas
    for slug in slugs:
        root = WORK / slug
        discovery = p.load_json(root / 'reports/discovery.json')
        inventory = p.load_json(root / 'reports/source-inventory.json')
        converted = p.load_json(root / 'reports/asset-convert.json')
        layout = p.load_json(root / 'reports/texture-layouts.json')
        layouts = {m['CharComponentTextureLayoutID'] for m in discovery['models']}
        layout['ChrModelTextureLayer'] = [{'_row_id': i, **r} for i, r in
            load_db2(DEFAULT, slug, 'ChrModelTextureLayer') if r['CharComponentTextureLayoutsID'] in layouts]
        save(root / 'reports/texture-layouts.json', layout)
        profile = profiles(slug)
        save(root / 'integration/codec.json', profile)
        materials = {r['ID']: r for r in discovery['linked']['ChrCustomizationMaterial']}
        textures = {r['MaterialResourcesID']: r['FileDataID'] for r in discovery['texture_files']}
        geosets = {r['ID']: r for r in discovery['linked']['ChrCustomizationGeoset']}
        bank = bytearray(struct.pack('<4I', 0x31544845, 1, 0, 0))
        blobs, records, report = {}, [], {'profiles': profile, 'models': {}, 'layers': []}
        art_root = root / 'integration/patch-root'

        def record(gender, kind, target, value, selectors=(), path=''):
            if len(selectors) > 3 or len(path.encode()) >= 128:
                raise ValueError('Native selection catalog capacity exceeded')
            fields = [i | j << 16 for i, j in selectors]
            records.append(struct.pack('<7I', gender, kind, target, value,
                *(fields + [0xffffffff] * (3 - len(fields)))) + path.encode().ljust(128, b'\0'))

        def image(file_id):
            data = p.Blp.parse(Path(inventory['assets'][str(file_id)]['path']).read_bytes()).decode_level(0)
            return Image.frombytes('RGBA', (data.width, data.height), bytes(data.data))

        def blob(art):
            identity = (art.size, hashlib.sha256(art.tobytes()).hexdigest())
            if identity not in blobs:
                data = lznt1(art.tobytes())
                blobs[identity] = len(bank)
                bank.extend(struct.pack('<3I', art.width, art.height, len(data)) + data)
            return blobs[identity]

        for gender in SPECS[slug]['genders']:
            sex = 'female' if gender else 'male'
            prof = profile[str(gender)]
            chr_model = next(m for m in discovery['models'] if m['Sex'] == gender)
            indices = {c['ID']: (i, j) for i, o in enumerate(prof['options']) for j, c in enumerate(o['choices'])}
            elements = [r for r in discovery['elements'] if r['ChrCustomizationChoiceID'] in indices
                        and (not r['RelatedChrCustomizationChoiceID']
                             or r['RelatedChrCustomizationChoiceID'] in indices)]
            elements.sort(key=lambda r: not r['RelatedChrCustomizationChoiceID'])
            file_id = inventory['core_models'][str(gender)]
            source_key = converted['models'][str(file_id)]['path']
            source_path = root.joinpath('output/patch-root', *PureWindowsPath(source_key).parts)
            model = e.v.read_player_model(source_path)
            skin = parse_skin(source_path.with_name(source_path.stem + '00.skin').read_bytes())
            hair_blends = {model.materials[e.v.u16(batch, 10)]['blending_mode'] for batch in skin.batches
                if model.textures[model.texture_combos[e.v.u16(batch, 16)]]['type'] == 6}
            skin_choice = prof['options'][0]['choices'][0]['ID']
            body_material = next(materials[r['ChrCustomizationMaterialID']] for r in elements
                if r['ChrCustomizationChoiceID'] == skin_choice and r['ChrCustomizationMaterialID']
                and materials[r['ChrCustomizationMaterialID']]['ChrModelTextureTargetID'] == 1)
            body = image(textures[body_material['MaterialResourcesID']])
            split = body.width == 2 * body.height
            atlas = split_atlas(model, skin) if split else {'body_vertices_remapped': 0}
            base_meshes = []
            for index, mesh in enumerate(skin.submeshes):
                batches = [b for b in skin.batches if e.v.u16(b, 4) == index]
                if e.v.u16(mesh, 0) == 0 and any(
                    model.textures[model.texture_combos[e.v.u16(b, 16)]]['type'] in (1, 8) for b in batches):
                    mesh = bytearray(mesh)
                    e.v.patch16(mesh, 0, 10000)
                    skin.submeshes[index] = bytes(mesh)
                    base_meshes.append(index)
            record(gender, 2, 0, 10000)
            for element in elements:
                geo = geosets.get(element['ChrCustomizationGeosetID'])
                if geo:
                    selectors = [indices[element['ChrCustomizationChoiceID']]]
                    record(gender, 0, geo['GeosetType'], geo['GeosetType'] * 100 + geo['GeosetID'], selectors)
            for group, default in ((7, 701), (10, 1001), (13, 1301), (18, 1800), (20, 2001)):
                available = sorted({e.v.u16(mesh, 0) for mesh in skin.submeshes if e.v.u16(mesh, 0) // 100 == group})
                if available and group not in (10, 13):
                    if group == 18 and slug == 'vrykul':
                        default = 1801
                    record(gender, 0, group, default if group == 18 or default in available else available[0])
            layers = sorted((r for r in layout['ChrModelTextureLayer']
                if r['CharComponentTextureLayoutsID'] == chr_model['CharComponentTextureLayoutID']),
                key=lambda r: r['Layer'])
            if not layers:
                raise ValueError('Missing source texture-layer order: ' + slug)
            for source_layer in layers:
                target = source_layer['ChrModelTextureTargetID'][0]
                for element in elements:
                    material = materials.get(element['ChrCustomizationMaterialID'])
                    if not material or material['ChrModelTextureTargetID'] != target:
                        continue
                    selectors = [indices[element['ChrCustomizationChoiceID']]]
                    if element['RelatedChrCustomizationChoiceID']:
                        selectors.append(indices[element['RelatedChrCustomizationChoiceID']])
                    fid = textures[material['MaterialResourcesID']]
                    art = image(fid)
                    outputs = {}
                    if target == 1:
                        if split:
                            art = art.resize((1024, 512), Image.Resampling.LANCZOS)
                            outputs[4] = art.crop((512, 0, 1024, 512))
                            art = art.crop((0, 0, 512, 512))
                        else:
                            art = art.resize((512, 512), Image.Resampling.LANCZOS)
                        outputs.update({0: art, 1: art.crop((0, 320, 256, 512))})
                    elif target == 10:
                        if hair_blends == {0}:
                            # Opaque hair materials use RGB even where Retail stores zero alpha.
                            # Alpha-over composition must not erase the authored braid/bead colors.
                            art.putalpha(255)
                        art.thumbnail((512, 512), Image.Resampling.LANCZOS)
                        outputs[2] = art
                    elif target in (4, 5, 8, 12):
                        if split:
                            outputs[4] = art.resize((512, 512), Image.Resampling.LANCZOS)
                        else:
                            canvas = Image.new('RGBA', (256, 192))
                            height, y = (64, 0) if target in (5, 12) else (128, 64)
                            canvas.alpha_composite(art.resize((256, height), Image.Resampling.LANCZOS), (0, y))
                            outputs[1] = canvas
                    elif target in (13, 14):
                        canvas = Image.new('RGBA', (512, 512))
                        kind = 5 if target == 13 else 3
                        section = next(r for r in layout['CharComponentTextureSections']
                            if r['CharComponentTextureLayoutID'] == chr_model['CharComponentTextureLayoutID']
                            and r['SectionType'] == kind)
                        scale = 1 if chr_model['CharComponentTextureLayoutID'] == 153 else .5
                        box = [int(section[k] * scale) for k in ('X', 'Y', 'Width', 'Height')]
                        canvas.alpha_composite(art.resize(tuple(box[2:]), Image.Resampling.LANCZOS), tuple(box[:2]))
                        outputs.update({0: canvas, 1: canvas.crop((0, 320, 256, 512))})
                    else:
                        raise ValueError(f'Unmapped {slug} source material target: {target}')
                    for group, pixels in outputs.items():
                        if not pixels.getchannel('A').getbbox():
                            continue
                        offset = blob(pixels)
                        record(gender, 3, group, offset, selectors, f'{target}:{source_layer["BlendMode"]}')
                        report['layers'].append({'gender': gender, 'target': target, 'group': group,
                            'file_id': fid, 'selectors': selectors, 'offset': offset})
            e.rebuild_sequence_lookup(model)
            e.share_material_defaults(model)
            e.tracks.embed(model, source_path.parent, source_path.stem)
            from creature_animation_repair import repair_model
            action_repair = repair_model(slug, gender, model)
            if slug == 'naga':
                for i, original in enumerate(skin.batches):
                    batch = bytearray(original)
                    first = model.texture_combos[e.v.u16(batch, 16)]
                    if model.textures[first]['type'] in (1, 8):
                        # The split body/head atlas uses one opaque sample, not Retail's reflective multiply pass.
                        batch[0] &= 0x7f
                        e.v.patch16(batch, 2, 0)
                        e.v.patch16(batch, 14, 1)
                        skin.batches[i] = bytes(batch)
            model.replacable_texture_lookup = [65535] * 16
            for i, texture in enumerate(model.textures):
                if texture['type']:
                    model.replacable_texture_lookup[texture['type']] = i
            if SPECS[slug]['hide_helm'] and len(model.attachment_lookup) > 11:
                model.attachment_lookup[11] = 65535
            equipment_repair = {}
            if slug == 'tuskarr':
                from tuskarr_equipment_repair import repair_geometry
                equipment_repair = repair_geometry(model, skin)
            elif slug == 'thinhuman':
                from thinhuman_equipment_repair import repair_geometry, prepare_helmets
                equipment_repair = repair_geometry(model, skin)
                prepare_helmets(art_root)
            skin = e.v.compact_bone_palettes(model, skin)
            model.num_skin_profiles = 1
            key = f'custom\\{slug}\\native\\{sex}\\{source_path.name}'
            target_path = art_root.joinpath(*PureWindowsPath(key).parts)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(write_md20(model))
            target_path.with_name(target_path.stem + '00.skin').write_bytes(write_skin(skin))
            for texture in model.textures:
                if texture['type'] == 0 and texture['filename']:
                    original = root.joinpath('output/patch-root', *PureWindowsPath(texture['filename']).parts)
                    dest = art_root.joinpath(*PureWindowsPath(texture['filename']).parts)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(original, dest)
            report['models'][str(gender)] = {'path': key, 'vertices': model.vertex_count,
                'skin_vertices': len(skin.vertices), 'sequences': len(model.sequences), 'events': len(model.events),
                'geosets': sorted({e.v.u16(mesh, 0) for mesh in skin.submeshes}), 'atlas': atlas,
                'unconditional_body_meshes': base_meshes, 'hide_helm': SPECS[slug]['hide_helm'],
                'action_repair': action_repair, 'equipment_repair': equipment_repair}
            print('PREPARED', slug, sex, model.vertex_count, len(model.sequences), flush=True)
        struct.pack_into('<I', bank, 8, len(blobs))
        struct.pack_into('<I', bank, 12, int.from_bytes(hashlib.sha256(bank[16:]).digest()[:4], 'little'))
        name = 'ThinHuman' if slug == 'thinhuman' else slug.title()
        STAGE.mkdir(parents=True, exist_ok=True)
        (STAGE / f'Esteria{name}Textures.bin').write_bytes(bank)
        (STAGE / f'Esteria{name}.bin').write_bytes(struct.pack('<3I', 0x314D4845, 1, len(records)) + b''.join(records))
        save(root / 'integration/rendering.json', report)
    header()


def reserve(slugs):
    import mechagnome_race_pack as db
    for table, ids in (('ChrRaces', {r for s in slugs for r in SPECS[s]['targets']}),
                       ('CreatureModelData', {r for s in slugs for r in MODEL_IDS[s]}),
                       ('CreatureDisplayInfo', {r for s in slugs for r in DISPLAY_IDS[s]})):
        p._ensure_id_free(p._full_table(p.CLIENT_DEFAULT / 'Data', table)[0], table, ids)
    if db.sql('SELECT COUNT(*) FROM characters WHERE race BETWEEN 54 AND 59;', 'acore_characters').strip() != '0':
        raise ValueError('New target characters require a reviewed appearance migration')
    for table, field in (('chrraces_dbc', 'ID'), ('playercreateinfo', 'race'), ('player_race_stats', 'Race')):
        if db.sql(f'SELECT COUNT(*) FROM {table} WHERE {field} BETWEEN 54 AND 59;').strip() != '0':
            raise ValueError('New race identity already exists in ' + table)
    allocation = p.load_json(p.ALLOCATION_PATH)
    registry_path = p.ROOT / 'modules/mod-custom-server/data/races/race_registry.json'
    registry = p.load_json(registry_path)
    for index, slug in enumerate(SPECS):
        if slug not in slugs:
            continue
        spec = SPECS[slug]
        allocation['race_ids'][slug] = spec['targets']
        named = {kind: {('female' if g else 'male'): ids[i] for i, g in enumerate(spec['genders'])}
                 for kind, ids in (('CreatureModelData', MODEL_IDS[slug]), ('CreatureDisplayInfo', DISPLAY_IDS[slug]))}
        named.update({n: [1000200 + index * 500, 1000699 + index * 500]
                      for n in ('CharSections', 'CharHairGeosets', 'BarberShopStyle')})
        named.update(CharStartOutfit=[21600 + index * 100, 21699 + index * 100],
                     NameGen=[36000 + index * 6000, 41999 + index * 6000])
        allocation['race_allocations'][slug] = named
        render = p.load_json(WORK / slug / 'integration/rendering.json')
        manifest = {'schema_version': 1, 'slug': slug, 'name': spec['name'], 'race_ids': spec['targets'],
            'client_file_strings': {str(r): token(slug, f) for r, f in zip(spec['targets'], spec['factions'])},
            'source_races': {str(r): donor_race(slug, f) for r, f in zip(spec['targets'], spec['factions'])},
            'classes': registry['classes'], 'source_patch_root': str(WORK / slug / 'output/patch-root'),
            'runtime_patch_root': str(WORK / slug / 'integration/patch-root'), 'asset_prefix': f'custom\\{slug}',
            'models': {('female' if g else 'male'): {'model_id': MODEL_IDS[slug][i],
                'display_id': DISPLAY_IDS[slug][i], 'model_path': render['models'][str(g)]['path']}
                for i, g in enumerate(spec['genders'])},
            'appearance': {'mode': 'native-stock-five-byte-v1', 'source_retail_race_ids': [spec['retail']],
                'supported_genders': spec['genders'], 'profiles': profiles(slug), 'hide_helm': spec['hide_helm'],
                'hide_feet': spec['hide_feet'], 'source_build': '12.1.0.69933'}}
        save(p.CONFIG_ROOT / (slug + '.json'), manifest)
        for race, faction in zip(spec['targets'], spec['factions']):
            entry = {'id': race, 'species_key': slug, 'display_name': spec['name'], 'faction': faction,
                'asset_owner': 'retroporter_' + slug, 'legacy_mask_race': donor_race(slug, faction),
                'visual_base_race': 10 if slug == 'naga' else 3 if slug == 'tuskarr' else 1,
                'start_profile': 'eversong' if slug == 'naga' else 'dun_morogh' if slug == 'tuskarr'
                                 else 'elwynn' if faction == 'alliance' else 'durotar',
                'supported_genders': spec['genders'], 'species_selection': len(spec['targets']) == 2}
            old = next((r for r in registry['playable'] if r['id'] == race), None)
            if old and old != entry:
                raise ValueError('Registry target ID already belongs to another contract')
            if not old:
                registry['playable'].append(entry)
        registry['sources']['retroporter_' + slug] = manifest['runtime_patch_root']
        if len(spec['targets']) == 2:
            pair = {'species_key': slug, 'alliance_id': spec['targets'][0], 'horde_id': spec['targets'][1]}
            if pair not in registry['faction_pairs']:
                registry['faction_pairs'].append(pair)
    for name, last in (('CreatureDisplayInfo', 60052), ('CharSections', 1002199), ('CharHairGeosets', 1002199),
                       ('BarberShopStyle', 1002199), ('CharStartOutfit', 21999), ('NameGen', 59999)):
        allocation['dbc_ranges'][name][1] = max(allocation['dbc_ranges'][name][1], last)
    save(p.ALLOCATION_PATH, allocation)
    save(registry_path, registry)
    print('RESERVED', slugs, flush=True)


def tables():
    names = ('ChrRaces', 'CreatureModelData', 'CreatureDisplayInfo', 'CharSections', 'CharHairGeosets',
             'CharHairTextures', 'CharacterFacialHairStyles', 'BarberShopStyle', 'CharBaseInfo',
             'CharStartOutfit', 'NameGen', 'Spell')
    result = {n: p._full_table(p.CLIENT_DEFAULT / 'Data', n)[0] for n in names}
    allocation = p.load_json(p.ALLOCATION_PATH)
    for index, (slug, spec) in enumerate(SPECS.items()):
        manifest = p.load_manifest(slug)
        render = p.load_json(WORK / slug / 'integration/rendering.json')
        for name in ('CreatureModelData', 'CreatureDisplayInfo'):
            table = p.RawWdbc(result[name])
            rows, pool = list(table.records), bytearray(table.strings)
            for gender in spec['genders']:
                sex = 'female' if gender else 'male'
                template_race = next(r for r in p.RawWdbc(result['ChrRaces']).records if p._value(r, 0) == 1)
                display = next(r for r in p.RawWdbc(result['CreatureDisplayInfo']).records
                               if p._value(r, 0) == p._value(template_race, (4 + gender) * 4))
                donor_id = p._value(display, 4) if name == 'CreatureModelData' else p._value(display, 0)
                donor = next(r for r in table.records if p._value(r, 0) == donor_id)
                target = manifest['models'][sex]['model_id' if name == 'CreatureModelData' else 'display_id']
                p._ensure_id_free(result[name], name, {target})
                row = p._clone_strings(name, table, donor, pool)
                row = p._replace(row, 0, 4, target)
                if name == 'CreatureModelData':
                    row = p._set_string(row, 2, pool, manifest['models'][sex]['model_path'])
                else:
                    row = p._replace(row, 4, 4, manifest['models'][sex]['model_id'])
                    row = p._replace(row, 7 * 4, 4, 0)
                    if 'display_scale' in spec:
                        row = row[:16] + struct.pack('<f', spec['display_scale']) + row[20:]
                rows.append(row)
            result[name] = table.build(rows, bytes(pool))
        for race_index, (race, faction) in enumerate(zip(spec['targets'], spec['factions'])):
            one = copy.deepcopy(manifest)
            one.update(race_ids=[race], source_race_id=donor_race(slug, faction))
            local_allocation = copy.deepcopy(allocation)
            local_allocation['race_allocations'][slug]['CreatureDisplayInfo'].setdefault('female', 0)
            for name, offset in (('CharStartOutfit', race_index * 50), ('NameGen', race_index * 3000)):
                local_allocation['race_allocations'][slug][name][0] += offset
            result['ChrRaces'] = p._merge_chr_races(result['ChrRaces'], one, local_allocation)
            table = p.RawWdbc(result['ChrRaces'])
            pool, rows = bytearray(table.strings), []
            for row in table.records:
                if p._value(row, 0) == race:
                    flags = (p._value(row, 4) & ~1) | 4 | (2 if spec['hide_feet'] else 0)
                    for field, value in ((1, flags), (7, 7 if faction == 'alliance' else 1), (12, 0),
                                         (13, 0 if faction == 'alliance' else 1)):
                        row = p._replace(row, field * 4, 4, value)
                    row = p._set_string(row, 6, pool, 'Th' if slug == 'thinhuman' else slug[:2].title())
                rows.append(row)
            result['ChrRaces'] = table.build(rows, bytes(pool))
            result['CharBaseInfo'] = p._build_char_base_info(result['CharBaseInfo'], one)
            result['CharStartOutfit'] = p._build_char_start_outfit(result['CharStartOutfit'], one, local_allocation)
            result['NameGen'] = p._clone_namegen(result['NameGen'], one, local_allocation)
            for name, gender_offset in (('CharStartOutfit', 6), ('NameGen', 12)):
                table = p.RawWdbc(result[name])
                layout = p.WDBC_LAYOUTS[name]
                result[name] = table.build([r for r in table.records if
                    p._value(r, layout.race_offset, layout.race_width) != race
                    or p._value(r, gender_offset, 1 if name == 'CharStartOutfit' else 4) in spec['genders']])
        discovery = p.load_json(WORK / slug / 'reports/discovery.json')
        geosets = {r['ID']: r for r in discovery['linked']['ChrCustomizationGeoset']}
        section = p.RawWdbc(result['CharSections'])
        pool, sections, hair, facial, barber = bytearray(section.strings), [], [], [], []
        next_id = allocation['race_allocations'][slug]['CharSections'][0]
        dummy = f'custom\\{slug}\\native\\dummy.blp'
        for race in spec['targets']:
            for gender in spec['genders']:
                prof = profiles(slug)[str(gender)]
                capacities = prof['capacities']

                def add(kind, style, color):
                    nonlocal next_id
                    row = struct.pack('<10I', next_id, race, gender, kind, 0, 0, 0,
                                      1 if kind == 1 else 17, style, color)
                    if kind == 0:
                        row = p._set_string(row, 4, pool, dummy)
                    sections.append(row)
                    next_id += 1

                for color in range(capacities[0]):
                    add(0, 0, color)
                    add(1, 0, color)
                    add(4, 0, color)
                for style in range(capacities[2]):
                    for color in range(capacities[3]):
                        add(3, style, color)
                    choice = prof['options'][2]['choices'][style]
                    geo = next(geosets[e['ChrCustomizationGeosetID']] for e in discovery['elements']
                               if e['ChrCustomizationChoiceID'] == choice['ID'] and e['ChrCustomizationGeosetID'])
                    hair.append(struct.pack('<6I', allocation['race_allocations'][slug]['CharHairGeosets'][0]
                        + len(hair), race, gender, style, geo['GeosetID'], 0))
                for style in range(capacities[4]):
                    for color in range(capacities[3]):
                        add(2, style, color)
                    choices = prof['options'][4]['choices']
                    values = [0] * 5
                    if choices:
                        for element in discovery['elements']:
                            geo = geosets.get(element['ChrCustomizationGeosetID'])
                            if element['ChrCustomizationChoiceID'] == choices[style]['ID'] and geo:
                                if not 1 <= geo['GeosetType'] <= 5:
                                    raise ValueError('Nonstandard facial group needs an explicit mapping')
                                values[geo['GeosetType'] - 1] = geo['GeosetID']
                    facial.append(struct.pack('<8I', race, gender, style, *values))
                source_barber = p.RawWdbc(result['BarberShopStyle'])
                for kind, field in ((0, 2), (2, 4), (3, 0)):
                    donor = next(r for r in source_barber.records if p._value(r, 4) == kind)
                    for value in range(capacities[field]):
                        row = donor
                        for offset, v in ((0, allocation['race_allocations'][slug]['BarberShopStyle'][0] + len(barber)),
                                          (148, race), (152, gender), (156, value)):
                            row = p._replace(row, offset, 4, v)
                        barber.append(row)
        for name, rows, strings in (('CharSections', sections, bytes(pool)), ('CharHairGeosets', hair, None),
                                   ('CharacterFacialHairStyles', facial, None), ('BarberShopStyle', barber, None)):
            table = p.RawWdbc(result[name])
            if name != 'CharacterFacialHairStyles':
                p._ensure_id_free(result[name], name, {p._value(r, 0) for r in rows})
            result[name] = table.build(list(table.records) + rows, table.strings if strings is None else strings)
        from wotlkconv.blp.image import Image as BlpImage
        palette = [(255, 255, 255)] * 256
        encoded = p._encode_wotlk_paletted(BlpImage(4, 4, bytearray([255] * 64)), palette, p.PaletteMapper(palette))
        target = WORK.joinpath(slug, 'integration/patch-root', *PureWindowsPath(dummy).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    return result


def sql():
    columns = {
        'playercreateinfo': ('race', 'class', 'map', 'zone', 'position_x', 'position_y', 'position_z', 'orientation'),
        'player_race_stats': ('Race', 'Strength', 'Agility', 'Stamina', 'Intellect', 'Spirit'),
        'playercreateinfo_item': ('race', 'class', 'itemid', 'amount', 'Note'),
        'playercreateinfo_action': ('race', 'class', 'button', 'action', 'type'),
    }
    lines = ['-- Retail NPC race starts; only new targets54-59 are changed.', '']
    for slug, spec in SPECS.items():
        for race, faction in zip(spec['targets'], spec['factions']):
            donor = donor_race(slug, faction)
            lines.extend([f'SET @RACE := {race};', f'SET @DONOR := {donor};', ''])
            for table, fields in columns.items():
                names = ', '.join('`' + n + '`' for n in fields)
                select = ', '.join(['@RACE'] + ['`' + n + '`' for n in fields[1:]])
                lines.extend([f'DELETE FROM `{table}` WHERE `{fields[0]}` = @RACE;',
                    f'INSERT INTO `{table}` ({names})', f'SELECT {select}',
                    f'FROM `{table}` WHERE `{fields[0]}` = @DONOR;', ''])
            lines.extend(['DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;',
                'INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)',
                'SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;', ''])
            spell, skill = (668, 98) if faction == 'alliance' else (669, 109)
            language = 'Common' if faction == 'alliance' else 'Orcish'
            lines.extend(['DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;',
                'INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES',
                f"(@RACE, 0, {spell}, 'Language {language}');", '',
                'DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;',
                'INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES',
                f"(@RACE, 0, {skill}, 0, 'Language {language}');", ''])
    text = '\n'.join(lines)
    if MIGRATION.exists() and MIGRATION.read_text() != text:
        raise ValueError('Migration revision is already occupied')
    MIGRATION.write_text(text, encoding='utf-8', newline='\n')


def glue():
    from luaparser import ast
    result = {}
    for name in ('CharacterCreate.lua', 'CharacterInfo.lua', 'GlueStrings.lua', 'GlueParent.lua',
                 'ECS_Schema.lua', 'ECS_Integrate.lua', 'CharacterSelect.lua'):
        text = p._effective_file(p.CLIENT_DEFAULT / 'Data', p.GLUE_ROOT + name)[0].decode('utf-8')
        if name == 'CharacterCreate.lua':
            text = text.replace('function SetCharacterGender(sex)\n',
                'function SetCharacterGender(sex)\n    if CharacterCreate.selectedRaceID and '
                'CharacterCreate.selectedRaceID >= 55 and CharacterCreate.selectedRaceID <= 59 then '
                'sex = SEX_MALE; end\n', 1)
            text = text.replace('        SetSelectedRace(id);\n        SetCharacterRace(id);',
                '        local target = _G["CharacterCreateRaceButton"..id];\n'
                '        if target and target.raceID and target.raceID >= 55 and target.raceID <= 59 then\n'
                '            SetSelectedSex(SEX_MALE);\n        end\n'
                '        SetSelectedRace(id);\n        SetCharacterRace(id);', 1)
            text += '''
-- Only Naga has an authored second playable body type in this NPC port.
local creatureOriginalSetRace = SetCharacterRace;
function SetCharacterRace(id)
    creatureOriginalSetRace(id);
    local race = CharacterCreate.selectedRaceID;
    local maleOnly = race and race >= 55 and race <= 59;
    if maleOnly then
        CharacterCreateGenderButtonMale:Hide();
        CharacterCreateGenderButtonFemale:Hide();
        if GetSelectedSex() ~= SEX_MALE then SetCharacterGender(SEX_MALE); end
    else
        CharacterCreateGenderButtonMale:Show();
        CharacterCreateGenderButtonFemale:Show();
    end
end
'''
            icon_rows = []
            for slug, spec in SPECS.items():
                for faction in spec['factions']:
                    art = token(slug, faction)
                    for gender in spec['genders']:
                        sex = 'Female' if gender else 'Male'
                        icon_rows.append(f'    ["{token(slug, faction).upper()}_{sex.upper()}"] = '
                            f'"Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-{art}{sex}",')
            text = text.replace('RACE_ICON_TEXTURES = {', 'RACE_ICON_TEXTURES = {\n' + '\n'.join(icon_rows), 1)
        elif name == 'CharacterInfo.lua':
            rows = []
            for slug, spec in SPECS.items():
                for race, faction in zip(spec['targets'], spec['factions']):
                    key = token(slug, faction)
                    rows.append(f'    [{race}] = {{ glueString="{key.upper()}", name="{spec["name"]}", '
                                f'faction="{faction.title()}", fileString="{key}" }},')
                    donor = 'DWARF' if slug == 'tuskarr' else 'HUMAN' if faction == 'alliance' else 'ORC'
                    text += ('\ndo local info = {};\n'
                        f'for key,value in pairs(RaceInfoByFileString.{donor} or {{}}) do info[key]=value; end\n'
                        f'info.Name={json.dumps(spec["name"])};\n'
                        f'RaceInfoByFileString.{key.upper()}=info; end\n')
            text += FORGOTTEN_GLUE
            text = text.replace('local EXACT_RACE_DATA = {', 'local EXACT_RACE_DATA = {\n' + '\n'.join(rows), 1)
        elif name == 'GlueStrings.lua':
            for slug, spec in SPECS.items():
                for faction in spec['factions']:
                    key = token(slug, faction).upper()
                    text += f'\n{key}={json.dumps(spec["name"])}; {key}_MALE={key}; {key}_FEMALE={key};\n'
        elif name == 'GlueParent.lua':
            for faction, anchor in (('alliance', 'local allianceRaces = {'), ('horde', 'local hordeRaces = {')):
                rows = [f'        ["{token(s, faction).upper()}"] = true,' for s, spec in SPECS.items()
                        if faction in spec['factions']]
                text = text.replace(anchor, anchor + '\n' + '\n'.join(rows), 1)
            for slug, spec in SPECS.items():
                for faction in spec['factions']:
                    key, donor = token(slug, faction).upper(), 'HUMAN' if faction == 'alliance' else 'ORC'
                    for table in ('CharModelFogInfo', 'CharModelGlowInfo', 'GlueAmbienceTracks'):
                        text += f'\n{table}["{key}"]={table}["{donor}"];\n'
        elif name == 'ECS_Schema.lua':
            rows = [f'    [{race}] = {{name="{spec["name"]}", faction={1 if f == "alliance" else 2}, '
                f'artKey="{token(slug, f)}"}},'
                for slug, spec in SPECS.items() for race, f in zip(spec['targets'], spec['factions'])]
            text = text.replace('S.RaceOverride = {', 'S.RaceOverride = {\n' + '\n'.join(rows), 1)
        elif name == 'CharacterSelect.lua':
            text = text.replace('elseif ( raceModel == "DARKFALLEN" ) then',
                'elseif ( raceModel == "DARKFALLEN" or raceModel == "TUSKARR" '
                'or raceModel == "VRYKUL" or raceModel == "THINHUMAN" ) then', 1)
        ast.parse(text)
        result[p.GLUE_ROOT + name] = text.encode('utf-8')
    return result


def stage(slugs):
    if set(slugs) != set(SPECS):
        raise ValueError('Stage all four species as one matching package')
    table_data = tables()
    updates = glue()
    assets = {}
    for slug in slugs:
        art = WORK / slug / 'integration/patch-root'
        for path in art.rglob('*'):
            if path.is_file():
                key = str(path.relative_to(art)).replace('/', '\\')
                assets[key] = path.read_bytes()
    updates.update(assets)
    updates.update({p.DBC_ROOT + n + '.dbc': b for n, b in table_data.items()})
    storm = p.Storm(p.DLL_DEFAULT)
    report = {'status': 'staged_awaiting_authorized_builds', 'assets': len(assets), 'source_hashes': {},
              'stage_hashes': {}, 'race_ids': {s: SPECS[s]['targets'] for s in slugs},
              'exe_sha256': p.sha256(p.CLIENT_DEFAULT / 'Wow.exe'),
              'portrait_policy': 'existing Human/Dwarf icons until species portrait artwork is supplied'}
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL):
        target = STAGE / 'pack' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        report['source_hashes'][str(rel)] = p.sha256(p.CLIENT_DEFAULT / rel)
        shutil.copy2(p.CLIENT_DEFAULT / rel, target)
        if p.sha256(target) != report['source_hashes'][str(rel)]:
            raise ValueError('Archive merge base copy differs')
        storm.replace_archive_entries(target, updates)
        if target.stat().st_size >= 0x80000000:
            raise ValueError('Staged archive exceeds the classic 2GiB limit')
        handle = storm.open_archive(target)
        try:
            for key, expected in updates.items():
                if storm.read(handle, key) != expected:
                    raise ValueError('Staged archive entry differs: ' + key)
        finally:
            storm.dll.SFileCloseArchive(handle)
        report['stage_hashes'][str(rel)] = p.sha256(target)
        print('STAGED', rel, flush=True)
    directory = STAGE / 'server-dbc'
    directory.mkdir(exist_ok=True)
    for name, data in table_data.items():
        (directory / (name + '.dbc')).write_bytes(data)
    baseline = (p.CLIENT_DEFAULT / 'EsteriaAppearanceGeometry.bin').read_bytes()
    magic, version, count = struct.unpack_from('<3I', baseline)
    if magic != 0x4D474145 or version != 1:
        raise ValueError('Installed native geometry catalog differs')
    additions = []
    for slug in slugs:
        render = p.load_json(WORK / slug / 'integration/rendering.json')
        for model in render['models'].values():
            key = model['path']
            path = WORK.joinpath(slug, 'integration/patch-root', *PureWindowsPath(key).parts)
            skin = path.with_name(path.stem + '00.skin').read_bytes()
            additions.append(key.encode().ljust(128, b'\0') + struct.pack('<I', len(skin)) + skin)
    (STAGE / 'EsteriaAppearanceGeometry.bin').write_bytes(
        struct.pack('<3I', magic, version, count + len(additions)) + baseline[12:] + b''.join(additions))
    (STAGE / 'glue').mkdir(exist_ok=True)
    for key, data in updates.items():
        if key.startswith(p.GLUE_ROOT):
            (STAGE / 'glue' / PureWindowsPath(key).name).write_bytes(data)
    report['catalog_hashes'] = {f.name: p.sha256(f) for f in STAGE.glob('Esteria*.bin')}
    report['migration'] = str(MIGRATION)
    report['migration_sha256'] = p.sha256(MIGRATION)
    save(STAGE / 'build-report.json', report)
    print(json.dumps(report), flush=True)


WORLD_TABLES = {'playercreateinfo': 'race', 'player_race_stats': 'Race', 'playercreateinfo_item': 'race',
                'playercreateinfo_action': 'race', 'player_totem_model': 'RaceID',
                'custom_race_start_spell': 'race', 'custom_race_start_skill': 'race'}


def preflight():
    import mechagnome_race_pack as db
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if 'wow.exe' in processes or 'eclipse.exe' in processes or 'mpqeditor.exe' in processes:
        raise RuntimeError('Close WoW, Eclipse and MPQEditor before installing the checked package')
    for table, field in WORLD_TABLES.items():
        if db.sql(f'SELECT COUNT(*) FROM {table} WHERE {field} BETWEEN 54 AND 59;').strip() != '0':
            raise ValueError('New target startup data already exists: ' + table)
    if db.sql('SELECT COUNT(*) FROM characters WHERE race BETWEEN 54 AND 59;',
              'acore_characters').strip() != '0':
        raise ValueError('Existing target characters need an explicit appearance migration')
    if db.sql(f"SELECT COUNT(*) FROM updates WHERE name='{MIGRATION.name}';").strip() != '0':
        raise ValueError('This dedicated migration already has a receipt')


def world_fingerprints():
    import mechagnome_race_pack as db
    return {table: hashlib.sha256('\n'.join(sorted(db.sql(
        f'SELECT * FROM {table} WHERE {field} NOT BETWEEN 54 AND 59;').splitlines())).encode()).hexdigest()
        for table, field in WORLD_TABLES.items()}


def backup(slugs):
    from test_creature_race_pack import check
    preflight()
    check()
    report = p.load_json(STAGE / 'build-report.json')
    if report.get('checks', {}).get('native_compile') != 'passed':
        raise ValueError('Native compilation is not verified')
    root = Path(r'C:\Users\Zach\.codex\backups') / ('creature-races-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    root.mkdir(parents=True, exist_ok=False)
    files = {name: str(STAGE / 'pack' / name) for name in report['stage_hashes']}
    names = ['EsteriaAppearance.dll', 'EsteriaAppearanceGeometry.bin']
    names.extend(f'Esteria{("ThinHuman" if s == "thinhuman" else s.title())}{suffix}.bin'
                 for s in SPECS for suffix in ('', 'Textures'))
    files.update({name: str(STAGE / name) for name in names})
    before = {}
    for name in files:
        live = p.CLIENT_DEFAULT / name
        before[name] = p.sha256(live) if live.exists() else None
        if live.exists():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, target)
            if p.sha256(target) != before[name]:
                raise ValueError('Client backup mismatch: ' + name)
    (root / 'server-dbc').mkdir()
    server_before = {}
    for name in p.SERVER_DBC_TABLES:
        live = p.SERVER_DBC_ROOT / (name + '.dbc')
        server_before[name] = p.sha256(live)
        shutil.copy2(live, root / 'server-dbc' / live.name)
        if p.sha256(root / 'server-dbc' / live.name) != server_before[name]:
            raise ValueError('Server DBC backup mismatch: ' + name)
    shutil.copy2(MIGRATION, root / MIGRATION.name)
    rollback_sql = '\n'.join(f'DELETE FROM {table} WHERE {field} BETWEEN 54 AND 59;'
                             for table, field in WORLD_TABLES.items())
    rollback_sql += f"\nDELETE FROM updates WHERE name='{MIGRATION.name}';\n"
    (root / 'rollback-world.sql').write_text(rollback_sql, encoding='utf-8', newline='\n')
    report.update(backup=str(root), files=files, before_hashes=before, server_before_hashes=server_before,
        install_hashes={name: p.sha256(Path(source)) for name, source in files.items()},
        unrelated_world_hashes=world_fingerprints(), status='backed_up_awaiting_coordinated_install')
    save(STAGE / 'install-plan.json', report)
    save(root / 'install-plan.json', report)
    print('VERIFIED BACKUP', root, len(files), 'client files,', len(server_before), 'server DBCs', flush=True)


def install(slugs):
    import mechagnome_race_pack as db
    preflight()
    report = p.load_json(STAGE / 'install-plan.json')
    old = Path(report['backup'])
    running = subprocess.check_output(['docker', 'inspect', 'ac-worldserver', '--format',
                                      '{{.State.Running}}'], text=True).strip()
    if running != 'false':
        raise ValueError('Stop only ac-worldserver before the coordinated install')
    if p.sha256(p.CLIENT_DEFAULT / 'Wow.exe') != report['exe_sha256']:
        raise ValueError('Executable changed since staging')
    for name, expected in report['before_hashes'].items():
        path = p.CLIENT_DEFAULT / name
        if (p.sha256(path) if path.exists() else None) != expected:
            raise ValueError('Live file changed since backup: ' + name)
        if p.sha256(Path(report['files'][name])) != report['install_hashes'][name]:
            raise ValueError('Staged file changed since backup: ' + name)
    for name, expected in report['server_before_hashes'].items():
        if p.sha256(p.SERVER_DBC_ROOT / (name + '.dbc')) != expected:
            raise ValueError('Server file changed since backup: ' + name)
    if p.sha256(MIGRATION) != report['migration_sha256']:
        raise ValueError('Migration changed since staging')
    if world_fingerprints() != report['unrelated_world_hashes']:
        raise ValueError('Unrelated startup data changed since backup')
    characters = db.sql('SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,extraAppearance '
                        'FROM characters ORDER BY guid;', 'acore_characters')
    receipt = hashlib.sha1(MIGRATION.read_bytes()).hexdigest().upper()
    try:
        db.sql('START TRANSACTION;\n' + MIGRATION.read_text() +
               f"\nINSERT INTO updates (name,hash,state) VALUES ('{MIGRATION.name}','{receipt}','PENDING');\nCOMMIT;")
        for name, source in report['files'].items():
            target = p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + '.creature-next')
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != report['install_hashes'][name]:
                raise ValueError('Install copy hash differs: ' + name)
            os.replace(temporary, target)
            print('INSTALLED', name, flush=True)
        for name in p.SERVER_DBC_TABLES:
            source = STAGE / 'server-dbc' / (name + '.dbc')
            target = p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if p.sha256(target) != p.sha256(source):
                raise ValueError('Installed server DBC differs: ' + name)
        if world_fingerprints() != report['unrelated_world_hashes']:
            raise ValueError('Unrelated startup rows changed during installation')
        if characters != db.sql('SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,extraAppearance '
                                'FROM characters ORDER BY guid;', 'acore_characters'):
            raise ValueError('Existing character appearance changed during installation')
    except Exception:
        for name, expected in report['before_hashes'].items():
            if expected is not None:
                shutil.copy2(old / name, p.CLIENT_DEFAULT / name)
            else:
                (p.CLIENT_DEFAULT / name).unlink(missing_ok=True)
        for name in p.SERVER_DBC_TABLES:
            shutil.copy2(old / 'server-dbc' / (name + '.dbc'), p.SERVER_DBC_ROOT / (name + '.dbc'))
        db.sql('START TRANSACTION;\n' + (old / 'rollback-world.sql').read_text() + '\nCOMMIT;')
        raise
    report.update(installed_hashes={n: p.sha256(p.CLIENT_DEFAULT / n) for n in report['files']},
        installed_server_hashes={n: p.sha256(p.SERVER_DBC_ROOT / (n + '.dbc')) for n in p.SERVER_DBC_TABLES},
        character_appearance_sha256=hashlib.sha256(characters.encode()).hexdigest(),
        migration_receipt_sha1=receipt, status='installed_awaiting_worldserver_recreation')
    save(STAGE / 'last-install.json', report)
    save(old / 'install-report.json', report)
    print('MATCHED PACKAGE INSTALLED', old, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("discover", "acquire", "candidates", "convert", "prepare",
                                           "reserve", "sql", "stage", "backup", "install"))
    parser.add_argument("--race", choices=tuple(SPECS), action="append")
    args = parser.parse_args()
    if args.action == "candidates":
        acquire(args.race or list(CANDIDATES), True)
    elif args.action == 'sql':
        sql()
    else:
        globals()[args.action](args.race or list(SPECS))


if __name__ == "__main__":
    main()
