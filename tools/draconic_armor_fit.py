"""Tighten only the male Drakkin/Drakonid garment shells; stage assets without installing."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
from wotlkconv.m2 import parse_m2, parse_skin


def shell_geoset(identity):
    return 20001 <= identity <= 20028


def repair(model_bytes, skin_bytes):
    model = parse_m2(model_bytes)
    skin = parse_skin(skin_bytes)
    count, vertices_offset = struct.unpack_from('<II', model_bytes, 60)
    material_count, materials_offset = struct.unpack_from('<II', model_bytes, 112)
    assert count == model.vertex_count and model_bytes[vertices_offset:vertices_offset + count * 48] == model.vertices
    assert material_count == len(model.materials)
    shells, body, materials = set(), set(), set()
    material_users = defaultdict(set)
    for index, row in enumerate(skin.submeshes):
        identity = struct.unpack_from('<H', row)[0]
        start, length = struct.unpack_from('<HH', row, 4)
        referenced = set(skin.vertices[start:start + length])
        if shell_geoset(identity):
            shells.update(referenced)
        elif identity in (0, 3501, 3502):
            body.update(referenced)
        for batch in skin.batches:
            if struct.unpack_from('<H', batch, 4)[0] != index:
                continue
            material = struct.unpack_from('<H', batch, 10)[0]
            texture = model.textures[model.texture_combos[struct.unpack_from('<H', batch, 16)[0]]]
            material_users[material].add((identity, texture['type']))
            if shell_geoset(identity):
                materials.add(material)
                assert texture['type'] == 14, 'Unexpected garment texture binding'
    assert shells and body and not shells.intersection(body)
    groups = defaultdict(list)
    for vertex in sorted(body):
        groups[model.vertices[vertex * 48 + 12:vertex * 48 + 20]].append(vertex)
    positions = np.array([struct.unpack_from('<3f', model.vertices, vertex * 48) for vertex in range(count)])
    output = bytearray(model_bytes)
    matches = []
    allowed = set()
    for vertex in sorted(shells):
        identity = model.vertices[vertex * 48 + 12:vertex * 48 + 20]
        candidates = groups.get(identity)
        assert candidates, 'No matching body skinning weights'
        squared = np.sum((positions[candidates] - positions[vertex]) ** 2, axis=1)
        parent = candidates[int(np.argmin(squared))]
        distance = float(np.linalg.norm(positions[vertex] - positions[parent]))
        assert 0.0001 < distance < 0.04, 'Unexpected existing shell clearance'
        fitted = positions[parent] + (positions[vertex] - positions[parent]) * 0.25
        offset = vertices_offset + vertex * 48
        struct.pack_into('<3f', output, offset, *fitted)
        allowed.update(range(offset, offset + 12))
        matches.append((vertex, parent))
    for material in sorted(materials):
        assert all(identity != 0 and texture == 14 for identity, texture in material_users[material]), \
            'Material shared with anatomy or a different texture'
        assert model.materials[material] == {'flags': 16, 'blending_mode': 2}
        offset = materials_offset + material * 4
        # Solid clothing needs cutout coverage and depth writes, rather than a blended body silhouette.
        struct.pack_into('<HH', output, offset, 0, 1)
        allowed.update(range(offset, offset + 4))
    changed = {index for index, (before, after) in enumerate(zip(model_bytes, output)) if before != after}
    assert len(output) == len(model_bytes) and changed and changed.issubset(allowed)
    after = parse_m2(bytes(output))
    for vertex in range(count):
        offset = vertex * 48
        if vertex in shells:
            assert model.vertices[offset + 12:offset + 48] == after.vertices[offset + 12:offset + 48]
        else:
            assert model.vertices[offset:offset + 48] == after.vertices[offset:offset + 48]
    assert model.sequences == after.sequences and model.key_bone_lookup == after.key_bone_lookup
    return bytes(output), {'shell_vertices': len(shells), 'changed_materials': sorted(materials),
                           'clearance_factor': 0.25, 'only_positions_and_owned_materials_changed': True,
                           'skinning_uvs_normals_anatomy_preserved': True, 'matches': matches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads((args.work / 'baseline.json').read_text())['files']
    reports = {}
    for name in ('drakkin', 'drakonid'):
        model = (args.work / (name + '.m2.before')).read_bytes()
        skin = (args.work / (name + '.skin.before')).read_bytes()
        assert hashlib.sha256(model).hexdigest() == baseline[name + '.m2']['sha256']
        assert hashlib.sha256(skin).hexdigest() == baseline[name + '.skin']['sha256']
        output, report = repair(model, skin)
        relative = Path(*baseline[name + '.m2']['entry'].split('\\'))
        destination = args.work / 'stage' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(output)
        report['sha256'] = hashlib.sha256(output).hexdigest()
        reports[name] = report
        print(name, {key: value for key, value in report.items() if key != 'matches'})
    (args.work / 'fit-validation.json').write_text(json.dumps(reports, indent=2) + '\n')


if __name__ == '__main__':
    main()
