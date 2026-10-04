"""Fit ThinHuman equipment to the pinned Retail reference and install a backed-up client-only repair."""

import argparse
from collections import Counter
import copy
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import shutil
import struct
import subprocess
from datetime import datetime

from wotlkconv.blp import convert_blp
from wotlkconv.casc import CascStorage, KeyRing, blte
from wotlkconv.casc.cdn import blte_header_md5
from wotlkconv.db.db2 import parse_db2
from wotlkconv.db.dbd import DbdIndex
from wotlkconv.m2 import convert_m2, parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin
from wotlkconv.options import Options

import creature_race_pack as c
import earthen_race_pack as e

ROOT = c.WORK / 'thinhuman'
STAGE = ROOT / 'integration/equipment-repair'
ART = ROOT / 'integration/patch-root'
MODEL = r'custom\thinhuman\native\male\thinhumanmale.m2'
SKIN = MODEL[:-3] + '00.skin'
DONOR = r'Character\Human2\Male\HumanMale2.m2'
RETAIL_BUILD = 'dcfc90fffd79ba00406ae46f5f657592'
RELATIVES = (c.p.GLOBAL_ARCHIVE_REL, c.p.LOCALE_ARCHIVE_REL)


def triangles(skin, mesh):
    start = e.v.u16(mesh, 8) | e.v.u16(mesh, 2) << 16
    return skin.indices[start:start + e.v.u16(mesh, 10)]


def repair_geometry(model, skin):
    """Keep Boots4 under the Boots5 selection; bind Human capes to the existing ThinHuman rig."""
    if any(1500 <= e.v.u16(row, 0) < 1600 for row in skin.submeshes):
        raise ValueError('ThinHuman cloak repair is already present')
    boot = next(i for i, row in enumerate(skin.submeshes) if e.v.u16(row, 0) == 504)
    row = bytearray(skin.submeshes[boot])
    e.v.patch16(row, 0, 505)
    index = len(skin.submeshes)
    skin.submeshes.append(bytes(row))
    for original in list(skin.batches):
        if e.v.u16(original, 4) == boot:
            batch = bytearray(original)
            e.v.patch16(batch, 4, index)
            e.v.patch16(batch, 6, index)
            skin.batches.append(bytes(batch))
    with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
        donor_data, provider = files.find(DONOR)
        donor_skin_data, _ = files.find(DONOR[:-3] + '00.skin')
    donor = parse_m2(donor_data)
    donor_skin = parse_skin(donor_skin_data)
    (STAGE / 'donors').mkdir(parents=True, exist_ok=True)
    c.immutable(STAGE / 'donors/HumanMale2.m2', donor_data)
    c.immutable(STAGE / 'donors/HumanMale200.skin', donor_skin_data)
    meshes = [row for row in donor_skin.submeshes if 1502 <= e.v.u16(row, 0) <= 1506]
    if {e.v.u16(row, 0) for row in meshes} != set(range(1502, 1507)):
        raise ValueError('Human donor does not contain every Wrath cape length')
    used = sorted({donor_skin.vertices[i] for row in meshes for i in triangles(donor_skin, row)})
    by_crc = {b['bone_name_crc']: i for i, b in enumerate(model.bones) if b['bone_name_crc']}
    if len(by_crc) != len(model.bones):
        raise ValueError('ThinHuman bone names are missing or ambiguous')
    vertex_base, lookup_base = model.vertex_count, len(skin.vertices)
    remap = {old: i for i, old in enumerate(used)}
    vertices = bytearray()
    for old in used:
        vertex = bytearray(donor.vertices[old * 48:(old + 1) * 48])
        position = list(struct.unpack_from('<3f', vertex))
        for slot in range(4):
            weight = vertex[12 + slot]
            if not weight:
                vertex[16 + slot] = 0
                continue
            source_bone = donor.bones[vertex[16 + slot]]
            target = by_crc[source_bone['bone_name_crc']]
            vertex[16 + slot] = target
            # Fit the authored cape weights to ThinHuman's bind pivots without changing its animation tracks.
            for axis in range(3):
                position[axis] += weight / 255 * (model.bones[target]['pivot'][axis] - source_bone['pivot'][axis])
        struct.pack_into('<3f', vertex, 0, *position)
        vertices.extend(vertex)
    model.vertices += bytes(vertices)
    model.vertex_count += len(used)
    skin.vertices.extend(vertex_base + i for i in range(len(used)))
    skin.bones += bytes(4 * len(used))  # compact_bone_palettes rebuilds the local palettes below.
    texture = len(model.textures)
    model.textures.append({'type': 2, 'flags': 0, 'filename': ''})
    combo = len(model.texture_combos)
    model.texture_combos.append(texture)
    material = len(model.materials)
    model.materials.append({'flags': 4, 'blending_mode': 1})
    for raw in meshes:
        row = bytearray(raw)
        start = len(skin.indices)
        indices = [lookup_base + remap[donor_skin.vertices[i]] for i in triangles(donor_skin, raw)]
        skin.indices.extend(indices)
        for offset, value in ((2, start >> 16), (4, lookup_base), (6, len(used)),
                              (8, start & 65535), (18, by_crc[donor.bones[e.v.u16(raw, 18)]['bone_name_crc']])):
            e.v.patch16(row, offset, value)
        points = [struct.unpack_from('<3f', model.vertices, skin.vertices[i] * 48) for i in indices]
        center = tuple((min(p[a] for p in points) + max(p[a] for p in points)) / 2 for a in range(3))
        struct.pack_into('<7f', row, 20, *center, *center, max(math.dist(center, p) for p in points))
        index = len(skin.submeshes)
        skin.submeshes.append(bytes(row))
        skin.batches.append(struct.pack('<12H', 16, 0, index, index, 65535, material, 0, 1, combo, 0, 0, 0))
    points = [struct.unpack_from('<3f', vertices, at) for at in range(0, len(vertices), 48)]
    bounds = model.bounding_box
    model.bounding_box = tuple(min(bounds[a], min(p[a] for p in points)) for a in range(3)) + tuple(
        max(bounds[a + 3], max(p[a] for p in points)) for a in range(3))
    model.bounding_sphere_radius = max(model.bounding_sphere_radius, max(math.dist((0, 0, 0), p) for p in points))
    model.replacable_texture_lookup = [65535] * 16
    for i, texture in enumerate(model.textures):
        if texture['type']:
            model.replacable_texture_lookup[texture['type']] = i
    return {'boot_dependency': [504, 505], 'cloak_vertices': len(used), 'cloak_geosets': list(range(1502, 1507)),
            'donor': DONOR, 'donor_provider': provider, 'donor_sha256': hashlib.sha256(donor_data).hexdigest()}


