"""Splitting a WMO group that outgrew 16-bit indices.

``MOVI`` stores triangle indices as ``uint16``, so a 3.3.5a group can address
at most 65 536 vertices. Shadowlands introduced ``MOVX`` with 32-bit indices
precisely because groups had grown past that, and those groups cannot be
narrowed -- but a WMO is a *collection* of groups, and nothing stops it having
more of them. So an oversized group is split into several, and the root file is
updated to reference them.

That makes the fix self-contained: the result is one WMO with more groups, not
a set of files the user has to wire up. Each part gets its own vertex arrays,
its own render batches with recomputed bounds, and a freshly built collision
tree, because the original tree indexes triangle numbers the split invalidates.
"""

from __future__ import annotations

import dataclasses
import struct
from collections.abc import Sequence

from ..limits import WMO_MAX_GROUP_VERTICES
from .bsp import build_bsp

MOBA_SIZE = 24
VERTEX_SIZE = 12
NORMAL_SIZE = 12
UV_SIZE = 8
COLOR_SIZE = 4
POLY_SIZE = 2


@dataclasses.dataclass
class Geometry:
    """A group's per-vertex and per-triangle arrays, unpacked for splitting."""

    vertices: list[bytes] = dataclasses.field(default_factory=list)
    normals: list[bytes] = dataclasses.field(default_factory=list)
    uvs: list[list[bytes]] = dataclasses.field(default_factory=list)
    colors: list[list[bytes]] = dataclasses.field(default_factory=list)
    triangles: list[tuple[int, int, int]] = dataclasses.field(default_factory=list)
    polys: list[bytes] = dataclasses.field(default_factory=list)
    batches: list[bytes] = dataclasses.field(default_factory=list)

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    def positions(self) -> list[tuple[float, float, float]]:
        return [struct.unpack("<3f", v) for v in self.vertices]


def unpack(vertices: bytes, normals: bytes, uv_layers: Sequence[bytes],
           colour_layers: Sequence[bytes], indices: Sequence[int],
           polys: bytes, batches: bytes) -> Geometry:
    """Turn the raw chunk payloads into per-element lists."""
    geo = Geometry()
    geo.vertices = [vertices[i:i + VERTEX_SIZE]
                    for i in range(0, len(vertices) - VERTEX_SIZE + 1, VERTEX_SIZE)]
    geo.normals = [normals[i:i + NORMAL_SIZE]
                   for i in range(0, len(normals) - NORMAL_SIZE + 1, NORMAL_SIZE)]
    geo.uvs = [[layer[i:i + UV_SIZE]
                for i in range(0, len(layer) - UV_SIZE + 1, UV_SIZE)]
               for layer in uv_layers]
    geo.colors = [[layer[i:i + COLOR_SIZE]
                   for i in range(0, len(layer) - COLOR_SIZE + 1, COLOR_SIZE)]
                  for layer in colour_layers]
    geo.triangles = [tuple(indices[i:i + 3])  # type: ignore[misc]
                     for i in range(0, len(indices) - 2, 3)]
    geo.polys = [polys[i:i + POLY_SIZE]
                 for i in range(0, len(polys) - POLY_SIZE + 1, POLY_SIZE)]
    geo.batches = [batches[i:i + MOBA_SIZE]
                   for i in range(0, len(batches) - MOBA_SIZE + 1, MOBA_SIZE)]
    return geo


@dataclasses.dataclass
class Part:
    """One output group produced from a split."""

    vertices: bytes = b""
    normals: bytes = b""
    uvs: list[bytes] = dataclasses.field(default_factory=list)
    colors: list[bytes] = dataclasses.field(default_factory=list)
    indices: list[int] = dataclasses.field(default_factory=list)
    polys: bytes = b""
    batches: bytes = b""
    mobn: bytes = b""
    mobr: bytes = b""
    bounding_box: tuple = (0.0,) * 6
    vertex_count: int = 0
    triangle_count: int = 0


