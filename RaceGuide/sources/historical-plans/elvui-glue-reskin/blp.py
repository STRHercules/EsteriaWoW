"""Minimal BLP2 codec for WotLK 3.3.5a client textures.

Supports decode of paletted (1), DXT (2: DXT1/DXT3/DXT5) and raw BGRA (3), and
encode as raw BGRA BLP2 with mipmaps -- the variant this client already loads
(see tools/derive_playable_race_portraits.py).

Header layout (BLP2):
    [0:4]   magic 'BLP2'
    [4:8]   uint32 type (0=JPEG, 1=uncompressed, 2=DXT)
    [8]     uint8  compression (1=paletted, 2=DXT, 3=raw BGRA)
    [9]     uint8  alphaDepth
    [10]    uint8  alphaEncoding (DXT: 0=DXT1, 1=DXT3, 7=DXT5)
    [11]    uint8  hasMips
    [12:16] uint32 width
    [16:20] uint32 height
    [20:84] uint32 offsets[16]
    [84:148] uint32 lengths[16]
    [148:1172] palette (256 * BGRA)
"""

from __future__ import annotations

import struct

from PIL import Image

HEADER_SIZE = 148
PALETTE_SIZE = 1024
DATA_OFFSET = HEADER_SIZE + PALETTE_SIZE
MAX_MIPS = 16


# --------------------------------------------------------------------------- decode


def _unpack_565(value: int) -> tuple[int, int, int]:
    r = (value >> 11) & 0x1F
    g = (value >> 5) & 0x3F
    b = value & 0x1F
    return (r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2)


