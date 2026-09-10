# -*- coding: utf-8 -*-
"""Build independent cardboard models: one M2 + skin per sprite BLP.

Writes loose files only. Does not pack MPQs.

    python tools/build_plane.py

Default dest:
    <Chromie>/Data/patch-W.mpq/Creature/Battlemon/
"""

from __future__ import annotations

import argparse
import math
import os
import shutil
import struct
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WOTLK = 264
HEADER_SIZE = 0x130  # MD20 v264 without texture-combiner-combos
SIZE = 256
PLANE_HALF_W = 0.6
PLANE_H = 1.2
# Tight card. Painting05's 2.86-yard canvas put nameplates in the trees;
# the sprite only fills the middle of that quad.
CARD_HALF_W = 0.7
CARD_H = 1.35
# Nameplates follow this box, not the letterboxed art. Sit it just above
# a typical sprite so Scale 1.5 grows the card without sending names up.
NAMEPLATE_H = 1.05
UV_INSET = 0.5 / SIZE

DEFAULT_PNG = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Interface\AddOns\Battlemon\assets\Front\0025_Pikachu.png"
)
FRONT_DIR = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Interface\AddOns\Battlemon\assets\Front"
)
FRONT_SHINY_DIR = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Interface\AddOns\Battlemon\assets\Front shiny"
)
DEFAULT_PATCH_W = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Data\patch-W.mpq\Creature\Battlemon"
)
DEFAULT_PATCH_Z = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Data\patch-z.mpq\Creature\Battlemon"
)
MODULE_CLIENT = Path(__file__).resolve().parents[1] / "client" / "Creature" / "Battlemon"


def u32(n: int) -> bytes:
    return struct.pack("<I", n & 0xFFFFFFFF)


def i32(n: int) -> bytes:
    return struct.pack("<i", n)


def u16(n: int) -> bytes:
    return struct.pack("<H", n & 0xFFFF)


def i16(n: int) -> bytes:
    return struct.pack("<h", n)


def f32(n: float) -> bytes:
    return struct.pack("<f", n)


def vec3(x: float, y: float, z: float) -> bytes:
    return struct.pack("<fff", x, y, z)


def vec2(x: float, y: float) -> bytes:
    return struct.pack("<ff", x, y)


def aabox(mn: tuple[float, float, float], mx: tuple[float, float, float]) -> bytes:
    return vec3(*mn) + vec3(*mx)


class Blob:
    """Grow-only buffer. Header is reserved first; arrays live after it."""

    def __init__(self, header_size: int) -> None:
        self.buf = bytearray(header_size)

    def tell(self) -> int:
        return len(self.buf)

    def align(self, n: int = 4) -> None:
        pad = (-len(self.buf)) % n
        if pad:
            self.buf.extend(b"\0" * pad)

    def add(self, data: bytes, align: int = 4) -> int:
        self.align(align)
        off = len(self.buf)
        self.buf.extend(data)
        return off

    def poke_u32(self, off: int, val: int) -> None:
        self.buf[off : off + 4] = u32(val)

    def poke_array(self, field_off: int, count: int, data_off: int) -> None:
        self.buf[field_off : field_off + 8] = u32(count) + u32(data_off if count else 0)


def empty_track() -> bytes:
    # interpolation 0, global_sequence -1, timestamps {0,0}, values {0,0}
    return u16(0) + i16(-1) + u32(0) + u32(0) + u32(0) + u32(0)


def constant_uint16_track(blob: Blob, value: int) -> bytes:
    """One stand-sequence key at t=0."""
    ts_vals = blob.add(u32(0))
    ts_arr = blob.add(u32(1) + u32(ts_vals))
    val_vals = blob.add(u16(value))
    val_arr = blob.add(u32(1) + u32(val_vals))
    return u16(0) + i16(-1) + u32(1) + u32(ts_arr) + u32(1) + u32(val_arr)