class RetailSource:
    """Read local CASC payloads and verify every model/texture against its installed content key."""

    def __init__(self):
        self.storage = CascStorage.open(c.DEFAULT.retail_root, product='wow', keys=KeyRing.load(c.DEFAULT.keys))
        if self.storage.build.build_key != RETAIL_BUILD:
            self.storage.close()
            raise ValueError('Installed Retail build differs from the ThinHuman source')
        self.listfile = c.Listfile.load(c.DEFAULT.listfile)
        self.definitions = DbdIndex(c.DEFAULT.dbd_dir)

    def by_file_id(self, file_id, extension=''):
        if not file_id:
            return None
        content = self.storage.root.ckey_for(file_id)
        if content is None:
            return None
        suffix = extension or PureWindowsPath(self.listfile.path_for(file_id) or '').suffix
        path = STAGE / 'raw' / f'{file_id}{suffix}'
        if path.exists():
            data = path.read_bytes()
        else:
            data, error = self.storage.try_read_file_id(file_id, zero_encrypted=suffix == '.db2')
            if data is None and 'not a BLTE stream' in error:
                encoding = self.storage.encoding.ekey_for(content)
                location = self.storage.index.find(encoding) if encoding else None
                if location:
                    with (c.DEFAULT.retail_root / 'Data/data' / f'data.{location.archive:03d}').open('rb') as stream:
                        stream.seek(location.offset)
                        encoded = stream.read(location.size)
                    if encoded.startswith(b'BLTE') and blte_header_md5(encoded) == encoding:
                        data = blte.decode(encoded, self.storage.keys, zero_missing=suffix == '.db2')
            if data is None:
                raise ValueError(f'Local Retail file {file_id} is unavailable: {error}')
            c.immutable(path, data)
        if suffix != '.db2' and hashlib.md5(data).digest() != content:
            raise ValueError(f'Retail content hash differs: {file_id}')
        return data

    def by_path(self, key):
        return self.by_file_id(self.listfile.id_for(key))

    def table(self, name):
        file_id = self.listfile.id_for('dbfilesclient/' + name.lower() + '.db2')
        return parse_db2(self.by_file_id(file_id, '.db2'), name, self.definitions, name)