def _decode_color_block(block: bytes, pixels: list[tuple[int, int, int]], force_four: bool):
    """Decode the 8-byte BC1-style colour half into 16 RGB tuples."""
    c0, c1, bits = struct.unpack("<HHI", block)
    r0, g0, b0 = _unpack_565(c0)
    r1, g1, b1 = _unpack_565(c1)
    table = [(r0, g0, b0), (r1, g1, b1)]
    if c0 > c1 or force_four:
        table.append(((2 * r0 + r1) // 3, (2 * g0 + g1) // 3, (2 * b0 + b1) // 3))
        table.append(((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3, (b0 + 2 * b1) // 3))
    else:
        table.append(((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2))
        table.append((0, 0, 0))
    for i in range(16):
        pixels[i] = table[(bits >> (2 * i)) & 0x3]


def _decode_dxt1(raw: bytes, width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height))
    out = img.load()
    pixels: list[tuple[int, int, int]] = [(0, 0, 0)] * 16
    pos = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 4):
            _decode_color_block(raw[pos : pos + 8], pixels, force_four=False)
            pos += 8
            for i in range(16):
                x, y = bx + (i % 4), by + (i // 4)
                if x < width and y < height:
                    r, g, b = pixels[i]
                    out[x, y] = (r, g, b, 255)
    return img


def _decode_dxt3(raw: bytes, width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height))
    out = img.load()
    pixels: list[tuple[int, int, int]] = [(0, 0, 0)] * 16
    pos = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 4):
            alpha_bits = int.from_bytes(raw[pos : pos + 8], "little")
            _decode_color_block(raw[pos + 8 : pos + 16], pixels, force_four=True)
            pos += 16
            for i in range(16):
                x, y = bx + (i % 4), by + (i // 4)
                if x < width and y < height:
                    r, g, b = pixels[i]
                    a = ((alpha_bits >> (4 * i)) & 0xF) * 17
                    out[x, y] = (r, g, b, a)
    return img


def _decode_dxt5(raw: bytes, width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height))
    out = img.load()
    pixels: list[tuple[int, int, int]] = [(0, 0, 0)] * 16
    pos = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 4):
            a0, a1 = raw[pos], raw[pos + 1]
            idx_bits = int.from_bytes(raw[pos + 2 : pos + 8], "little")
            alpha = [a0, a1]
            if a0 > a1:
                for i in range(1, 7):
                    alpha.append(((7 - i) * a0 + i * a1) // 7)
            else:
                for i in range(1, 5):
                    alpha.append(((5 - i) * a0 + i * a1) // 5)
                alpha.extend([0, 255])
            _decode_color_block(raw[pos + 8 : pos + 16], pixels, force_four=True)
            pos += 16
            for i in range(16):
                x, y = bx + (i % 4), by + (i // 4)
                if x < width and y < height:
                    r, g, b = pixels[i]
                    a = alpha[(idx_bits >> (3 * i)) & 0x7]
                    out[x, y] = (r, g, b, a)
    return img


def decode_blp(data: bytes) -> Image.Image:
    if data[:4] != b"BLP2":
        raise ValueError(f"not a BLP2 file (magic={data[:4]!r})")
    compression, alpha_depth, alpha_enc, has_mips = data[8:12]
    width, height = struct.unpack("<2I", data[12:20])
    offsets = struct.unpack("<16I", data[20:84])
    lengths = struct.unpack("<16I", data[84:148])
    base = data[offsets[0] : offsets[0] + lengths[0]]

    if compression == 3:
        return Image.frombytes("RGBA", (width, height), base, "raw", "BGRA")
    if compression == 1:
        palette = data[HEADER_SIZE:DATA_OFFSET]
        if alpha_depth == 8:
            alpha = base[: width * height]
            indices = base[width * height : width * height * 2]
        else:
            alpha = None
            indices = base[: width * height]
        img = Image.frombytes("P", (width, height), indices)
        img.putpalette(palette, rawmode="BGRA")
        rgba = img.convert("RGBA")
        if alpha is not None:
            rgba.putalpha(Image.frombytes("L", (width, height), alpha))
        return rgba
    if compression == 2:
        if alpha_enc == 7:
            return _decode_dxt5(base, width, height)
        if alpha_enc == 1:
            return _decode_dxt3(base, width, height)
        return _decode_dxt1(base, width, height)
    raise ValueError(f"unsupported BLP2 compression {compression}")


def describe_blp(data: bytes) -> str:
    compression, alpha_depth, alpha_enc, has_mips = data[8:12]
    width, height = struct.unpack("<2I", data[12:20])
    lengths = struct.unpack("<16I", data[84:148])
    mips = [n for n in lengths if n]
    kinds = {1: "paletted", 2: "DXT", 3: "rawBGRA"}
    enc = {0: "DXT1", 1: "DXT3", 7: "DXT5"}.get(alpha_enc, str(alpha_enc))
    kind = kinds.get(compression, str(compression))
    if compression == 2:
        kind = f"DXT({enc})"
    return (
        f"{kind} {width}x{height} alphaDepth={alpha_depth} mips={len(mips)} "
        f"bytes={len(data)}"
    )


# --------------------------------------------------------------------------- encode


def _mip_sizes(width: int, height: int, mip_count: int) -> list[tuple[int, int]]:
    sizes = []
    for level in range(mip_count):
        w = max(1, width >> level)
        h = max(1, height >> level)
        sizes.append((w, h))
    return sizes


def encode_blp_bgra(image: Image.Image, mip_count: int = 16) -> bytes:
    """Encode as BLP2 compression=3 (raw BGRA) with mipmaps.

    mip_count is clamped so the chain ends at 1x1.
    """
    image = image.convert("RGBA")
    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError("image must have positive dimensions")
    max_levels, w, h = 1, width, height
    while (w > 1 or h > 1) and max_levels < MAX_MIPS:
        w, h = max(1, w // 2), max(1, h // 2)
        max_levels += 1
    mip_count = max(1, min(mip_count, max_levels, MAX_MIPS))
    sizes = _mip_sizes(width, height, mip_count)

    payloads: list[bytes] = []
    for index, (w, h) in enumerate(sizes):
        mip = image if index == 0 else image.resize((w, h), Image.Resampling.LANCZOS)
        payloads.append(mip.convert("RGBA").tobytes("raw", "BGRA"))

    offsets: list[int] = []
    lengths: list[int] = []
    cursor = DATA_OFFSET
    for payload in payloads:
        offsets.append(cursor)
        lengths.append(len(payload))
        cursor += len(payload)
    offsets.extend([0] * (MAX_MIPS - len(offsets)))
    lengths.extend([0] * (MAX_MIPS - len(lengths)))

    header = bytearray()
    header += b"BLP2"
    header += struct.pack("<I", 1)                 # type = uncompressed
    header += bytes((3, 8, 8, 1 if mip_count > 1 else 0))  # rawBGRA, alphaDepth 8, alphaEnc 8
    header += struct.pack("<2I", width, height)
    header += struct.pack("<16I", *offsets)
    header += struct.pack("<16I", *lengths)
    header += bytes(PALETTE_SIZE)
    assert len(header) == DATA_OFFSET, len(header)
    return bytes(header) + b"".join(payloads)
