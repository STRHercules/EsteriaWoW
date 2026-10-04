"""Rasterise which texels the Vulpera forearm / upper arm actually sample.

Reads the live model out of Patch-C, labels triangles by the key bones of their
vertices (ArmL/R = forearm, ShoulderL/R = upper arm), rasterises their UVs into
the body texture space, and writes a couple of overlay images for inspection.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

MODEL_STRIDE = 48


def load(storm: Storm, archive: Path, wanted: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return storm.read(handle, names[wanted.casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)


def decode_blp(data: bytes) -> Image.Image:
    width, height = struct.unpack_from("<II", data, 12)
    mip_offsets = struct.unpack_from("<16I", data, 20)
    palette = data[148:148 + 1024]
    pal = []
    for i in range(256):
        b, g, r, a = palette[i * 4:i * 4 + 4]
        pal.extend((r, g, b))
    image = Image.frombytes("P", (width, height), data[mip_offsets[0]:mip_offsets[0] + width * height])
    image.putpalette(pal)
    return image.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default=r"character\vulpera\male\vulperamale.m2")
    parser.add_argument("--skin", default=r"character\vulpera\male\vulperamale00.skin")
    parser.add_argument("--texture", default=r"character\vulpera\male\vulperamaleskin00_00.blp")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    storm = Storm(DLL_DEFAULT)
    m2 = load(storm, args.patch_c, args.model)
    skin = load(storm, args.patch_c, args.skin)
    texture = decode_blp(load(storm, args.patch_c, args.texture))
    width, height = texture.size

    vcount, voff = struct.unpack_from("<II", m2, 0x3C)
    kcount, koff = struct.unpack_from("<II", m2, 0x34)
    keybones = struct.unpack_from(f"<{kcount}H", m2, koff)
    forearm_bones = {keybones[0], keybones[1]}
    upper_bones = {keybones[2], keybones[3]}

    def vertex(i: int):
        o = voff + i * MODEL_STRIDE
        pos = struct.unpack_from("<3f", m2, o)
        bones = m2[o + 16:o + 20]
        weights = m2[o + 12:o + 16]
        uv = struct.unpack_from("<2f", m2, o + 32)
        return pos, bones, weights, uv

    def dominant(i: int) -> int:
        _, bones, weights, _ = vertex(i)
        best, best_w = -1, 0
        for b, w in zip(bones, weights):
            if w > best_w:
                best, best_w = b, w
        return best

    nIndices, ofsIndices, numTri, ofsTri, numBones, ofsBones, nsub, ofsSub, nbatch, ofsBatch = struct.unpack_from("<10I", skin, 4)
    global_of_local = struct.unpack_from(f"<{nIndices}H", skin, ofsIndices)
    triangles = struct.unpack_from(f"<{numTri}H", skin, ofsTri)

    masks = {"forearm": Image.new("1", (width, height), 0), "upperArm": Image.new("1", (width, height), 0)}
    drawers = {name: ImageDraw.Draw(mask) for name, mask in masks.items()}
    counts = {name: 0 for name in masks}
    for t in range(0, numTri, 3):
        tri = [global_of_local[triangles[t + k]] for k in range(3)]
        labels = {"forearm": 0, "upperArm": 0}
        for vi in tri:
            bone = dominant(vi)
            if bone in forearm_bones:
                labels["forearm"] += 1
            elif bone in upper_bones:
                labels["upperArm"] += 1
        uvs = [vertex(vi)[3] for vi in tri]
        points = [(u * width, (1.0 - v) * height) for u, v in uvs]
        for name, hits in labels.items():
            if hits >= 2:
                drawers[name].polygon(points, fill=1)
                counts[name] += 1

    for name, mask in masks.items():
        overlay = texture.copy()
        tint = Image.new("RGB", overlay.size, (255, 0, 0) if name == "forearm" else (0, 128, 255))
        overlay = Image.composite(Image.blend(overlay, tint, 0.55), overlay, mask)
        overlay.save(args.out / f"uv_{name}.png")
        mask.save(args.out / f"uv_{name}_mask.png")
        print(f"{name}: triangles={counts[name]} texels={sum(mask.point(lambda p: 1 if p else 0).getdata())}")
    texture.save(args.out / "vulpera_texture.png")
    print(f"images written to {args.out}")


if __name__ == "__main__":
    main()