def repair_helmet_materials(model, skin, source_skin):
    """Express Retail's alpha-masked metal reflection as Wrath's reflection and diffuse-overlay passes."""
    if len(skin.batches) != len(source_skin.batches):
        raise ValueError('Helmet batch layout changed during conversion')
    selected = []
    for i, original in enumerate(source_skin.batches):
        shader = e.v.u16(original, 2)
        batch = skin.batches[i]
        texture = model.texture_combos[e.v.u16(batch, 16)]
        if (original[0] & 0x80 and shader in (0x8000, 0x800c) and e.v.u16(batch, 14) == 2
                and model.textures[texture]['type'] == 2
                and model.materials[e.v.u16(batch, 10)]['blending_mode'] == 0):
            selected.append(i)
    if not selected:
        return 0
    old_combiners = list(model.texture_combiner_combos)
    had_combiners = bool(model.global_flags & 8)
    model.global_flags |= 8
    model.texture_combiner_combos = []
    batches = []
    for i, raw in enumerate(skin.batches):
        batch = bytearray(raw)
        count, shader = e.v.u16(batch, 14), e.v.u16(batch, 2)
        if shader & 0x8000 and i not in selected:
            batches.append(bytes(batch))
            continue
        if had_combiners:
            combiners = old_combiners[shader:shader + count]
            if len(combiners) != count:
                raise ValueError('Helmet shader references a truncated combiner run')
        else:
            material = model.materials[e.v.u16(batch, 10)]
            combiners = [int(material['blending_mode'] != 0)] + [0] * (count - 1)
        if i in selected:
            combiners = [1, 4 if e.v.u16(source_skin.batches[i], 2) == 0x8000 else 1]
        # Wrath 0x00836980 indexes this table through shaderId, independent of textureComboIndex.
        start = len(model.texture_combiner_combos)
        model.texture_combiner_combos.extend(combiners)
        e.v.patch16(batch, 2, start)
        if i in selected:
            batch[0] &= 0x7f
            overlay = bytearray(batch)
            material = dict(model.materials[e.v.u16(batch, 10)])
            material.update(flags=material['flags'] | 16, blending_mode=2)
            e.v.patch16(overlay, 10, len(model.materials))
            model.materials.append(material)
            e.v.patch16(overlay, 12, e.v.u16(batch, 12) + 1)
            e.v.patch16(overlay, 14, 1)
            batches.extend((bytes(batch), bytes(overlay)))
        else:
            batches.append(bytes(batch))
    skin.batches = batches
    return len(selected)


def native_helmet_shader(model, batch):
    """Read the actual Wrath load-time contract at 0x00836980, including its shader-index lookup."""
    shader, count = e.v.u16(batch, 2), e.v.u16(batch, 14)
    if shader & 0x8000:
        return shader
    assert model.global_flags & 8 and 1 <= count <= 2
    assert shader + count <= len(model.texture_combiner_combos)
    start = e.v.u16(batch, 18)
    assert start + count <= len(model.texture_coord_combos)
    modes = list(model.texture_combiner_combos[shader:shader + count])
    if model.materials[e.v.u16(batch, 10)]['blending_mode'] == 0:
        modes[0] = 0
    result = 0
    for i, mode in enumerate(modes):
        coord = model.texture_coord_combos[start + i]
        if coord > 2:
            mode |= 8
        if coord == 1 and i + 1 == count:
            result |= 0x4000
        result |= mode << (4 if i == 0 else 0)
    return result


def check_helmet_materials(art):
    checked = 0
    for row in c.p.load_json(STAGE / 'helmets.json')['converted']:
        if not row.get('material_repairs'):
            continue
        path = art.joinpath(*PureWindowsPath(row['target']).parts)
        model = parse_m2(path.read_bytes())
        skin = parse_skin(path.with_name(path.stem + '00.skin').read_bytes())
        assert model.global_flags & 8
        for batch in skin.batches:
            native_helmet_shader(model, batch)
        source = parse_m2((STAGE / 'raw' / f'{row["file_id"]}.m2').read_bytes())
        source_skin = parse_skin((STAGE / 'raw' / f'{source.skin_file_ids[0]}.skin').read_bytes())
        overlays, at = 0, 0
        for original in source_skin.batches:
            batch = skin.batches[at]
            at += 1
            first, count = e.v.u16(batch, 16), e.v.u16(batch, 14)
            source_texture = source.textures[source.texture_combos[e.v.u16(original, 16)]]
            shader = e.v.u16(original, 2)
            if not (original[0] & 0x80 and shader in (0x8000, 0x800c) and count == 2
                    and source_texture['type'] == 2
                    and source.materials[e.v.u16(original, 10)]['blending_mode'] == 0):
                continue
            start = e.v.u16(batch, 2)
            codes = model.texture_combiner_combos[start:start + 2]
            assert codes == [1, 4 if shader == 0x8000 else 1]
            assert native_helmet_shader(model, batch) == (0x000c if shader == 0x8000 else 0x0009)
            overlay = skin.batches[at]
            at += 1
            assert e.v.u16(overlay, 4) == e.v.u16(batch, 4) and e.v.u16(overlay, 14) == 1
            assert e.v.u16(overlay, 16) == first
            assert native_helmet_shader(model, overlay) == 0x0010
            material = model.materials[e.v.u16(overlay, 10)]
            assert material['blending_mode'] == 2 and material['flags'] & 16
            assert material['flags'] & 1 == model.materials[e.v.u16(batch, 10)]['flags'] & 1
            for alpha in (0, .3, 1):
                for diffuse, reflection in ((.15, .02), (.35, .17), (.7, .6)):
                    factor = 2 if codes[1] == 4 else 1
                    native = diffuse * reflection * factor * (1 - alpha) + diffuse * alpha
                    retail = diffuse * (reflection * factor + alpha * (1 - reflection * factor))
                    assert math.isclose(native, retail, abs_tol=1e-7)
            overlays += 1
        assert overlays == row['material_repairs'], row['stem']
        assert at == len(skin.batches), row['stem']
        checked += 1
    assert checked > 0
    reference = next(r for r in c.p.load_json(STAGE / 'helmets.json')['converted'] if r['file_id'] == 331348)
    legacy_model = parse_m2((STAGE / 'legacy-materials/331348.m2').read_bytes())
    legacy_skin = parse_skin((STAGE / 'legacy-materials/331348.skin').read_bytes())
    current = parse_m2(art.joinpath(*PureWindowsPath(reference['target']).parts).read_bytes())
    current_skin = parse_skin(art.joinpath(*PureWindowsPath(reference['target'][:-3] + '00.skin').parts).read_bytes())

    def programs(character, profile):
        return sorted((e.v.u16(b, 4), native_helmet_shader(character, b), e.v.u16(b, 14),
                       character.materials[e.v.u16(b, 10)]['blending_mode'], e.v.u16(b, 12))
                      for b in profile.batches)

    assert programs(current, current_skin) == programs(legacy_model, legacy_skin)
    print(f'PASS: {checked} helmet families use bounded shader lookups; Ymirjar matches the stock Wrath program.',
          flush=True)
    return checked


