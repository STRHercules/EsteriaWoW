"""Round the installed Tuskarr feet and retain its calves when Wrath selects a robe."""

import argparse
from collections import Counter, defaultdict
import copy
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import shutil
import struct
import subprocess

from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin

import creature_race_pack as c
import earthen_race_pack as e

ROOT = c.WORK / 'tuskarr'
STAGE = ROOT / 'integration/equipment-repair'
MODEL = r'custom\tuskarr\native\male\tuskarrmale.m2'
SKIN = MODEL[:-3] + '00.skin'
RELATIVES = (c.p.GLOBAL_ARCHIVE_REL, c.p.LOCALE_ARCHIVE_REL)


def triangles(skin, mesh):
    start = e.v.u16(mesh, 8) | e.v.u16(mesh, 2) << 16
    indices = skin.indices[start:start + e.v.u16(mesh, 10)]
    return [tuple(skin.vertices[i] for i in indices[at:at + 3]) for at in range(0, len(indices), 3)]


def position(vertices, index):
    return struct.unpack_from('<3f', vertices, index * 48)


def rounded_feet(vertices, faces):
    """Two Loop subdivisions; weld UV seams geometrically and keep the open ankle rims fixed."""
    for _ in range(2):
        used = {i for face in faces for i in face}
        points = {i: position(vertices, i) for i in used}
        welded = {}
        identity = {i: welded.setdefault(tuple(round(v, 6) for v in points[i]), i) for i in sorted(used)}
        neighbors, edges = defaultdict(set), defaultdict(list)
        for face in faces:
            a, b, d = (identity[i] for i in face)
            for first, second, opposite in ((a, b, d), (b, d, a), (d, a, b)):
                if first == second:
                    raise ValueError('Degenerate Tuskarr foot triangle')
                neighbors[first].add(second)
                neighbors[second].add(first)
                edges[tuple(sorted((first, second)))].append(opposite)
        if any(len(opposites) > 2 for opposites in edges.values()):
            raise ValueError('Non-manifold Tuskarr foot surface')
        boundary = {i for edge, opposites in edges.items() if len(opposites) == 1 for i in edge}
        moved = {}
        for index, adjacent in neighbors.items():
            count = len(adjacent)
            beta = (0.625 - (0.375 + 0.25 * math.cos(2 * math.pi / count)) ** 2) / count
            moved[index] = points[index] if index in boundary else tuple(
                (1 - count * beta) * points[index][axis] + beta * sum(points[j][axis] for j in adjacent)
                for axis in range(3))
            if points[index][2] < 0.001:
                moved[index] = (*moved[index][:2], points[index][2])
        source = bytes(vertices)
        for index in used:
            struct.pack_into('<3f', vertices, index * 48, *moved[identity[index]])
        splits = {}

        def midpoint(first, second):
            key = tuple(sorted((first, second)))
            if key in splits:
                return splits[key]
            edge = tuple(sorted((identity[first], identity[second])))
            opposite = edges[edge]
            point = tuple((points[first][axis] + points[second][axis]) / 2 for axis in range(3))
            if len(opposite) == 2:
                point = tuple(0.375 * (points[first][axis] + points[second][axis])
                              + 0.125 * sum(points[j][axis] for j in opposite) for axis in range(3))
            if max(points[first][2], points[second][2]) < 0.001:
                point = (*point[:2], (points[first][2] + points[second][2]) / 2)
            vertex = bytearray(source[first * 48:(first + 1) * 48])
            struct.pack_into('<3f', vertex, 0, *point)
            for offset in (32, 40):
                values = [struct.unpack_from('<2f', source, i * 48 + offset) for i in (first, second)]
                struct.pack_into('<2f', vertex, offset, *((values[0][a] + values[1][a]) / 2 for a in range(2)))
            weights = defaultdict(float)
            for index in (first, second):
                for slot in range(4):
                    weights[source[index * 48 + 16 + slot]] += source[index * 48 + 12 + slot] / 2
            active = sorted(((bone, weight) for bone, weight in weights.items() if weight),
                            key=lambda row: (-row[1], row[0]))
            if len(active) > 4:
                raise ValueError('Foot subdivision exceeds four skin influences')
            quantized = [int(weight) for _, weight in active]
            quantized[0] += 255 - sum(quantized)
            vertex[12:20] = bytes(quantized + [0] * (4 - len(active))
                                  + [bone for bone, _ in active] + [0] * (4 - len(active)))
            splits[key] = len(vertices) // 48
            vertices.extend(vertex)
            return splits[key]

        refined = []
        for a, b, d in faces:
            ab, bd, da = midpoint(a, b), midpoint(b, d), midpoint(d, a)
            refined.extend(((a, ab, da), (ab, b, bd), (da, bd, d), (ab, bd, da)))
        faces = refined
    # Smooth normals across duplicated atlas seam vertices without changing their UVs.
    normals = defaultdict(lambda: [0.0, 0.0, 0.0])
    for face in faces:
        points = [position(vertices, i) for i in face]
        first = [points[1][a] - points[0][a] for a in range(3)]
        second = [points[2][a] - points[0][a] for a in range(3)]
        normal = (first[1] * second[2] - first[2] * second[1],
                  first[2] * second[0] - first[0] * second[2],
                  first[0] * second[1] - first[1] * second[0])
        for point in points:
            accumulated = normals[tuple(round(v, 6) for v in point)]
            for axis in range(3):
                accumulated[axis] += normal[axis]
    for index in {i for face in faces for i in face}:
        normal = normals[tuple(round(v, 6) for v in position(vertices, index))]
        length = math.sqrt(sum(value * value for value in normal))
        if length < 1e-9:
            raise ValueError('Invalid rounded foot normal')
        struct.pack_into('<3f', vertices, index * 48 + 20, *(value / length for value in normal))
    return faces


