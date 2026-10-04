"""``.skin`` profiles -- the per-LOD draw data that sits next to an M2.

A skin holds the vertex/index lists, the submesh table and the draw batches.
The 3.3.5a header is 48 bytes; Legion appended an ``M2Array<M2ShadowBatch>``
for its shadow pass, giving 56.  Nothing else about the file changed, so a
downgrade is mostly "drop the shadow batches, then check that the model still
fits inside 16-bit indices and the old renderer's per-batch limits".
"""

from __future__ import annotations

import dataclasses
import struct

from ..binio import Writer
from ..errors import MalformedFileError, UnsupportedFormatError
from ..limits import (
    M2_MAX_BONE_INFLUENCES,
    M2_MAX_BONES_PER_SUBMESH,
    M2_MAX_TEXTURE_UNITS,
    M2_MAX_VERTICES,
    SKIN_HEADER_SIZE_LEGION,
    SKIN_HEADER_SIZE_WOTLK,
    SKIN_MAGIC,
)
from ..options import Options
from ..report import FileResult, Status

SUBMESH_SIZE = 48
BATCH_SIZE = 24
SHADOW_BATCH_SIZE = 12

#: Byte offsets inside M2Batch.
BATCH_SHADER_ID = 0x02
BATCH_TEXTURE_COUNT = 0x0E
BATCH_TEXTURE_COORD_COMBO = 0x12

#: M2Batch.shader_id bit meaning "index into the model's texture combiner combos".
SHADER_COMBINER_FLAG = 0x8000


@dataclasses.dataclass
class Skin:
    vertices: list[int] = dataclasses.field(default_factory=list)
    indices: list[int] = dataclasses.field(default_factory=list)
    bones: bytes = b""          # 4 bytes per vertex, opaque
    submeshes: list[bytes] = dataclasses.field(default_factory=list)
    batches: list[bytes] = dataclasses.field(default_factory=list)
    bone_count_max: int = 0
    shadow_batch_count: int = 0
    had_legion_header: bool = False

    @property
    def triangle_count(self) -> int:
        return len(self.indices) // 3


def _array(data: bytes, pos: int) -> tuple[int, int]:
    return struct.unpack_from("<II", data, pos)


def _read_u16s(data: bytes, count: int, offset: int, what: str, name: str) -> list[int]:
    if count == 0:
        return []
    end = offset + count * 2
    if offset <= 0 or end > len(data):
        raise MalformedFileError(
            f"{name}: {what}[{count}] at {offset} runs past end of file")
    return list(struct.unpack_from("<" + "H" * count, data, offset))


def _read_blobs(data: bytes, count: int, offset: int, size: int,
                what: str, name: str) -> list[bytes]:
    if count == 0:
        return []
    end = offset + count * size
    if offset <= 0 or end > len(data):
        raise MalformedFileError(
            f"{name}: {what}[{count}] at {offset} runs past end of file")
    return [data[offset + i * size : offset + (i + 1) * size] for i in range(count)]


def _looks_like_legion(data: bytes) -> bool:
    """Decide between the 48- and 56-byte header.

    The five arrays are the same in both layouts, so the only difference is
    whether the eight bytes at 0x30 are a shadow-batch ``M2Array`` or the start
    of the payload.  Data that begins at exactly 48 settles it; otherwise the
    candidate array is checked for plausibility.
    """
    offsets = []
    for i in range(5):
        count, offset = _array(data, 4 + i * 8)
        if count:
            offsets.append(offset)
    if offsets and min(offsets) <= SKIN_HEADER_SIZE_WOTLK:
        return False
    if len(data) < SKIN_HEADER_SIZE_LEGION:
        return False
    count, offset = _array(data, 0x30)
    if count == 0:
        # Ambiguous. Treat a payload that starts at 56 as the Legion layout.
        return bool(offsets) and min(offsets) >= SKIN_HEADER_SIZE_LEGION
    return offset >= SKIN_HEADER_SIZE_LEGION and \
        offset + count * SHADOW_BATCH_SIZE <= len(data)


