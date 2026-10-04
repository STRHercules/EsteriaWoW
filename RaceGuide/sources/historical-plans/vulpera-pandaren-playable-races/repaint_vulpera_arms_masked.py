"""Repaint only the Vulpera arm islands, located from the model geometry.

Arm vertices are picked by position (well outside the torso in X, above the
hips, below the neck) instead of bone tables, their UV triangles are rasterised
into a mask, and the dark warm band inside that mask gets a gentle gamma lift so
the fur reads as one piece while shading survives.
"""

from __future__ import annotations

import argparse
import colorsys
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(HERE))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from repaint_vulpera_arms import decode, encode  # noqa: E402

X_MIN = 0.13
Z_MIN, Z_MAX = 0.40, 1.08
GAMMA = 0.62


def read(storm: Storm, archive: Path, wanted: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return storm.read(handle, names[wanted.casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)


def arm_mask(m2: bytes, skin: bytes, width: int, height: int) -> Image.Image:
    vcount, voff = struct.unpack_from("<II", m2, 0x3C)
    nIdx, ofsIdx, numTri, ofsTri, *_ = struct.unpack_from("<10I", skin, 4)
    local_to_global = struct.unpack_from(f"<{nIdx}H", skin, ofsIdx)
    indices = struct.unpack_from(f"<{numTri}H", skin, ofsTri)

    def vertex(i: int):
        o = voff + i * 48
        return struct.unpack_from("<3f", m2, o), struct.unpack_from("<2f", m2, o + 32)

    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    used = 0
    for t in range(0, numTri, 3):
        tri = [local_to_global[indices[t + k]] for k in range(3)]
        info = [vertex(i) for i in tri]
        if not all(abs(pos[0]) > X_MIN and Z_MIN < pos[2] < Z_MAX for pos, _ in info):
            continue
        points = [(uv[0] * width, (1.0 - uv[1]) * height) for _, uv in info]
        draw.polygon(points, fill=255)
        used += 1
    print(f"   arm triangles rasterised: {used}")
    return mask.filter(ImageFilter.GaussianBlur(1.2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--dump-mask", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    storm = Storm(DLL_DEFAULT)
    mask_m = arm_mask(
        read(storm, args.patch_c, r"character\vulpera\male\vulperamale.m2"),
        read(storm, args.patch_c, r"character\vulpera\male\vulperamale00.skin"),
        512, 512,
    )
    mask_f = arm_mask(
        read(storm, args.patch_c, r"character\vulpera\female\vulperafemale.m2"),
        read(storm, args.patch_c, r"character\vulpera\female\vulperafemale00.skin"),
        512, 512,
    )
    if args.dump_mask:
        side = Image.new("L", (1024, 512), 0)
        side.paste(mask_m, (0, 0))
        side.paste(mask_f, (512, 0))
        side.point(lambda p: 255 if p > 40 else 0).save(args.dump_mask)

    handle = storm.open_archive(args.patch_c)
    try:
        entries = [name for name, *_ in storm.list_files(handle)]
        targets = sorted(
            name for name in entries
            if name.casefold().startswith("character\\vulpera\\")
            and name.rsplit("\\", 1)[-1].casefold().startswith(("vulperamaleskin", "vulperafemaleskin"))
        )
        updates = {}
        changed_total = 0
        for name in targets:
            data = storm.read(handle, name)
            indices, lookup, width, height, offsets, sizes, pal, template = decode(data)
            mask = mask_m if "male" in name.casefold() else mask_f
            weights = mask.load()
            cache: dict[tuple[int, int, int], int] = {}

            def nearest(rgb):
                key = (rgb[0] >> 3, rgb[1] >> 3, rgb[2] >> 3)
                hit = cache.get(key)
                if hit is None:
                    hit = min(range(256), key=lambda i: sum((lookup[i][k] - rgb[k]) ** 2 for k in range(3)))
                    cache[key] = hit
                return hit

            before = bytes(indices)
            for y in range(height):
                for x in range(width):
                    w = weights[x, y] / 255.0
                    if w < 0.25:
                        continue
                    pos = y * width + x
                    r, g, b = lookup[indices[pos]]
                    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                    if s < 0.20 or v > 0.72:
                        continue
                    v_new = v + ((v ** GAMMA) - v) * w
                    nr, ng, nb = colorsys.hsv_to_rgb(h, s, v_new)
                    new_index = nearest((int(nr * 255), int(ng * 255), int(nb * 255)))
                    if new_index != indices[pos]:
                        indices[pos] = new_index
                        changed_total += 1
            updates[name] = encode(indices, pal, template, width, height, offsets, sizes)
            if args.preview and name.casefold().endswith("vulperamaleskin00_00.blp"):
                def to_image(buf):
                    img = Image.frombytes("P", (width, height), bytes(buf))
                    img.putpalette(pal)
                    return img.convert("RGB")
                side = Image.new("RGB", (512, 512))
                side.paste(to_image(before), (0, 0))
                side.paste(to_image(indices), (256, 0))
                side.resize((1024, 1024), Image.NEAREST).save(args.preview)
        print(f"repainted {len(updates)} textures, {changed_total} pixels changed")
    finally:
        storm.dll.SFileCloseArchive(handle)

    staging = args.out / "staged"
    if staging.exists():
        import shutil
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
