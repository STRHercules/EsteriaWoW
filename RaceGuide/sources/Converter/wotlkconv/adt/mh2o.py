"""Terrain liquids (``MH2O``).

The chunk kept its shape from Wrath to now: a header per map chunk, then
liquid instances, each with an optional exists-bitmap and a block of vertex
data.  What changed is the second word of an instance.  In 3.3.5a it is the
*liquid vertex format* (LVF), which says what the vertex block holds:

====  ===================================  ===============
LVF   per vertex                           bytes
====  ===================================  ===============
0     height (float) + depth (u8)          5
1     height (float) + UV (2 x u16)        8
2     depth (u8)                           1
3     height + UV + depth (Cataclysm on)   9
====  ===================================  ===============

From Warlords of Draenor on, a value of 42 or more is a ``LiquidObject`` id
instead, and the format has to be looked up: Ocean (liquid type 2) is always
depth-only, and every other type uses the vertex format of its
``LiquidMaterial``.  Nearly every retail instance is written that way, so an
old reader takes an object id for a format it has never heard of.  (Both
halves of that rule were checked against the vertex block sizes of 94,000
retail instances; every one agreed.)

3.3.5a only knows formats 0 to 2, and picks between them by the kind of
liquid, as its own Northrend tiles and Noggit's writer both show: magma and
slime carry UVs (1), ocean lying flat at height 0 is depth-only (2), and
everything else is height and depth (0).  So each instance is decoded in its
retail format and re-encoded in the one 3.3.5a expects for its liquid, with a
missing height filled from the instance's minimum, a missing depth as fully
deep and missing UVs laid out the way Noggit lays out new ones.  The liquid
type id itself is kept; the converted ``LiquidType.dbc`` carries every retail
type.

A tile whose instances already use 3.3.5a formats is left byte for byte.
"""

from __future__ import annotations

import dataclasses
import struct

from ..report import FileResult

LVF_HEIGHT_DEPTH = 0
LVF_HEIGHT_UV = 1
LVF_DEPTH = 2
LVF_HEIGHT_UV_DEPTH = 3
#: Bytes of vertex data per vertex, by format.
VERTEX_BYTES = {LVF_HEIGHT_DEPTH: 5, LVF_HEIGHT_UV: 8, LVF_DEPTH: 1,
                LVF_HEIGHT_UV_DEPTH: 9}
#: The highest format 3.3.5a reads.
WRATH_MAX_LVF = LVF_DEPTH
#: From here on an instance's second word is a LiquidObject id.
FIRST_LIQUID_OBJECT = 42
#: The one liquid type whose format does not come from its material.
OCEAN_LIQUID_TYPE = 2

#: LiquidType.SoundBank, the basic kind of liquid.
BASIC_WATER, BASIC_OCEAN, BASIC_MAGMA, BASIC_SLIME = 0, 1, 2, 3

HEADER = struct.Struct("<III")          # instances, layer count, attributes
INSTANCE = struct.Struct("<HHffBBBBII")
ATTRIBUTES_SIZE = 16
MAP_CHUNKS = 256
#: Vertex block sizes can carry up to 3 bytes of alignment padding.
PADDING = 4


@dataclasses.dataclass(frozen=True, slots=True)
class LiquidTypes:
    """What converting a liquid needs to know about each liquid type."""

    #: LiquidType id -> SoundBank (the basic kind of liquid).
    basic: dict[int, int]
    #: LiquidType id -> its material's vertex format.
    vertex_format: dict[int, int]

    @classmethod
    def from_tables(cls, tables) -> LiquidTypes | None:
        types = tables.get("LiquidType")
        materials = tables.get("LiquidMaterial")
        if types is None or materials is None:
            return None
        lvf = {int(mid): row.get("LVF") for mid, row in materials.rows.items()}
        basic: dict[int, int] = {}
        formats: dict[int, int] = {}
        for tid, row in types.rows.items():
            if row.get("SoundBank") is not None:
                basic[int(tid)] = int(row["SoundBank"])
            fmt = lvf.get(row.get("MaterialID"))
            if fmt is not None:
                formats[int(tid)] = int(fmt)
        return cls(basic, formats)