def harden_alpha(im: Image.Image) -> Image.Image:
    """Binary alpha + bleed sprite color into the hole so DXT does not
    invent teal/white fringe in transparent blocks."""
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            pix[x, y] = (r, g, b, 0 if a < 16 else 255)
    for _ in range(2):
        nxt = im.copy()
        out = nxt.load()
        src = im.load()
        for y in range(h):
            for x in range(w):
                if src[x, y][3] != 0:
                    continue
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and src[xx, yy][3] == 255:
                        r, g, b, _ = src[xx, yy]
                        out[x, y] = (r, g, b, 0)
                        break
        im = nxt
    return im


def pad_sprite(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    x = (SIZE - im.width) // 2
    y = (SIZE - im.height) // 2
    canvas.paste(im, (x, y), im)
    return harden_alpha(canvas)


def _rgb565(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def _from565(c: int) -> tuple[int, int, int]:
    r = ((c >> 11) & 31) * 255 // 31
    g = ((c >> 5) & 63) * 255 // 63
    b = (c & 31) * 255 // 31
    return r, g, b


def _dxt1_color(pixels: list[tuple[int, int, int, int]]) -> bytes:
    opaque = [p for p in pixels if p[3] > 8] or pixels
    c0p = max(opaque, key=lambda p: p[0] + p[1] + p[2])
    c1p = min(opaque, key=lambda p: p[0] + p[1] + p[2])
    c0 = _rgb565(c0p[0], c0p[1], c0p[2])
    c1 = _rgb565(c1p[0], c1p[1], c1p[2])
    if c0 == c1:
        c0 = min(0xFFFF, c0 + 1)
    if c0 < c1:
        c0, c1 = c1, c0
    r0, g0, b0 = _from565(c0)
    r1, g1, b1 = _from565(c1)
    colors = [
        (r0, g0, b0),
        (r1, g1, b1),
        ((2 * r0 + r1) // 3, (2 * g0 + g1) // 3, (2 * b0 + b1) // 3),
        ((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3, (b0 + 2 * b1) // 3),
    ]
    idx = 0
    for i, p in enumerate(pixels):
        best = min(
            range(4),
            key=lambda k: (colors[k][0] - p[0]) ** 2
            + (colors[k][1] - p[1]) ** 2
            + (colors[k][2] - p[2]) ** 2,
        )
        idx |= best << (2 * i)
    return struct.pack("<HH", c0, c1) + idx.to_bytes(4, "little")


def _dxt3_block(pixels: list[tuple[int, int, int, int]]) -> bytes:
    """16 RGBA pixels -> 16-byte DXT3 block (explicit 4-bit alpha + DXT1 color)."""
    alpha = bytearray(8)
    for i, p in enumerate(pixels):
        a4 = p[3] >> 4
        if i % 2 == 0:
            alpha[i // 2] = a4
        else:
            alpha[i // 2] |= a4 << 4
    return bytes(alpha) + _dxt1_color(pixels)


def compress_dxt3(img: Image.Image) -> bytes:
    img = img.convert("RGBA")
    w, h = img.size
    pix = img.load()
    out = bytearray()
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            block = []
            for j in range(4):
                for i in range(4):
                    block.append(pix[min(x + i, w - 1), min(y + j, h - 1)])
            out.extend(_dxt3_block(block))
    return bytes(out)


def write_blp2(path: Path, img: Image.Image) -> None:
    """BLP2 DXT3 + palette. Same layout as this client's creature/alpha skins."""
    img = img.convert("RGBA")
    w, h = img.size
    if w != h or w & (w - 1) or w == 0:
        raise SystemExit(f"BLP needs square power-of-two, got {w}x{h}")

    mips: list[Image.Image] = []
    cur = img
    while True:
        mips.append(cur)
        if cur.size[0] <= 1:
            break
        nw = max(1, cur.size[0] // 2)
        nh = max(1, cur.size[1] // 2)
        cur = cur.resize((nw, nh), Image.Resampling.BOX)

    mip_bytes = [compress_dxt3(m) for m in mips]
    offsets = [0] * 16
    sizes = [0] * 16
    pos = 148 + 1024  # header + unused 256-color palette
    for i, data in enumerate(mip_bytes):
        offsets[i] = pos
        sizes[i] = len(data)
        pos += len(data)

    out = BytesIO()
    out.write(b"BLP2")
    out.write(u32(1))
    out.write(bytes((2, 8, 1, 1)))  # DXT, alpha 8, DXT3, hasMips
    out.write(u32(w) + u32(h))
    out.write(struct.pack("<16I", *offsets))
    out.write(struct.pack("<16I", *sizes))
    out.write(b"\0" * 1024)
    for data in mip_bytes:
        out.write(data)
    path.write_bytes(out.getvalue())


def fallback_image() -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    inset = 48
    d.rectangle((inset, inset, SIZE - inset - 1, SIZE - inset - 1), fill=(255, 204, 0, 255))
    d.rectangle((inset + 8, inset + 8, SIZE - inset - 9, SIZE - inset - 9), outline=(40, 24, 0, 255), width=6)
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except OSError:
        font = ImageFont.load_default()
    text = "?"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((SIZE - tw) / 2, (SIZE - th) / 2 - 12), text, fill=(40, 24, 0, 255), font=font)
    return im


def m2_vertex(
    pos: tuple[float, float, float],
    normal: tuple[float, float, float],
    uv: tuple[float, float],
) -> bytes:
    return (
        vec3(*pos)
        + bytes((255, 0, 0, 0))
        + bytes((0, 0, 0, 0))
        + vec3(*normal)
        + vec2(*uv)
        + vec2(0.0, 0.0)
    )


def m2_cstr(s: str) -> bytes:
    try:
        return s.encode("ascii") + b"\0"
    except UnicodeEncodeError:
        return s.encode("latin-1") + b"\0"


def build_m2(model_name: str = "BattlemonPlane", texture: str = r"Creature\Battlemon\0025_Pikachu.blp") -> bytes:
    b = Blob(HEADER_SIZE)
    b.buf[0:4] = b"MD20"
    b.poke_u32(0x004, WOTLK)

    name = m2_cstr(model_name)
    name_off = b.add(name)
    b.poke_array(0x008, len(name), name_off)
    b.poke_u32(0x010, 0)  # global flags

    # sequences: one Stand (id 0), data in .m2 (flag 0x20)
    # Quad lives in YZ (faces +X, creature forward). Thin on X.
    bb_min = (-0.05, -PLANE_HALF_W, 0.0)
    bb_max = (0.05, PLANE_HALF_W, PLANE_H)
    radius = math.sqrt(PLANE_HALF_W**2 + (PLANE_H * 0.5) ** 2)
    seq = (
        u16(0)  # id Stand
        + u16(0)  # variation
        + u32(3333)  # duration ms
        + f32(0.0)  # movespeed
        + u32(0x20)  # in-m2
        + i16(32767)  # frequency
        + u16(0)
        + u32(0)
        + u32(0)  # replay
        + u32(150)  # blendTime
        + aabox(bb_min, bb_max)
        + f32(radius)
        + i16(-1)  # variationNext
        + u16(0)  # aliasNext
    )
    assert len(seq) == 64, len(seq)
    seq_off = b.add(seq)
    b.poke_array(0x01C, 1, seq_off)

    look_off = b.add(u16(0))
    b.poke_array(0x024, 1, look_off)

    # Static bone. Billboard flags (0x8 / 0x10) hang 3.3.5 when several of
    # these cards exist in one frame.
    bone = (
        i32(-1)  # key_bone_id
        + u32(0x200)
        + i16(-1)  # parent
        + u16(0)
        + u32(0)  # name crc
        + empty_track()
        + empty_track()
        + empty_track()
        + vec3(0.0, 0.0, 0.0)
    )
    assert len(bone) == 88, len(bone)
    bone_off = b.add(bone)
    b.poke_array(0x02C, 1, bone_off)

    key_off = b.add(i16(-1))
    b.poke_array(0x034, 1, key_off)

    # YZ plane, normal +X (creature forward). Viewer in front sees the face.
    nrm = (1.0, 0.0, 0.0)
    verts = (
        m2_vertex((0.0, -PLANE_HALF_W, 0.0), nrm, (0.0, 1.0))
        + m2_vertex((0.0, PLANE_HALF_W, 0.0), nrm, (1.0, 1.0))
        + m2_vertex((0.0, -PLANE_HALF_W, PLANE_H), nrm, (0.0, 0.0))
        + m2_vertex((0.0, PLANE_HALF_W, PLANE_H), nrm, (1.0, 0.0))
    )
    assert len(verts) == 48 * 4
    vert_off = b.add(verts)
    b.poke_array(0x03C, 4, vert_off)

    b.poke_u32(0x044, 1)  # num_skin_profiles

    # Type 0 hardcoded BLP. Each form has its own M2 so the client never
    # walks thousands of TextureVariation rows on one model.
    tex_name = m2_cstr(texture)
    tex_off_name = b.add(tex_name)
    tex = u32(0) + u32(0) + u32(len(tex_name)) + u32(tex_off_name)
    tex_off = b.add(tex)
    b.poke_array(0x050, 1, tex_off)

    weight = constant_uint16_track(b, 0x7FFF)
    weight_off = b.add(weight)
    b.poke_array(0x058, 1, weight_off)

    b.poke_array(0x068, 0, 0)

    # Unlit, one-sided, alpha-key. Two-sided + blend Alpha hung the
    # 3.3.5 renderer after the BLPs were already in memory.
    mat_off = b.add(u16(0x01) + u16(1))
    b.poke_array(0x070, 1, mat_off)

    bone_lu = b.add(u16(0))
    b.poke_array(0x078, 1, bone_lu)
    tex_lu = b.add(u16(0))
    b.poke_array(0x080, 1, tex_lu)
    unit_lu = b.add(i16(0))
    b.poke_array(0x088, 1, unit_lu)
    trans_lu = b.add(u16(0))
    b.poke_array(0x090, 1, trans_lu)
    uv_lu = b.add(i16(-1))
    b.poke_array(0x098, 1, uv_lu)

    b.buf[0x0A0:0x0B8] = aabox(bb_min, bb_max)
    b.buf[0x0B8:0x0BC] = f32(radius)
    b.buf[0x0BC:0x0D4] = aabox(bb_min, bb_max)
    b.buf[0x0D4:0x0D8] = f32(radius)

    # click prism = the same quad
    cidx = u16(0) + u16(1) + u16(3) + u16(0) + u16(3) + u16(2)
    cidx_off = b.add(cidx)
    b.poke_array(0x0D8, 6, cidx_off)
    cverts = (
        vec3(0.0, -PLANE_HALF_W, 0.0)
        + vec3(0.0, PLANE_HALF_W, 0.0)
        + vec3(0.0, -PLANE_HALF_W, PLANE_H)
        + vec3(0.0, PLANE_HALF_W, PLANE_H)
    )
    cv_off = b.add(cverts)
    b.poke_array(0x0E0, 4, cv_off)
    cnrms = vec3(*nrm) + vec3(*nrm)
    cn_off = b.add(cnrms)
    b.poke_array(0x0E8, 2, cn_off)

    return bytes(b.buf)


def build_skin() -> bytes:
    # WotLK SKIN header is 48 bytes.
    header = 48
    b = Blob(header)
    b.buf[0:4] = b"SKIN"

    v_off = b.add(u16(0) + u16(1) + u16(2) + u16(3))
    b.poke_array(0x04, 4, v_off)

    # two triangles, right-handed, normal -Y
    t_off = b.add(u16(0) + u16(1) + u16(3) + u16(0) + u16(3) + u16(2))
    b.poke_array(0x0C, 6, t_off)

    bones = bytes(16)  # four vertices, each four bone indices (all 0)
    bn_off = b.add(bones)
    b.poke_array(0x14, 4, bn_off)

    cx, cy, cz = 0.0, 0.0, CARD_H * 0.5
    sort_r = math.sqrt(CARD_HALF_W**2 + (CARD_H * 0.5) ** 2)
    sub = (
        u16(0)  # skinSectionId
        + u16(0)  # level
        + u16(0)
        + u16(4)  # verts
        + u16(0)
        + u16(6)  # indices
        + u16(1)  # boneCount
        + u16(0)  # boneComboIndex
        + u16(1)  # boneInfluences
        + u16(0)  # centerBone
        + vec3(cx, cy, cz)
        + vec3(cx, cy, cz)
        + f32(sort_r)
    )
    assert len(sub) == 0x30, len(sub)
    sub_off = b.add(sub)
    b.poke_array(0x1C, 1, sub_off)

    batch = (
        bytes((0x10,))  # flags: static
        + bytes((0,))  # priorityPlane
        + u16(0)  # shader
        + u16(0)  # skinSection
        + u16(0)  # geoset
        + u16(0xFFFF)  # no color
        + u16(0)  # material
        + u16(0)  # layer
        + u16(1)  # textureCount
        + u16(0)  # texture combo -> M2 texture 0 (hardcoded BLP)
        + u16(0)  # texcoord combo
        + u16(0)  # weight combo
        + u16(0xFFFF)  # no uv anim
    )
    assert len(batch) == 0x18, len(batch)
    bat_off = b.add(batch)
    b.poke_array(0x24, 1, bat_off)
    b.poke_u32(0x2C, 256)  # boneCountMax
    return bytes(b.buf)


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
TEMPLATE_M2 = TEMPLATE_DIR / "Painting05.m2"
TEMPLATE_SKIN = TEMPLATE_DIR / "Painting0500.skin"


def _bbox_radius(mn: tuple[float, float, float], mx: tuple[float, float, float]) -> float:
    cx = (mn[0] + mx[0]) * 0.5
    cy = (mn[1] + mx[1]) * 0.5
    cz = (mn[2] + mx[2]) * 0.5
    return math.sqrt((mx[0] - cx) ** 2 + (mx[1] - cy) ** 2 + (mx[2] - cz) ** 2)


def _set_bbox(buf: bytearray, half_w: float, height: float) -> None:
    mn = (-0.02, -half_w, 0.0)
    mx = (0.02, half_w, height)
    radius = _bbox_radius(mn, mx)
    struct.pack_into("<fff", buf, 0xA0, *mn)
    struct.pack_into("<fff", buf, 0xAC, *mx)
    struct.pack_into("<f", buf, 0xB8, radius)
    nseq, oseq = struct.unpack_from("<II", buf, 0x1C)
    for i in range(nseq):
        off = oseq + i * 64 + 32
        struct.pack_into("<fff", buf, off, *mn)
        struct.pack_into("<fff", buf, off + 12, *mx)
        struct.pack_into("<f", buf, off + 24, radius)


def flatten_to_card(template: bytes) -> bytes:
    """Keep Painting05 bones/sequences; draw one YZ card, not the 3D frame.

    The frame's UVs sit on the right ~30% of the texture, which is why
    Abomasnow grew teal needles and Tauros grew white specks.
    """
    buf = bytearray(template)
    nvert, overt = struct.unpack_from("<II", buf, 0x3C)
    if nvert < 4:
        raise SystemExit("template M2 needs at least 4 verts")
    nrm = (1.0, 0.0, 0.0)
    u0, u1 = UV_INSET, 1.0 - UV_INSET
    v0, v1 = UV_INSET, 1.0 - UV_INSET
    corners = (
        ((0.0, -CARD_HALF_W, 0.0), (u0, v1)),
        ((0.0, CARD_HALF_W, 0.0), (u1, v1)),
        ((0.0, -CARD_HALF_W, CARD_H), (u0, v0)),
        ((0.0, CARD_HALF_W, CARD_H), (u1, v0)),
    )
    bone_w = buf[overt + 12 : overt + 16]
    bone_i = buf[overt + 16 : overt + 20]
    for i, (pos, uv) in enumerate(corners):
        off = overt + i * 48
        struct.pack_into("<fff", buf, off, *pos)
        buf[off + 12 : off + 16] = bone_w
        buf[off + 16 : off + 20] = bone_i
        struct.pack_into("<fff", buf, off + 20, *nrm)
        struct.pack_into("<ff", buf, off + 32, *uv)
        struct.pack_into("<ff", buf, off + 40, 0.0, 0.0)
    # Keep the original vert count. Shrinking it made Wow/WarcraftXL
    # index a 0xFFFF lookup and ACCESS_VIOLATION. Unused verts sit on
    # the card so leftover skin triangles cannot resurrect the frame.
    for i in range(4, nvert):
        src = overt + (i % 4) * 48
        dst = overt + i * 48
        buf[dst : dst + 48] = buf[src : src + 48]
    _set_bbox(buf, CARD_HALF_W, NAMEPLATE_H)
    return bytes(buf)


def cardify_skin(template: bytes) -> bytes:
    """Keep Painting05's batch (uv-anim 0). Only two triangles."""
    buf = bytearray(template)
    nidx, oidx = struct.unpack_from("<II", buf, 0x04)
    ntri, otri = struct.unpack_from("<II", buf, 0x0C)
    if nidx < 4 or ntri < 6:
        raise SystemExit("template skin is too small to cardify")
    struct.pack_into("<HHHH", buf, oidx, 0, 1, 2, 3)
    struct.pack_into("<I", buf, 0x04, 4)
    struct.pack_into("<HHHHHH", buf, otri, 0, 1, 3, 0, 3, 2)
    struct.pack_into("<I", buf, 0x0C, 6)
    nsub, osub = struct.unpack_from("<II", buf, 0x1C)
    for i in range(nsub):
        off = osub + i * 48
        struct.pack_into("<H", buf, off + 6, 4)
        struct.pack_into("<H", buf, off + 10, 6)
        struct.pack_into("<fff", buf, off + 20, 0.0, 0.0, CARD_H * 0.5)
        struct.pack_into("<fff", buf, off + 32, 0.0, 0.0, CARD_H * 0.5)
        struct.pack_into(
            "<f", buf, off + 44, math.sqrt(CARD_HALF_W**2 + (CARD_H * 0.5) ** 2)
        )
    return bytes(buf)


def retarget_m2(template: bytes, texture: str) -> bytes:
    """Keep Blizzard file; point texture 0 at our BLP.

    Unlit + two-sided + alpha-key. Blend Alpha showed DXT fringe as
    needles; key punches those pixels out.
    """
    buf = bytearray(template)
    ntex, otex = struct.unpack_from("<II", buf, 0x50)
    if ntex < 1:
        raise SystemExit("template M2 has no textures")
    tex_name = m2_cstr(texture)
    off = len(buf)
    buf.extend(tex_name)
    pad = (-len(buf)) % 4
    buf.extend(b"\0" * pad)
    struct.pack_into("<IIII", buf, otex, 0, 0, len(tex_name), off)

    nmat, omat = struct.unpack_from("<II", buf, 0x70)
    for i in range(nmat):
        struct.pack_into("<HH", buf, omat + i * 4, 0x01 | 0x04, 1)
    return bytes(flatten_to_card(bytes(buf)))


def emit_independent_models(dest: Path) -> int:
    """One Painting05-wrapped card M2 + 4-vert skin per sprite BLP."""
    dest.mkdir(parents=True, exist_ok=True)
    if not TEMPLATE_M2.is_file() or not TEMPLATE_SKIN.is_file():
        raise SystemExit(f"missing templates in {TEMPLATE_DIR}")
    template = TEMPLATE_M2.read_bytes()
    skin = cardify_skin(TEMPLATE_SKIN.read_bytes())
    n = 0
    for blp in sorted(dest.glob("*.blp")):
        stem = blp.stem
        if stem == "BattlemonPlane":
            continue
        tex = f"Creature\\Battlemon\\{stem}.blp"
        (dest / f"{stem}.m2").write_bytes(retarget_m2(template, tex))
        (dest / f"{stem}00.skin").write_bytes(skin)
        n += 1
    return n


def convert_png_to_blp(src_dst: tuple[str, str]) -> tuple[str, str]:
    src_s, dst_s = src_dst
    src, dst = Path(src_s), Path(dst_s)
    if dst.is_file() and src.is_file() and dst.stat().st_mtime >= src.stat().st_mtime:
        head = dst.read_bytes()[:24]
        if (
            len(head) >= 24
            and head[:4] == b"BLP2"
            and head[8:12] == bytes((2, 8, 1, 1))
            and struct.unpack_from("<I", head, 20)[0] == 1172
        ):
            return ("skip", dst_s)
    dst.parent.mkdir(parents=True, exist_ok=True)
    write_blp2(dst, pad_sprite(Image.open(src)))
    return ("ok", dst_s)


def sprite_jobs(front: Path, shiny: Path, dest: Path) -> list[tuple[str, str]]:
    jobs: list[tuple[str, str]] = []
    if front.is_dir():
        for png in sorted(front.glob("*.png")):
            jobs.append((str(png), str(dest / f"{png.stem}.blp")))
    if shiny.is_dir():
        for png in sorted(shiny.glob("*.png")):
            stem = png.stem if png.stem.endswith("_s") else f"{png.stem}_s"
            jobs.append((str(png), str(dest / f"{stem}.blp")))
    return jobs


def convert_sprites(jobs: list[tuple[str, str]]) -> tuple[int, int]:
    if not jobs:
        return 0, 0
    wrote = skipped = 0
    workers = min(8, os.cpu_count() or 2)
    print(f"converting {len(jobs)} sprites with {workers} workers")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(convert_png_to_blp, job) for job in jobs]
        done = 0
        total = len(jobs)
        for fut in as_completed(futs):
            status, _ = fut.result()
            if status == "skip":
                skipped += 1
            else:
                wrote += 1
            done += 1
            if done % 100 == 0 or done == total:
                print(f"sprites {done}/{total}  wrote {wrote}  skipped {skipped}")
    return wrote, skipped


def copy_blps(src_dir: Path, dst_dir: Path) -> int:
    dst_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for blp in src_dir.glob("*.blp"):
        shutil.copy2(blp, dst_dir / blp.name)
        n += 1
    return n


def write_listfile(archive_root: Path, creature_dir: Path) -> None:
    lines = []
    for p in sorted(creature_dir.iterdir()):
        if p.is_file() and p.name not in ("(listfile)", "(attributes)"):
            lines.append(f"Creature\\Battlemon\\{p.name}")
    (archive_root / "(listfile)").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", type=Path, default=DEFAULT_PNG)
    ap.add_argument("--front", type=Path, default=FRONT_DIR)
    ap.add_argument("--front-shiny", type=Path, default=FRONT_SHINY_DIR)
    ap.add_argument("--dest", type=Path, default=DEFAULT_PATCH_W)
    ap.add_argument("--module-client", type=Path, default=MODULE_CLIENT)
    ap.add_argument("--sprites", action="store_true", help="Convert Front PNGs into --dest")
    args = ap.parse_args()

    dest = args.dest
    dest.mkdir(parents=True, exist_ok=True)
    if args.sprites:
        jobs = sprite_jobs(args.front, args.front_shiny, dest)
        if not jobs:
            raise SystemExit(f"no PNGs in {args.front} / {args.front_shiny}")
        convert_sprites(jobs)
    n = emit_independent_models(dest)
    write_listfile(dest.parents[1], dest)
    print(f"wrote {n} independent m2+skin pairs into {dest}")


if __name__ == "__main__":
    main()