def fix_helmet_materials():
    directory = STAGE / 'materials'
    art = directory / 'art'
    headers = prepare_helmets(art)
    check_helmet_materials(art)
    protected = {n: c.p.sha256(c.p.CLIENT_DEFAULT / n)
                 for n in ('Wow.exe', 'EsteriaAppearance.dll', 'EsteriaAppearanceGeometry.bin')}
    updates, before = {}, {}
    with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
        for key in (MODEL, SKIN, r'DBFilesClient\ChrRaces.dbc'):
            protected[key] = hashlib.sha256(files.find(key)[0]).hexdigest()
        for row in headers['converted']:
            if not row.get('material_repairs'):
                continue
            for key in (row['target'], row['target'][:-3] + '00.skin'):
                old = files.find(key)[0]
                new = art.joinpath(*PureWindowsPath(key).parts).read_bytes()
                if key.endswith('.m2'):
                    old_model, new_model = parse_m2(old), parse_m2(new)
                    assert old_model.vertices == new_model.vertices
                    assert old_model.bounding_box == new_model.bounding_box
                    assert old_model.textures == new_model.textures
                else:
                    old_skin, new_skin = parse_skin(old), parse_skin(new)
                    assert old_skin.vertices == new_skin.vertices and old_skin.indices == new_skin.indices
                    assert old_skin.submeshes == new_skin.submeshes and old_skin.bones == new_skin.bones
                if old != new:
                    updates[key] = new
                    before[key] = hashlib.sha256(old).hexdigest()
    if not updates:
        raise ValueError('Helmet material repair is already installed')
    storm = c.p.Storm(c.p.DLL_DEFAULT)
    originals, staged_hashes = {}, {}
    for relative in RELATIVES:
        live = c.p.CLIENT_DEFAULT / relative
        staged = directory / 'pack' / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        originals[str(relative)] = c.p.sha256(live)
        shutil.copy2(live, staged)
        assert c.p.sha256(staged) == originals[str(relative)]
        storm.replace_archive_entries(staged, updates)
        if staged.stat().st_size >= 0x80000000:
            raise ValueError('Material repair exceeds the classic archive reader boundary')
        archive = storm.open_archive(staged)
        try:
            for key, data in updates.items():
                assert storm.read(archive, key) == data, key
        finally:
            storm.dll.SFileCloseArchive(archive)
        staged_hashes[str(relative)] = c.p.sha256(staged)
        print('MATERIALS STAGED', relative, flush=True)
    backup = Path(r'G:\EsteriaBackups') / ('thinhuman-materials-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    for relative in RELATIVES:
        live = c.p.CLIENT_DEFAULT / relative
        if c.p.sha256(live) != originals[str(relative)]:
            raise ValueError('Client archive changed during material preparation')
        destination = backup / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, destination)
        assert c.p.sha256(destination) == originals[str(relative)]
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(name in processes for name in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Close WoW/Eclipse/MPQEditor before installing the checked material repair')
    try:
        for relative in RELATIVES:
            destination = c.p.CLIENT_DEFAULT / relative
            temporary = destination.with_suffix('.materials-next')
            shutil.copy2(directory / 'pack' / relative, temporary)
            assert c.p.sha256(temporary) == staged_hashes[str(relative)]
            os.replace(temporary, destination)
        with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
            for key, data in updates.items():
                assert files.find(key)[0] == data, key
            for key, digest in protected.items():
                payload = files.find(key)[0] if '\\' in key else (c.p.CLIENT_DEFAULT / key).read_bytes()
                assert hashlib.sha256(payload).hexdigest() == digest, key
    except Exception:
        for relative in RELATIVES:
            shutil.copy2(backup / relative, c.p.CLIENT_DEFAULT / relative)
        raise
    for key, data in updates.items():
        for root in (ART, STAGE / 'art'):
            destination = root.joinpath(*PureWindowsPath(key).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    receipt = {'status': 'installed', 'backup': str(backup), 'source_hashes': originals,
               'installed_hashes': staged_hashes, 'protected_hashes': protected,
               'before_entries': before, 'entries': {k: hashlib.sha256(v).hexdigest() for k, v in updates.items()},
               'helmet_families': sum(bool(r.get('material_repairs')) for r in headers['converted'])}
    c.save(directory / 'last-install.json', receipt)
    c.save(backup / 'install-report.json', receipt)
    return {k: receipt[k] for k in ('status', 'backup', 'helmet_families')}


def prepare_helmets(art=ART):
    import mechagnome_race_pack as db
    displays = {int(x) for x in db.sql('SELECT DISTINCT displayid FROM item_template '
                                      'WHERE InventoryType=1 AND displayid<>0;').split()}
    table = c.p.RawWdbc(c.p._full_table(c.p.CLIENT_DEFAULT / 'Data', 'ItemDisplayInfo')[0])
    stems = {PureWindowsPath(c.p._string(table.strings, c.p._value(row, 4)).decode()).stem
             for row in table.records if c.p._value(row, 0) in displays}
    stems.discard('')
    source = RetailSource()
    converted, legacy = [], []
    try:
        model_rows = list(source.table('ModelFileData'))
        components = dict(source.table('ComponentModelFileData'))
        resource_by_file = {r['FileDataID']: r['ModelResourcesID'] for _, r in model_rows}
        resources = {}
        resource_by_stem = {}
        for _, row in model_rows:
            resources.setdefault(row['ModelResourcesID'], []).append(row['FileDataID'])
            logical = (source.listfile.path_for(row['FileDataID']) or '').replace('\\', '/').lower()
            if logical.startswith('item/objectcomponents/head/'):
                resource_by_stem.setdefault(PureWindowsPath(logical).stem.rsplit('_', 1)[0], row['ModelResourcesID'])
        with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as installed:
            for stem in sorted(stems):
                human = source.listfile.id_for(f'item/objectcomponents/head/{stem}_hum.m2'.lower())
                resource = resource_by_file.get(human, resource_by_stem.get(stem.lower()))
                options = resources.get(resource, [])
                target_stem = stem + '_ThM'
                key = 'Item\\ObjectComponents\\Head\\' + target_stem + '.m2'
                if not options:
                    # Keep legacy-only equipment available; the Retail resolver has no variant for these families.
                    try:
                        payload, _ = installed.find('Item\\ObjectComponents\\Head\\' + stem + '_HuM.m2')
                    except FileNotFoundError:
                        legacy.append(stem)
                        continue
                    model = parse_m2(payload)
                    updates = {key: payload}
                    if model.num_skin_profiles:
                        updates[key[:-3] + '00.skin'] = installed.find(
                            'Item\\ObjectComponents\\Head\\' + stem + '_HuM00.skin')[0]
                    for name, data in updates.items():
                        destination = art.joinpath(*PureWindowsPath(name).parts)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(data)
                    legacy.append(stem)
                    continue
                # Match wow.export's exact race/gender, race/any, generic, then first-model resolver.
                file_id = next((i for i in options if components.get(i, {}).get('RaceID') == 33
                                and components[i]['GenderIndex'] == 0), None)
                file_id = file_id or next((i for i in options if components.get(i, {}).get('RaceID') == 33
                                          and components[i]['GenderIndex'] == 2), None)
                file_id = file_id or next((i for i in options if components.get(i, {}).get('RaceID') == 0), options[0])
                raw = source.by_file_id(file_id, '.m2')
                source_key = source.listfile.path_for(file_id)
                data, result, companions = convert_m2(raw, source_key, Options(
                    path_prefix=r'custom\thinhuman\equipment'), source.listfile, source, output_stem=target_stem)
                if not result.ok or any(not a.result.ok for a in companions):
                    raise ValueError('Retail helmet conversion failed: ' + stem)
                model = parse_m2(data)
                destination = art.joinpath(*PureWindowsPath(key).parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                for companion in companions:
                    (destination.parent / companion.filename).write_bytes(companion.data)
                original = parse_m2(raw)
                model = e.v.read_player_model(destination)
                skin_path = destination.with_name(destination.stem + '00.skin')
                profile = parse_skin(skin_path.read_bytes())
                source_profile = parse_skin(source.by_file_id(original.skin_file_ids[0], '.skin'))
                material_repairs = repair_helmet_materials(model, profile, source_profile)
                if material_repairs:
                    destination.write_bytes(write_md20(model))
                    skin_path.write_bytes(write_skin(profile))
                texture_ids = original.texture_file_ids or [0] * len(model.textures)
                for texture, texture_id in zip(model.textures, texture_ids, strict=True):
                    if texture['type'] or not texture['filename']:
                        continue
                    payload = (source.by_file_id(texture_id, '.blp') if texture_id
                               else source.by_path(texture['filename']))
                    bitmap, result = convert_blp(payload, texture['filename'], Options())
                    if not result.ok:
                        raise ValueError('Helmet hard texture failed: ' + texture['filename'])
                    destination = art.joinpath(*PureWindowsPath(texture['filename']).parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(bitmap)
                converted.append({'stem': stem, 'file_id': file_id, 'source': source_key, 'target': key,
                                  'sha256': hashlib.sha256(raw).hexdigest(), 'material_repairs': material_repairs})
                if len(converted) % 50 == 0:
                    print('RETAIL HELMETS', len(converted), flush=True)
    finally:
        source.storage.close()
    report = {'build': RETAIL_BUILD, 'converted': converted, 'legacy_only': legacy, 'families': len(stems)}
    c.save(STAGE / 'helmets.json', report)
    return report


def replace_geometry(data, skin):
    magic, version, count = struct.unpack_from('<3I', data)
    if (magic, version) != (0x4D474145, 1):
        raise ValueError('Unexpected native geometry catalog')
    at, records, changed = 12, [], 0
    for _ in range(count):
        key = data[at:at + 128].split(b'\0')[0].decode()
        size = struct.unpack_from('<I', data, at + 128)[0]
        end = at + 132 + size
        if end > len(data):
            raise ValueError('Truncated geometry record')
        records.append(data[at:at + 128] + struct.pack('<I', len(skin)) + skin
                       if key.lower() == MODEL.lower() else data[at:end])
        changed += key.lower() == MODEL.lower()
        at = end
    if at != len(data) or changed != 1:
        raise ValueError('Expected one complete ThinHuman geometry record')
    return data[:12] + b''.join(records)


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    c.save(STAGE / 'build-report.json', {'status': 'preparing'})
    with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
        original = files.find(MODEL)[0]
        original_skin = files.find(SKIN)[0]
        races_data = files.find(r'DBFilesClient\ChrRaces.dbc')[0]
    for name, data in (('ThinHuman.m2', original), ('ThinHuman00.skin', original_skin), ('ChrRaces.dbc', races_data)):
        c.immutable(STAGE / 'before' / name, data)
    model, skin = parse_m2(original), parse_skin(original_skin)
    repair = repair_geometry(model, skin)
    skin = e.v.compact_bone_palettes(model, skin)
    (STAGE / 'ThinHuman.m2').write_bytes(write_md20(model))
    (STAGE / 'ThinHuman00.skin').write_bytes(write_skin(skin))
    helmets = prepare_helmets(STAGE / 'art')
    races = c.p.RawWdbc(races_data)
    if any(c.p._value(row, 0) not in (58, 59) and c.p._string(races.strings, c.p._value(row, 24)) == b'Th'
           for row in races.records):
        raise ValueError('ThinHuman helmet prefix collides with another race')
    pool = bytearray(races.strings)
    prefix = c.p._append_string(pool, 'Th')
    rows = [c.p._replace(row, 24, 4, prefix) if c.p._value(row, 0) in (58, 59) else row for row in races.records]
    if sum(old != new for old, new in zip(races.records, rows, strict=True)) != 2:
        raise ValueError('Expected only the two ThinHuman helmet prefixes to change')
    updates = {MODEL: (STAGE / 'ThinHuman.m2').read_bytes(), SKIN: (STAGE / 'ThinHuman00.skin').read_bytes(),
               r'DBFilesClient\ChrRaces.dbc': races.build(rows, bytes(pool))}
    for path in (STAGE / 'art').rglob('*'):
        if path.is_file():
            updates[str(PureWindowsPath(path.relative_to(STAGE / 'art')))] = path.read_bytes()
    geometry = (c.p.CLIENT_DEFAULT / 'EsteriaAppearanceGeometry.bin').read_bytes()
    c.immutable(STAGE / 'before/EsteriaAppearanceGeometry.bin', geometry)
    (STAGE / 'EsteriaAppearanceGeometry.bin').write_bytes(replace_geometry(geometry, updates[SKIN]))
    report = {'status': 'staged', 'repair': repair, 'helmet_families': helmets['families'],
              'legacy_only_helmets': helmets['legacy_only'], 'source_hashes': {}, 'stage_hashes': {},
              'entries': {k: hashlib.sha256(v).hexdigest() for k, v in updates.items()},
              'runtime_hashes': {n: c.p.sha256(c.p.CLIENT_DEFAULT / n) for n in ('Wow.exe', 'EsteriaAppearance.dll')}}
    storm = c.p.Storm(c.p.DLL_DEFAULT)
    for relative in RELATIVES:
        live = c.p.CLIENT_DEFAULT / relative
        staged = STAGE / 'pack' / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        report['source_hashes'][str(relative)] = c.p.sha256(live)
        shutil.copy2(live, staged)
        if c.p.sha256(staged) != report['source_hashes'][str(relative)]:
            raise ValueError('Archive staging copy differs')
        storm.replace_archive_entries(staged, updates)
        if staged.stat().st_size >= 0x80000000:
            raise ValueError('Repair exceeds the classic archive reader boundary')
        archive = storm.open_archive(staged)
        try:
            for key, data in updates.items():
                if storm.read(archive, key) != data:
                    raise ValueError('Staged archive entry differs: ' + key)
        finally:
            storm.dll.SFileCloseArchive(archive)
        report['stage_hashes'][str(relative)] = c.p.sha256(staged)
        print('STAGED', relative, flush=True)
    name = 'EsteriaAppearanceGeometry.bin'
    report['source_hashes'][name] = hashlib.sha256(geometry).hexdigest()
    report['stage_hashes'][name] = c.p.sha256(STAGE / name)
    c.save(STAGE / 'build-report.json', report)
    check()
    return {'status': report['status'], 'repair': repair, 'helmet_families': helmets['families'],
            'legacy_only_helmets': helmets['legacy_only']}


def check():
    original = parse_m2((STAGE / 'before/ThinHuman.m2').read_bytes())
    original_skin = parse_skin((STAGE / 'before/ThinHuman00.skin').read_bytes())
    model = parse_m2((STAGE / 'ThinHuman.m2').read_bytes())
    skin = parse_skin((STAGE / 'ThinHuman00.skin').read_bytes())
    assert model.vertices[:len(original.vertices)] == original.vertices
    for before, after in zip(original.tracks(), model.tracks(), strict=True):
        before.timestamp_spans = after.timestamp_spans = []
        if hasattr(before, 'values'):
            before.value_spans = after.value_spans = []
    assert model.bones == original.bones and model.attachments == original.attachments
    assert model.sequences == original.sequences and model.events == original.events
    assert len(skin.vertices) <= 65535 and skin.bone_count_max <= 75
    assert all(not track.external for track in model.tracks())

    def geometry(profile, geoset):
        return [tuple(profile.vertices[i] for i in triangles(profile, row))
                for row in profile.submeshes if e.v.u16(row, 0) == geoset]

    for geoset in {e.v.u16(row, 0) for row in original_skin.submeshes}:
        expected = geometry(original_skin, geoset)
        if geoset == 505:
            expected += geometry(original_skin, 504)
        assert geometry(skin, geoset) == expected, geoset
    assert all(geometry(skin, i) for i in range(1502, 1507))
    assert model.textures[model.replacable_texture_lookup[2]]['type'] == 2
    for i, mesh in enumerate(skin.submeshes):
        if not 1502 <= e.v.u16(mesh, 0) <= 1506:
            continue
        assert all(model.textures[model.texture_combos[e.v.u16(batch, 16)]]['type'] == 2
                   for batch in skin.batches if e.v.u16(batch, 4) == i)
        for lookup in triangles(skin, mesh):
            vertex = skin.vertices[lookup] * 48
            for slot in range(4):
                if model.vertices[vertex + 12 + slot]:
                    bone = model.vertices[vertex + 16 + slot]
                    assert bone < len(model.bones)
                    assert original.bones[bone]['bone_name_crc'] == model.bones[bone]['bone_name_crc']
    assert replace_geometry((STAGE / 'before/EsteriaAppearanceGeometry.bin').read_bytes(),
                            (STAGE / 'ThinHuman00.skin').read_bytes()) == (
                                STAGE / 'EsteriaAppearanceGeometry.bin').read_bytes()
    helmets = c.p.load_json(STAGE / 'helmets.json')
    reference = next(r for r in helmets['converted'] if r['stem'].lower() == 'helm_plate_raidwarrior_h_01')
    assert reference['file_id'] == 331348  # Exact variant selected by the installed wow.export resolver.
    for row in helmets['converted']:
        raw = (STAGE / 'raw' / f'{row["file_id"]}.m2').read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        before = parse_m2(raw)
        path = (STAGE / 'art').joinpath(*PureWindowsPath(row['target']).parts)
        after = parse_m2(path.read_bytes())
        assert before.bounding_box == after.bounding_box
        if after.num_skin_profiles:
            source_skin = parse_skin((STAGE / 'raw' / f'{before.skin_file_ids[0]}.skin').read_bytes())
            target_skin = parse_skin(path.with_name(path.stem + '00.skin').read_bytes())

            def surface(character, profile):
                result = Counter()
                for mesh in profile.submeshes:
                    indices = triangles(profile, mesh)
                    for at in range(0, len(indices), 3):
                        records = [profile.vertices[i] * 48 for i in indices[at:at + 3]]
                        result[(e.v.u16(mesh, 0), tuple(character.vertices[i:i + 48] for i in records))] += 1
                return result

            assert surface(before, source_skin) == surface(after, target_skin), row['stem']
    report = c.p.load_json(STAGE / 'build-report.json')
    old_races = c.p.RawWdbc((STAGE / 'before/ChrRaces.dbc').read_bytes())
    updated = c.p.RawWdbc(c.p._read_archive_entry(c.p.Storm(c.p.DLL_DEFAULT),
        STAGE / 'pack' / c.p.LOCALE_ARCHIVE_REL, r'DBFilesClient\ChrRaces.dbc'))
    assert updated.strings == old_races.strings + b'Th\0'
    for before, after in zip(old_races.records, updated.records, strict=True):
        expected = c.p._replace(before, 24, 4, len(old_races.strings)) if c.p._value(before, 0) in (58, 59) else before
        assert after == expected
    for relative, digest in report['stage_hashes'].items():
        path = STAGE / 'pack' / relative if relative in map(str, RELATIVES) else STAGE / relative
        assert c.p.sha256(path) == digest, relative
    print('PASS: Boots4 retained with Boots5; five skinned cape lengths; Retail helmet surfaces; '
          'original body, bones, animations and attachments preserved.', flush=True)


def install():
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(name in processes for name in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Close WoW/Eclipse/MPQEditor before installing the checked repair')
    check()
    report = c.p.load_json(STAGE / 'build-report.json')
    if report['status'] != 'staged':
        raise ValueError('Repair staging did not finish')
    for name, digest in report['runtime_hashes'].items():
        if c.p.sha256(c.p.CLIENT_DEFAULT / name) != digest:
            raise ValueError('Client runtime changed since staging: ' + name)
    backup = Path(r'G:\EsteriaBackups') / ('thinhuman-equipment-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    files = {str(relative): STAGE / 'pack' / relative for relative in RELATIVES}
    files['EsteriaAppearanceGeometry.bin'] = STAGE / 'EsteriaAppearanceGeometry.bin'
    for name in files:
        live = c.p.CLIENT_DEFAULT / name
        if c.p.sha256(live) != report['source_hashes'][name]:
            raise ValueError('Client file changed since staging: ' + name)
        destination = backup / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, destination)
        if c.p.sha256(destination) != report['source_hashes'][name]:
            raise ValueError('Backup hash differs: ' + name)
    for path in (ART / 'custom/thinhuman/native/male').glob('*'):
        destination = backup / 'integration' / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    shutil.copy2(ROOT / 'integration/rendering.json', backup / 'rendering.json')
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(name in processes for name in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Client opened during preparation; the repair and backups are preserved')
    try:
        for name, source in files.items():
            destination = c.p.CLIENT_DEFAULT / name
            temporary = destination.with_suffix(destination.suffix + '.thinhuman-next')
            shutil.copy2(source, temporary)
            if c.p.sha256(temporary) != report['stage_hashes'][name]:
                raise ValueError('Installation copy differs: ' + name)
            os.replace(temporary, destination)
        with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as client:
            for key, digest in report['entries'].items():
                if hashlib.sha256(client.find(key)[0]).hexdigest() != digest:
                    raise ValueError('Winning archive entry differs after installation: ' + key)
        for name, digest in report['runtime_hashes'].items():
            if c.p.sha256(c.p.CLIENT_DEFAULT / name) != digest:
                raise ValueError('Runtime unexpectedly changed: ' + name)
    except Exception:
        for name in files:
            shutil.copy2(backup / name, c.p.CLIENT_DEFAULT / name)
        raise
    for name, path in ((MODEL, STAGE / 'ThinHuman.m2'), (SKIN, STAGE / 'ThinHuman00.skin')):
        shutil.copy2(path, ART.joinpath(*PureWindowsPath(name).parts))
    shutil.copytree(STAGE / 'art', ART, dirs_exist_ok=True)
    rendering = c.p.load_json(ROOT / 'integration/rendering.json')
    model = parse_m2((STAGE / 'ThinHuman.m2').read_bytes())
    skin = parse_skin((STAGE / 'ThinHuman00.skin').read_bytes())
    rendering['models']['0'].update(vertices=model.vertex_count, skin_vertices=len(skin.vertices),
        geosets=sorted({e.v.u16(row, 0) for row in skin.submeshes}), equipment_repair=report['repair'])
    c.save(ROOT / 'integration/rendering.json', rendering)
    report.update(status='installed', backup=str(backup),
                  installed_hashes={name: c.p.sha256(c.p.CLIENT_DEFAULT / name) for name in files})
    c.save(STAGE / 'last-install.json', report)
    c.save(backup / 'install-report.json', report)
    return {'status': 'installed', 'backup': str(backup), 'helmet_families': report['helmet_families'],
            'legacy_only_helmets': report['legacy_only_helmets']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'check', 'install', 'materials'))
    args = parser.parse_args()
    actions = {'prepare': prepare, 'check': check, 'install': install, 'materials': fix_helmet_materials}
    print(json.dumps(actions[args.command](), indent=2))
