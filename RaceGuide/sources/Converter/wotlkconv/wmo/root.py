"""WMO root files.

The nominal version never moved off 17, which makes modern WMOs look
deceptively compatible.  What actually changed is where the *references* live:

* ``MODI`` replaced ``MODN`` -- doodads are FileDataIDs, not filenames, and
  ``MODD.nameIndex`` became an index into that array instead of a byte offset.
* ``MOSI`` replaced ``MOSB`` for the skybox.
* ``GFID`` lists the group files by FileDataID, where 3.3.5a globs for
  ``<root>_000.wmo`` .. ``<root>_NNN.wmo`` next to the root.
* When ``MOTX`` is absent, ``SMOMaterial``'s texture fields hold FileDataIDs
  directly rather than byte offsets into it.

Add a pile of Legion/BfA-only chunks the old parser would choke on, and the
conversion is: rebuild the string tables, repoint everything at them, clamp the
material shaders, and drop what is left.
"""

from __future__ import annotations

import dataclasses
import struct

from ..chunks import Chunk, ChunkReader
from ..errors import MalformedFileError, UnsupportedFormatError
from ..limits import (
    MOHD_SIZE,
    WMO_ROOT_CHUNKS_KNOWN,
    WMO_VERSION,
)

#: Post-Wrath root chunks, with what each one carries.
MODERN_ROOT_CHUNKS = {
    "GFID": "group file data IDs",
    "MODI": "doodad file data IDs",
    "MOSI": "skybox file data ID",
    "MOUV": "animated texture UV scroll rates",
    "MAVG": "global ambient volumes",
    "MAVD": "ambient volumes",
    "MBVD": "box volumes",
    "MFED": "fog extra data",
    "MLSP": "light spline points",
    "MLSK": "light skybox references",
    "MLSO": "spot light animations",
    "MOLS": "spot lights",
    "MOLP": "point lights",
    "MOP2": "extended portal data",
    "MPVD": "particulate volumes",
    "MNLD": "new light definitions",
    "MDDI": "doodad extra instance data",
    "MPY2": "extended material references",
    "MOLM": "lightmap texel data",
    "MOLD": "lightmap definitions",
    "MOMX": "extended material data",
    "MOTA": "tangent arrays",
    "MOPB": "prepass batches",
    "MOQG": "query face flags",
    "MOSB2": "secondary skybox",
    "MGI2": "group LOD assignments",
    "MOPE": "extra portal data",
    "MDDL": "detail doodad layers",
    "MOLV": "light direction volumes",
}

#: The chunks that were actually reachable in ``ALL_KNOWN`` for auto-detection.
ALL_KNOWN = set(WMO_ROOT_CHUNKS_KNOWN) | set(MODERN_ROOT_CHUNKS)


@dataclasses.dataclass
class WmoRoot:
    version: int = WMO_VERSION
    chunks: dict[str, list[Chunk]] = dataclasses.field(default_factory=dict)
    reverse_magic: bool = True

    n_textures: int = 0
    n_groups: int = 0
    n_doodad_names: int = 0
    n_doodad_defs: int = 0
    header_flags: int = 0
    num_lod: int = 0

    def first(self, name: str) -> Chunk | None:
        entries = self.chunks.get(name)
        return entries[0] if entries else None

    def payload(self, name: str) -> bytes:
        chunk = self.first(name)
        return chunk.data if chunk else b""


def parse_root(data: bytes, name: str = "<wmo>") -> WmoRoot:
    if len(data) < 8:
        raise MalformedFileError(f"{name}: file is only {len(data)} bytes")
    reader = ChunkReader.auto(data, ALL_KNOWN, name=name)
    root = WmoRoot(reverse_magic=reader.reverse)
    for chunk in reader:
        root.chunks.setdefault(chunk.name, []).append(chunk)

    if "MOHD" not in root.chunks:
        raise UnsupportedFormatError(f"{name}: not a WMO root (no MOHD chunk)")

    mver = root.first("MVER")
    if mver and len(mver.data) >= 4:
        root.version = struct.unpack_from("<I", mver.data, 0)[0]

    mohd = root.first("MOHD")
    if len(mohd.data) < MOHD_SIZE:
        raise MalformedFileError(f"{name}: MOHD is {len(mohd.data)} bytes, expected "
                                 f"{MOHD_SIZE}")
    (root.n_textures, root.n_groups, _n_portals, _n_lights, root.n_doodad_names,
     root.n_doodad_defs, _n_sets) = struct.unpack_from("<7I", mohd.data, 0)
    # Wrath reads one uint32 of flags here; Legion split it into flags + numLod.
    flags_word = struct.unpack_from("<I", mohd.data, 60)[0]
    root.header_flags = flags_word & 0xFFFF
    root.num_lod = (flags_word >> 16) & 0xFFFF
    return root


# ---------------------------------------------------------------------------
# String tables
# ---------------------------------------------------------------------------
def split_string_table(blob: bytes) -> dict[int, str]:
    """Map each byte offset in a MOTX/MODN blob to the string starting there."""
    out: dict[int, str] = {}
    start = 0
    for i, byte in enumerate(blob):
        if byte == 0:
            if i > start:
                out[start] = blob[start:i].decode("latin-1")
            start = i + 1
    if start < len(blob):
        out[start] = blob[start:].decode("latin-1")
    return out


class StringTable:
    """Builds a MOTX/MODN blob and hands back each entry's byte offset."""

    def __init__(self) -> None:
        self.buf = bytearray()
        self._offsets: dict[str, int] = {}

    def add(self, text: str) -> int:
        key = text.lower()
        hit = self._offsets.get(key)
        if hit is not None:
            return hit
        offset = len(self.buf)
        self.buf += text.encode("latin-1") + b"\0"
        # Blizzard pads entries so the next one starts on a 4-byte boundary.
        while len(self.buf) % 4:
            self.buf += b"\0"
        self._offsets[key] = offset
        return offset

    @property
    def count(self) -> int:
        return len(self._offsets)

    def getvalue(self) -> bytes:
        return bytes(self.buf) if self.buf else b"\0" * 4
