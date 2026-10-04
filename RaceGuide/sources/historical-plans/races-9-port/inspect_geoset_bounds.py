"""Per-geoset bounding boxes for a client model, to locate ear/head meshes."""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))

from inspect_client_races import Client  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--lod", type=int, default=0)
    args = parser.parse_args()
    client = Client()
    stem = args.model[:-4] if args.model.lower().endswith((".m2", ".mdx")) else args.model
    model = client.find(stem + ".m2") or client.find(stem + ".mdx")
    skin = client.find(f"{stem}0{args.lod}.skin")
    if model is None or skin is None:
        raise SystemExit("model or skin missing")
    version = struct.unpack_from("<I", model, 4)[0]
    vertex_count, vertex_offset = struct.unpack_from("<II", model, 0x3C)
    stride = 48
    print(f"version={version} vertices={vertex_count} offset=0x{vertex_offset:x} stride={stride}")
    positions = [
        struct.unpack_from("<3f", model, vertex_offset + index * stride) for index in range(vertex_count)
    ]
    vals = struct.unpack_from("<10I", skin, 4)
    n_sub, ofs_sub = vals[6], vals[7]
    boxes: dict[int, list[float]] = {}
    for sub in range(n_sub):
        o = ofs_sub + sub * 48
        gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", skin, o)
        if not v_count or v_start + v_count > vertex_count:
            continue
        box = boxes.setdefault(gid, [1e9, -1e9, 1e9, -1e9, 1e9, -1e9, 0, 0])
        for index in range(v_start, v_start + v_count):
            x, y, z = positions[index]
            box[0] = min(box[0], x)
            box[1] = max(box[1], x)
            box[2] = min(box[2], y)
            box[3] = max(box[3], y)
            box[4] = min(box[4], z)
            box[5] = max(box[5], z)
        box[6] += i_count // 3
        box[7] += 1
    for gid in sorted(boxes):
        x0, x1, y0, y1, z0, z1, tris, subs = boxes[gid]
        print(
            f"geoset {gid:>5}: submeshes={subs:>2} tris={tris:>5} "
            f"x=[{x0:8.3f},{x1:8.3f}] y=[{y0:8.3f},{y1:8.3f}] z=[{z0:8.3f},{z1:8.3f}]"
        )


if __name__ == "__main__":
    main()
