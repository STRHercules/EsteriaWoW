"""BLP downgrade: make any modern texture something 3.3.5a can sample.

Three things break a modern BLP on the old client:

1. ``alpha_type = 11`` (BC5).  Legion normal maps use it and 3.3.5a has no
   decoder, so the texture has to be transcoded.
2. Non-power-of-two dimensions, which the old client only tolerates for
   unmipped UI textures.
3. Sheer size.  The 32-bit 3.3.5a binary has a small texture budget and 2K/4K
   art from Dragonflight will evict everything else.

When none of those apply -- which is the common case, because Blizzard still
ships DXT1/DXT5 for most diffuse art -- the block payload is copied through
untouched so no generation loss is introduced.
"""

from __future__ import annotations

import time

from ..limits import (
    BLP_COMPRESSION_ARGB8888,
    BLP_COMPRESSION_DXT,
    BLP_COMPRESSION_PALETTE,
    BLP_MAX_MIPS,
)
from ..options import Options, TextureFormat
from ..report import FileResult, Status
from . import bcn
from .blp import FORMAT_NAMES, Blp, EmptyTextureError, PreferredFormat
from .image import Image, is_pot, nearest_pot
from .quantize import PaletteMapper, build_palette


def _choose_format(images: list[Image], src: Blp, opts: Options) -> tuple[int, int, int]:
    """Return (compression, alpha_type, alpha_size) for the output."""
    fmt = opts.texture_format

    if fmt is TextureFormat.KEEP:
        ok, _ = src.is_wotlk_compatible()
        if ok:
            return src.compression, src.alpha_type, src.alpha_size
        fmt = TextureFormat.AUTO  # source encoding is unusable; fall back

    if fmt is TextureFormat.DXT1:
        return BLP_COMPRESSION_DXT, PreferredFormat.DXT1, 1
    if fmt is TextureFormat.DXT3:
        return BLP_COMPRESSION_DXT, PreferredFormat.DXT3, 8
    if fmt is TextureFormat.DXT5:
        return BLP_COMPRESSION_DXT, PreferredFormat.DXT5, 8
    if fmt is TextureFormat.RAW:
        return BLP_COMPRESSION_ARGB8888, PreferredFormat.ARGB8888, 8
    if fmt is TextureFormat.PAL:
        _lo, _hi, binary = images[0].alpha_stats()
        if images[0].is_opaque():
            return BLP_COMPRESSION_PALETTE, PreferredFormat.UNSPECIFIED, 0
        return BLP_COMPRESSION_PALETTE, PreferredFormat.UNSPECIFIED, 1 if binary else 8

    # AUTO: let the alpha channel decide.
    base = images[0]
    if src.compression == BLP_COMPRESSION_DXT and src.alpha_type == PreferredFormat.BC5:
        # A normal map. 3.3.5a has no normal-mapped shader path at all, so the
        # alpha channel carries nothing; DXT1 keeps it small.
        return BLP_COMPRESSION_DXT, PreferredFormat.DXT1, 0
    if base.is_opaque():
        return BLP_COMPRESSION_DXT, PreferredFormat.DXT1, 0
    _lo, _hi, binary = base.alpha_stats()
    if binary:
        return BLP_COMPRESSION_DXT, PreferredFormat.DXT1, 1
    return BLP_COMPRESSION_DXT, PreferredFormat.DXT5, 8


