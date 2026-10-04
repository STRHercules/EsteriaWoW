"""Block-compression codecs used by BLP2 textures.

Decoders cover every encoding that has appeared in a BLP2 alpha_type field:
BC1 (DXT1), BC2 (DXT3), BC3 (DXT5), BC4 and BC5.  Encoders cover only the
three the 3.3.5a client can sample -- BC1, BC2 and BC3 -- because those are the
only ones worth producing.

Everything is deliberately dependency-free: a modding toolchain that needs a
compiler or a wheel to run is a toolchain people stop using.  The hot paths use
precomputed tables and local-variable binding rather than numpy.
"""

from __future__ import annotations

from collections.abc import Sequence

# ---------------------------------------------------------------------------
# 5/6-bit <-> 8-bit colour conversion tables
# ---------------------------------------------------------------------------
_R5 = [(i * 527 + 23) >> 6 for i in range(32)]   # 5-bit -> 8-bit, round-to-nearest
_G6 = [(i * 259 + 33) >> 6 for i in range(64)]   # 6-bit -> 8-bit
_TO5 = [(v * 31 + 127) // 255 for v in range(256)]
_TO6 = [(v * 63 + 127) // 255 for v in range(256)]


def pack565(r: int, g: int, b: int) -> int:
    return (_TO5[r] << 11) | (_TO6[g] << 5) | _TO5[b]


def unpack565(c: int) -> tuple[int, int, int]:
    return _R5[(c >> 11) & 0x1F], _G6[(c >> 5) & 0x3F], _R5[c & 0x1F]


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------
def _colour_palette(c0: int, c1: int, punchthrough: bool) -> list[tuple[int, int, int, int]]:
    r0, g0, b0 = unpack565(c0)
    r1, g1, b1 = unpack565(c1)
    if punchthrough and c0 <= c1:
        # 3-colour + transparent black (BC1 only).
        return [
            (r0, g0, b0, 255),
            (r1, g1, b1, 255),
            ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255),
            (0, 0, 0, 0),
        ]
    return [
        (r0, g0, b0, 255),
        (r1, g1, b1, 255),
        ((2 * r0 + r1) // 3, (2 * g0 + g1) // 3, (2 * b0 + b1) // 3, 255),
        ((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3, (b0 + 2 * b1) // 3, 255),
    ]


def _alpha_palette(a0: int, a1: int) -> list[int]:
    if a0 > a1:
        return [a0, a1,
                (6 * a0 + 1 * a1) // 7, (5 * a0 + 2 * a1) // 7,
                (4 * a0 + 3 * a1) // 7, (3 * a0 + 4 * a1) // 7,
                (2 * a0 + 5 * a1) // 7, (1 * a0 + 6 * a1) // 7]
    return [a0, a1,
            (4 * a0 + 1 * a1) // 5, (3 * a0 + 2 * a1) // 5,
            (2 * a0 + 3 * a1) // 5, (1 * a0 + 4 * a1) // 5,
            0, 255]


def _blocks(width: int, height: int) -> tuple[int, int]:
    return (width + 3) // 4, (height + 3) // 4


def _decode_blocks(data: bytes, width: int, height: int, block_bytes: int,
                   decode_block) -> bytearray:
    """Shared driver: walk 4x4 blocks and splat them into an RGBA buffer."""
    bw, bh = _blocks(width, height)
    need = bw * bh * block_bytes
    if len(data) < need:
        data = bytes(data) + b"\0" * (need - len(data))
    out = bytearray(width * height * 4)
    stride = width * 4
    texels: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * 16
    for by in range(bh):
        y0 = by * 4
        rows = min(4, height - y0)
        for bx in range(bw):
            off = (by * bw + bx) * block_bytes
            decode_block(data, off, texels)
            x0 = bx * 4
            cols = min(4, width - x0)
            for ty in range(rows):
                dst = (y0 + ty) * stride + x0 * 4
                base = ty * 4
                for tx in range(cols):
                    r, g, b, a = texels[base + tx]
                    p = dst + tx * 4
                    out[p] = r
                    out[p + 1] = g
                    out[p + 2] = b
                    out[p + 3] = a
    return out


def decode_bc1(data: bytes, width: int, height: int) -> bytearray:
    def blk(src: bytes, off: int, texels: list) -> None:
        c0 = src[off] | (src[off + 1] << 8)
        c1 = src[off + 2] | (src[off + 3] << 8)
        pal = _colour_palette(c0, c1, True)
        bits = src[off + 4] | (src[off + 5] << 8) | (src[off + 6] << 16) | (src[off + 7] << 24)
        for i in range(16):
            texels[i] = pal[(bits >> (2 * i)) & 3]

    return _decode_blocks(data, width, height, 8, blk)


def decode_bc2(data: bytes, width: int, height: int) -> bytearray:
    def blk(src: bytes, off: int, texels: list) -> None:
        alpha = int.from_bytes(src[off : off + 8], "little")
        c0 = src[off + 8] | (src[off + 9] << 8)
        c1 = src[off + 10] | (src[off + 11] << 8)
        pal = _colour_palette(c0, c1, False)
        bits = int.from_bytes(src[off + 12 : off + 16], "little")
        for i in range(16):
            r, g, b, _ = pal[(bits >> (2 * i)) & 3]
            a = (alpha >> (4 * i)) & 0xF
            texels[i] = (r, g, b, a * 17)

    return _decode_blocks(data, width, height, 16, blk)


def decode_bc3(data: bytes, width: int, height: int) -> bytearray:
    def blk(src: bytes, off: int, texels: list) -> None:
        apal = _alpha_palette(src[off], src[off + 1])
        abits = int.from_bytes(src[off + 2 : off + 8], "little")
        c0 = src[off + 8] | (src[off + 9] << 8)
        c1 = src[off + 10] | (src[off + 11] << 8)
        pal = _colour_palette(c0, c1, False)
        bits = int.from_bytes(src[off + 12 : off + 16], "little")
        for i in range(16):
            r, g, b, _ = pal[(bits >> (2 * i)) & 3]
            texels[i] = (r, g, b, apal[(abits >> (3 * i)) & 7])

    return _decode_blocks(data, width, height, 16, blk)


def _decode_bc4_block(src: bytes, off: int, out: list) -> None:
    pal = _alpha_palette(src[off], src[off + 1])
    bits = int.from_bytes(src[off + 2 : off + 8], "little")
    for i in range(16):
        out[i] = pal[(bits >> (3 * i)) & 7]


def decode_bc5(data: bytes, width: int, height: int,
               reconstruct_z: bool = True) -> bytearray:
    """Two-channel BC5 -> RGBA.

    BC5 in modern WoW is a tangent-space normal map storing X in red and Y in
    green.  With ``reconstruct_z`` the Z component is rebuilt into blue so the
    result is a usable normal map for a 3.3.5a-era DXT5 repack; otherwise blue
    is left at zero.
    """
    reds = [0] * 16
    greens = [0] * 16

    def blk(src: bytes, off: int, texels: list) -> None:
        _decode_bc4_block(src, off, reds)
        _decode_bc4_block(src, off + 8, greens)
        for i in range(16):
            r = reds[i]
            g = greens[i]
            if reconstruct_z:
                nx = r / 127.5 - 1.0
                ny = g / 127.5 - 1.0
                t = 1.0 - nx * nx - ny * ny
                nz = t ** 0.5 if t > 0.0 else 0.0
                b = int((nz + 1.0) * 127.5 + 0.5)
                if b > 255:
                    b = 255
            else:
                b = 0
            texels[i] = (r, g, b, 255)

    return _decode_blocks(data, width, height, 16, blk)


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------
def _gather_block(rgba: Sequence[int], width: int, height: int,
                  bx: int, by: int) -> list[tuple[int, int, int, int]]:
    """Read one 4x4 block, clamping at the edges for non-multiple-of-4 sizes."""
    block = []
    stride = width * 4
    for ty in range(4):
        y = by * 4 + ty
        if y >= height:
            y = height - 1
        row = y * stride
        for tx in range(4):
            x = bx * 4 + tx
            if x >= width:
                x = width - 1
            p = row + x * 4
            block.append((rgba[p], rgba[p + 1], rgba[p + 2], rgba[p + 3]))
    return block


def _fit_colour_line(block: Sequence[tuple[int, int, int, int]],
                     mask: Sequence[bool] | None) -> tuple[int, int]:
    """Pick two 565 endpoints by bounding-box fit, then inset the box.

    A bounding-box fit is what every real-time DXT compressor starts from; the
    1/16th inset is the standard correction that stops the two extreme texels
    from dragging the whole line and washing the block out.
    """
    lo = [255, 255, 255]
    hi = [0, 0, 0]
    any_used = False
    for i, (r, g, b, _a) in enumerate(block):
        if mask is not None and not mask[i]:
            continue
        any_used = True
        if r < lo[0]:
            lo[0] = r
        if g < lo[1]:
            lo[1] = g
        if b < lo[2]:
            lo[2] = b
        if r > hi[0]:
            hi[0] = r
        if g > hi[1]:
            hi[1] = g
        if b > hi[2]:
            hi[2] = b
    if not any_used:
        return 0, 0
    for c in range(3):
        inset = (hi[c] - lo[c]) >> 4
        lo[c] = min(255, lo[c] + inset)
        hi[c] = max(0, hi[c] - inset)
        if lo[c] > hi[c]:
            lo[c] = hi[c] = (lo[c] + hi[c]) // 2
    return pack565(*hi), pack565(*lo)


def _colour_indices(block: Sequence[tuple[int, int, int, int]],
                    pal: Sequence[tuple[int, int, int, int]],
                    alpha_cut: int | None) -> int:
    """Assign each texel to its nearest palette entry (squared RGB distance)."""
    bits = 0
    n = len(pal)
    for i, (r, g, b, a) in enumerate(block):
        if alpha_cut is not None and a < alpha_cut:
            bits |= 3 << (2 * i)
            continue
        best = 0
        best_d = 1 << 30
        for j in range(n):
            pr, pg, pb, pa = pal[j]
            if pa == 0:
                continue
            dr = r - pr
            dg = g - pg
            db = b - pb
            d = dr * dr + dg * dg + db * db
            if d < best_d:
                best_d = d
                best = j
        bits |= best << (2 * i)
    return bits


def _encode_colour_block(block: Sequence[tuple[int, int, int, int]],
                         punchthrough_cut: int | None) -> bytes:
    """Emit the 8-byte BC1 colour block.

    ``punchthrough_cut`` enables BC1's 1-bit alpha mode: texels below the cutoff
    become the transparent index and the endpoints are ordered c0 <= c1.
    """
    mask = None
    use_punchthrough = False
    if punchthrough_cut is not None:
        mask = [t[3] >= punchthrough_cut for t in block]
        use_punchthrough = not all(mask)
        if not any(mask):
            # Fully transparent block: c0 == c1 with 3-colour mode, all index 3.
            return b"\x00\x00\x00\x00\xff\xff\xff\xff"

    c0, c1 = _fit_colour_line(block, mask)

    if use_punchthrough:
        if c0 > c1:
            c0, c1 = c1, c0
        if c0 == c1 and c0 == 0xFFFF:
            c0 = 0xFFFE
        pal = _colour_palette(c0, c1, True)
        bits = _colour_indices(block, pal, punchthrough_cut)
    else:
        if c0 < c1:
            c0, c1 = c1, c0
        if c0 == c1:
            # Flat block: force 4-colour mode so index 0 stays opaque.
            if c0 > 0:
                c1 = c0 - 1
            else:
                c0 = 1
        pal = _colour_palette(c0, c1, False)
        bits = _colour_indices(block, pal, None)

    return bytes((
        c0 & 0xFF, (c0 >> 8) & 0xFF,
        c1 & 0xFF, (c1 >> 8) & 0xFF,
        bits & 0xFF, (bits >> 8) & 0xFF, (bits >> 16) & 0xFF, (bits >> 24) & 0xFF,
    ))


def _encode_bc3_alpha(block: Sequence[tuple[int, int, int, int]]) -> bytes:
    alphas = [t[3] for t in block]
    a_hi = max(alphas)
    a_lo = min(alphas)
    if a_hi == a_lo:
        # Constant alpha: two identical endpoints, every index 0.
        return bytes((a_hi, a_lo, 0, 0, 0, 0, 0, 0))
    # 8-value mode (a0 > a1) gives the finest gradient; endpoints are inset by
    # one step so the extremes stay exactly representable.
    a0, a1 = a_hi, a_lo
    pal = _alpha_palette(a0, a1)
    bits = 0
    for i, a in enumerate(alphas):
        best = 0
        best_d = 1 << 30
        for j in range(8):
            d = abs(a - pal[j])
            if d < best_d:
                best_d = d
                best = j
        bits |= best << (3 * i)
    return bytes((a0, a1)) + bits.to_bytes(6, "little")


def _encode_bc2_alpha(block: Sequence[tuple[int, int, int, int]]) -> bytes:
    bits = 0
    for i, t in enumerate(block):
        bits |= ((t[3] * 15 + 127) // 255) << (4 * i)
    return bits.to_bytes(8, "little")


def encode_bc1(rgba: Sequence[int], width: int, height: int,
               alpha_cutoff: int | None = 128) -> bytes:
    """Encode RGBA bytes as BC1/DXT1.

    ``alpha_cutoff`` of ``None`` forces opaque 4-colour blocks everywhere;
    otherwise texels below the cutoff are encoded as BC1's punch-through
    transparent index.
    """
    bw, bh = _blocks(width, height)
    out = bytearray()
    for by in range(bh):
        for bx in range(bw):
            block = _gather_block(rgba, width, height, bx, by)
            out += _encode_colour_block(block, alpha_cutoff)
    return bytes(out)


def encode_bc2(rgba: Sequence[int], width: int, height: int) -> bytes:
    bw, bh = _blocks(width, height)
    out = bytearray()
    for by in range(bh):
        for bx in range(bw):
            block = _gather_block(rgba, width, height, bx, by)
            out += _encode_bc2_alpha(block)
            out += _encode_colour_block(block, None)
    return bytes(out)


def encode_bc3(rgba: Sequence[int], width: int, height: int) -> bytes:
    bw, bh = _blocks(width, height)
    out = bytearray()
    for by in range(bh):
        for bx in range(bw):
            block = _gather_block(rgba, width, height, bx, by)
            out += _encode_bc3_alpha(block)
            out += _encode_colour_block(block, None)
    return bytes(out)
