"""LiquidType textures and materials 3.3.5a can draw.

3.3.5a animates a liquid from ``Texture[0]``, a ``%d`` pattern it fills in
with frames 1 to 30 -- every animation in its own archives has exactly those
thirty -- and draws it with one of three LiquidMaterials: water, magma or
procedural water.  Legion rebuilt liquids around new materials that take a set
of still textures (shallow, deep, specular, shore, emissive), so most retail
liquid types have no animation in ``Texture[0]`` at all, and a few have one
whose frames are not all the same size.  3.3.5a (and Noggit, which loads the
frames as one texture array) cannot use either.

A type whose animation is complete keeps its textures and, if 3.3.5a has it,
its material.  Any other type gets the textures and material of the 3.3.5a
liquid of the same kind (``SoundBank``: water, ocean, magma, slime), taken from
the client's own first four LiquidType rows.
"""

from __future__ import annotations

import struct
from typing import Any

from ..listfile import normalise

FRAMES = 30
#: 3.3.5a's own textures for each basic kind of liquid, LiquidType rows 1-4.
WRATH_TEXTURES = {
    0: ("XTextures\\river\\lake_a.%d.blp", "proceduralRiverDepthTex", "", "", "", ""),
    1: ("XTextures\\ocean\\ocean_h.%d.blp", "proceduralOceanDepthTex", "", "", "", ""),
    2: ("XTextures\\lava\\lava.%d.blp", "", "", "", "", ""),
    3: ("XTextures\\slime\\slime.%d.blp", "", "", "", "", ""),
}
#: LiquidMaterial ids 3.3.5a ships: water, magma, procedural water.
WRATH_MATERIALS = (1, 2, 3)
MAGMA_KINDS = (2, 3)


class LiquidTextures:
    """Decides, per LiquidType row, whether its own textures are drawable."""

    def __init__(self, listfile, storage=None):
        self.listfile = listfile
        self.storage = storage
        self._animations: dict[str, bool] = {}

    def _frame_size(self, path: str):
        file_id = self.listfile.id_for(normalise(path)) if self.listfile else None
        if file_id is None:
            return None
        if self.storage is None:
            return ()
        if file_id not in self.storage:
            return None
        data, _why = self.storage.try_read_file_id(file_id)
        if data is None or len(data) < 20:
            return None
        return struct.unpack_from("<II", data, 12)

    def complete_animation(self, pattern: str) -> bool:
        """All thirty frames exist, and at one size."""
        if "%d" not in pattern:
            return False
        if pattern not in self._animations:
            sizes = set()
            complete = True
            for frame in range(1, FRAMES + 1):
                size = self._frame_size(pattern.replace("%d", str(frame)))
                if size is None:
                    complete = False
                    break
                sizes.add(size)
            self._animations[pattern] = complete and len(sizes) <= 1
        return self._animations[pattern]

    def usable(self, row: dict[str, Any]) -> bool:
        textures = row.get("Texture") or []
        return bool(textures) and self.complete_animation(str(textures[0] or ""))

    def textures(self, row: dict[str, Any]) -> tuple[str, ...]:
        if self.usable(row):
            own = [str(t or "") for t in row.get("Texture") or []]
            return tuple((own + [""] * 6)[:6])
        return WRATH_TEXTURES.get(int(row.get("SoundBank") or 0), WRATH_TEXTURES[0])

    def material(self, row: dict[str, Any]) -> int:
        material = int(row.get("MaterialID") or 0)
        if self.usable(row) and material in WRATH_MATERIALS:
            return material
        return 2 if row.get("SoundBank") in MAGMA_KINDS else 1


def textures_for(ctx: Any) -> LiquidTextures:
    if "liquidtextures" not in ctx.cache:
        storage = getattr(ctx.tables, "storage", None) if ctx.tables else None
        ctx.cache["liquidtextures"] = LiquidTextures(ctx.listfile, storage)
    return ctx.cache["liquidtextures"]


RESOLVERS = {
    "liquid.material": lambda row, ctx: textures_for(ctx).material(row),
    "liquid.texture": lambda row, ctx, index=0: textures_for(ctx).textures(row)[index],
}
