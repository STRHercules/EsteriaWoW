"""Which UV set each texture unit of a batch samples.

3.3.5a answers that through the model's ``textureCoordCombos`` table (the
"texture unit lookup"): a batch names a run of ``textureCount`` entries
starting at ``textureCoordComboIndex``, and each entry says 0 for the first UV
set, 1 for the second, or -1 for sphere-mapped environment coordinates.  The
client builds the batch's shader from those values and never checks the index.

Retail stopped using the table.  The vertex shader is chosen from the batch's
shader id instead, the table is written empty, and a batch's index is 0 or
0xFFFF -- past the end of it either way.  A converted model that kept that
would have 3.3.5a read whatever bytes follow the table as UV selectors, and
Noggit logs every such batch and substitutes its own guess.

So when a batch's run is out of range, the run it needs is worked out and the
batch pointed at it, appending to the table only what is not already there.
For a batch whose shader id carries the 0x8000 flag the retail shader table
names the vertex shader, which spells the units out (``Diffuse_T1_Env`` is UV
set 0 then environment mapping).  Any other batch gets the plain reading the
old client used by default: the first unit on UV set 0, the second on UV
set 1.  Batches already in range are left exactly as they are.
"""

from __future__ import annotations

import struct

from ..limits import M2_MAX_TEXTURE_UNITS
from ..report import FileResult
from .model import M2Model
from .skin import (
    BATCH_SHADER_ID,
    BATCH_TEXTURE_COORD_COMBO,
    BATCH_TEXTURE_COUNT,
    SHADER_COMBINER_FLAG,
    Skin,
)

#: Lookup values: UV set 0, UV set 1, sphere-mapped environment coordinates.
T1, T2, ENV = 0, 1, 0xFFFF

#: Retail vertex shaders, by id, as the texture-unit sources they read.  3.3.5a
#: has no third UV set and draws at most two units, so a third unit is omitted.
VERTEX_SHADER_UNITS = {
    0: (T1,),              # Diffuse_T1
    1: (ENV,),             # Diffuse_Env
    2: (T1, T2),           # Diffuse_T1_T2
    3: (T1, ENV),          # Diffuse_T1_Env
    4: (ENV, T1),          # Diffuse_Env_T1
    5: (ENV, ENV),         # Diffuse_Env_Env
    6: (T1, ENV, T1),      # Diffuse_T1_Env_T1
    7: (T1, T1),           # Diffuse_T1_T1
    8: (T1, T1, T1),       # Diffuse_T1_T1_T1
    9: (T1,),              # Diffuse_EdgeFade_T1
    10: (T2,),             # Diffuse_T2
    11: (T1, ENV, T2),     # Diffuse_T1_Env_T2
    12: (T1, T2),          # Diffuse_EdgeFade_T1_T2
    13: (ENV,),            # Diffuse_EdgeFade_Env
    14: (T1, T2, T1),      # Diffuse_T1_T2_T1
    15: (T1, T2),          # Diffuse_T1_T2_T3
    16: (T1, T2),          # Color_T1_T2_T3
    17: (T1,),             # BW_Diffuse_T1
    18: (T1, T2),          # BW_Diffuse_T1_T2
}

#: The vertex shader of each entry in retail's M2 shader table, which a batch
#: shader id with the 0x8000 flag indexes.
SHADER_TABLE_VERTEX = (
    3, 3, 3, 6, 3, 7, 7, 3, 3, 6, 7, 3, 3, 3, 7, 2, 3, 6,
    0, 9, 11, 12, 2, 7, 11, 13, 14, 2, 14, 7, 15, 16, 0, 12, 9, 12,
)


def batch_units(shader_id: int, texture_count: int) -> tuple[int, ...]:
    """The lookup run a batch needs, as many entries as units 3.3.5a draws."""
    count = max(1, min(texture_count, M2_MAX_TEXTURE_UNITS))
    index = shader_id & ~SHADER_COMBINER_FLAG
    if shader_id & SHADER_COMBINER_FLAG and index < len(SHADER_TABLE_VERTEX):
        units = VERTEX_SHADER_UNITS[SHADER_TABLE_VERTEX[index]]
        # A shader with fewer coordinate outputs than textures samples the
        # extra textures with the last one it has.
        return (units + units[-1:] * count)[:count]
    return (T1, T2)[:count]


def _find_run(table: list[int], run: tuple[int, ...]) -> int:
    for start in range(len(table) - len(run) + 1):
        if tuple(table[start:start + len(run)]) == run:
            return start
    return -1


def assign_texture_coord_combos(model: M2Model, skins: dict[int, Skin],
                                result: FileResult) -> None:
    """Point every batch at a lookup run inside the model's table.

    Must run before the skins are downgraded, while batches still carry the
    shader id the retail vertex shader is read from.
    """
    table = list(model.texture_coord_combos)
    # Judge each batch against the table it was written for, not the entries
    # appended for the batches before it.
    original = len(table)
    repointed = 0
    seen: set[int] = set()
    for skin in skins.values():
        if id(skin) in seen:
            continue
        seen.add(id(skin))
        batches = []
        for raw in skin.batches:
            shader_id, = struct.unpack_from("<H", raw, BATCH_SHADER_ID)
            count, = struct.unpack_from("<H", raw, BATCH_TEXTURE_COUNT)
            start, = struct.unpack_from("<H", raw, BATCH_TEXTURE_COORD_COMBO)
            drawn = max(1, min(count, M2_MAX_TEXTURE_UNITS))
            if start + drawn <= original:
                batches.append(raw)
                continue
            run = batch_units(shader_id, count)
            at = _find_run(table, run)
            if at < 0:
                at = len(table)
                table.extend(run)
            batch = bytearray(raw)
            struct.pack_into("<H", batch, BATCH_TEXTURE_COORD_COMBO, at)
            batches.append(bytes(batch))
            repointed += 1
        skin.batches = batches
    if repointed:
        # A split piece shares its lists with the model it came from.
        model.texture_coord_combos = table
        result.info("m2.texture_coord_combos.rebuilt",
                    f"pointed {repointed} batch(es) whose texture coordinate "
                    f"lookup ran past the model's table (retail leaves it "
                    f"empty) at entries built from their shaders",
                    batches=repointed, entries=len(table))
