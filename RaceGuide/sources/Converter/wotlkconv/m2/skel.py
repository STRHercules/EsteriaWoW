"""Legion+ ``.skel`` skeleton files.

From Legion onwards Blizzard hoisted the shared parts of a model -- bones, key
bone lookups, attachments, global loops and the sequence table -- out of the M2
and into a ``.skel`` file referenced by the ``SKID`` chunk, so that every
variant of a race or creature could share one rig.  A 3.3.5a M2 has nowhere to
put that: the client reads bones and sequences straight out of the model.  So
converting any Legion-era character model means folding the skeleton back in,
which is what this module exists to do.

Skeletons can themselves chain to a parent skeleton via ``SKPD``; the loader
follows that chain and the first definition of each section wins.
"""

from __future__ import annotations

import dataclasses
import struct
from collections.abc import Callable

from ..chunks import Chunk, ChunkReader
from ..errors import MalformedFileError, UnsupportedFormatError
from . import schemas
from .model import AnimFileRef, _read_structs, external_sequences, tracks_in
from .types import Schema, StructReader, mark_external

KNOWN_SKEL_CHUNKS = {"SKL1", "SKA1", "SKB1", "SKS1", "SKPD", "AFID", "BFID"}


@dataclasses.dataclass
class Skeleton:
    """Everything a ``.skel`` can contribute to an M2."""

    name: str = ""
    flags: int = 0
    bones: list[dict] = dataclasses.field(default_factory=list)
    key_bone_lookup: list[int] = dataclasses.field(default_factory=list)
    attachments: list[dict] = dataclasses.field(default_factory=list)
    attachment_lookup: list[int] = dataclasses.field(default_factory=list)
    global_loops: list[int] = dataclasses.field(default_factory=list)
    sequences: list[dict] = dataclasses.field(default_factory=list)
    sequence_lookups: list[int] = dataclasses.field(default_factory=list)
    parent_skel_file_id: int = 0
    anim_file_ids: list[AnimFileRef] = dataclasses.field(default_factory=list)
    bone_file_ids: list[int] = dataclasses.field(default_factory=list)
    sequence_schema: Schema = schemas.SEQUENCE_272

    def merge_parent(self, parent: Skeleton) -> None:
        """Fill in sections this skeleton does not define itself."""
        for field in ("bones", "key_bone_lookup", "attachments", "attachment_lookup",
                      "global_loops", "sequences", "sequence_lookups",
                      "anim_file_ids", "bone_file_ids"):
            if not getattr(self, field):
                setattr(self, field, getattr(parent, field))
        if not self.name:
            self.name = parent.name

    def settle_external(self) -> None:
        """Mark the bone and attachment keyframes that live in ``.anim`` files.

        The sequences decide, and a skeleton's sequences may come from its
        parent, so this runs once the sections are final.  Until then an
        external sub-array was read out of this file at an offset that means
        something only inside the ``.anim`` -- and in a skeleton whose bone
        chunk runs to megabytes, that offset almost always lands on bytes that
        parse as keyframes instead of failing.
        """
        external = external_sequences(self.sequences, chunked=True)
        if external:
            for track in tracks_in(self.bones, self.attachments):
                mark_external(track, external)


def _candidate_views(whole: bytes, chunk: Chunk) -> list[bytes]:
    """Buffers to try when resolving a chunk's internal offsets.

    ``.skel`` offsets are relative to the start of the chunk's payload, but
    files written by third-party tooling sometimes include the 8-byte chunk
    header in the base.  Trying both costs nothing and avoids rejecting an
    otherwise fine skeleton.
    """
    views = [chunk.data]
    header_start = max(0, chunk.offset - 8)
    views.append(whole[header_start : chunk.offset + chunk.size])
    return views


