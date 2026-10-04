import collections
import json
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import retroported_race_pack as p
from wotlkconv.m2 import parse_m2, parse_skin

dtype = np.dtype({'names': ['pos', 'norm', 'uv'], 'formats': [('f4', 3), ('f4', 3), ('f4', 2)],
                  'offsets': [0, 20, 32], 'itemsize': 48})
with p.ClientFiles(str(p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
    for sex in ('male', 'female'):
        manifest = p.load_manifest('maghar')
        name = manifest['models'][sex]['runtime_model_path']
        dst = parse_m2(files.find(name)[0])
        skin = parse_skin(files.find(name[:-3] + '00.skin')[0])
        source_path = p._patch_root_path(Path(manifest['source_patch_root']), manifest['models'][sex]['model_path'])
        src = parse_m2(source_path.read_bytes())
        sv = np.frombuffer(src.vertices, dtype=dtype)
        dv = np.frombuffer(dst.vertices, dtype=dtype)
        lookup = collections.defaultdict(list)
        for i, vertex in enumerate(sv):
            lookup[tuple(round(float(x), 4) for x in vertex['pos'])].append(i)
        head = set()
        for i, submesh in enumerate(skin.submeshes):
            geoset, _, start, count = struct.unpack_from('<4H', submesh)
            batches = [b for b in skin.batches if struct.unpack_from('<H', b, 4)[0] == i]
            if geoset == 0 and any(dst.textures[dst.texture_combos[struct.unpack_from('<H', b, 16)[0]]]['type'] == 1
                                   for b in batches):
                head.update(j for j in skin.vertices[start:start + count] if dv[j]['uv'][1] >= .625)
        matches = []
        for j in head:
            vertex = dv[j]
            for k in lookup[tuple(round(float(x), 4) for x in vertex['pos'])]:
                if sv[k]['uv'][0] >= .5 and np.linalg.norm(sv[k]['norm'] - vertex['norm']) < .05:
                    matches.append((j, k))
        a = np.array([dv[j]['uv'] for j, k in matches])
        b = np.array([[(float(sv[k]['uv'][0]) - .5) * 2, float(sv[k]['uv'][1])] for j, k in matches])
        matrix = np.column_stack((a, np.ones(len(a))))
        rng = np.random.default_rng(0)
        best = None
        count = 0
        for _ in range(800):
            ids = rng.choice(len(matrix), 3, replace=False)
            if abs(np.linalg.det(matrix[ids])) < 1e-6:
                continue
            affine = np.linalg.solve(matrix[ids], b[ids])
            keep = np.linalg.norm(matrix @ affine - b, axis=1) < .0003
            if int(sum(keep)) > count:
                count = int(sum(keep))
                best = keep
        affine = np.linalg.lstsq(matrix[best], b[best], rcond=None)[0]
        result = {'sex': sex, 'pairs': len(matches), 'consensus': count,
                  'vertices_in_consensus': len({matches[i][0] for i in np.where(best)[0]}),
                  'head_vertices': len(head), 'affine': affine.tolist()}
        print(json.dumps(result), flush=True)
        (Path(__file__).parent / (sex + '-uv-report.json')).write_text(json.dumps(result, indent=2))