def _encode_level(img: Image, compression: int, alpha_type: int, alpha_size: int,
                  opts: Options, mapper: PaletteMapper | None) -> bytes:
    if compression == BLP_COMPRESSION_DXT:
        if alpha_type == PreferredFormat.DXT1:
            cutoff = opts.dxt1_alpha_cutoff if alpha_size else None
            return bcn.encode_bc1(img.data, img.width, img.height, cutoff)
        if alpha_type == PreferredFormat.DXT3:
            return bcn.encode_bc2(img.data, img.width, img.height)
        return bcn.encode_bc3(img.data, img.width, img.height)

    if compression == BLP_COMPRESSION_ARGB8888:
        return bytes(img.to_bgra())

    # Palettised.
    assert mapper is not None
    out = bytearray(mapper.map_image(img.data))
    if alpha_size == 8:
        out += img.data[3::4]
    elif alpha_size == 4:
        alphas = img.data[3::4]
        packed = bytearray((len(alphas) + 1) // 2)
        for i, a in enumerate(alphas):
            nib = (a * 15 + 127) // 255
            if i & 1:
                packed[i >> 1] |= nib << 4
            else:
                packed[i >> 1] |= nib
        out += packed
    elif alpha_size == 1:
        alphas = img.data[3::4]
        packed = bytearray((len(alphas) + 7) // 8)
        for i, a in enumerate(alphas):
            if a >= opts.dxt1_alpha_cutoff:
                packed[i >> 3] |= 1 << (i & 7)
        out += packed
    return bytes(out)


def _target_dimensions(width: int, height: int, opts: Options,
                       result: FileResult) -> tuple[int, int]:
    tw, th = width, height
    if opts.force_power_of_two and not (is_pot(tw) and is_pot(th)):
        tw, th = nearest_pot(tw), nearest_pot(th)
        result.lossy(
            "blp.resize.npot",
            f"resized {width}x{height} to power-of-two {tw}x{th}; "
            f"3.3.5a only mipmaps power-of-two textures",
            source=[width, height], target=[tw, th],
        )
    cap = opts.texture_ext_cap()
    if tw > cap or th > cap:
        scale = max(tw / cap, th / cap)
        nw = max(1, int(tw / scale))
        nh = max(1, int(th / scale))
        if opts.force_power_of_two:
            nw, nh = nearest_pot(nw), nearest_pot(nh)
            nw = min(nw, cap)
            nh = min(nh, cap)
        result.lossy(
            "blp.resize.cap",
            f"downscaled {tw}x{th} to {nw}x{nh} (--max-texture-size {cap})",
            source=[tw, th], target=[nw, nh],
        )
        tw, th = nw, nh
    return tw, th


def _agree_alpha_depth(src: Blp, res: FileResult) -> None:
    """Make a block texture's alpha depth say what its blocks are.

    3.3.5a picks the block format from the alpha depth first -- 0 or 1 means
    DXT1 -- and only then from the alpha type, so a DXT5 texture declaring
    depth 0, or any texture declaring a depth like 72 (33 retail textures do),
    is decoded as the wrong format.
    """
    if src.compression != BLP_COMPRESSION_DXT:
        return
    depth = src.alpha_size
    if src.alpha_type == PreferredFormat.DXT1:
        fixed = depth if depth in (0, 1) else 1
    else:
        fixed = depth if depth in (4, 8) else 8
    if fixed != depth:
        src.alpha_size = fixed
        res.info("blp.alpha_depth",
                 f"alpha depth {depth} does not match "
                 f"{FORMAT_NAMES.get(src.alpha_type, src.alpha_type)} blocks, and "
                 f"3.3.5a picks the block format from it; wrote {fixed}",
                 source=depth, written=fixed)


def convert_blp(data: bytes, source_name: str, opts: Options,
                result: FileResult | None = None) -> tuple[bytes, FileResult]:
    """Convert one BLP payload. Returns (output bytes, result)."""
    started = time.time()
    res = result or FileResult(source=source_name, kind="blp")
    res.kind = "blp"
    res.bytes_in = len(data)

    try:
        src = Blp.parse(data, source_name)
    except EmptyTextureError as exc:
        res.status = Status.SKIPPED
        res.elapsed = time.time() - started
        res.info("blp.empty", f"{exc}; a placeholder with nothing to convert, "
                 "so no file is written")
        return b"", res
    res.source_version = f"BLP2/{src.encoding_name} {src.width}x{src.height} " \
                         f"mips={src.mip_count}"

    compatible, why = src.is_wotlk_compatible()
    size_ok = (not opts.force_power_of_two or (is_pot(src.width) and is_pot(src.height)))
    cap = opts.texture_ext_cap()
    size_ok = size_ok and src.width <= cap and src.height <= cap
    keep_encoding = opts.texture_format in (TextureFormat.KEEP, TextureFormat.AUTO)

    if compatible and size_ok and keep_encoding and src.mip_count:
        # Nothing to do: re-emit the container verbatim so block data is bit
        # identical and no generation loss creeps in.
        _agree_alpha_depth(src, res)
        out = src.serialize()
        res.status = Status.PASSTHROUGH
        res.target_version = res.source_version
        res.bytes_out = len(out)
        res.elapsed = time.time() - started
        res.info("blp.passthrough", f"already 3.3.5a-compatible ({src.encoding_name})")
        return out, res

    if not compatible:
        res.lossy("blp.transcode", f"source uses {why}, which 3.3.5a cannot sample",
                  source_format=FORMAT_NAMES.get(src.alpha_type, src.alpha_type))

    is_bc5 = (src.compression == BLP_COMPRESSION_DXT
              and src.alpha_type == PreferredFormat.BC5)
    base = src.decode_level(0, opts.reconstruct_normal_z)
    if is_bc5:
        res.info("blp.normalmap",
                 "BC5 normal map transcoded; 3.3.5a has no normal-mapped shader "
                 "path, so this texture is only useful as a diffuse or overlay")

    tw, th = _target_dimensions(base.width, base.height, opts, res)
    if (tw, th) != (base.width, base.height):
        base = base.resize(tw, th)

    images = base.mip_chain(BLP_MAX_MIPS)
    compression, alpha_type, alpha_size = _choose_format(images, src, opts)

    mapper = None
    palette: list[int] | None = None
    if compression == BLP_COMPRESSION_PALETTE:
        entries = build_palette(base.data, 256)
        mapper = PaletteMapper(entries)
        palette = [(r << 16) | (g << 8) | b for (r, g, b) in entries]
        res.lossy("blp.palettise", "quantised to a 256-colour palette")

    payloads = [_encode_level(img, compression, alpha_type, alpha_size, opts, mapper)
                for img in images]

    out_blp = Blp.from_images(images, compression=compression, alpha_type=alpha_type,
                              alpha_size=alpha_size, palette=palette, payloads=payloads)
    out = out_blp.serialize()

    res.target_version = (f"BLP2/{out_blp.encoding_name} {out_blp.width}x{out_blp.height} "
                          f"mips={out_blp.mip_count}")
    if compression == BLP_COMPRESSION_DXT and src.compression == BLP_COMPRESSION_DXT \
            and compatible and src.alpha_type != alpha_type:
        res.lossy("blp.recompress",
                  f"re-encoded {FORMAT_NAMES.get(src.alpha_type)} -> "
                  f"{FORMAT_NAMES.get(alpha_type)}")
    res.bytes_out = len(out)
    res.elapsed = time.time() - started
    if res.status is Status.OK:
        res.status = Status.OK
    return out, res


def inspect_blp(data: bytes, source_name: str) -> dict:
    """Human-readable description of a BLP, for the ``inspect`` command."""
    src = Blp.parse(data, source_name)
    ok, why = src.is_wotlk_compatible()
    return {
        "kind": "blp",
        "width": src.width,
        "height": src.height,
        "encoding": src.encoding_name,
        "compression": src.compression,
        "alpha_type": src.alpha_type,
        "alpha_bits": src.alpha_size,
        "mip_levels": src.mip_count,
        "power_of_two": is_pot(src.width) and is_pot(src.height),
        "wotlk_compatible": ok,
        "incompatibility": why or None,
    }