def _read_section(whole: bytes, chunk: Chunk, name: str,
                  parse: Callable[[StructReader, bytes], None]) -> None:
    errors = []
    for view in _candidate_views(whole, chunk):
        sr = StructReader(view, f"{name}:{chunk.name}")
        try:
            parse(sr, view)
            return
        except (MalformedFileError, ValueError, struct.error) as exc:
            errors.append(str(exc))
    raise MalformedFileError(
        f"{name}: could not resolve offsets inside {chunk.name} ({'; '.join(errors)})"
    )


def parse_skel(data: bytes, name: str = "<skel>") -> Skeleton:
    """Parse one ``.skel`` file (without following its parent chain)."""
    if len(data) < 8:
        raise MalformedFileError(f"{name}: file is only {len(data)} bytes")

    reader = ChunkReader.auto(data, KNOWN_SKEL_CHUNKS, name=name)
    chunks = {c.name: c for c in reader}
    if "SKL1" not in chunks and "SKB1" not in chunks:
        raise UnsupportedFormatError(
            f"{name}: not a .skel file (no SKL1/SKB1 chunk)")

    skel = Skeleton()

    if (c := chunks.get("SKL1")) is not None:
        skel.flags = struct.unpack_from("<I", c.data, 0)[0]

        def parse_skl1(sr: StructReader, view: bytes) -> None:
            skel.name = sr.read_string_array(4)

        _read_section(data, c, name, parse_skl1)

    if (c := chunks.get("SKB1")) is not None:
        def parse_skb1(sr: StructReader, view: bytes) -> None:
            skel.bones = _read_structs(sr, schemas.BONE, view, 0)
            skel.key_bone_lookup = sr.read_array("u16", 8)

        _read_section(data, c, name, parse_skb1)

    if (c := chunks.get("SKA1")) is not None:
        def parse_ska1(sr: StructReader, view: bytes) -> None:
            skel.attachments = _read_structs(sr, schemas.ATTACHMENT, view, 0)
            skel.attachment_lookup = sr.read_array("u16", 8)

        _read_section(data, c, name, parse_ska1)

    if (c := chunks.get("SKS1")) is not None:
        def parse_sks1(sr: StructReader, view: bytes) -> None:
            skel.global_loops = sr.read_array("u32", 0)
            skel.sequences = _read_structs(sr, schemas.SEQUENCE_272, view, 8)
            skel.sequence_lookups = sr.read_array("u16", 16)

        _read_section(data, c, name, parse_sks1)

    if (c := chunks.get("SKPD")) is not None and len(c.data) >= 12:
        skel.parent_skel_file_id = struct.unpack_from("<I", c.data, 8)[0]

    if (c := chunks.get("AFID")) is not None:
        n = len(c.data) // 8
        skel.anim_file_ids = [
            AnimFileRef(*struct.unpack_from("<HHI", c.data, i * 8)) for i in range(n)
        ]

    if (c := chunks.get("BFID")) is not None:
        n = len(c.data) // 4
        skel.bone_file_ids = list(struct.unpack_from("<" + "I" * n, c.data, 0)) if n else []

    skel.settle_external()
    return skel


def load_skeleton_chain(loader: Callable[[int], bytes | None], file_id: int,
                        name: str = "<skel>", max_depth: int = 8) -> Skeleton | None:
    """Load a skeleton and flatten its ``SKPD`` parent chain.

    ``loader`` maps a FileDataID to bytes, or returns ``None`` when the file is
    not available; a missing parent degrades to whatever the child defines
    rather than failing the whole model.
    """
    seen: set[int] = set()
    root: Skeleton | None = None
    current_id = file_id
    depth = 0
    while current_id and current_id not in seen and depth < max_depth:
        seen.add(current_id)
        raw = loader(current_id)
        if raw is None:
            break
        skel = parse_skel(raw, f"{name}#{current_id}")
        if root is None:
            root = skel
        else:
            root.merge_parent(skel)
        current_id = skel.parent_skel_file_id
        depth += 1
    if root is not None:
        root.settle_external()
    return root
