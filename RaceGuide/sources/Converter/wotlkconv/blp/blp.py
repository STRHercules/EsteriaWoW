"""BLP2 container read/write.

Header layout (1172 bytes, little-endian)::

    char   magic[4]        'BLP2'
    uint32 version         1
    uint8  compression     1 palette, 2 block-compressed, 3/4 raw BGRA
    uint8  alpha_size      0, 1, 4 or 8 bits
    uint8  alpha_type      "preferred format" -- see PreferredFormat
    uint8  has_mips
    uint32 width, height
    uint32 mip_offsets[16]
    uint32 mip_sizes[16]
    uint32 palette[256]    BGRA, present whatever the compression is

3.3.5a understands compression 1, 2 (with alpha_type 0/1/7) and 3.  Legion-era
files additionally use alpha_type 11 (BC5) for normal maps, which is what makes
a straight copy of a modern texture fail on the old client.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence

from ..binio import Reader, Writer
from ..errors import MalformedFileError, UnsupportedFormatError
from ..limits import (
    BLP_COMPRESSION_ARGB8888,
    BLP_COMPRESSION_ARGB8888_DUP,
    BLP_COMPRESSION_DXT,
    BLP_COMPRESSION_JPEG,
    BLP_COMPRESSION_PALETTE,
    BLP_MAX_MIPS,
)
from . import bcn
from .image import Image


class EmptyTextureError(MalformedFileError):
    """A well-formed BLP header that declares no image data at all.

    Retail ships a few of these as placeholders (12.1 has 1,172-byte
    minimap tiles: header and zeroed palette, every mip offset and size
    zero).  There is nothing to convert, which is not the same thing as a
    broken file.
    """

HEADER_SIZE = 1172
MAGIC = b"BLP2"
MAGIC_BLP1 = b"BLP1"


class PreferredFormat:
    DXT1 = 0
    DXT3 = 1
    ARGB8888 = 2
    ARGB1555 = 3
    ARGB4444 = 4
    RGB565 = 5
    A8 = 6
    DXT5 = 7
    UNSPECIFIED = 8
    ARGB2565 = 9
    BC5 = 11


#: What each preferred_format means, for diagnostics.
FORMAT_NAMES = {
    0: "DXT1", 1: "DXT3", 2: "ARGB8888", 3: "ARGB1555", 4: "ARGB4444",
    5: "RGB565", 6: "A8", 7: "DXT5", 8: "UNSPECIFIED", 9: "ARGB2565",
    11: "BC5",
}

COMPRESSION_NAMES = {
    0: "JPEG", 1: "PALETTE", 2: "BLOCK", 3: "RAW_BGRA", 4: "RAW_BGRA2",
}

#: Encodings the 3.3.5a client can sample.
SUPPORTED_BLOCK_FORMATS = (PreferredFormat.DXT1, PreferredFormat.DXT3,
                           PreferredFormat.DXT5)


@dataclasses.dataclass(slots=True)
class Blp:
    width: int
    height: int
    compression: int = BLP_COMPRESSION_DXT
    alpha_size: int = 8
    alpha_type: int = PreferredFormat.DXT5
    has_mips: int = 1
    palette: list[int] = dataclasses.field(default_factory=lambda: [0] * 256)
    mips: list[bytes] = dataclasses.field(default_factory=list)

    # -- description ----------------------------------------------------
    @property
    def encoding_name(self) -> str:
        comp = COMPRESSION_NAMES.get(self.compression, f"?{self.compression}")
        if self.compression == BLP_COMPRESSION_DXT:
            return FORMAT_NAMES.get(self.alpha_type, f"?{self.alpha_type}")
        if self.compression == BLP_COMPRESSION_PALETTE:
            return f"PAL8A{self.alpha_size}"
        return comp

    @property
    def mip_count(self) -> int:
        return len(self.mips)

    def level_size(self, level: int) -> tuple[int, int]:
        return (max(1, self.width >> level), max(1, self.height >> level))

    def is_wotlk_compatible(self) -> tuple[bool, str]:
        """Whether the 3.3.5a client can sample this texture as-is."""
        if self.compression == BLP_COMPRESSION_JPEG:
            return False, "JPEG-compressed BLP1 payload"
        if self.compression == BLP_COMPRESSION_DXT:
            if self.alpha_type not in SUPPORTED_BLOCK_FORMATS:
                return False, f"block format {FORMAT_NAMES.get(self.alpha_type, self.alpha_type)}"
            return True, ""
        if self.compression in (BLP_COMPRESSION_PALETTE, BLP_COMPRESSION_ARGB8888,
                                BLP_COMPRESSION_ARGB8888_DUP):
            return True, ""
        return False, f"unknown compression {self.compression}"

    # -- parsing --------------------------------------------------------
    @classmethod
    def parse(cls, data: bytes, name: str = "<memory>") -> Blp:
        if len(data) < 8:
            raise MalformedFileError(f"{name}: too short to be a BLP")
        if data[:4] == MAGIC_BLP1:
            raise UnsupportedFormatError(
                f"{name}: BLP1 (Warcraft III / vanilla alpha) is not supported"
            )
        if data[:4] != MAGIC:
            raise UnsupportedFormatError(f"{name}: not a BLP2 file (magic {data[:4]!r})")

        r = Reader(data, name)
        r.skip(4)
        version = r.u32()
        if version != 1:
            raise UnsupportedFormatError(f"{name}: BLP2 version {version}, expected 1")
        compression = r.u8()
        alpha_size = r.u8()
        alpha_type = r.u8()
        has_mips = r.u8()
        width = r.u32()
        height = r.u32()
        offsets = r.u32s(BLP_MAX_MIPS)
        sizes = r.u32s(BLP_MAX_MIPS)
        palette = r.u32s(256)

        if width == 0 or height == 0:
            raise MalformedFileError(f"{name}: zero-sized texture {width}x{height}")

        mips: list[bytes] = []
        for level in range(BLP_MAX_MIPS):
            off, size = offsets[level], sizes[level]
            if size == 0 or off == 0:
                break
            if off + size > len(data):
                if off >= len(data):
                    break
                size = len(data) - off
            mips.append(data[off : off + size])
            if max(1, width >> level) == 1 and max(1, height >> level) == 1:
                break
        if not mips:
            if not any(offsets) and not any(sizes):
                raise EmptyTextureError(
                    f"{name}: the texture declares no image data (every mip "
                    f"offset and size is zero)")
            raise MalformedFileError(f"{name}: BLP has no mip levels")

        return cls(width, height, compression, alpha_size, alpha_type,
                   has_mips, palette, mips)

    # -- decoding -------------------------------------------------------
    def decode_level(self, level: int = 0, reconstruct_normal_z: bool = True) -> Image:
        if level >= len(self.mips):
            raise IndexError(f"mip level {level} of {len(self.mips)}")
        w, h = self.level_size(level)
        payload = self.mips[level]
        comp = self.compression

        if comp == BLP_COMPRESSION_DXT:
            at = self.alpha_type
            if at == PreferredFormat.DXT1:
                rgba = bcn.decode_bc1(payload, w, h)
            elif at == PreferredFormat.DXT3:
                rgba = bcn.decode_bc2(payload, w, h)
            elif at == PreferredFormat.DXT5:
                rgba = bcn.decode_bc3(payload, w, h)
            elif at == PreferredFormat.BC5:
                rgba = bcn.decode_bc5(payload, w, h, reconstruct_normal_z)
            else:
                raise UnsupportedFormatError(
                    f"BLP block format {FORMAT_NAMES.get(at, at)} cannot be decoded"
                )
            return Image(w, h, rgba)

        if comp == BLP_COMPRESSION_PALETTE:
            return self._decode_palettised(payload, w, h)

        if comp in (BLP_COMPRESSION_ARGB8888, BLP_COMPRESSION_ARGB8888_DUP):
            if self.alpha_type == PreferredFormat.A8:
                out = bytearray(w * h * 4)
                for i in range(min(w * h, len(payload))):
                    v = payload[i]
                    p = i * 4
                    out[p] = out[p + 1] = out[p + 2] = 255
                    out[p + 3] = v
                return Image(w, h, out)
            return Image.from_bgra(w, h, payload)

        raise UnsupportedFormatError(f"BLP compression {comp} cannot be decoded")

    def _decode_palettised(self, payload: bytes, w: int, h: int) -> Image:
        count = w * h
        if len(payload) < count:
            payload = bytes(payload) + b"\0" * (count - len(payload))
        pal = self.palette
        out = bytearray(count * 4)
        for i in range(count):
            entry = pal[payload[i]]
            p = i * 4
            out[p] = (entry >> 16) & 0xFF      # palette is BGRA
            out[p + 1] = (entry >> 8) & 0xFF
            out[p + 2] = entry & 0xFF
            out[p + 3] = 255
        bits = self.alpha_size
        if bits:
            apos = count
            if bits == 8:
                for i in range(count):
                    out[i * 4 + 3] = payload[apos + i] if apos + i < len(payload) else 255
            elif bits == 4:
                for i in range(count):
                    byte_i = apos + (i >> 1)
                    if byte_i >= len(payload):
                        break
                    nib = payload[byte_i]
                    v = (nib & 0xF) if (i & 1) == 0 else (nib >> 4)
                    out[i * 4 + 3] = v * 17
            elif bits == 1:
                for i in range(count):
                    byte_i = apos + (i >> 3)
                    if byte_i >= len(payload):
                        break
                    out[i * 4 + 3] = 255 if (payload[byte_i] >> (i & 7)) & 1 else 0
        return Image(w, h, out)

    # -- construction ---------------------------------------------------
    @classmethod
    def from_images(cls, images: Sequence[Image], *, compression: int,
                    alpha_type: int = PreferredFormat.DXT5,
                    alpha_size: int = 8,
                    palette: Sequence[int] | None = None,
                    payloads: Sequence[bytes] | None = None) -> Blp:
        """Assemble a BLP from an already-encoded mip chain.

        ``payloads`` carries the encoded bytes per level; ``images`` is only
        used for the base dimensions and level count.
        """
        if not images:
            raise ValueError("at least one mip level is required")
        blp = cls(images[0].width, images[0].height, compression, alpha_size,
                  alpha_type, 1 if len(images) > 1 else 0)
        if palette is not None:
            blp.palette = list(palette)[:256] + [0] * max(0, 256 - len(palette))
        blp.mips = list(payloads or [])
        return blp

    # -- serialising ----------------------------------------------------
    def serialize(self) -> bytes:
        if len(self.mips) > BLP_MAX_MIPS:
            raise MalformedFileError(
                f"BLP supports at most {BLP_MAX_MIPS} mip levels, got {len(self.mips)}"
            )
        w = Writer()
        w.raw(MAGIC)
        w.u32(1)
        w.u8(self.compression)
        w.u8(self.alpha_size)
        w.u8(self.alpha_type)
        w.u8(1 if len(self.mips) > 1 else 0)
        w.u32(self.width)
        w.u32(self.height)
        offsets_pos = w.reserve(4 * BLP_MAX_MIPS)
        sizes_pos = w.reserve(4 * BLP_MAX_MIPS)
        pal = list(self.palette)[:256]
        pal += [0] * (256 - len(pal))
        w.u32s(pal)
        assert w.tell() == HEADER_SIZE, f"BLP header is {w.tell()} bytes"

        for level, payload in enumerate(self.mips):
            w.patch_u32(offsets_pos + 4 * level, w.tell())
            w.patch_u32(sizes_pos + 4 * level, len(payload))
            w.raw(payload)
        return w.getvalue()