@dataclasses.dataclass(slots=True)
class _Instance:
    liquid_type: int
    field: int
    minimum: float
    maximum: float
    x: int
    y: int
    width: int
    height: int
    bitmap: bytes
    heights: bytes | None = None
    uvs: bytes | None = None
    depths: bytes | None = None
    has_vertices: bool = False

    @property
    def vertices(self) -> int:
        return (self.width + 1) * (self.height + 1)


def source_format(liquid_type: int, field: int,
                  liquid_types: LiquidTypes | None) -> int | None:
    """The vertex format a retail instance was written in, if it can be told."""
    if field < FIRST_LIQUID_OBJECT:
        return field if field in VERTEX_BYTES else None
    if liquid_type == OCEAN_LIQUID_TYPE:
        return LVF_DEPTH
    if liquid_types is not None:
        return liquid_types.vertex_format.get(liquid_type)
    return None


def wrath_format(basic: int | None, source: int | None,
                 minimum: float, maximum: float) -> int:
    """The format 3.3.5a expects for this kind of liquid."""
    if basic is None:
        # No LiquidType to ask: the data's own shape says what it was.
        if source in (LVF_HEIGHT_UV, LVF_HEIGHT_UV_DEPTH):
            basic = BASIC_MAGMA
        elif source == LVF_DEPTH:
            basic = BASIC_OCEAN
        else:
            basic = BASIC_WATER
    if basic in (BASIC_MAGMA, BASIC_SLIME):
        return LVF_HEIGHT_UV
    if basic == BASIC_OCEAN and minimum == 0.0 and maximum == 0.0:
        return LVF_DEPTH
    return LVF_HEIGHT_DEPTH


def _split_vertices(block: bytes, fmt: int, n: int):
    at = 0
    heights = uvs = depths = None
    if fmt in (LVF_HEIGHT_DEPTH, LVF_HEIGHT_UV, LVF_HEIGHT_UV_DEPTH):
        heights, at = block[at:at + 4 * n], at + 4 * n
    if fmt in (LVF_HEIGHT_UV, LVF_HEIGHT_UV_DEPTH):
        uvs, at = block[at:at + 4 * n], at + 4 * n
    if fmt in (LVF_HEIGHT_DEPTH, LVF_DEPTH, LVF_HEIGHT_UV_DEPTH):
        depths = block[at:at + n]
    return heights, uvs, depths


def _loses_data(inst: _Instance, fmt: int) -> bool:
    """Whether writing the instance in ``fmt`` leaves some of its data out."""
    return bool((inst.heights and fmt == LVF_DEPTH)
                or (inst.uvs and fmt != LVF_HEIGHT_UV)
                or (inst.depths and fmt == LVF_HEIGHT_UV))


def _default_uvs(inst: _Instance) -> bytes:
    out = bytearray()
    for z in range(inst.y, inst.y + inst.height + 1):
        for x in range(inst.x, inst.x + inst.width + 1):
            out += struct.pack("<HH", int(x / 4 * 255), int(z / 4 * 255))
    return bytes(out)


def _encode_vertices(inst: _Instance, fmt: int) -> bytes:
    n = inst.vertices
    heights = inst.heights or struct.pack(f"<{n}f", *([inst.minimum] * n))
    depths = inst.depths or b"\xff" * n
    if fmt == LVF_HEIGHT_UV:
        return heights + (inst.uvs or _default_uvs(inst))
    if fmt == LVF_DEPTH:
        return depths
    return heights + depths


