"""Report which bones each geoset is skinned to, with bone bind positions.

Ear meshes hang off dedicated ear bones, so this is what identifies them
without guessing from bounding boxes.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))

from inspect_client_races import Client  # noqa: E402

STRIDES = (88, 84, 80, 92, 96, 104, 108)


def bone_table(model: bytes, stride: int):
    count, offset = struct.unpack_from("<II", model, 0x2C)
    bones = []
    for index in range(count):
        base = offset + index * stride
        key, flags = struct.unpack_from("<II", model, base)
        parent, submesh = struct.unpack_from("<hH", model, base + 8)
        pivot = struct.unpack_from("<3f", model, base + stride - 12)
        bones.append((key, parent, submesh, pivot))
    return bones


def world_pivots(bones):
    positions = []
    for index, (_key, parent, _submesh, pivot) in enumerate(bones):
        x, y, z = pivot
        seen = set()
        current = parent
        while 0 <= current < len(bones) and current not in seen:
            seen.add(current)
            px, py, pz = bones[current][3]
            if abs(px) < 50 and abs(py) < 50 and abs(pz) < 50:
                x += px
                y += py
                z += pz
            current = bones[current][1]
        positions.append((x, y, z))
    return positions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--lod", type=int, default=0)
    parser.add_argument("--lateral", type=float, default=0.08)
    args = parser.parse_args()
    client = Client()
    stem = args.model[:-4] if args.model.lower().endswith((".m2", ".mdx")) else args.model
    model = client.find(stem + ".m2") or client.find(stem + ".mdx")
    skin = client.find(f"{stem}0{args.lod}.skin")
    if model is None or skin is None:
        raise SystemExit("model or skin missing")

    count, offset = struct.unpack_from("<II", model, 0x2C)
    stride = None
    best = -1
    for candidate in STRIDES:
        if offset + count * candidate >= len(model):
            continue
        sane = 0
        for index in range(min(count, 60)):
            base = offset + index * candidate
            key, flags = struct.unpack_from("<Ii", model, base)
            parent, submesh = struct.unpack_from("<hH", model, base + 8)
            if -1 <= parent < count and 0 <= submesh <= 40 and 0 <= flags < 0x10000:
                sane += 1
        print(f"stride {candidate}: sane records {sane}/{min(count, 60)}")
        if sane > best:
            best, stride = sane, candidate
    if stride is None:
        raise SystemExit("no usable bone stride")
    bones = bone_table(model, stride)
    positions = world_pivots(bones)
    print(f"using stride {stride}, {len(bones)} bones")
    head = [i for i, p in enumerate(positions) if p[2] > 1.5]
    lateral = [i for i in head if abs(positions[i][1]) > args.lateral]
    print(f"head bones: {len(head)}, lateral head bones (|y|>{args.lateral}): {lateral}")
    for index in lateral:
        x, y, z = positions[index]
        print(f"   bone {index:>3}: pivot=({x:6.3f},{y:6.3f},{z:6.3f}) parent={bones[index][1]}")

    vertex_count, vertex_offset = struct.unpack_from("<II", model, 0x3C)
    indices = []
    for index in range(vertex_count):
        base = vertex_offset + index * 48 + 12
        weights = model[base : base + 4]
        bones4 = model[base + 4 : base + 8]
        indices.append((weights, bones4))

    vals = struct.unpack_from("<10I", skin, 4)
    n_sub, ofs_sub = vals[6], vals[7]
    per_geoset: dict[int, dict[int, int]] = {}
    for sub in range(n_sub):
        offset = ofs_sub + sub * 48
        gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", skin, offset)
        bucket = per_geoset.setdefault(gid, {})
        for vertex in range(v_start, min(v_start + v_count, vertex_count)):
            weights, used = indices[vertex]
            for slot in range(4):
                if weights[slot]:
                    bucket[used[slot]] = bucket.get(used[slot], 0) + weights[slot]
    print("geoset -> dominant bones (weight, bone, world pivot)")
    for gid in sorted(per_geoset):
        top = sorted(per_geoset[gid].items(), key=lambda item: -item[1])[:3]
        detail = []
        for bone, weight in top:
            position = positions[bone] if bone < len(positions) else (float("nan"),) * 3
            detail.append(f"b{bone}(w{weight})@({position[0]:.2f},{position[1]:.2f},{position[2]:.2f})")
        print(f"  {gid:>5}: " + " ".join(detail))


if __name__ == "__main__":
    main()