def parse_skin(data: bytes, name: str = "<skin>") -> Skin:
    if len(data) < SKIN_HEADER_SIZE_WOTLK:
        raise MalformedFileError(f"{name}: file is only {len(data)} bytes")
    magic = data[:4].decode("latin-1")
    if magic != SKIN_MAGIC:
        raise UnsupportedFormatError(f"{name}: not a .skin file (magic {magic!r})")

    skin = Skin()
    vc, vo = _array(data, 0x04)
    ic, io = _array(data, 0x0C)
    bc, bo = _array(data, 0x14)
    sc, so = _array(data, 0x1C)
    ac, ao = _array(data, 0x24)
    skin.bone_count_max = struct.unpack_from("<I", data, 0x2C)[0]

    skin.vertices = _read_u16s(data, vc, vo, "vertices", name)
    skin.indices = _read_u16s(data, ic, io, "indices", name)
    if bc:
        end = bo + bc * 4
        if bo <= 0 or end > len(data):
            raise MalformedFileError(f"{name}: bone table runs past end of file")
        skin.bones = data[bo:end]
    skin.submeshes = _read_blobs(data, sc, so, SUBMESH_SIZE, "submeshes", name)
    skin.batches = _read_blobs(data, ac, ao, BATCH_SIZE, "batches", name)

    if _looks_like_legion(data):
        skin.had_legion_header = True
        shc, _sho = _array(data, 0x30)
        skin.shadow_batch_count = shc
    return skin