def repair_geometry(model, skin):
    if any(1300 <= e.v.u16(mesh, 0) < 1400 for mesh in skin.submeshes):
        raise ValueError('Tuskarr already has robe geometry; audit it before replacing it')
    body = next(i for i, mesh in enumerate(skin.submeshes) if e.v.u16(mesh, 0) in (0, 10000))
    meshes = [triangles(skin, mesh) for mesh in skin.submeshes]
    # ponytail: cutoff is tied to the pinned Tuskarr mesh; re-audit if its source geometry changes.
    feet = [face for face in meshes[body] if max(position(model.vertices, i)[2] for i in face) < 0.17]
    original_feet = {i for face in feet for i in face}
    if len(original_feet) != 116 or any(len(set(face)) != 3 for face in feet):
        raise ValueError('Installed Tuskarr feet differ from the pinned source')
    vertices = bytearray(model.vertices)
    refined = rounded_feet(vertices, feet)
    foot_faces = set(feet)
    meshes[body] = [face for face in meshes[body] if face not in foot_faces] + refined
    before = model.vertex_count
    model.vertices, model.vertex_count = bytes(vertices), len(vertices) // 48
    skin.vertices = list(range(model.vertex_count))
    skin.bones = bytes(4 * model.vertex_count)
    skin.indices = []
    for index, faces in enumerate(meshes):
        start = len(skin.indices)
        skin.indices.extend(i for face in faces for i in face)
        row = bytearray(skin.submeshes[index])
        for offset, value in ((2, start >> 16), (4, 0), (6, model.vertex_count),
                              (8, start & 65535), (10, len(faces) * 3)):
            e.v.patch16(row, offset, value)
        skin.submeshes[index] = bytes(row)
    # Wrath hides group 5 with a robe. Its missing group 13 must retain the same calf surface.
    boot = next(i for i, mesh in enumerate(skin.submeshes) if e.v.u16(mesh, 0) == 501)
    row = bytearray(skin.submeshes[boot])
    e.v.patch16(row, 0, 1302)
    robe = len(skin.submeshes)
    skin.submeshes.append(bytes(row))
    for original in list(skin.batches):
        if e.v.u16(original, 4) == boot:
            batch = bytearray(original)
            e.v.patch16(batch, 4, robe)
            e.v.patch16(batch, 6, robe)
            skin.batches.append(bytes(batch))
    return {'foot_vertices': model.vertex_count - before, 'original_foot_vertices': sorted(original_feet),
            'foot_triangles_before': len(feet), 'foot_triangles_after': len(refined), 'robe_calf_geoset': 1302}