def convert_mh2o(payload: bytes, liquid_types: LiquidTypes | None,
                 result: FileResult) -> bytes:
    """Re-encode every liquid instance in a vertex format 3.3.5a reads."""
    if len(payload) < MAP_CHUNKS * HEADER.size:
        result.warn("adt.liquid.truncated",
                    f"MH2O is {len(payload)} bytes, too short for its "
                    f"{MAP_CHUNKS} chunk headers; dropped")
        return b""

    headers = [HEADER.unpack_from(payload, i * HEADER.size)
               for i in range(MAP_CHUNKS)]
    raw: list[list[tuple]] = []
    for offset, layers, _attributes in headers:
        if layers and offset + layers * INSTANCE.size > len(payload):
            result.warn("adt.liquid.truncated",
                        "an MH2O instance table runs past the end of the "
                        "chunk; the tile's liquid was dropped")
            return b""
        raw.append([INSTANCE.unpack_from(payload, offset + k * INSTANCE.size)
                    for k in range(layers)])

    if all(inst[1] <= WRATH_MAX_LVF for chunk in raw for inst in chunk):
        return payload

    # Where each block starts, so a vertex block's extent can be checked.
    starts = {len(payload)}
    for (offset, layers, attributes), chunk in zip(headers, raw):
        if layers:
            starts.add(offset)
        if attributes:
            starts.add(attributes)
        for inst in chunk:
            starts.update(o for o in inst[8:10] if o)
    ordered = sorted(starts)

    def room(offset: int) -> int:
        for start in ordered:
            if start > offset:
                return start - offset
        return 0

    counts = {"objects": 0, "unreadable": 0, "reshaped": 0}
    chunks: list[tuple[list[_Instance], bytes]] = []
    for (_offset, _layers, attributes), chunk in zip(headers, raw):
        attrs = payload[attributes:attributes + ATTRIBUTES_SIZE] if attributes else b""
        converted = []
        for (ltype, field, lo, hi, x, y, w, h, bitmap_at, vertices_at) in chunk:
            bits = (w * h + 7) // 8
            inst = _Instance(ltype, field, lo, hi, x, y, w, h,
                             payload[bitmap_at:bitmap_at + bits] if bitmap_at else b"")
            if field >= FIRST_LIQUID_OBJECT:
                counts["objects"] += 1
            fmt = source_format(ltype, field, liquid_types)
            if vertices_at:
                space = room(vertices_at)
                n = inst.vertices
                if fmt is None or VERTEX_BYTES[fmt] * n > space:
                    fits = [f for f, per in VERTEX_BYTES.items()
                            if 0 <= space - per * n < PADDING]
                    fmt = fits[0] if len(fits) == 1 else None
                if fmt is None:
                    counts["unreadable"] += 1
                else:
                    inst.heights, inst.uvs, inst.depths = _split_vertices(
                        payload[vertices_at:vertices_at + VERTEX_BYTES[fmt] * n],
                        fmt, n)
                    inst.has_vertices = True
            basic = liquid_types.basic.get(ltype) if liquid_types else None
            if basic is None and ltype == OCEAN_LIQUID_TYPE:
                basic = BASIC_OCEAN
            inst.field = wrath_format(basic, fmt, lo, hi)
            if inst.has_vertices and _loses_data(inst, inst.field):
                counts["reshaped"] += 1
            converted.append(inst)
        chunks.append((converted, attrs))

    out = bytearray(MAP_CHUNKS * HEADER.size)
    for index, (instances, attrs) in enumerate(chunks):
        if not instances:
            continue
        table_at = len(out)
        out += bytes(INSTANCE.size * len(instances))
        attrs_at = 0
        if attrs:
            attrs_at = len(out)
            out += attrs
        HEADER.pack_into(out, index * HEADER.size, table_at, len(instances),
                         attrs_at)
        for k, inst in enumerate(instances):
            bitmap_at = 0
            if inst.bitmap:
                bitmap_at = len(out)
                out += inst.bitmap
            vertices_at = 0
            if inst.has_vertices:
                vertices_at = len(out)
                out += _encode_vertices(inst, inst.field)
            INSTANCE.pack_into(out, table_at + k * INSTANCE.size,
                               inst.liquid_type, inst.field, inst.minimum,
                               inst.maximum, inst.x, inst.y, inst.width,
                               inst.height, bitmap_at, vertices_at)

    result.info("adt.liquid.converted",
                f"re-encoded the tile's liquid in 3.3.5a vertex formats; "
                f"{counts['objects']} instance(s) named a LiquidObject where "
                f"3.3.5a reads a format", **counts)
    if counts["reshaped"]:
        result.lossy("adt.liquid.reshaped",
                      f"{counts['reshaped']} liquid instance(s) stored vertex "
                      f"data the 3.3.5a format for their liquid has no room "
                      f"for (UVs on water, depth on magma); that part was "
                      f"left out", instances=counts["reshaped"])
    if counts["unreadable"]:
        result.lossy("adt.liquid.flat",
                      f"{counts['unreadable']} liquid instance(s) had vertex "
                      f"data in a format that could not be determined; they "
                      f"lie flat at their minimum height",
                      instances=counts["unreadable"])
    return bytes(out)
