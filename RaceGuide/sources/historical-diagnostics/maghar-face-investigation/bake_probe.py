import collections
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import retroported_race_pack as p
from wotlkconv.m2 import parse_m2, parse_skin


def key(model, index):
    return tuple(round(x, 4) for x in struct.unpack_from('<3f', model.vertices, index * 48))


def triangles(skin, submesh):
    _, level, _, _, start, count = struct.unpack_from('<6H', submesh)
    start += level << 16
    return [tuple(skin.vertices[j] for j in skin.indices[i:i + 3]) for i in range(start, start + count, 3)]


def uv(model, index):
    return np.array(struct.unpack_from('<2f', model.vertices, index * 48 + 32))


with p.ClientFiles(str(p.CLIENT_DEFAULT / 'Data'), 'enUS') as files:
    for sex, stem in (('male', 'orcmale'), ('female', 'orcfemale')):
        manifest = p.load_manifest('maghar')
        name = manifest['models'][sex]['runtime_model_path']
        dst = parse_m2(files.find(name)[0])
        ds = parse_skin(files.find(name[:-3] + '00.skin')[0])
        path = p._patch_root_path(Path(manifest['source_patch_root']), manifest['models'][sex]['model_path'])
        src = parse_m2(path.read_bytes())
        ss = parse_skin(path.with_name(path.stem + '00.skin').read_bytes())
        source_triangles = {}
        source_vertices = collections.defaultdict(list)
        for sm in ss.submeshes:
            if struct.unpack_from('<H', sm)[0] != 3202:
                continue
            for triangle in triangles(ss, sm):
                source_triangles[tuple(sorted(key(src, i) for i in triangle))] = triangle
                for i in triangle:
                    source_vertices[key(src, i)].append(i)
        coords = np.full((192, 256, 2), np.nan)
        matched = missing = fallback = painted = 0
        distances = []
        for i, sm in enumerate(ds.submeshes):
            batches = [b for b in ds.batches if struct.unpack_from('<H', b, 4)[0] == i]
            if struct.unpack_from('<H', sm)[0] != 0 or not any(
                dst.textures[dst.texture_combos[struct.unpack_from('<H', b, 16)[0]]]['type'] == 1
                for b in batches
            ):
                continue
            for triangle in triangles(ds, sm):
                target_uv = np.array([uv(dst, j) for j in triangle])
                if target_uv[:, 1].min() < .625:
                    continue
                source_triangle = source_triangles.get(tuple(sorted(key(dst, j) for j in triangle)))
                if source_triangle:
                    matched += 1
                    mapped = [next(k for k in source_triangle if key(src, k) == key(dst, j)) for j in triangle]
                else:
                    missing += 1
                    mapped = []
                    for j in triangle:
                        candidates = source_vertices.get(key(dst, j), [])
                        if not candidates:
                            position = np.array(struct.unpack_from('<3f', dst.vertices, j * 48))
                            nearest = min(source_vertices, key=lambda point: np.linalg.norm(np.array(point) - position))
                            distances.append(float(np.linalg.norm(np.array(nearest) - position)))
                            candidates = source_vertices[nearest]
                            fallback += 1
                        normal = np.array(struct.unpack_from('<3f', dst.vertices, j * 48 + 20))
                        mapped.append(min(candidates, key=lambda k: np.linalg.norm(
                            np.array(struct.unpack_from('<3f', src.vertices, k * 48 + 20)) - normal)))
                source_uv = np.array([[(uv(src, j)[0] - .5) * 2, uv(src, j)[1]] for j in mapped])
                target_uv = target_uv * 512 - np.array([0, 320])
                transform = np.column_stack((target_uv, np.ones(3)))
                if abs(np.linalg.det(transform)) < 1e-8:
                    continue
                x0 = max(0, math.floor(target_uv[:, 0].min()))
                x1 = min(256, math.ceil(target_uv[:, 0].max()))
                y0 = max(0, math.floor(target_uv[:, 1].min()))
                y1 = min(192, math.ceil(target_uv[:, 1].max()))
                yy, xx = np.mgrid[y0:y1, x0:x1]
                points = np.stack((xx + .5, yy + .5, np.ones_like(xx)), axis=-1)
                weights = points @ np.linalg.inv(transform)
                inside = (weights >= -1e-6).all(axis=-1)
                coords[y0:y1, x0:x1][inside] = (weights @ source_uv)[inside]
                painted += int(inside.sum())
        valid = np.isfinite(coords).all(axis=-1)
        blp_path = path.parent / (stem + 'clanfaceupper00_00.blp')
        img = p.Blp.parse(blp_path.read_bytes()).decode_level(0)
        pixels = np.frombuffer(img.data, dtype=np.uint8).reshape(img.height, img.width, 4)
        target = np.zeros((192, 256, 4), dtype=np.uint8)
        samples = np.clip((coords[valid] * [img.width, img.height]).astype(int), 0, 511)
        target[valid] = pixels[samples[:, 1], samples[:, 0]]
        p.Image.fromarray(target).resize((512, 384)).save(Path(__file__).parent / (sex + '-baked-face-probe.png'))
        np.save(Path(__file__).parent / (sex + '-uv-map.npy'), coords)
        print(json.dumps({'sex': sex, 'triangles_matched': matched, 'triangles_unmatched': missing,
                          'fallback_vertices': fallback, 'max_distance': max(distances, default=0),
                          'covered_pixels': int(valid.sum()), 'painted': painted}), flush=True)