def geometry_catalog(data, replacement):
    magic, version, count = struct.unpack_from('<3I', data)
    if (magic, version) != (0x4D474145, 1) or count > 64:
        raise ValueError('Unexpected native geometry catalog')
    at, changed, records = 12, 0, []
    for _ in range(count):
        key = data[at:at + 128].split(b'\0')[0].decode('ascii')
        length = struct.unpack_from('<I', data, at + 128)[0]
        end = at + 132 + length
        if end > len(data):
            raise ValueError('Truncated native geometry record')
        if key.lower() == MODEL.lower():
            records.append(data[at:at + 128] + struct.pack('<I', len(replacement)) + replacement)
            changed += 1
        else:
            records.append(data[at:end])
        at = end
    if at != len(data) or changed != 1:
        raise ValueError('Expected exactly one complete Tuskarr geometry record')
    return data[:12] + b''.join(records)


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    c.save(STAGE / 'build-report.json', {'status': 'preparing'})
    with c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
        original, original_skin = files.find(MODEL)[0], files.find(SKIN)[0]
    c.immutable(STAGE / 'before/Tuskarr.m2', original)
    c.immutable(STAGE / 'before/Tuskarr00.skin', original_skin)
    model, skin = parse_m2(original), parse_skin(original_skin)
    repair = repair_geometry(model, skin)
    skin = e.v.compact_bone_palettes(model, skin)
    (STAGE / 'Tuskarr.m2').write_bytes(write_md20(model))
    (STAGE / 'Tuskarr00.skin').write_bytes(write_skin(skin))
    updates = {MODEL: (STAGE / 'Tuskarr.m2').read_bytes(), SKIN: (STAGE / 'Tuskarr00.skin').read_bytes()}
    geometry = (c.p.CLIENT_DEFAULT / 'EsteriaAppearanceGeometry.bin').read_bytes()
    c.immutable(STAGE / 'before/EsteriaAppearanceGeometry.bin', geometry)
    (STAGE / 'EsteriaAppearanceGeometry.bin').write_bytes(geometry_catalog(geometry, updates[SKIN]))
    report = {'status': 'staged', 'repair': repair, 'source_hashes': {}, 'stage_hashes': {},
              'entries': {key: hashlib.sha256(data).hexdigest() for key, data in updates.items()},
              'runtime_hashes': {name: c.p.sha256(c.p.CLIENT_DEFAULT / name) for name in (
                  'Wow.exe', 'EsteriaAppearance.dll', 'EsteriaAppearance.bin', 'EsteriaAppearanceMaterials.bin',
                  'EsteriaTuskarr.bin', 'EsteriaTuskarrTextures.bin')}}
    selections = (c.p.CLIENT_DEFAULT / 'EsteriaTuskarr.bin').read_bytes()
    assert not any(struct.unpack_from('<3I', selections, 12 + i * 156)[1:] == (0, 13)
                   for i in range(struct.unpack_from('<I', selections, 8)[0]))
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
    return {'status': 'staged', 'added_foot_vertices': repair['foot_vertices'], 'robe_calf_geoset': 1302}