def write_skin(skin: Skin) -> bytes:
    """Serialise as a 48-byte-header 3.3.5a skin."""
    w = Writer()
    w.magic(SKIN_MAGIC)
    heads = [w.reserve(8) for _ in range(5)]
    w.u32(skin.bone_count_max)
    assert w.tell() == SKIN_HEADER_SIZE_WOTLK

    def emit(head: int, count: int, payload: bytes) -> None:
        w.align(4)
        w.patch_u32(head, count)
        w.patch_u32(head + 4, w.tell())
        w.raw(payload)

    emit(heads[0], len(skin.vertices),
         struct.pack("<" + "H" * len(skin.vertices), *skin.vertices))
    emit(heads[1], len(skin.indices),
         struct.pack("<" + "H" * len(skin.indices), *skin.indices))
    emit(heads[2], len(skin.bones) // 4, skin.bones)
    emit(heads[3], len(skin.submeshes), b"".join(skin.submeshes))
    emit(heads[4], len(skin.batches), b"".join(skin.batches))
    return w.getvalue()


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------
def _clamp_batches(skin: Skin, uses_combiner_combos: bool,
                   result: FileResult) -> None:
    too_many_textures = 0
    bad_shader = 0
    out: list[bytes] = []
    for raw in skin.batches:
        b = bytearray(raw)
        shader_id = struct.unpack_from("<H", b, BATCH_SHADER_ID)[0]
        texture_count = struct.unpack_from("<H", b, BATCH_TEXTURE_COUNT)[0]

        if texture_count > M2_MAX_TEXTURE_UNITS:
            too_many_textures += 1
            struct.pack_into("<H", b, BATCH_TEXTURE_COUNT, M2_MAX_TEXTURE_UNITS)

        if shader_id & SHADER_COMBINER_FLAG:
            if not uses_combiner_combos:
                # The batch points into a combiner table the model does not
                # carry; 3.3.5a would index off the end of the header.
                bad_shader += 1
                struct.pack_into("<H", b, BATCH_SHADER_ID, 0)
        elif shader_id > 0xFF:
            bad_shader += 1
            struct.pack_into("<H", b, BATCH_SHADER_ID, 0)
        out.append(bytes(b))
    skin.batches = out

    if too_many_textures:
        result.lossy("skin.batch.textures",
                     f"{too_many_textures} batch(es) sampled more than "
                     f"{M2_MAX_TEXTURE_UNITS} textures; extra units dropped",
                     batches=too_many_textures)
    if bad_shader:
        result.lossy("skin.batch.shader",
                     f"{bad_shader} batch(es) referenced a shader 3.3.5a does "
                     f"not have; reset to the default combiner",
                     batches=bad_shader)


def _validate_submeshes(skin: Skin, opts: Options, result: FileResult) -> None:
    over_bones = 0
    over_influences = 0
    over_indices = 0
    for _i, raw in enumerate(skin.submeshes):
        (_sid, _level, vertex_start, vertex_count, _istart, _index_count,
         bone_count, _bone_combo, influences, _center) = struct.unpack_from(
            "<10H", raw, 0)
        if bone_count > M2_MAX_BONES_PER_SUBMESH:
            over_bones += 1
        if influences > M2_MAX_BONE_INFLUENCES:
            over_influences += 1
        if vertex_start + vertex_count > M2_MAX_VERTICES + 1:
            over_indices += 1
    if over_indices:
        result.lossy("skin.limit.submesh_range",
                     f"{over_indices} submesh(es) address vertices past the "
                     f"end of the 16-bit range", submeshes=over_indices)
    if over_bones:
        msg = (f"{over_bones} submesh(es) reference more than "
               f"{M2_MAX_BONES_PER_SUBMESH} bones in one draw call; 3.3.5a will "
               f"render them with the wrong transforms. Split the mesh in a "
               f"model editor before shipping it")
        if opts.strict_limits:
            result.fail("skin.limit.bones", msg, submeshes=over_bones)
        else:
            result.lossy("skin.limit.bones", msg, submeshes=over_bones)
    if over_influences:
        result.lossy("skin.limit.influences",
                     f"{over_influences} submesh(es) declare more than "
                     f"{M2_MAX_BONE_INFLUENCES} bone influences per vertex",
                     submeshes=over_influences)


#: The bone palette sizes 3.3.5a's skins declare.  Every one of its 23,941
#: skins names the smallest of these that holds its largest submesh's bones
#: (41 name a larger one); retail writes 0 in all of them.
BONE_PALETTE_SIZES = (21, 53, 64, 256)


def _settle_bone_count_max(skin: Skin, res: FileResult) -> None:
    """Declare a bone palette that holds every submesh's bones."""
    needed = max((struct.unpack_from("<H", raw, 12)[0] for raw in skin.submeshes),
                 default=0)
    if skin.bone_count_max >= needed and skin.bone_count_max:
        return
    size = next((s for s in BONE_PALETTE_SIZES if s >= needed), BONE_PALETTE_SIZES[-1])
    res.info("skin.bone_count_max",
             f"declared a bone palette of {size} (the source said "
             f"{skin.bone_count_max}; its largest submesh uses {needed} bones)",
             source=skin.bone_count_max, written=size)
    skin.bone_count_max = size


def downgrade_skin(skin: Skin, opts: Options, uses_combiner_combos: bool,
                   res: FileResult) -> bool:
    """Apply the 3.3.5a clamps to an already-parsed skin. False if unusable."""
    if len(skin.vertices) > M2_MAX_VERTICES:
        res.fail("skin.limit.vertices",
                 f"{len(skin.vertices)} vertices exceeds the 16-bit index limit "
                 f"of {M2_MAX_VERTICES}", vertices=len(skin.vertices))
        return False

    if skin.shadow_batch_count:
        res.lossy("skin.shadow_batches",
                  f"dropped {skin.shadow_batch_count} shadow batch(es); 3.3.5a "
                  f"draws model shadows from a blob texture instead",
                  batches=skin.shadow_batch_count)
        skin.shadow_batch_count = 0

    _clamp_batches(skin, uses_combiner_combos, res)
    _validate_submeshes(skin, opts, res)
    _settle_bone_count_max(skin, res)
    return res.ok


def convert_skin(data: bytes, source_name: str, opts: Options,
                 uses_combiner_combos: bool = False,
                 result: FileResult | None = None) -> tuple[bytes, FileResult]:
    res = result or FileResult(source=source_name, kind="skin")
    res.kind = "skin"
    res.bytes_in = len(data)

    skin = parse_skin(data, source_name)
    was_legion = skin.had_legion_header
    res.source_version = (f"SKIN {'legion' if was_legion else 'wotlk'} "
                          f"{len(skin.vertices)} verts, {skin.triangle_count} tris, "
                          f"{len(skin.submeshes)} submeshes")

    if not downgrade_skin(skin, opts, uses_combiner_combos, res):
        return b"", res

    out = write_skin(skin)
    res.bytes_out = len(out)
    res.target_version = f"SKIN wotlk {len(skin.vertices)} verts"
    if not was_legion and res.status is Status.OK:
        # Already a Wrath-shaped skin; it was only normalised, not downgraded.
        res.status = Status.PASSTHROUGH
        res.info("skin.passthrough", "already a 3.3.5a skin layout")
    return out, res


def inspect_skin(data: bytes, source_name: str) -> dict:
    skin = parse_skin(data, source_name)
    return {
        "kind": "skin",
        "header": "legion" if skin.had_legion_header else "wotlk",
        "vertices": len(skin.vertices),
        "triangles": skin.triangle_count,
        "submeshes": len(skin.submeshes),
        "batches": len(skin.batches),
        "shadow_batches": skin.shadow_batch_count,
        "bone_count_max": skin.bone_count_max,
    }