def _triangle_groups(geo: Geometry) -> list[list[int]]:
    """Bundle triangles by render batch, so a batch never straddles a part."""
    assigned: set[int] = set()
    groups: list[list[int]] = []
    for batch in geo.batches:
        start_index, count = struct.unpack_from("<IH", batch, 12)
        first = start_index // 3
        last = min(len(geo.triangles), (start_index + count + 2) // 3)
        faces = [f for f in range(first, last) if f not in assigned]
        assigned.update(faces)
        if faces:
            groups.append(faces)
    # Triangles no batch draws are collision geometry; they still need a home.
    leftover = [f for f in range(len(geo.triangles)) if f not in assigned]
    if leftover:
        groups.append(leftover)
    return groups


def _distinct_vertices(geo: Geometry, faces: Sequence[int]) -> set[int]:
    out: set[int] = set()
    for face in faces:
        out.update(geo.triangles[face])
    return out


def plan_parts(geo: Geometry, limit: int = WMO_MAX_GROUP_VERTICES
               ) -> list[list[int]]:
    """Partition triangles so no part references more than ``limit`` vertices."""
    parts: list[list[int]] = []
    current: list[int] = []
    current_vertices: set[int] = set()

    for group in _triangle_groups(geo):
        needed = _distinct_vertices(geo, group)
        if len(needed) > limit:
            # A single batch too large for one part: break it up by triangle,
            # which costs a few duplicated vertices along the seam.
            if current:
                parts.append(current)
                current, current_vertices = [], set()
            chunk: list[int] = []
            chunk_vertices: set[int] = set()
            for face in group:
                face_vertices = set(geo.triangles[face])
                if chunk and len(chunk_vertices | face_vertices) > limit:
                    parts.append(chunk)
                    chunk, chunk_vertices = [], set()
                chunk.append(face)
                chunk_vertices |= face_vertices
            if chunk:
                parts.append(chunk)
            continue

        if current and len(current_vertices | needed) > limit:
            parts.append(current)
            current, current_vertices = [], set()
        current.extend(group)
        current_vertices |= needed

    if current:
        parts.append(current)
    return parts or [[]]


def _batches_for(geo: Geometry, faces: Sequence[int],
                 remap: dict[int, int], positions: list[tuple[float, float, float]],
                 index_of_face: dict[int, int]) -> bytes:
    """Rebuild the render batches that survive into this part."""
    face_set = set(faces)
    out = bytearray()
    for batch in geo.batches:
        start_index, count = struct.unpack_from("<IH", batch, 12)
        first = start_index // 3
        last = min(len(geo.triangles), (start_index + count + 2) // 3)
        kept = [f for f in range(first, last) if f in face_set]
        if not kept:
            continue
        # The partitioner keeps a batch's triangles together and in order, so
        # they stay contiguous in the part's index buffer.
        positions_in_part = [index_of_face[f] for f in kept]
        new_start = min(positions_in_part) * 3
        new_count = len(kept) * 3

        lo = [32767, 32767, 32767]
        hi = [-32768, -32768, -32768]
        used: list[int] = []
        for face in kept:
            for vertex in geo.triangles[face]:
                used.append(remap[vertex])
                x, y, z = positions[vertex]
                for axis, value in enumerate((x, y, z)):
                    lo[axis] = min(lo[axis], int(value) - 1)
                    hi[axis] = max(hi[axis], int(value) + 1)

        record = bytearray(batch)
        clamp = lambda v: max(-32768, min(32767, v))  # noqa: E731
        struct.pack_into("<6h", record, 0, clamp(lo[0]), clamp(lo[1]),
                         clamp(lo[2]), clamp(hi[0]), clamp(hi[1]), clamp(hi[2]))
        struct.pack_into("<IHHH", record, 12, new_start, new_count,
                         min(used), max(used))
        out += record
    return bytes(out)


def split(geo: Geometry, limit: int = WMO_MAX_GROUP_VERTICES) -> list[Part]:
    """Split ``geo`` into parts that each fit inside 16-bit indices."""
    positions = geo.positions()
    parts: list[Part] = []

    for faces in plan_parts(geo, limit):
        part = Part()
        remap: dict[int, int] = {}
        vertices = bytearray()
        normals = bytearray()
        uvs = [bytearray() for _ in geo.uvs]
        colors = [bytearray() for _ in geo.colors]
        polys = bytearray()
        indices: list[int] = []
        index_of_face: dict[int, int] = {}
        lo = [float("inf")] * 3
        hi = [float("-inf")] * 3

        for position, face in enumerate(faces):
            index_of_face[face] = position
            for vertex in geo.triangles[face]:
                new = remap.get(vertex)
                if new is None:
                    new = len(remap)
                    remap[vertex] = new
                    vertices += geo.vertices[vertex]
                    if vertex < len(geo.normals):
                        normals += geo.normals[vertex]
                    for layer, source in enumerate(geo.uvs):
                        if vertex < len(source):
                            uvs[layer] += source[vertex]
                    for layer, source in enumerate(geo.colors):
                        if vertex < len(source):
                            colors[layer] += source[vertex]
                    x, y, z = positions[vertex]
                    for axis, value in enumerate((x, y, z)):
                        lo[axis] = min(lo[axis], value)
                        hi[axis] = max(hi[axis], value)
                indices.append(new)
            if face < len(geo.polys):
                polys += geo.polys[face]
            else:
                polys += b"\0\0"

        part.vertices = bytes(vertices)
        part.normals = bytes(normals)
        part.uvs = [bytes(layer) for layer in uvs]
        part.colors = [bytes(layer) for layer in colors]
        part.indices = indices
        part.polys = bytes(polys)
        part.vertex_count = len(remap)
        part.triangle_count = len(faces)
        part.batches = _batches_for(geo, faces, remap, positions, index_of_face)
        part.bounding_box = (
            tuple(lo) + tuple(hi) if remap else (0.0,) * 6)  # type: ignore[assignment]

        local_positions = [(0.0, 0.0, 0.0)] * len(remap)
        for old, new in remap.items():
            local_positions[new] = positions[old]
        local_triangles = [tuple(indices[i:i + 3])  # type: ignore[misc]
                           for i in range(0, len(indices), 3)]
        part.mobn, part.mobr = build_bsp(local_positions, local_triangles)
        parts.append(part)

    return parts