def check():
    before = parse_m2((STAGE / 'before/Tuskarr.m2').read_bytes())
    before_skin = parse_skin((STAGE / 'before/Tuskarr00.skin').read_bytes())
    after = parse_m2((STAGE / 'Tuskarr.m2').read_bytes())
    skin = parse_skin((STAGE / 'Tuskarr00.skin').read_bytes())
    report = c.p.load_json(STAGE / 'build-report.json')
    foot_vertices = set(report['repair']['original_foot_vertices'])
    assert after.vertex_count == before.vertex_count + report['repair']['foot_vertices']
    assert all(before.vertices[i * 48:(i + 1) * 48] == after.vertices[i * 48:(i + 1) * 48]
               for i in range(before.vertex_count) if i not in foot_vertices)
    expected = copy.deepcopy(before)
    expected.vertices, expected.vertex_count, expected.bone_combos = (
        after.vertices, after.vertex_count, after.bone_combos)
    assert write_md20(expected) == write_md20(after), 'Non-foot model data changed'

    def surface(model, profile, geoset, exclude_feet=False):
        return Counter(tuple(model.vertices[i * 48:(i + 1) * 48] for i in face)
                       for mesh in profile.submeshes if e.v.u16(mesh, 0) == geoset
                       for face in triangles(profile, mesh) if not exclude_feet or not set(face) <= foot_vertices)

    for geoset in {e.v.u16(mesh, 0) for mesh in before_skin.submeshes}:
        old = surface(before, before_skin, geoset, geoset == 10000)
        new = surface(after, skin, geoset)
        if geoset == 10000:
            new = Counter(tuple(after.vertices[i * 48:(i + 1) * 48] for i in face)
                          for mesh in skin.submeshes if e.v.u16(mesh, 0) == geoset
                          for face in triangles(skin, mesh)
                          if max(position(after.vertices, i)[2] for i in face) >= 0.17)
        assert new == old, geoset
    assert surface(after, skin, 1302) == surface(after, skin, 501)
    assert len(skin.vertices) <= 65535 and skin.bone_count_max <= 75
    assert all(e.v.u16(mesh, 2) == 0 and e.v.u16(mesh, 12) <= 75 for mesh in skin.submeshes)
    for mesh in skin.submeshes:
        start = e.v.u16(mesh, 4)
        palette = e.v.u16(mesh, 14)
        for lookup in range(start, start + e.v.u16(mesh, 6)):
            index = skin.vertices[lookup]
            assert index < after.vertex_count
            vertex = after.vertices[index * 48:(index + 1) * 48]
            assert sum(vertex[12:16]) == 255
            for slot in range(4):
                if vertex[12 + slot]:
                    assert after.bone_combos[palette + skin.bones[lookup * 4 + slot]] == vertex[16 + slot]
    refined = [face for mesh in skin.submeshes if e.v.u16(mesh, 0) == 10000
               for face in triangles(skin, mesh) if max(position(after.vertices, i)[2] for i in face) < 0.17]
    assert len(refined) == 16 * report['repair']['foot_triangles_before']
    assert any(position(before.vertices, i) != position(after.vertices, i) for i in foot_vertices)
    for index in {i for face in refined for i in face}:
        normal = struct.unpack_from('<3f', after.vertices, index * 48 + 20)
        assert abs(sum(value * value for value in normal) - 1) < 1e-5
    def catalog_records(data):
        at, records = 12, {}
        for _ in range(struct.unpack_from('<I', data, 8)[0]):
            key = data[at:at + 128].split(b'\0')[0].decode('ascii')
            length = struct.unpack_from('<I', data, at + 128)[0]
            assert key not in records
            records[key] = data[at + 132:at + 132 + length]
            at += 132 + length
        assert at == len(data)
        return records

    old_catalog = catalog_records((STAGE / 'before/EsteriaAppearanceGeometry.bin').read_bytes())
    new_catalog = catalog_records((STAGE / 'EsteriaAppearanceGeometry.bin').read_bytes())
    assert old_catalog.keys() == new_catalog.keys()
    assert all(old_catalog[key] == new_catalog[key] for key in old_catalog if key.lower() != MODEL.lower())
    assert new_catalog[MODEL] == (STAGE / 'Tuskarr00.skin').read_bytes()
    for name, digest in report['stage_hashes'].items():
        path = STAGE / 'pack' / name if name in map(str, RELATIVES) else STAGE / name
        assert c.p.sha256(path) == digest, name
    print('PASS: Rounded, weighted feet; calves retained with a robe; original non-foot surfaces, '
          'rig, animations, UVs, materials and other geometry catalog records preserved.', flush=True)


def require_closed_client():
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(name in processes for name in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Close WoW/Eclipse/MPQEditor before installing the checked repair')


def install():
    require_closed_client()
    check()
    report = c.p.load_json(STAGE / 'build-report.json')
    if report['status'] != 'staged':
        raise ValueError('Repair staging did not finish')
    for name, digest in report['runtime_hashes'].items():
        if c.p.sha256(c.p.CLIENT_DEFAULT / name) != digest:
            raise ValueError('Client runtime changed since staging: ' + name)
    files = {str(relative): STAGE / 'pack' / relative for relative in RELATIVES}
    files['EsteriaAppearanceGeometry.bin'] = STAGE / 'EsteriaAppearanceGeometry.bin'
    backup = Path(r'G:\EsteriaBackups') / ('tuskarr-equipment-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    for name in files:
        live = c.p.CLIENT_DEFAULT / name
        if c.p.sha256(live) != report['source_hashes'][name]:
            raise ValueError('Client file changed since staging: ' + name)
        destination = backup / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, destination)
        if c.p.sha256(destination) != report['source_hashes'][name]:
            raise ValueError('Backup hash differs: ' + name)
    art = ROOT / 'integration/patch-root'
    for key in (MODEL, SKIN):
        live = art.joinpath(*PureWindowsPath(key).parts)
        destination = backup / 'integration' / PureWindowsPath(key).name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, destination)
        if c.p.sha256(destination) != c.p.sha256(live):
            raise ValueError('Integration backup hash differs')
    shutil.copy2(ROOT / 'integration/rendering.json', backup / 'rendering.json')
    if c.p.sha256(backup / 'rendering.json') != c.p.sha256(ROOT / 'integration/rendering.json'):
        raise ValueError('Rendering report backup hash differs')
    require_closed_client()
    for name, digest in report['source_hashes'].items():
        if c.p.sha256(c.p.CLIENT_DEFAULT / name) != digest:
            raise ValueError('Client file changed during backup: ' + name)
    try:
        for name, source in files.items():
            destination = c.p.CLIENT_DEFAULT / name
            temporary = destination.with_suffix(destination.suffix + '.tuskarr-next')
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
        for key, source in ((MODEL, STAGE / 'Tuskarr.m2'), (SKIN, STAGE / 'Tuskarr00.skin')):
            shutil.copy2(source, art.joinpath(*PureWindowsPath(key).parts))
        rendering = c.p.load_json(ROOT / 'integration/rendering.json')
        model = parse_m2((STAGE / 'Tuskarr.m2').read_bytes())
        skin = parse_skin((STAGE / 'Tuskarr00.skin').read_bytes())
        rendering['models']['0'].update(vertices=model.vertex_count, skin_vertices=len(skin.vertices),
            geosets=sorted({e.v.u16(row, 0) for row in skin.submeshes}), equipment_repair=report['repair'])
        c.save(ROOT / 'integration/rendering.json', rendering)
    except Exception:
        for name in files:
            shutil.copy2(backup / name, c.p.CLIENT_DEFAULT / name)
        for key in (MODEL, SKIN):
            shutil.copy2(backup / 'integration' / PureWindowsPath(key).name,
                         art.joinpath(*PureWindowsPath(key).parts))
        shutil.copy2(backup / 'rendering.json', ROOT / 'integration/rendering.json')
        raise
    report.update(status='installed', backup=str(backup), live_client='unverified',
                  installed_hashes={name: c.p.sha256(c.p.CLIENT_DEFAULT / name) for name in files})
    c.save(STAGE / 'last-install.json', report)
    c.save(backup / 'install-report.json', report)
    return {'status': 'installed', 'backup': str(backup), 'live_client': 'unverified'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'check', 'install'))
    args = parser.parse_args()
    print(json.dumps({'prepare': prepare, 'check': check, 'install': install}[args.command](), indent=2))
